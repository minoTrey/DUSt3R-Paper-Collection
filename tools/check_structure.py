#!/usr/bin/env python3
"""논문 문서가 AGENTS.md의 7섹션 구조를 지키는지 검사한다. CI용.

이 검사가 없어서 섹션 이름과 순서가 4가지로 갈라져 있었다
(45편 / 8편 / 1편 / 1편). 구조는 사람이 눈으로 지킬 수 없다.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# AGENTS.md 규정. 순서까지 포함해 정본이다.
STD = [
    "📋 Overview",
    "🎯 Key Contributions",
    "🔧 Technical Details",
    "📊 Results",
    "💡 Insights & Impact",
    "🔗 Related Work",
    "📚 Key Takeaways",
]
# Overview 필수 키
REQUIRED = ["Authors", "Institution", "Venue", "Links", "TL;DR"]


def main() -> int:
    recs = json.loads(
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "extract_meta.py"), "--json"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    bad = 0
    for r in recs:
        errs = []
        if r["sections"] != STD:
            if set(r["sections"]) != set(STD):
                d = set(r["sections"]) ^ set(STD)
                errs.append(f"섹션 불일치: {sorted(d)}")
            else:
                errs.append("섹션 순서가 AGENTS.md와 다름")
        missing = [k for k in REQUIRED if k not in r["fields"]]
        if missing:
            errs.append(f"Overview 필수 키 누락: {missing}")
        if "Institutions" in r["fields"]:
            errs.append("`Institutions` → `Institution` (단수형)")
        if not r["arxiv_id"] and "arxiv" in (r["fields"].get("Links") or "").lower():
            errs.append("Links에 arXiv 링크가 있으나 ID를 파싱할 수 없음")
        if errs:
            bad += 1
            print(f"❌ {r['file']}", file=sys.stderr)
            for e in errs:
                print(f"     {e}", file=sys.stderr)

    if bad:
        print(f"\n{bad}/{len(recs)}편 위반. AGENTS.md 참조.", file=sys.stderr)
        return 1
    print(f"✅ {len(recs)}편 전부 구조 정합")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
