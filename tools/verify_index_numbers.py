#!/usr/bin/env python3
"""README와 카테고리 README의 수치가 개별 논문 문서에 실재하는지 검사한다.

⚠️ 이 검사가 없어서 루트 README의 대표 비교표가 오랫동안 날조된 상태로 남아 있었다.
개별 논문 문서(`vggt.md` 등)에서 잘못된 수치를 걷어냈지만 README에 복사된 사본은
그대로 살아 있었다. `verify_benchmarks.py`가 `docs/*/*.md`만 보고 README를
건너뛰었기 때문이다.

원리: 색인 문서(README)는 1차 출처가 아니다. 거기 적힌 모든 수치는 개별 논문
문서 어딘가에 있어야 한다. 개별 문서는 이미 원논문 PDF와 대조돼 있으므로,
"README 수치 ⊆ 논문 문서 수치"가 성립하면 README도 원문까지 추적된다.

한계: 문서 간 합산·평균 같은 파생값은 잡지 못한다. README에 파생값을 쓰지 마라.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NUM = re.compile(r"(?<![\w.])(\d{1,4}\.\d{1,4})(?![\w.])")
# 배지·URL·날짜는 수치가 아니다
SKIP_LINE = re.compile(r"img\.shields\.io|https?://|^\s*<|badge/", re.I)


def paper_numbers() -> set[str]:
    """개별 논문 문서 전체에 등장하는 수치. 이것이 허용 집합이다."""
    nums: set[str] = set()
    for p in ROOT.glob("docs/*/*.md"):
        if p.name == "README.md":
            continue
        for line in p.read_text(encoding="utf-8").split("\n"):
            if SKIP_LINE.search(line):
                continue
            nums.update(NUM.findall(line))
    return nums


def index_files() -> list[pathlib.Path]:
    out = [ROOT / "README.md"]
    out += sorted(ROOT.glob("docs/*/README.md"))
    return [p for p in out if p.exists()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="CI용: 불일치 시 non-zero")
    args = ap.parse_args()

    allowed = paper_numbers()
    bad = 0
    total = 0
    for p in index_files():
        hits = []
        for i, line in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
            if SKIP_LINE.search(line):
                continue
            for v in NUM.findall(line):
                total += 1
                if v not in allowed:
                    hits.append((i, v, line.strip()[:96]))
        if hits:
            bad += len(hits)
            print(f"\n❌ {p.relative_to(ROOT)}", file=sys.stderr)
            for i, v, ctx in hits[:20]:
                print(f"   L{i:<4} {v:>9}  | {ctx}", file=sys.stderr)
            if len(hits) > 20:
                print(f"   ... 외 {len(hits) - 20}건", file=sys.stderr)

    if bad:
        print(
            f"\n{bad}/{total}개 수치가 논문 문서에 없다. "
            f"색인은 1차 출처가 아니므로 개별 문서에서 가져오거나 지워야 한다.",
            file=sys.stderr,
        )
        return 1 if args.check else 0
    print(f"✅ 색인 수치 {total}개 전부 논문 문서에서 추적됨")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
