#!/usr/bin/env python3
"""산문 속 배속·배수 주장(`45× faster`, `3× fewer` 등)을 원논문 PDF와 대조한다.

`verify_benchmarks.py`는 표 안의 수치만 본다. 배속 주장은 대개 표가 아니라
문장에 있고("VGGT보다 45× 빠르다"), 게다가 파생 배수라 표에도 없다. 이 도구가
그 사각지대를 메운다.

원리: 배속 주장의 배수(45)가 원논문 PDF에 배속 문맥(`45×`, `45x`, `45-fold`,
`45 times`)으로 존재하는지 본다. 없으면 문서가 계산했거나 지어낸 것이다.

⚠️ 이 도구도 "틀렸다"고 단정하지 않는다. "원문에서 못 찾았다"고만 말한다.
   정당한 미검출: 원문이 소수로 쓴 값(11.6× vs "11.6 times"), 범위 표기,
   저자가 초록에서만 언급한 값 등. 판단은 사람이 원문을 열어 한다.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "raw" / "pdftext"

# 성능 키워드가 배수 표기와 가까이 있는 것만 배속/개선 주장으로 본다.
# 해상도(512×512)·패치(9×9)·차원(3×3 SVD)을 배제하는 핵심 장치다.
KW = (
    r"faster|speedup|speed-up|acceleration|accelerat|reduction|reduce|fewer|"
    r"smaller|lower|higher|more efficient|less memory|compression|compress|"
    r"speed|throughput|shorter"
)
CLAIM = re.compile(
    rf"(\d+(?:\.\d+)?)\s*(?:[×x]|-fold\b|\s+times\b)\s+(?:\w+[\s,]+){{0,4}}?(?:{KW})"
    rf"|(?:{KW})\s+(?:\w+[\s,]+){{0,3}}?(\d+(?:\.\d+)?)\s*(?:[×x]|-fold|\s+times)",
    re.I,
)


def pdf_speedups(txt: str) -> set[str]:
    """PDF에 배속 문맥으로 등장하는 배수를 모은다.

    ⚠️ pdftotext는 `49×`를 `49 ×`로 띄우거나 줄바꿈으로 쪼갠다. `\\s*` 대신
    임의 공백(개행 포함)을 허용해야 실재하는 배속을 놓치지 않는다. 이걸 안 하면
    실제로 원문에 있는 `320×`·`>49 ×` 같은 값이 전부 오탐으로 뜬다.
    """
    flat = re.sub(r"\s+", " ", txt)  # 개행·다중공백을 단일 공백으로
    nums: set[str] = set()
    for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)\s?(?:[×x]|-?fold\b|times\b)", flat):
        v = m.group(1)
        nums.add(v)
        try:
            f = float(v)
        except ValueError:
            continue
        # 42.0 ↔ 42, 소수 반올림 흡수
        nums.add(f"{f:.0f}")
        nums.add(f"{f:.1f}")
        nums.add(f"{f:.1f}".rstrip("0").rstrip("."))
    return nums


# 파생값 인용: 같은 문장에 근거 수치 두 개가 괄호로 인용돼 있으면
# (예: "10× lower variance (0.003 vs 0.033)") 저자가 계산을 드러낸 것이다.
# 원문에 배수 리터럴이 없어도 이건 정당하다 — 미검출로 세지 않는다.
# 두 패턴 중 하나면 파생값으로 본다:
#  A. "(0.003 vs 0.033)" — 괄호 안 두 수치를 vs/슬래시로 대조
#  B. "(313–443 min) ... 5.33/6.58 min" — 근거 단위값이 문장에 흩어져 있음
#     (min·ms·GB 등 단위 붙은 수치가 2개 이상이면 저자가 근거를 제시한 것)
_UNIT = r"\d+(?:\.\d+)?\s*(?:ms|s|min|GB|MB|FPS|dB|M|B)\b"
DERIVED = re.compile(
    r"\(\s*[~≈<>]?\s*\d+(?:\.\d+)?\s*(?:ms|s|min|GB|MB|%)?\s*"
    r"(?:vs\.?|versus|→|/)\s*[~≈<>]?\s*\d"  # 패턴 A
    rf"|{_UNIT}.{{0,60}}?{_UNIT}"  # 패턴 B: 단위값 2개
    r"|\d[\d,]{3,}\D{0,40}?\d[\d,]{3,}",  # 패턴 C: 콤마 천단위 두 수치(247,153 vs 5,550,940)
    re.I,
)


def claims(path: pathlib.Path) -> list[tuple[int, str, str]]:
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        s = line.strip()
        if s.startswith("|") or s.startswith("#"):  # 표·헤더 제외 = 산문만
            continue
        if DERIVED.search(s):  # 근거 수치가 인용된 파생값 → 검증 통과
            continue
        for m in CLAIM.finditer(s):
            v = m.group(1) or m.group(2)
            out.append((i, v, s[m.start() : m.start() + 60]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="특정 slug만 (쉼표 구분)")
    ap.add_argument("--check", action="store_true", help="CI용: 미검출 있으면 non-zero")
    args = ap.parse_args()

    recs = json.loads(
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "extract_meta.py"), "--json"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    if args.only:
        want = set(args.only.split(","))
        recs = [r for r in recs if r["slug"] in want]

    total = missing = 0
    flagged: list[tuple[str, int, str, str]] = []
    for r in recs:
        cs = claims(ROOT / r["file"])
        if not cs:
            continue
        tf = CACHE / f"{r['slug']}.txt"
        if not tf.exists():
            continue
        pdf = pdf_speedups(tf.read_text(errors="ignore"))
        for ln, v, ctx in cs:
            total += 1
            if v not in pdf:
                missing += 1
                flagged.append((r["file"], ln, v, ctx))

    print(f"배속/개선 주장 {total}개 / 원문 미검출 {missing}개", file=sys.stderr)
    for f, ln, v, ctx in flagged:
        print(f"  {f}:{ln}  {v}×  | {ctx}", file=sys.stderr)

    if args.check and missing:
        print(
            "\n원문에 없는 배속 주장이 있다. 파생값이면 원 수치로 바꾸거나 지운다.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
