#!/usr/bin/env python3
"""docs/papers-list.md 를 131편 전체에서 재생성한다.

이 파일은 README 배지(Papers-131)가 가리키는 전체 목록이다. 손으로 관리돼
오랫동안 55편에 멈춰 있었고 venue 오류(MASt3R-SLAM을 arXiv 2024로 표기 등)도
그대로였다. 이제 개별 문서에서 자동 생성한다 — 개별 문서는 검증을 거쳤으므로
목록도 자동으로 원문까지 추적된다.

--check 는 CI용. 현재 파일이 생성 결과와 다르면 non-zero.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "papers-list.md"

# 루트 README와 같은 카테고리 순서·표기
CATEGORY_ORDER = [
    ("foundation", "Foundation Models"),
    ("reconstruction", "3D Reconstruction"),
    ("dynamic", "Dynamic Scenes"),
    ("gaussian-splatting", "Gaussian Splatting"),
    ("understanding", "Scene Understanding"),
    ("reasoning", "Scene Reasoning"),
    ("robotics", "Robotics"),
    ("surveys", "Surveys & Analysis"),
    ("pose", "Pose Estimation"),
    ("medical", "Medical"),
]
H1 = re.compile(r"^(.+?):\s*(.+?)\s*\(([^()]*(?:\([^)]*\))?[^()]*)\)\s*$")


def load() -> list[dict]:
    return json.loads(
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "extract_meta.py"), "--json"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )


def parse_h1(rec: dict) -> tuple[str, str, str]:
    """H1에서 (이름, 부제, venue)를 뽑는다. Venue 필드를 우선한다."""
    h = rec["h1"] or rec["slug"]
    m = H1.match(h)
    venue = rec["fields"].get("Venue", "").strip()
    if m:
        name, sub, h1venue = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        return name, sub, venue or h1venue
    return h, "", venue


def build() -> str:
    recs = load()
    by_cat: dict[str, list[dict]] = {}
    for r in recs:
        by_cat.setdefault(r["cat"], []).append(r)

    total = len(recs)
    lines = [
        "# Complete Papers List",
        "",
        "> 이 목록은 `tools/build_papers_list.py` 가 개별 논문 문서에서 자동 생성한다.",
        "> 손으로 편집하지 말 것 — 개별 문서를 고치고 스크립트를 다시 돌린다.",
        "",
        f"**Total: {total} papers**",
        "",
    ]

    seen = set()
    for cat, title in CATEGORY_ORDER:
        recs_c = sorted(by_cat.get(cat, []), key=lambda r: r["slug"])
        if not recs_c:
            continue
        seen.add(cat)
        lines.append(f"## {title} ({len(recs_c)})")
        lines.append("")
        for r in recs_c:
            name, sub, venue = parse_h1(r)
            link = pathlib.Path(r["file"]).name  # docs/<cat>/<slug>.md → <slug>.md
            rel = f"{cat}/{link}"
            tail = f" — {sub}" if sub else ""
            lines.append(f"- [**{name}**]({rel}) ({venue}){tail}")
        lines.append("")

    # CATEGORY_ORDER에 없는 카테고리가 생기면 조용히 빠지지 않게 경고
    missing = set(by_cat) - seen
    if missing:
        lines.append(f"<!-- ⚠️ CATEGORY_ORDER에 없는 카테고리: {sorted(missing)} -->")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


CAT_BEGIN = "<!-- GENERATED:paper-index -->"
CAT_END = "<!-- /GENERATED -->"


def category_block(recs_c: list[dict]) -> str:
    """카테고리 README 끝에 붙는 자동 생성 전체 목록 블록.

    손으로 큐레이션한 테마별 리스트는 그대로 두고, 이 블록이 '빠짐없는 전체
    목록'을 보장한다. 큐레이션이 최신 논문을 놓쳐도 여기엔 반드시 있다.
    """
    lines = [
        CAT_BEGIN,
        "",
        f"## 📄 All Papers in This Category ({len(recs_c)})",
        "",
        "> 자동 생성 (`tools/build_papers_list.py`). 손대지 말 것.",
        "",
    ]
    for r in sorted(recs_c, key=lambda r: r["slug"]):
        name, sub, venue = parse_h1(r)
        link = pathlib.Path(r["file"]).name
        tail = f" — {sub}" if sub else ""
        lines.append(f"- [**{name}**]({link}) ({venue}){tail}")
    lines += ["", CAT_END]
    return "\n".join(lines)


def apply_category(recs: list[dict], check: bool) -> tuple[int, list[str]]:
    """각 카테고리 README에 자동 목록 블록을 삽입/갱신한다."""
    by_cat: dict[str, list[dict]] = {}
    for r in recs:
        by_cat.setdefault(r["cat"], []).append(r)
    changed, stale = 0, []
    for cat, recs_c in by_cat.items():
        rp = ROOT / "docs" / cat / "README.md"
        if not rp.exists():
            continue
        old = rp.read_text(encoding="utf-8")
        block = category_block(recs_c)
        if CAT_BEGIN in old:
            new = re.sub(
                re.escape(CAT_BEGIN) + r".*?" + re.escape(CAT_END),
                block,
                old,
                flags=re.S,
            )
        else:  # 처음이면 파일 끝(푸터 앞)에 삽입
            new = old.rstrip() + "\n\n" + block + "\n"
        # 낡은 "(N papers)" 헤더 카운트도 실제 수로
        n = len(recs_c)
        new = re.sub(
            r"(Paper List \()\d+( papers?\))",
            rf"\g<1>{n}\g<2>",
            new,
        )
        if new != old:
            changed += 1
            stale.append(cat)
            if not check:
                rp.write_text(new, encoding="utf-8")
    return changed, stale


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    recs = load()
    new = build()
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    cat_changed, cat_stale = apply_category(recs, args.check)

    if args.check:
        bad = new != old or cat_changed
        if bad:
            if new != old:
                print("❌ docs/papers-list.md 가 문서 실태와 다르다.", file=sys.stderr)
            if cat_changed:
                print(f"❌ 카테고리 README {cat_stale} 목록이 낡았다.", file=sys.stderr)
            print("   `python3 tools/build_papers_list.py` 실행 필요", file=sys.stderr)
            return 1
        print("✅ papers-list.md + 카테고리 목록 정합")
        return 0

    OUT.write_text(new, encoding="utf-8")
    print(f"✅ papers-list.md 재생성 ({new.count('- [')}편)")
    if cat_changed:
        print(f"✅ 카테고리 README 목록 갱신: {cat_stale}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
