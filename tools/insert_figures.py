#!/usr/bin/env python3
"""이미지 없는 논문 문서에 핵심 그림(아키텍처/파이프라인)을 삽입한다.

fetch_figures.py로 arXiv HTML에서 메소드 그림 URL을 얻어, 기존 문서 관행대로
H1 바로 뒤에 삽입한다:
    # 제목 (venue)

    ![<이름> — figure](<url>)
    _<캡션>_

    ## 📋 Overview

핫링크만 한다(리포에 이미지 저장 안 함). 그림을 못 찾으면 건드리지 않는다.
--dry-run 으로 미리 본다.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from fetch_figures import best_figure  # noqa: E402

ARXIV = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})")


def has_image(txt: str) -> bool:
    return bool(re.search(r"!\[[^\]]*\]\(", txt))


def doc_arxiv(txt: str) -> str | None:
    m = re.search(r"\*\*Links\*\*:([^\n]+)", txt)
    if not m:
        return None
    a = ARXIV.search(m.group(1))
    return a.group(1) if a else None


def short_caption(cap: str) -> str:
    """'Figure 2 : ...' 접두 제거하고 깔끔한 한 문장으로."""
    cap = re.sub(r"^\s*(?:figure|fig\.?)\s*\d+\s*[:.]?\s*", "", cap, flags=re.I)
    cap = cap.split(". ")[0].strip()
    # 서브그림 라벨 제거로 생긴 빈 괄호·잔재 정리
    cap = re.sub(r"\(\s*\)", "", cap)  # 빈 괄호
    cap = re.sub(r"\s{2,}", " ", cap).strip(" ,;:")
    if len(cap) > 150:
        # 150자 넘으면 단어 경계에서 자르고 … 붙인다 (단어 중간 잘림 방지)
        cut = cap[:150].rsplit(" ", 1)[0].rstrip(" ,;:(")
        cap = cut + "…"
    return cap


def insert(path: pathlib.Path, dry: bool) -> str:
    txt = path.read_text(encoding="utf-8")
    if has_image(txt):
        return "skip:이미 이미지 있음"
    aid = doc_arxiv(txt)
    if not aid:
        return "skip:arXiv ID 없음"
    fig = best_figure(aid)
    if not fig:
        return "miss:그림 없음(HTML/figure 없음)"

    name = path.stem
    m = re.match(r"(#\s+.+?)\n", txt)
    if not m:
        return "skip:H1 없음"
    h1 = m.group(1)
    cap = short_caption(fig["caption"])
    block = f'\n\n![{name} — architecture]({fig["url"]})\n\n_{cap} (원논문 Fig. {fig["num"]})_'
    new = txt[: m.end(1)] + block + txt[m.end(1):]
    if dry:
        return f"would:{fig['url']}"
    path.write_text(new, encoding="utf-8")
    return f"ok:{fig['url']}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="특정 slug만 (쉼표)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sleep", type=float, default=1.5, help="arXiv 요청 간격")
    args = ap.parse_args()

    docs = [
        p
        for p in sorted(ROOT.glob("docs/*/*.md"))
        if p.name not in ("README.md", "paper-template.md", "papers-list.md")
    ]
    if args.only:
        want = set(args.only.split(","))
        docs = [p for p in docs if p.stem in want]
    # 이미지 없는 것만
    todo = [p for p in docs if not has_image(p.read_text(encoding="utf-8"))]
    if args.limit:
        todo = todo[: args.limit]

    print(f"이미지 없는 문서 {len(todo)}편 처리", file=sys.stderr)
    stats = {"ok": 0, "miss": 0, "skip": 0, "would": 0}
    misses = []
    for i, p in enumerate(todo, 1):
        r = insert(p, args.dry_run)
        tag = r.split(":", 1)[0]
        stats[tag] = stats.get(tag, 0) + 1
        if tag == "miss":
            misses.append(p.stem)
        print(f"  [{i}/{len(todo)}] {p.parent.name}/{p.stem}: {r[:70]}", file=sys.stderr)
        if tag in ("ok", "would", "miss"):
            time.sleep(args.sleep)
    print(f"\n{stats}", file=sys.stderr)
    if misses:
        print(f"그림 못 찾음({len(misses)}): {misses}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
