#!/usr/bin/env python3
"""arXiv HTML에서 논문의 핵심 그림(아키텍처/파이프라인/teaser) URL을 뽑는다.

논문 정리 페이지에 아키텍처·메소드 그림이 없으면 글만 있는 반쪽 페이지다.
기존 문서(vggt·pi3 등)는 저자 project page 이미지를 핫링크했다. 신규 문서는
그게 빠졌다. arXiv HTML(arxiv.org/html/<id>)의 그림은 모든 논문에 있고
안정적으로 핫링크되므로(검증됨: 200 image/png), 캡션으로 메소드 그림을 골라 쓴다.

⚠️ 그림을 리포에 저장하지 않는다 — 저자가 arXiv에 공개한 그림을 링크할 뿐이다
   (기존 54편과 동일한 핫링크 방식). 리포에 바이너리를 담지 않는다.

선택 규칙: 캡션에 architecture/pipeline/framework/overview/method/network 가
있는 그림 우선. 없으면 Figure 1(대개 teaser). 정성 결과(qualitative/comparison/
example) 그림은 배제한다.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request

UA = "DUSt3R-Paper-Collection/1.0 (github.com/minoTrey/DUSt3R-Paper-Collection)"

# 메소드/구조 그림일 가능성 (높을수록 우선)
METHOD_KW = re.compile(
    r"\b(architecture|pipeline|framework|overview|method|approach|network|"
    r"model|design|our\s+\w+\s+(?:framework|method|model|pipeline))\b",
    re.I,
)
# 배제: 정성 결과·비교·예시·데이터셋 그림
SKIP_KW = re.compile(
    r"\b(qualitative|comparison|example|gallery|visualization of results|"
    r"failure|ablation|dataset|gallery|more results|additional)\b",
    re.I,
)
FIG_NUM = re.compile(r"(?:figure|fig\.?)\s*(\d+)", re.I)


def fetch(url: str) -> tuple[str, str] | None:
    """(본문, 리다이렉트 후 최종 URL) — 상대 이미지 경로 해석의 기준."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read().decode("utf-8", "ignore"), r.geturl()
    except Exception:
        return None


def best_figure(arxiv_id: str) -> dict | None:
    """(url, caption, fignum) 반환. 없으면 None."""
    got = fetch(f"https://arxiv.org/html/{arxiv_id}")
    if not got:
        return None
    doc, base = got  # base = 버전 포함 최종 URL (예: .../html/2607.17803v1)
    # <figure>...</figure> 블록을 먼저 잘라, img·figcaption을 같은 블록 안에서 짝짓는다.
    # (전역 정규식은 페이지 아이콘 img를 엉뚱한 figcaption에 물린다.)
    figs = []
    for block in re.findall(r"<figure\b.*?</figure>", doc, re.S):
        cap_m = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", block, re.S)
        if not cap_m:
            continue
        raw = cap_m.group(1)
        # 태그를 공백 아닌 빈 문자열로 지운다 — <em>D</em>ynamic 이 "D ynamic"으로
        # 깨지는 것을 막는다. 태그 사이 글자를 붙인 뒤 공백 정규화.
        raw = re.sub(r"<[^>]+>", "", raw)
        cap = " ".join(html.unescape(raw).split())
        # 블록 내 실제 그림(png/jpg/svg) — arXiv 아이콘(/static/) 제외, 가장 큰 첫 것
        srcs = [
            s
            for s in re.findall(r'<img[^>]+src="([^"]+\.(?:png|jpg|jpeg|svg))"', block)
            if "/static/" not in s and "smiley" not in s
        ]
        if not srcs:
            continue
        src = srcs[0]
        # src 패턴이 두 가지다:
        #  - "2607.17803v1/x1.png" (id 포함) → arxiv.org/html/ 기준
        #  - "x2.png" / "figs/..." (버전 디렉터리 상대) → arxiv.org/html/<id>/ 기준
        if src.startswith("http"):
            url = src
        elif re.match(r"\d{4}\.\d{4,5}", src):
            url = "https://arxiv.org/html/" + src
        else:
            url = f"https://arxiv.org/html/{arxiv_id}/{src.lstrip('/')}"
        num_m = FIG_NUM.search(cap)
        num = int(num_m.group(1)) if num_m else 99
        figs.append({"url": url, "caption": cap, "num": num})
    if not figs:
        return None

    def score(f):
        c = f["caption"]
        s = 0
        if SKIP_KW.search(c):
            s -= 10
        if METHOD_KW.search(c):
            s += 5
        # Figure 1·2 가 대개 teaser·architecture
        if f["num"] == 1:
            s += 3
        elif f["num"] == 2:
            s += 2
        return s

    figs.sort(key=score, reverse=True)
    top = figs[0]
    if score(top) <= 0:  # 쓸 만한 게 없으면 Figure 1으로
        f1 = [f for f in figs if f["num"] == 1]
        top = f1[0] if f1 else figs[0]
    return top


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arxiv_ids", nargs="+", help="arXiv ID(들)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = {}
    for aid in args.arxiv_ids:
        r = best_figure(aid)
        out[aid] = r
        if not args.json:
            if r:
                print(f"{aid}\n  {r['url']}\n  Fig {r['num']}: {r['caption'][:90]}")
            else:
                print(f"{aid}  ❌ 그림 없음(HTML 없거나 figure 없음)")
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
