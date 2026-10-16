#!/usr/bin/env python3
"""Export source-backed paper metadata for future English summary cards.

This tool does not create cards, alter notes, infer absent links, or mark work complete.
Run with --check to compare the tracked exports against the current note snapshot.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import pathlib
import re
import unicodedata
from collections import Counter, defaultdict

from extract_meta import parse, papers
from build_papers_list import CATEGORY_ORDER, CAT_BEGIN, CAT_END, parse_h1

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "data"
GITHUB = "https://github.com/minoTrey/DUSt3R-Paper-Collection/blob/main/"
RAW = "https://raw.githubusercontent.com/minoTrey/DUSt3R-Paper-Collection/main/"
MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
CORE = {"dust3r": 0, "mast3r": 1, "vggt": 2}
CSV_FIELDS = [
    "record_id", "slug", "title", "short_title", "category", "category_title",
    "note_path", "note_url", "raw_note_url", "paper_url", "arxiv_id",
    "paper_pdf_urls", "project_url", "project_link_status", "code_url",
    "verification_as_recorded", "note_sha256", "planned_card_path", "card_asset_present",
    "card_production_status", "card_review_status", "card_publication_status",
]


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip().casefold()


def duplicates(rows: list[dict], key: str, normalize=False) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        value = row.get(key)
        if value:
            groups[normalized(value) if normalize else value].append(row["record_id"])
    return [{"value": value, "records": ids} for value, ids in sorted(groups.items()) if len(ids) > 1]


def own_pdfs(text: str, arxiv_id: str | None) -> list[str]:
    if not arxiv_id:
        return []
    urls = re.findall(r"https?://[^\s<>()\]]+", text)
    pattern = re.compile(r"https?://(?:www\.)?arxiv\.org/pdf/" + re.escape(arxiv_id) + r"(?:v\d+)?(?:\.pdf)?(?:[?#].*)?$")
    return sorted({url.rstrip(".,;") for url in urls if pattern.fullmatch(url.rstrip(".,;"))})


def note_content(text: str) -> str:
    """Exclude only the marked card presentation block from source-content hashes."""
    return re.sub(r"^<!-- PAPER-CARD:en -->\n.*?^<!-- /PAPER-CARD -->\n\n", "", text, flags=re.M | re.S)


def produce() -> tuple[dict, dict]:
    recs = [parse(p) for p in papers()]
    category_names = dict(CATEGORY_ORDER)
    order = {name: i for i, (name, _) in enumerate(CATEGORY_ORDER)}
    progress_path = DEST / "paper-card-progress.jsonl"
    progress_records = [json.loads(line) for line in progress_path.read_text(encoding="utf-8").splitlines() if line.strip()] if progress_path.exists() else []
    progress = {record["record_id"]: record for record in progress_records}
    rows = []
    for rec in recs:
        note = ROOT / rec["file"]
        text = note.read_text(encoding="utf-8")
        links = [{"label": label, "url": url} for label, url in MD_LINK.findall(rec["fields"].get("Links", ""))]
        paper_links = [link for link in links if link["label"].casefold() == "paper"]
        projects = [link for link in links if link["label"].casefold() in {"project", "project page", "project website"}]
        codes = [link for link in links if link["label"].casefold() == "code"]
        name, subtitle, venue = parse_h1(rec)
        title = name + (": " + subtitle if subtitle else "")
        paper_url = paper_links[0]["url"] if paper_links else None
        identity = "arxiv:" + rec["arxiv_id"] if rec["arxiv_id"] else ("url:" + paper_url if paper_url else None)
        planned = f"assets/paper-cards/en/{rec['cat']}/{rec['slug']}.png"
        state = progress.get(f"{rec['cat']}/{rec['slug']}", {})
        rows.append({
            "record_id": f"{rec['cat']}/{rec['slug']}",
            "slug": rec["slug"], "title": title, "short_title": name,
            "note_heading": rec["h1"], "category": rec["cat"],
            "category_title": category_names.get(rec["cat"], rec["cat"]),
            "note_path": rec["file"], "note_url": GITHUB + rec["file"],
            "raw_note_url": RAW + rec["file"],
            "paper_url": paper_url, "paper_source_identity": identity,
            "arxiv_id": rec["arxiv_id"], "paper_pdf_urls": own_pdfs(text, rec["arxiv_id"]),
            "project_url": projects[0]["url"] if projects else None,
            "project_links": projects, "project_link_status": "recorded" if projects else "not_recorded",
            "code_url": codes[0]["url"] if codes else None,
            "overview_links": links, "overview_links_as_recorded": rec["fields"].get("Links", ""),
            "venue_as_recorded": venue,
            "verification_as_recorded": rec["fields"].get("Verification", ""),
            "note_sha256": hashlib.sha256(note_content(text).encode("utf-8")).hexdigest(),
            "planned_card_path": planned, "card_asset_present": (ROOT / planned).is_file(),
            "card_production_status": state.get("production_status", "not_started"),
            "card_review_status": state.get("status", "not_started"),
            "card_publication_status": state.get("publication_status", "not_published"),
        })
    rows.sort(key=lambda r: (0, CORE[r["slug"]]) if r["slug"] in CORE else (1, order.get(r["category"], 999), r["slug"]))
    paths = {r["note_path"] for r in rows}
    detected = set()
    for p in (ROOT / "docs").rglob("*.md"):
        if p.name == "README.md" or p.name == "paper-template.md" or "VERIFICATION" in p.name:
            continue
        text = p.read_text(encoding="utf-8")
        if re.search(r"^##[^\n]*Overview", text, re.M) and re.search(r"\*\*Links\*\*\s*:", text):
            detected.add(p.relative_to(ROOT).as_posix())
    index = (ROOT / "docs/papers-list.md").read_text(encoding="utf-8")
    indexed = ["docs/" + x for x in re.findall(r"^- \[\*\*[^\n]+?\*\*\]\(([^)]+\.md)\)", index, re.M)]
    category_index_paths = []
    for cat, _ in CATEGORY_ORDER:
        text = (ROOT / "docs" / cat / "README.md").read_text(encoding="utf-8")
        block = text.split(CAT_BEGIN, 1)[1].split(CAT_END, 1)[0]
        category_index_paths.extend(f"docs/{cat}/" + x for x in re.findall(r"^- \[\*\*[^\n]+?\*\*\]\(([^)]+\.md)\)", block, re.M))
    dup = {key: duplicates(rows, key, key in {"title", "short_title"}) for key in ["record_id", "slug", "note_path", "paper_source_identity", "title", "short_title"]}
    missing = {key: [r["record_id"] for r in rows if not r.get(key)] for key in ["title", "paper_url", "project_url", "code_url", "arxiv_id"]}
    snapshot = hashlib.sha256("\n".join(f"{r['note_path']} {r['note_sha256']}" for r in sorted(rows, key=lambda x: x["note_path"])).encode()).hexdigest()
    invalid_progress = []
    by_id = {r["record_id"]: r for r in rows}
    for item in progress_records:
        rid = item["record_id"]
        row = by_id.get(rid)
        if row is None:
            invalid_progress.append({"record_id": rid, "issue": "record is absent from inventory"})
            continue
        if item.get("production_status") == "complete":
            expected = ROOT / row["planned_card_path"]
            valid = (
                item.get("status") in {"visual_reviewed", "published"}
                and item.get("source_note_sha256") == row["note_sha256"]
                and item.get("asset_path") == row["planned_card_path"]
                and expected.is_file()
                and item.get("asset_sha256") == hashlib.sha256(expected.read_bytes()).hexdigest()
                and bool(item.get("review_evidence"))
            )
            if not valid:
                invalid_progress.append({"record_id": rid, "issue": "complete state lacks matching source, asset or review evidence"})
        if item.get("publication_status") == "published" and not item.get("published_commit"):
            invalid_progress.append({"record_id": rid, "issue": "published state lacks a commit"})
    duplicate_progress = [rid for rid, n in Counter(x["record_id"] for x in progress_records).items() if n > 1]
    audit = {
        "source_snapshot_sha256": snapshot,
        "counts": {"papers": len(rows), "detected_note_candidates": len(detected), "complete_index_entries": len(indexed), "category_index_entries": len(category_index_paths), "categories": dict(sorted(Counter(r["category"] for r in rows).items())), "arxiv_sources": sum(bool(r["arxiv_id"]) for r in rows), "project_links_recorded": sum(bool(r["project_url"]) for r in rows), "project_links_not_recorded": len(missing["project_url"]), "existing_card_assets_at_planned_paths": sum(r["card_asset_present"] for r in rows), "card_production_statuses": dict(Counter(r["card_production_status"] for r in rows)), "cards_published": sum(r["card_publication_status"] == "published" for r in rows)},
        "coverage": {"unindexed_note_candidates": sorted(detected - paths), "records_without_detected_note": sorted(paths - detected), "missing_from_complete_index": sorted(paths - set(indexed)), "extra_in_complete_index": sorted(set(indexed) - paths), "missing_from_category_indexes": sorted(paths - set(category_index_paths)), "extra_in_category_indexes": sorted(set(category_index_paths) - paths), "duplicate_complete_index_paths": [x for x, n in Counter(indexed).items() if n > 1], "duplicate_category_index_paths": [x for x, n in Counter(category_index_paths).items() if n > 1]},
        "duplicates": dup, "missing_fields": missing,
        "progress_findings": {"invalid_records": invalid_progress, "duplicate_record_ids": duplicate_progress},
        "non_arxiv_primary_sources": [{"record_id": r["record_id"], "paper_url": r["paper_url"]} for r in rows if not r["arxiv_id"]],
        "core_papers": [{k: r[k] for k in ["slug", "title", "note_path", "note_url", "paper_url", "paper_pdf_urls", "project_url", "code_url"]} for r in rows if r["slug"] in CORE],
        "notes": [
            "Source links are copied from each note's Overview, not inferred from Related Work.",
            "Only explicitly stored PDF URLs for the same arXiv ID are included; absent PDF/project/code URLs are not invented.",
            "Short-name collisions are not automatically merged; compare full titles and primary source identities.",
            "DUSt3R and MASt3R currently store the same Project Page URL. The inventory preserves that value; verify its destination before card attribution.",
            "This is an inventory audit, not a fresh source-content, venue, benchmark or live-link audit.",
            "No cards are generated or marked complete by this export.",
            "Card production status is copied only from separately reviewed progress records; production completion is distinct from main publication.",
        ],
        "card_generation_performed": False,
    }
    errors = []
    for key, values in audit["coverage"].items():
        if values:
            errors.append(key)
    for key in ["record_id", "slug", "note_path", "paper_source_identity"]:
        if dup[key]:
            errors.append("duplicate " + key)
    if missing["title"] or missing["paper_url"]:
        errors.append("missing title or paper_url")
    if any(r["category"] not in category_names for r in rows):
        errors.append("unknown category")
    if invalid_progress or duplicate_progress:
        errors.append("invalid card progress records")
    audit["blocking_findings"] = errors
    inventory = {"schema_version": 1, "source": "Existing paper-note Overviews and titles; generated by tools/build_card_inventory.py", "hash_normalization": "UTF-8 note text with LF line endings; marked PAPER-CARD:en presentation block excluded", "source_snapshot_sha256": snapshot, "audit_file": "paper-card-inventory-audit.json", "progress_file": "paper-card-progress.jsonl", "audit_passed": not errors, "total_papers": len(rows), "card_assets_generated_by_this_export": 0, "papers": rows}
    return inventory, audit


def outputs(inventory: dict, audit: dict) -> dict[pathlib.Path, bytes]:
    csvbuf = io.StringIO(newline="")
    writer = csv.DictWriter(csvbuf, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in inventory["papers"]:
        flat = {key: row.get(key) for key in CSV_FIELDS}
        flat["paper_pdf_urls"] = " | ".join(row["paper_pdf_urls"])
        flat["card_asset_present"] = str(row["card_asset_present"]).lower()
        writer.writerow(flat)
    return {
        DEST / "paper-card-inventory.json": (json.dumps(inventory, ensure_ascii=False, indent=2) + "\n").encode(),
        DEST / "paper-card-inventory.csv": csvbuf.getvalue().encode("utf-8-sig"),
        DEST / "paper-card-inventory-audit.json": (json.dumps(audit, ensure_ascii=False, indent=2) + "\n").encode(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    inventory, audit = produce()
    stale = []
    for path, value in outputs(inventory, audit).items():
        if args.check:
            if not path.exists() or path.read_bytes() != value:
                stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(value)
    print(json.dumps({"counts": audit["counts"], "blocking_findings": audit["blocking_findings"], "stale_exports": stale}, indent=2))
    return 1 if audit["blocking_findings"] or stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
