#!/usr/bin/env python3
"""검증 결과를 문서에 반영한다. AGENTS.md의 Venue 표기법을 강제한다.

기본은 dry-run이다. --write 를 줘야 실제로 쓴다.
CONFIRMED만 자동 반영하고, LIKELY 이하는 사람이 판단하도록 보고만 한다.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# 긴 이름 → AGENTS.md 규정 약칭
ABBREV = {
    "computer vision and pattern recognition": "CVPR",
    "international conference on computer vision": "ICCV",
    "european conference on computer vision": "ECCV",
    "neural information processing systems": "NeurIPS",
    "neurips": "NeurIPS",
    "international conference on learning representations": "ICLR",
    "international conference on machine learning": "ICML",
    "international conference on 3d vision": "3DV",
    "int conf 3d vis": "3DV",
    "3dv": "3DV",
    "ieee robotics and automation letters": "RA-L",
    "ral": "RA-L",
    "acm multimedia": "ACM MM",
    "international conference on acoustics, speech and signal processing": "ICASSP",
    "icassp": "ICASSP",
    "ieee trans. image process.": "IEEE TIP",
    "ieee transactions on image processing": "IEEE TIP",
    "medical image computing and computer assisted intervention": "MICCAI",
}
# Venue 안에 섞여 있던 수상 표기 → Award 필드로 분리
AWARDS = re.compile(
    r"\(?\b(Oral(?:\s+Presentation)?|Spotlight|Highlight(?:\s+Paper)?|"
    r"Best\s+Paper(?:\s+Award)?|Best\s+Demo(?:\s+Honorable\s+Mention)?)\b\)?",
    re.I,
)


def canon(venue: str) -> str:
    """검증된 venue 문자열을 AGENTS.md 표기법으로 정규화."""
    v = venue.strip()
    m = re.search(r"\b(19|20)\d{2}\b", v)
    year = m.group(0) if m else ""
    name = v[: m.start()].strip() if m else v
    key = re.sub(r"[^a-z0-9 .]", "", name.lower()).strip()
    for long, short in ABBREV.items():
        if key == long or key.startswith(long):
            name = short
            break
    else:
        name = name.strip() or v
    if name.isupper() and name not in ABBREV.values():
        name = name.upper()
    return f"{name} {year}".strip()


def patch(path: pathlib.Path, venue: str, verdict: str, award: str | None) -> str | None:
    txt = path.read_text(encoding="utf-8")
    orig = txt

    def repl_venue(m: re.Match) -> str:
        return f"{m.group(1)}{venue}"

    txt, n = re.subn(
        r"^(\s*[-*]\s*\*\*Venue\*\*\s*:\s*).*$", repl_venue, txt, count=1, flags=re.M
    )
    if not n:
        return None

    today = dt.date.today().isoformat()
    ver_line = f"- **Verification**: {verdict} ({today})"
    if re.search(r"^\s*[-*]\s*\*\*Verification\*\*\s*:", txt, re.M):
        txt = re.sub(
            r"^\s*[-*]\s*\*\*Verification\*\*\s*:.*$", ver_line, txt, count=1, flags=re.M
        )
    else:  # TL;DR 앞에 삽입
        txt = re.sub(
            r"^(\s*[-*]\s*\*\*TL;DR\*\*)", ver_line + r"\n\1", txt, count=1, flags=re.M
        )

    if award:
        aline = f"- **Award**: {award}"
        if re.search(r"^\s*[-*]\s*\*\*Award\*\*\s*:", txt, re.M):
            txt = re.sub(
                r"^\s*[-*]\s*\*\*Award\*\*\s*:.*$", aline, txt, count=1, flags=re.M
            )
        else:  # Venue 바로 뒤
            txt = re.sub(
                r"^(\s*[-*]\s*\*\*Venue\*\*\s*:.*)$",
                r"\1\n" + aline,
                txt,
                count=1,
                flags=re.M,
            )

    # H1의 (venue) 도 맞춘다
    txt = re.sub(r"^(#\s+.*?)\s*\(([^)]*)\)\s*$", rf"\1 ({venue})", txt, count=1, flags=re.M)
    return txt if txt != orig else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="실제로 파일을 수정")
    ap.add_argument(
        "--include-likely", action="store_true", help="LIKELY도 반영 (기본: CONFIRMED만)"
    )
    args = ap.parse_args()

    V = json.loads((ROOT / "raw" / "verdicts.json").read_text())
    tiers = {"CONFIRMED"} | ({"LIKELY"} if args.include_likely else set())

    changed = skipped = 0
    for r in sorted(V, key=lambda x: x["file"]):
        if r["verdict"] not in tiers or not r.get("venue"):
            continue
        doc = r.get("doc_venue") or ""
        award = None
        am = AWARDS.search(doc)
        if am:
            award = am.group(1).strip()
        venue = canon(r["venue"])
        # 이미 같으면 건너뛴다 (수상 분리만 필요한 경우는 제외)
        cur = AWARDS.sub("", doc).replace("()", "").strip(" |()")
        if canon(cur) == venue and not award:
            skipped += 1
            continue
        p = ROOT / r["file"]
        new = patch(p, venue, r["verdict"], award)
        if new is None:
            continue
        changed += 1
        print(f"{'✏️ ' if args.write else '  '}{r['file']}")
        print(f"     Venue : {doc!r} → {venue!r}")
        if award:
            print(f"     Award : {award!r} (Venue에서 분리)")
        if args.write:
            p.write_text(new, encoding="utf-8")

    print(f"\n{'반영' if args.write else 'dry-run'}: {changed}건 변경, {skipped}건 이미 정합")
    if not args.write:
        print("실제 반영하려면 --write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
