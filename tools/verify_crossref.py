#!/usr/bin/env python3
"""문서 간 정합성을 검사한다 — 사실 카드(raw/facts/) 기반.

verify_benchmarks 는 한 문서 안의 수치만 본다. 이 도구는 그 사각지대,
'문서 A가 문서 B를 언급할 때 B의 사실과 일치하는가'를 본다.

A1 참조 정합성: 논문 X를 링크한 곳의 venue 표기가 X 자기 문서의 정본 venue와
   같은가. (예: vggt를 "CVPR 2024"로 인용했는데 vggt 문서는 "CVPR 2025")
A2 수치 귀속: 논문 X를 링크하며 그 옆에 적은 수치가 X 자기 문서의 표에
   존재하는가. (다른 논문 표에서 빌려온 값·오타를 잡는다)

⚠️ "틀렸다"가 아니라 "대상 문서와 어긋난다"를 보고한다. 파생·요약 문맥의
   오탐이 있을 수 있어 판단은 사람이 한다. --check 는 CI용(엄격).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FACTS = ROOT / "raw" / "facts"

VENUE = re.compile(
    r"\b(CVPR|ICCV|ECCV|NeurIPS|NIPS|ICLR|ICML|3DV|WACV|SIGGRAPH|RA-L|ICRA|IROS|"
    r"ACM MM|ICASSP|MICCAI|TPAMI|IJCV|AAAI|CoRL|RSS|BMVC)\b\s*'?(\d{2,4})?",
    re.I,
)
NUM = re.compile(r"\d+\.\d+")


def load_cards() -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text()) for p in FACTS.glob("*.json")}


def venue_key(v: str) -> tuple[str, str] | None:
    m = VENUE.search(v or "")
    if not m:
        return None
    name = m.group(1).upper().replace("NIPS", "NEURIPS")
    yr = m.group(2) or ""
    if len(yr) == 2:
        yr = "20" + yr
    return name, yr


def own_table_values(card: dict) -> set[str]:
    vals = set()
    for t in card.get("tables", []):
        for row in t.get("rows", []):
            for cell in row:
                vals.update(NUM.findall(cell))
    return vals


def own_method_values(card: dict) -> set[str]:
    """자기 이름 행의 수치만 (그 논문 '자신의' 성능)."""
    nm = re.sub(r"[^a-z0-9]", "", (card.get("name") or "").lower())
    vals = set()
    if not nm:
        return vals
    for t in card.get("tables", []):
        for row in t.get("rows", []):
            if row and nm in re.sub(r"[^a-z0-9]", "", row[0].lower()):
                for cell in row[1:]:
                    vals.update(NUM.findall(cell))
    return vals


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    cards = load_cards()
    path2slug = {pathlib.Path(c["file"]).name: s for s, c in cards.items()}

    a1, a2 = [], []
    for s, c in cards.items():
        txt = (ROOT / c["file"]).read_text(encoding="utf-8")

        # A1: 링크 뒤 45자의 venue 표기 vs 대상 정본
        for m in re.finditer(r"\[[^\]]+\]\(([^)]*?([a-z0-9._-]+\.md))\)", txt):
            tgt = path2slug.get(m.group(2))
            if not tgt or tgt == s:
                continue
            canon = venue_key(cards[tgt]["venue"])
            cited = venue_key(txt[m.end() : m.end() + 45])
            if canon and cited and canon[0] != "ARXIV":
                if cited[0] != canon[0] or (cited[1] and canon[1] and cited[1] != canon[1]):
                    a1.append((s, tgt, f"{cited} vs 정본 {canon}"))

        # A2: 링크 + 60자 내 수치가 대상 자기 표에 있나
        for m in re.finditer(
            r"\[[^\]]+\]\(([^)]*?([a-z0-9._-]+\.md))\)[^.\n|]{0,60}?(\d+\.\d+)", txt
        ):
            tgt = path2slug.get(m.group(2))
            if not tgt or tgt == s:
                continue
            num = m.group(3)
            tv = own_table_values(cards[tgt])
            if tv and num not in tv:
                a2.append((s, tgt, num, txt[m.start() : m.start() + 65].replace("\n", " ")))

    print(f"A1 참조 venue 불일치: {len(a1)}건", file=sys.stderr)
    for s, t, d in a1[:15]:
        print(f"   {s} → {t}: {d}", file=sys.stderr)
    print(f"A2 수치 귀속 의심: {len(a2)}건", file=sys.stderr)
    for s, t, n, ctx in a2[:15]:
        print(f"   {s} inv {t} '{n}' | {ctx[:55]}", file=sys.stderr)

    if args.check and a1:  # A2는 오탐이 많아 경고만, A1만 CI 차단
        print("\n❌ 문서 간 venue 인용이 정본과 다르다. 인용 쪽을 고쳐라.", file=sys.stderr)
        return 1
    if not a1 and not a2:
        print("✅ 문서 간 정합성 이상 없음")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
