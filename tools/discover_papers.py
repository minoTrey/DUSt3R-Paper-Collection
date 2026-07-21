#!/usr/bin/env python3
"""새 논문 발굴 — DUSt3R/후속을 초석으로 하는 feed-forward 3D recon 논문.

두 소스의 합집합으로 후보를 모은다:
  1. Semantic Scholar 피인용: DUSt3R·VGGT·MASt3R·π³ 등 앵커 논문을 인용한 논문.
     (3R 이름이 아니어도 이들을 초석으로 하면 잡힌다 — 이게 핵심 요구사항이다.)
  2. arXiv 키워드: cs.CV 최신 중 pointmap/feed-forward 3D reconstruction/*3R.

기존 사실 카드의 arxiv_id와 대조해 신규만 candidates/queue.jsonl 에 append.
PDF·문서는 만들지 않는다 — 사람/에이전트 승인 후 add-paper 흐름을 탄다.

⚠️ 이건 '발굴'이지 '추가'가 아니다. 후보를 큐에 쌓는 것까지만.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FACTS = ROOT / "raw" / "facts"
CAND = ROOT / "candidates"
QUEUE = CAND / "queue.jsonl"
UA = "DUSt3R-Paper-Collection-discover/1.0 (github.com/minoTrey/DUSt3R-Paper-Collection)"

# 피인용을 추적할 앵커 논문 (이들을 초석으로 하는 후속을 발굴)
ANCHORS = {
    "dust3r": "2312.14132",
    "mast3r": "2406.09756",
    "vggt": "2503.11651",
    "pi3": "2507.13347",
    "cut3r": "2501.12387",
    "fast3r": "2501.13928",
}
# arXiv 키워드 (3R 이름 밖의 것까지 잡는 그물)
KW = [
    "feed-forward 3D reconstruction",
    "pointmap",
    "visual geometry transformer",
    "uncalibrated 3D reconstruction",
]
VENUE_HINT = re.compile(r"3R\b|pointmap|feed-?forward|uncalibrated|geometry transformer", re.I)


def http_json(url: str, tries: int = 3) -> dict | None:
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read())
        except Exception as e:
            if i < tries - 1:
                time.sleep(4 * (i + 1))
            else:
                print(f"    ⚠️ 실패: {e}", file=sys.stderr)
    return None


def known_ids() -> set[str]:
    ids = set()
    for p in FACTS.glob("*.json"):
        aid = json.loads(p.read_text()).get("arxiv_id")
        if aid:
            ids.add(aid)
    return ids


def from_citations(known: set[str]) -> dict[str, dict]:
    """앵커 논문을 인용한 논문들 (Semantic Scholar)."""
    found = {}
    fields = "title,externalIds,year,publicationDate"
    for name, aid in ANCHORS.items():
        url = (
            f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{aid}/citations"
            f"?fields={fields}&limit=200"
        )
        data = http_json(url)
        time.sleep(2)
        if not data:
            continue
        for item in data.get("data", []):
            cp = item.get("citingPaper", {})
            ext = cp.get("externalIds") or {}
            cid = ext.get("ArXiv")
            if not cid or cid in known or cid in found:
                continue
            title = cp.get("title") or ""
            # DUSt3R 계열일 개연성: 제목에 관련 키워드가 있거나 3R 이름
            if VENUE_HINT.search(title) or re.search(r"3R\b", title):
                found[cid] = {
                    "arxiv_id": cid,
                    "title": title,
                    "date": cp.get("publicationDate") or str(cp.get("year") or ""),
                    "via": f"cites:{name}",
                    "status": "new",
                }
        print(f"  피인용 {name}: 누적 후보 {len(found)}", file=sys.stderr)
    return found


def from_arxiv(known: set[str], found: dict) -> dict:
    """arXiv 키워드 검색 (최근순)."""
    for kw in KW:
        q = urllib.parse.quote(f'all:"{kw}"')
        url = (
            f"https://export.arxiv.org/api/query?search_query={q}"
            f"&sortBy=submittedDate&sortOrder=descending&max_results=40"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                xml = r.read().decode()
        except Exception as e:
            print(f"    ⚠️ arXiv {kw}: {e}", file=sys.stderr)
            continue
        for m in re.finditer(
            r"<id>http://arxiv\.org/abs/([\d.]+)v?\d*</id>.*?<title>(.*?)</title>",
            xml,
            re.S,
        ):
            cid, title = m.group(1), " ".join(m.group(2).split())
            if cid in known or cid in found:
                continue
            found[cid] = {
                "arxiv_id": cid,
                "title": title,
                "date": "",
                "via": f"kw:{kw[:20]}",
                "status": "new",
            }
        time.sleep(3.5)
        print(f"  키워드 '{kw[:24]}': 누적 후보 {len(found)}", file=sys.stderr)
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-arxiv", action="store_true", help="피인용만")
    ap.add_argument("--limit", type=int, default=0, help="후보 상한(테스트)")
    args = ap.parse_args()

    CAND.mkdir(exist_ok=True)
    known = known_ids()
    print(f"기지 논문 {len(known)}편. 발굴 시작…", file=sys.stderr)

    found = from_citations(known)
    if not args.no_arxiv:
        found = from_arxiv(known, found)

    # 기존 큐와 병합 (중복 방지)
    existing = set()
    if QUEUE.exists():
        for line in QUEUE.read_text().splitlines():
            if line.strip():
                existing.add(json.loads(line)["arxiv_id"])
    new = [v for k, v in found.items() if k not in existing]
    if args.limit:
        new = new[: args.limit]

    with QUEUE.open("a") as f:
        for rec in new:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    (CAND / "last_run.txt").write_text(dt.date.today().isoformat())

    print(f"\n✅ 신규 후보 {len(new)}편 → candidates/queue.jsonl", file=sys.stderr)
    for rec in new[:15]:
        print(f"   {rec['arxiv_id']}  [{rec['via']}]  {rec['title'][:60]}", file=sys.stderr)
    if len(new) > 15:
        print(f"   … 외 {len(new) - 15}편", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
