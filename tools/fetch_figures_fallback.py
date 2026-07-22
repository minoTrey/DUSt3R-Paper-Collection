#!/usr/bin/env python3
"""arXiv HTML이 없는 논문의 핵심 그림을 project page / GitHub README에서 찾는다.

fetch_figures.py 는 arxiv.org/html 을 쓰지만, 최신(아직 HTML 미생성) 논문은
그게 404다. 그런 논문은 저자 project page의 og:image(대개 teaser/pipeline)나
GitHub README의 첫 그림이 유일한 출처다.

우선순위: (1) project page og:image → (2) project page teaser/pipeline 이미지
→ (3) GitHub README 첫 그림. 모두 실제로 200 + image 컨텐트타입인지 검증한다.

⚠️ 핫링크만 한다(리포에 이미지 저장 안 함). 기존 관행과 동일.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (DUSt3R-Paper-Collection; github.com/minoTrey/DUSt3R-Paper-Collection)"

# teaser/pipeline/architecture 로 보이는 파일명 (우선순위 높음)
GOOD_IMG = re.compile(
    r"(teaser|pipeline|architecture|overview|method|framework|model|main|"
    r"fig1|figure1|fig_1|banner|approach)", re.I
)
IMG_EXT = re.compile(r"\.(png|jpg|jpeg|webp)(\?|$)", re.I)


def fetch(url: str, binary: bool = False):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as r:
            if binary:
                return r.headers.get("Content-Type", ""), r.geturl()
            return r.read().decode("utf-8", "ignore"), r.geturl()
    except Exception:
        return None


def is_image(url: str) -> bool:
    got = fetch(url, binary=True)
    if not got:
        return False
    ctype, _ = got
    return ctype.startswith("image/")


def from_project(url: str) -> list[str]:
    """project page에서 이미지 후보 URL들을 우선순위대로."""
    got = fetch(url)
    if not got:
        return []
    doc, base = got
    cands: list[str] = []
    # 1) og:image (가장 신뢰도 높음 — 저자가 대표 이미지로 지정)
    for m in re.finditer(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', doc, re.I
    ):
        cands.append(urllib.parse.urljoin(base, m.group(1)))
    # 2) 본문 <img> 중 파일명이 teaser/pipeline 류
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', doc, re.I)
    good = [urllib.parse.urljoin(base, s) for s in imgs if GOOD_IMG.search(s) and IMG_EXT.search(s)]
    other = [urllib.parse.urljoin(base, s) for s in imgs if IMG_EXT.search(s)]
    cands += good + other
    # 중복 제거(순서 유지)
    seen, out = set(), []
    for c in cands:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def gh_readme_imgs(repo_url: str) -> list[str]:
    """github.com/<owner>/<repo> → README의 이미지 URL들(raw로 해석)."""
    m = re.search(r"github\.com/([^/]+)/([^/#?]+)", repo_url)
    if not m:
        return []
    owner, repo = m.group(1), m.group(2).rstrip("/")
    for branch in ("main", "master"):
        raw_base = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"
        got = fetch(raw_base + "README.md")
        if not got:
            continue
        doc, _ = got
        srcs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", doc)  # 마크다운 이미지
        srcs += re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', doc, re.I)  # HTML 이미지
        cands = []
        for s in srcs:
            s = s.split(" ")[0].strip()
            if not IMG_EXT.search(s):
                continue
            if s.startswith("http"):
                cands.append(s)
            else:
                cands.append(raw_base + s.lstrip("./"))
        good = [c for c in cands if GOOD_IMG.search(c)]
        other = [c for c in cands if not GOOD_IMG.search(c)]
        ordered = good + other
        if ordered:
            return ordered
    return []


def best(project: str | None, github: str | None) -> str | None:
    for cand in (from_project(project) if project else []):
        if is_image(cand):
            return cand
    for cand in (gh_readme_imgs(github) if github else []):
        if is_image(cand):
            return cand
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    # slug\tproject\tgithub 를 stdin 으로
    args = ap.parse_args()
    out = {}
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        slug = parts[0]
        project = parts[1] if len(parts) > 1 and parts[1] else None
        github = parts[2] if len(parts) > 2 and parts[2] else None
        url = best(project, github)
        out[slug] = url
        print(f"{slug}\t{url or 'MISS'}", file=sys.stderr)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
