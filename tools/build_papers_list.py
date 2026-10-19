#!/usr/bin/env python3
"""Generate paper indexes and curated highlights from stored Overview metadata.

Publication years come from Venue (including preprint years), never Verification.
Within each year, preserve configured topics and use stable slug order.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "papers-list.md"
CATEGORY_ORDER = [
    ("foundation", "Foundation Models"),
    ("extensions", "Model Extensions"),
    ("reconstruction", "3D Reconstruction"),
    ("dynamic", "Dynamic Scenes"),
    ("gaussian-splatting", "Gaussian Splatting"),
    ("understanding", "Scene Understanding"),
    ("reasoning", "Scene Reasoning"),
    ("robotics", "Robotics"),
    ("surveys", "Surveys, Benchmarks & Analysis"),
    ("pose", "Pose Estimation"),
    ("medical", "Medical"),
]
H1 = re.compile(r"^(.+?):\s*(.+?)\s*\(([^()]*(?:\([^)]*\))?[^()]*)\)\s*$")
YEAR = re.compile(r"\b(20\d{2})\b")
CAT_BEGIN = "<!-- GENERATED:paper-index -->"
CAT_END = "<!-- /GENERATED -->"
FEAT_BEGIN = "<!-- GENERATED:featured -->"
FEAT_END = "<!-- /GENERATED:featured -->"


def load() -> list[dict]:
    return json.loads(subprocess.run(
        [sys.executable, "-X", "utf8", str(ROOT / "tools" / "extract_meta.py"), "--json"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout)


def record_id(rec: dict) -> str:
    return f"{rec['cat']}/{rec['slug']}"


def parse_h1(rec: dict) -> tuple[str, str, str]:
    """Extract display text; prefer the Overview Venue for the venue label."""
    heading = rec["h1"] or rec["slug"]
    match = H1.match(heading)
    venue = rec["fields"].get("Venue", "").strip()
    if match:
        name, subtitle, h1venue = (s.strip() for s in match.groups())
        return name, subtitle, venue or h1venue
    return heading, "", venue


def paper_year(rec: dict) -> int:
    """The first Overview venue/preprint year; missing years sort last."""
    match = YEAR.search(rec["fields"].get("Venue", ""))
    return int(match.group(1)) if match else 0


def year_groups(recs: list[dict]) -> list[tuple[int, list[dict]]]:
    years: dict[int, list[dict]] = {}
    for rec in recs:
        years.setdefault(paper_year(rec), []).append(rec)
    return [(year, sorted(years[year], key=lambda r: r["slug"]))
            for year in sorted(years, reverse=True)]


def paper_line(rec: dict, prefix: str = "") -> str:
    name, subtitle, venue = parse_h1(rec)
    link = prefix + pathlib.Path(rec["file"]).name
    tail = f" — {subtitle}" if subtitle else ""
    return f"- [**{name}**]({link}) ({venue or 'Venue not recorded'}){tail}"


def build(recs: list[dict] | None = None) -> str:
    recs = load() if recs is None else recs
    by_cat: dict[str, list[dict]] = {}
    for rec in recs:
        by_cat.setdefault(rec["cat"], []).append(rec)
    missing = set(by_cat) - {cat for cat, _ in CATEGORY_ORDER}
    if missing:
        raise ValueError(f"Categories missing from CATEGORY_ORDER: {sorted(missing)}")
    lines = [
        "# Complete Papers List", "",
        "> Generated from individual paper notes by `tools/build_papers_list.py`.",
        "> Years use the recorded Overview Venue or preprint year, newest first; verification dates are not publication dates. Within each year, entries are ordered by slug.",
        "> Links open collection notes and their English summary cards; original papers are linked in each Overview. Some legacy passages are in Korean.",
        "", f"**Total: {len(recs)} papers**", "",
    ]
    for cat, title in CATEGORY_ORDER:
        recs_c = by_cat.get(cat, [])
        if not recs_c:
            continue
        lines += [f"## {title} ({len(recs_c)})", ""]
        for year, members in year_groups(recs_c):
            lines += [f"### {year or 'Year not recorded'}", ""]
            lines += [paper_line(rec, f"{cat}/") for rec in members]
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def load_featured(recs: list[dict]) -> dict:
    config = json.loads((ROOT / "data/category-featured.json").read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported category-featured schema version")
    if config.get("selection_status", "curated") not in {
        "curated", "provisional_pending_primary_contribution_classification_review"
    }:
        raise ValueError("Unknown Featured selection status")
    date.fromisoformat(config["reviewed_on"])
    by_cat: dict[str, set[str]] = {}
    for rec in recs:
        by_cat.setdefault(rec["cat"], set()).add(record_id(rec))
    if set(config["categories"]) != set(by_cat):
        raise ValueError("Featured configuration must cover every current category exactly")
    for cat, entries in config["categories"].items():
        if not entries or len(entries) > 8:
            raise ValueError(f"Featured category {cat} must have between 1 and 8 selections")
        seen = set()
        for entry in entries:
            rid = entry["record_id"]
            if rid not in by_cat[cat] or rid in seen:
                raise ValueError(f"Invalid or duplicate Featured member: {rid}")
            if entry["selection"] not in {"recent", "representative"}:
                raise ValueError(f"Unknown Featured selection type: {rid}")
            if not entry["reason"].strip() or "\n" in entry["reason"]:
                raise ValueError(f"Featured reason must be one nonempty line: {rid}")
            seen.add(rid)
    return config


def featured_block(recs_c: list[dict], config: dict) -> str:
    by_id = {record_id(rec): rec for rec in recs_c}
    category = recs_c[0]["cat"]
    lines = [
        FEAT_BEGIN, "", "## \u2b50 Featured Papers", "",
        f"> **Curated for recency and representative methods; reviewed {config['reviewed_on']}.** "
        "[Selection settings](../../data/category-featured.json) record the reason for each choice. "
        "This is a reading route, not a performance ranking. Preprint labels mean no independently confirmed conference/journal publication is stored; "
        "other unconfirmed venues are marked. See All Papers in This Category for every entry.", "",
    ]
    if config.get("selection_status") == "provisional_pending_primary_contribution_classification_review":
        lines[4:4] = [
            "> **Provisional choices: primary-contribution classification review is pending.** "
            "Featured selections will be reconsidered after that review.", ">",
        ]
    for entry in config["categories"][category]:
        rec = by_id[entry["record_id"]]
        name, _, venue = parse_h1(rec)
        fields = rec["fields"]
        preprint = re.search(r"arxiv|preprint|\bcorr\b", venue, re.I)
        confirmed = re.match(r"^CONFIRMED\b", fields.get("Verification", ""))
        status = " — **Preprint**" if preprint else "" if confirmed else " — **Venue unconfirmed**"
        award = f" — **{fields['Award']}**" if fields.get("Award") else ""
        role = entry["selection"].capitalize()
        lines.append(f"- [**{name}**]({pathlib.Path(rec['file']).name}) ({venue}){status}{award} — **{role}:** {entry['reason']}")
    return "\n".join(lines + ["", FEAT_END])


def topic_groups(recs_c: list[dict]) -> list[tuple[str, list[dict]]]:
    category = recs_c[0]["cat"] if recs_c else ""
    config = json.loads((ROOT / "data/category-groups.json").read_text(encoding="utf-8"))
    groups = config["categories"].get(category, [])
    by_id = {record_id(rec): rec for rec in recs_c}
    grouped, seen = [], set()
    for group in groups:
        members = []
        for rid in group["record_ids"]:
            if rid not in by_id or rid in seen:
                raise ValueError(f"Invalid category group member: {rid}")
            seen.add(rid)
            members.append(by_id[rid])
        grouped.append((group["title"], members))
    remaining = [rec for rid, rec in by_id.items() if rid not in seen]
    if remaining:
        fallback = "Surveys and analysis" if category == "surveys" else "Other extensions" if groups else ""
        grouped.append((fallback, remaining))
    return grouped


def category_block(recs_c: list[dict]) -> str:
    lines = [
        CAT_BEGIN, "", f"## \U0001f4c4 All Papers in This Category ({len(recs_c)})", "",
        "> Generated by `tools/build_papers_list.py`. Years use the recorded Overview Venue or preprint year, newest first; "
        "verification dates are not publication dates. Topics, where present, are nested below each year; "
        "entries within each year/topic are ordered by slug. Links open notes and their English summary cards.", "",
    ]
    topics = topic_groups(recs_c)
    for year, _ in year_groups(recs_c):
        lines += [f"### {year or 'Year not recorded'}", ""]
        for heading, recs_t in topics:
            members = sorted((r for r in recs_t if paper_year(r) == year), key=lambda r: r["slug"])
            if not members:
                continue
            if heading:
                lines += [f"#### {heading}", ""]
            lines += [paper_line(rec) for rec in members]
            lines.append("")
    return "\n".join(lines + [CAT_END])


def apply_category(recs: list[dict], check: bool, config: dict | None = None) -> tuple[int, list[str]]:
    config = load_featured(recs) if config is None else config
    by_cat: dict[str, list[dict]] = {}
    for rec in recs:
        by_cat.setdefault(rec["cat"], []).append(rec)
    # Prepare all results before writing, so invalid settings cannot partially update files.
    updates = []
    for cat, recs_c in by_cat.items():
        path = ROOT / "docs" / cat / "README.md"
        old = path.read_text(encoding="utf-8")
        new = old
        for begin, end, block in [
            (CAT_BEGIN, CAT_END, category_block(recs_c)),
            (FEAT_BEGIN, FEAT_END, featured_block(recs_c, config)),
        ]:
            if new.count(begin) != 1 or new.count(end) != 1:
                raise ValueError(f"Expected exactly one generated block: {path} {begin}")
            new = re.sub(re.escape(begin) + r".*?" + re.escape(end), lambda _: block, new, flags=re.S)
        if new != old:
            updates.append((cat, path, new))
    if not check:
        for _, path, new in updates:
            path.write_text(new, encoding="utf-8", newline="\n")
    return len(updates), [cat for cat, _, _ in updates]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    recs = load()
    config = load_featured(recs)
    new = build(recs)
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    changed, stale = apply_category(recs, args.check, config)
    if args.check:
        if new != old or changed:
            print(f"Stale indexes: papers-list={new != old}, categories={stale}. "
                  "Run python tools/build_papers_list.py", file=sys.stderr)
            return 1
        print("Paper list and all category READMEs match the generator and curated settings.")
        return 0
    OUT.write_text(new, encoding="utf-8", newline="\n")
    print(f"Generated papers-list.md ({len(recs)} papers); updated category READMEs: {stale}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
