#!/usr/bin/env python3
"""논문당 구조화된 사실 카드(raw/facts/<slug>.json)를 생성한다.

이 카드는 개별 문서에서 파싱한 '사실의 단일 소스'다. 이후 문서 간 정합성
검사(verify_crossref.py)와 외부 링크 검사가 전부 이 카드를 읽는다. 카드를
따로 두는 이유: 매번 131개 마크다운을 재파싱하지 않고, 검증 계층이 같은
구조화 데이터를 공유하게 하기 위해서다.

각 카드:
  slug, file, category, arxiv_id, title, name(약칭), authors[], institution,
  venue, award, verification, links{paper,code,project}, tables[]
tables[i] = {header:[...], rows:[[...]]}  — (method,dataset,metric,value) 교차
대조의 원천. 값 자체는 verify_benchmarks가 이미 PDF와 대조했으므로, 카드는
'어떤 값이 어느 라벨에 붙어 있나'를 구조로 남긴다.

--check : 문서에서 재생성한 카드가 저장된 카드와 다르면 non-zero (CI용).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FACTS = ROOT / "raw" / "facts"

H1 = re.compile(r"^#\s+(.+?)\s*$")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
SEP = re.compile(r"^\s*\|[\s:|+-]+\|\s*$")


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_tables(lines: list[str]) -> list[dict]:
    """헤더 + 구분선 + 데이터로 이뤄진 마크다운 표를 뽑는다. 코드펜스 안은 건너뜀."""
    out = []
    inside_fence = False
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("```"):
            inside_fence = not inside_fence
            i += 1
            continue
        if (
            not inside_fence
            and lines[i].strip().startswith("|")
            and i + 1 < len(lines)
            and SEP.match(lines[i + 1])
        ):
            header = cells(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(cells(lines[j]))
                j += 1
            out.append({"header": header, "rows": rows})
            i = j
        else:
            i += 1
    return out


def field_block(txt: str) -> dict:
    ov = re.search(r"^##\s*[^\n]*Overview\s*$(.*?)(?=^##\s)", txt, re.M | re.S)
    fields = {}
    if ov:
        for line in ov.group(1).splitlines():
            m = re.match(r"^\s*[-*]\s*\*\*([^*]+)\*\*\s*:\s*(.*?)\s*$", line)
            if m:
                fields[m.group(1).strip()] = m.group(2).strip()
    return fields


def build_card(rec: dict) -> dict:
    p = ROOT / rec["file"]
    txt = p.read_text(encoding="utf-8")
    lines = txt.split("\n")
    f = field_block(txt)

    # 이름 약칭 = H1의 콜론 앞
    h1 = rec["h1"] or ""
    name = h1.split(":", 1)[0].strip() if ":" in h1 else h1

    # Links 파싱
    links = {}
    for label, url in LINK.findall(f.get("Links", "")):
        low = label.lower()
        key = (
            "paper"
            if ("paper" in low or "arxiv" in low or "published" in low or "ieee" in low)
            else "code"
            if "code" in low
            else "project"
            if ("project" in low or "page" in low)
            else low
        )
        links.setdefault(key, url)

    authors = [a.strip() for a in f.get("Authors", "").split(",") if a.strip()]

    return {
        "slug": rec["slug"],
        "file": rec["file"],
        "category": rec["cat"],
        "arxiv_id": rec["arxiv_id"],
        "title": h1,
        "name": name,
        "authors": authors,
        "institution": f.get("Institution", ""),
        "venue": f.get("Venue", ""),
        "award": f.get("Award", ""),
        "verification": f.get("Verification", ""),
        "links": links,
        "tables": parse_tables(lines),
    }


def all_cards() -> list[dict]:
    recs = json.loads(
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "extract_meta.py"), "--json"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    return [build_card(r) for r in recs]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    cards = all_cards()
    FACTS.mkdir(parents=True, exist_ok=True)

    if args.check:
        stale = []
        for c in cards:
            fp = FACTS / f"{c['slug']}.json"
            new = json.dumps(c, ensure_ascii=False, indent=1, sort_keys=True)
            old = fp.read_text(encoding="utf-8") if fp.exists() else ""
            if new != old:
                stale.append(c["slug"])
        if stale:
            print(f"❌ 사실 카드가 문서와 다르다: {stale[:8]}", file=sys.stderr)
            print("   `python3 tools/build_fact_cards.py` 실행 필요", file=sys.stderr)
            return 1
        print(f"✅ 사실 카드 {len(cards)}개 정합")
        return 0

    for c in cards:
        (FACTS / f"{c['slug']}.json").write_text(
            json.dumps(c, ensure_ascii=False, indent=1, sort_keys=True),
            encoding="utf-8",
        )
    # 오래된 카드(삭제된 문서) 정리
    valid = {c["slug"] for c in cards}
    for fp in FACTS.glob("*.json"):
        if fp.stem not in valid:
            fp.unlink()
    print(f"✅ 사실 카드 {len(cards)}개 생성 → raw/facts/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
