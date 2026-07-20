#!/usr/bin/env python3
"""문서의 벤치마크 수치를 원논문 PDF와 대조한다.

원리: 문서 표에 적힌 수치가 원논문 PDF 텍스트 어디에도 없다면 의심스럽다.
전사 오류이거나, 다른 논문에서 가져왔거나, 지어낸 것이다.

⚠️ 이 도구는 "틀렸다"고 단정하지 않는다. "원문에서 못 찾았다"고만 말한다.
   정당한 미검출 사유가 있다:
   - 원논문이 소수 자릿수를 다르게 표기 (0.834 vs 83.4)
   - 문서 저자가 여러 표를 재구성하며 평균을 계산
   - PDF 텍스트 추출이 표 레이아웃을 깨뜨림
   - 수치가 그림 안에만 있음
   따라서 출력은 "검토 대상"이지 "오류 목록"이 아니다.
   판단은 사람이 원문을 열어보고 한다.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDFDIR = ROOT / "docs" / "papers"
CACHE = ROOT / "raw" / "pdftext"

# 표 셀에서 뽑을 수치. 소수점 있는 것만 본다 —
# 정수는 연도/뷰 개수/차원 등 노이즈가 너무 많다.
# ⚠️ 소수 자릿수는 4까지 본다. 3까지만 보던 시절 EPS3D(0.4701 같은 4자리)가
#    통째로 건너뛰어져 "검증됨"으로 보였다. 자릿수 상한이 곧 사각지대다.
NUM = re.compile(r"(?<![\w.])(\d{1,4}\.\d{1,4})(?![\w.])")
# 대조 제외: 백분율 변화량(+17%)처럼 문서가 계산한 파생값일 수 있는 것
SKIP_ROW = re.compile(r"improvement|증감|change|delta|speedup|×|배", re.I)


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def pdf_text(slug: str, pmap: dict[str, pathlib.Path]) -> str | None:
    CACHE.mkdir(parents=True, exist_ok=True)
    c = CACHE / f"{slug}.txt"
    if c.exists():
        return c.read_text(encoding="utf-8", errors="ignore")
    k = norm(slug)
    p = (
        pmap.get(k)
        or pmap.get(k.replace("plus", "+"))
        or next((v for kk, v in pmap.items() if kk.startswith(k[:7]) and len(k) > 6), None)
    )
    if not p:
        return None
    try:
        # -layout 은 표 구조를 살려 수치가 붙어버리는 것을 막는다
        out = subprocess.run(
            ["pdftotext", "-layout", str(p), "-"],
            capture_output=True,
            text=True,
            timeout=120,
        ).stdout
    except Exception as e:
        print(f"    ⚠️ {slug}: pdftotext 실패 {e}", file=sys.stderr)
        return None
    c.write_text(out, encoding="utf-8")
    return out


def pdf_numbers(txt: str) -> set[str]:
    """PDF에서 가능한 모든 수치 표현을 모은다. 반올림 변형도 함께."""
    nums: set[str] = set()
    for m in re.finditer(r"(?<![\w])(\d{1,4}\.\d{1,4})(?![\w])", txt):
        v = m.group(1)
        nums.add(v)
        try:
            f = float(v)
        except ValueError:
            continue
        # 표기 변형 흡수: 0.834 ↔ 83.4, 소수 자릿수 반올림
        for cand in (f, f * 100, f / 100):
            for d in (1, 2, 3):
                nums.add(f"{cand:.{d}f}".rstrip("0").rstrip("."))
                nums.add(f"{cand:.{d}f}")
    return nums


def doc_numbers(path: pathlib.Path) -> list[tuple[int, str, str]]:
    """(줄번호, 수치, 행 전문) 목록. 표 행에서만."""
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        s = line.strip()
        if not s.startswith("|") or SKIP_ROW.search(s):
            continue
        for m in NUM.finditer(s):
            out.append((i, m.group(1), s[:110]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="특정 slug만 (쉼표 구분)")
    ap.add_argument("--threshold", type=float, default=0.85, help="경고 커버리지")
    ap.add_argument("--out", default="raw/benchmark_report.json")
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

    pmap = {norm(p.stem): p for p in PDFDIR.glob("*.pdf")}
    results = []
    for r in recs:
        dn = doc_numbers(ROOT / r["file"])
        if not dn:
            continue
        txt = pdf_text(r["slug"], pmap)
        if txt is None:
            results.append({**mini(r), "status": "NO_PDF", "total": len(dn)})
            continue
        pn = pdf_numbers(txt)
        missing = [(ln, v, ctx) for ln, v, ctx in dn if v not in pn]
        cov = 1 - len(missing) / len(dn)
        results.append(
            {
                **mini(r),
                "status": "OK" if cov >= args.threshold else "REVIEW",
                "total": len(dn),
                "missing": len(missing),
                "coverage": round(cov, 3),
                "samples": [
                    {"line": ln, "value": v, "row": ctx} for ln, v, ctx in missing[:12]
                ],
            }
        )
        print(
            f"  {r['slug']:26s} {cov * 100:5.1f}%  ({len(dn) - len(missing)}/{len(dn)})",
            file=sys.stderr,
        )

    (ROOT / args.out).write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    rev = [x for x in results if x["status"] == "REVIEW"]
    print(f"\n검토 대상 {len(rev)}/{len(results)}편 → {args.out}", file=sys.stderr)
    for x in sorted(rev, key=lambda y: y["coverage"]):
        print(
            f"  {x['coverage'] * 100:5.1f}%  {x['file']}  ({x['missing']}/{x['total']} 미검출)",
            file=sys.stderr,
        )
    return 0


def mini(r: dict) -> dict:
    return {"file": r["file"], "slug": r["slug"]}


if __name__ == "__main__":
    raise SystemExit(main())
