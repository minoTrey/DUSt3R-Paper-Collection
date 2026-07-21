#!/usr/bin/env python3
"""전체 검증 스위트를 한 번에 실행하고, 사각지대까지 명시한다.

--fast : 오프라인·결정론적 검사만 (CI에서 도는 것). 네트워크·PDF 불필요한 것 중심.
--full : PDF 대조(벤치·산문)와 링크 생존까지. 로컬에서 표를 건드렸을 때.

핵심 설계: 마지막에 '검증되지 않는 것'을 항상 출력한다. 커버리지 100%가
검증됐다는 뜻이 아니라는 걸 매 실행이 상기시킨다 — 이 리포가 사각지대마다
날조를 숨겨온 이력의 교훈이다.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

# (이름, argv, 네트워크 필요?, PDF 필요?)
CHECKS = [
    ("마크다운 구조/lint", ["npx", "markdownlint-cli2"], False, False),
    ("서식(prettier)", ["npx", "prettier", "--check", "**/*.md"], False, False),
    ("7섹션·Overview 스키마", ["python3", "tools/check_structure.py"], False, False),
    ("README 카운트", ["python3", "tools/update_stats.py", "--check"], False, False),
    ("papers-list·카테고리 목록", ["python3", "tools/build_papers_list.py", "--check"], False, False),
    ("색인 수치 추적", ["python3", "tools/verify_index_numbers.py", "--check"], False, False),
    ("사실 카드 정합", ["python3", "tools/build_fact_cards.py", "--check"], False, False),
    ("문서 간 참조(A1)", ["python3", "tools/verify_crossref.py", "--check"], False, False),
    ("링크 생존(캐시)", ["python3", "tools/verify_links.py", "--check"], False, False),
    # --full 전용 (PDF/네트워크)
    ("벤치마크 수치(PDF)", ["python3", "tools/verify_benchmarks.py"], False, True),
    ("산문 배속(PDF)", ["python3", "tools/verify_prose_claims.py", "--check"], False, True),
    ("링크 생존(라이브)", ["python3", "tools/verify_links.py"], True, False),
]

BLIND_SPOTS = [
    "정수 지표: `verify_benchmarks.py --int` 로 별도 실행해야 본다 (기본은 소수만).",
    "수치 귀속(A2): 문맥 오탐이 많아 경고만. 사람이 원문 대조해야 확정.",
    "의미 정합: TL;DR↔본문, 요약의 정확성은 기계 검증 밖 (LLM/사람 필요).",
    "UNKNOWN venue: 1차 출처가 아직 없는 논문 — 학회 색인 대기 상태이지 검증 아님.",
    "소속: PDF 1페이지 저자 블록 대조는 했으나, 저자 순서·표기 변형은 놓칠 수 있다.",
]


def run(name, argv):
    r = subprocess.run(argv, capture_output=True, text=True)
    ok = r.returncode == 0
    mark = "✅" if ok else "❌"
    print(f"{mark} {name}")
    if not ok:
        tail = (r.stderr or r.stdout).strip().splitlines()[-6:]
        for line in tail:
            print(f"      {line}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="PDF·네트워크 검사 포함")
    args = ap.parse_args()

    print("=== 검증 스위트 ===\n")
    failed = 0
    for name, argv, needs_net, needs_pdf in CHECKS:
        if not args.full and (needs_net or needs_pdf):
            print(f"⏭️  {name} (--full 에서만)")
            continue
        if not run(name, argv):
            failed += 1

    print("\n=== ⚠️ 검증되지 않는 것 (사각지대) ===")
    for b in BLIND_SPOTS:
        print(f"  · {b}")

    print()
    if failed:
        print(f"❌ {failed}개 검사 실패")
        return 1
    print("✅ 실행된 검사 전부 통과")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
