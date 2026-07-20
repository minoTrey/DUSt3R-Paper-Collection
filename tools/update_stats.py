#!/usr/bin/env python3
"""README의 논문 수·배지·연도 히스토그램을 재생성한다.

손으로 세면 반드시 틀어진다. 실제로 오랫동안 틀려 있었다:
  실제 55편 / 배지 "Papers-54" / 본문 "54 papers" 3곳 / dynamic 12(실제11) /
  gaussian-splatting 루트README 11(실제10) / 히스토그램 합 54

`--check`는 CI용. 불일치가 있으면 non-zero로 종료한다.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

CATEGORY_TITLE = {
    "foundation": "Foundation Models",
    "reconstruction": "3D Reconstruction",
    "dynamic": "Dynamic Scenes",
    "gaussian-splatting": "Gaussian Splatting",
    "pose": "Pose Estimation",
    "reasoning": "Reasoning",
    "understanding": "Scene Understanding",
    "robotics": "Robotics",
    "medical": "Medical",
    "surveys": "Surveys & Analysis",
}


def load() -> list[dict]:
    out = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "extract_meta.py"), "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)


def venue_year(rec: dict, verdicts: dict) -> str | None:
    """연도는 검증된 venue에서 뽑는다. 없으면 문서의 Venue 문자열에서."""
    v = verdicts.get(rec["slug"], {}).get("venue")
    src = v or rec["fields"].get("Venue") or ""
    m = re.search(r"\b(20\d{2})\b", src)
    return m.group(1) if m else None


def compute() -> dict:
    recs = load()
    vpath = ROOT / "raw" / "verdicts.json"
    verdicts = {}
    if vpath.exists():
        verdicts = {v["slug"]: v for v in json.loads(vpath.read_text())}

    cats = collections.Counter(r["cat"] for r in recs)
    years = collections.Counter()
    unknown = 0
    for r in recs:
        y = venue_year(r, verdicts)
        if y:
            years[y] += 1
        else:
            unknown += 1
    return {
        "total": len(recs),
        "categories": dict(sorted(cats.items())),
        "years": dict(sorted(years.items())),
        "year_unknown": unknown,
        "verified": len(verdicts),
    }


def histogram(years: dict[str, int]) -> str:
    if not years:
        return ""
    mx = max(years.values())
    width = 64
    lines = []
    for y, n in sorted(years.items()):
        bar = "█" * max(1, round(n / mx * width))
        lines.append(f"{y} {bar} {n} paper{'s' if n != 1 else ''}")
    return "\n".join(lines)


def apply(text: str, st: dict) -> tuple[str, list[str]]:
    """README를 실제 수치로 갱신. 무엇을 바꿨는지 함께 반환한다."""
    changes: list[str] = []
    total = st["total"]

    def sub(pattern: str, repl, label: str, s: str, flags: int = 0) -> str:
        new, n = re.subn(pattern, repl, s, flags=flags)
        if n and new != s:
            changes.append(f"{label} ({n}곳)")
        return new

    # 배지
    text = sub(
        r"(badge/Papers-)\d+(-green)", rf"\g<1>{total}\g<2>", "Papers 배지", text
    )
    # 본문 "54 papers", "54+ research papers"
    # ⚠️ 생성 블록 안에서는 치환하지 않는다. 예전에 이 규칙이 연도 히스토그램
    #    안까지 들어가 각 연도 수를 전부 총계로 덮어썼다 (2024·2025가 나란히
    #    "131 papers"가 됐다). 마커 사이는 통째로 재생성하므로 건드리면 안 된다.
    def outside_blocks(s: str, fn) -> str:
        parts = re.split(r"(<!-- GENERATED:\w+ -->.*?<!-- /GENERATED -->)", s, flags=re.S)
        return "".join(p if p.startswith("<!-- GENERATED:") else fn(p) for p in parts)

    _before = text
    text = outside_blocks(
        text,
        lambda s: re.sub(
            r"\b\d+(\+?) (research )?papers\b",
            lambda m: f"{total}{m.group(1)} {m.group(2) or ''}papers",
            s,
        ),
    )
    if text != _before:
        changes.append("본문 논문 수")
    text = sub(
        r"\*\*\d+ papers\*\*", f"**{total} papers**", "강조된 논문 수", text
    )
    # 카테고리별 "(N papers)" — 링크 뒤에 오는 것만
    for cat, n in st["categories"].items():
        text = sub(
            rf"(\(docs/{re.escape(cat)}/\)\s*)\(\d+ papers?\)",
            rf"\g<1>({n} paper{'s' if n != 1 else ''})",
            f"{cat} 카운트",
            text,
        )
    # 연도 히스토그램 — 마커 사이를 통째로 재생성한다.
    # 예전에는 히스토그램 줄 모양을 정규식으로 맞추려 했는데, 줄 끝에 주석이
    # 붙은 형식("1 paper   (CroCo - NeurIPS)")을 못 맞춰 한 번도 작동하지 않았다.
    # 마커는 모양에 의존하지 않는다.
    hist = histogram(st["years"])
    if hist:
        text = sub(
            r"<!-- GENERATED:histogram -->.*?<!-- /GENERATED -->",
            "<!-- GENERATED:histogram -->\n\n```text\n"
            + hist
            + "\n```\n\n<!-- /GENERATED -->",
            "연도 히스토그램",
            text,
            re.S,
        )
    return text, changes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="CI용: 불일치 시 non-zero")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    st = compute()
    if args.json:
        print(json.dumps(st, ensure_ascii=False, indent=1))
        return 0

    print(f"논문 총계 : {st['total']}")
    print(f"검증 완료 : {st['verified']}")
    for c, n in st["categories"].items():
        print(f"  {c:20s} {n}")
    print(f"연도 미상 : {st['year_unknown']}")

    old = README.read_text(encoding="utf-8")
    new, changes = apply(old, st)

    if args.check:
        if new != old:
            print("\n❌ README가 실제 수치와 다르다:", file=sys.stderr)
            for c in changes:
                print(f"   - {c}", file=sys.stderr)
            print("   `python3 tools/update_stats.py` 실행 필요", file=sys.stderr)
            return 1
        print("\n✅ README 수치 정합")
        return 0

    if new != old:
        README.write_text(new, encoding="utf-8")
        print("\n✅ README 갱신:")
        for c in changes:
            print(f"   - {c}")
    else:
        print("\n변경 없음")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
