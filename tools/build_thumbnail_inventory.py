#!/usr/bin/env python3
"""Export unassigned thumbnail jobs without generating art or claiming production."""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def produce():
    inventory = json.loads((ROOT / "data/paper-card-inventory.json").read_text(encoding="utf-8"))
    art = json.loads((ROOT / "data/paper-thumbnails.json").read_text(encoding="utf-8"))
    progress = {r["record_id"]: r for r in [json.loads(line) for line in (ROOT / "data/paper-card-progress.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]}
    issues = json.loads((ROOT / "data/classification-review-2026-10-19.json").read_text(encoding="utf-8"))["separate_metadata_issues"]
    existing = set(art["thumbnails"])
    jobs = []
    for row in inventory["papers"]:
        rid = row["record_id"]
        if rid in existing:
            continue
        state = progress[rid]
        jobs.append({
            "record_id": rid, "category": row["category"], "title": row["title"], "short_title": row["short_title"],
            "paper_source_identity": row["paper_source_identity"], "paper_url": row["paper_url"], "reviewed_paper_revision_as_recorded": state.get("paper_revision"),
            "note_path": row["note_path"], "note_url": row["note_url"], "note_content_sha256": row["note_sha256"],
            "reference_poster_path": row["planned_card_path"], "reference_poster_sha256": state["asset_sha256"],
            "target_master_path": f"assets/paper-thumbnails/en/{rid}.png", "target_delivery_path": f"assets/paper-thumbnails/en/{rid}.webp",
            "production_status": "unassigned", "assigned_to": None, "original_source_review_required": True,
            "recorded_source_issues": [issue for issue in issues if issue["record_id"] == rid],
        })
    ids = [row["record_id"] for row in jobs]
    assert len(ids) == len(set(ids)) and not set(ids) & existing
    assert len(jobs) + len(existing) == inventory["total_papers"]
    return {
        "schema_version": 1, "scope": "Production handoff only. This export generates no images and assigns no jobs; the parent coordinates claims to prevent duplicate generation.",
        "source_inventory_snapshot_sha256": inventory["source_snapshot_sha256"],
        "already_handled": sorted(existing), "remaining": len(jobs), "categories": dict(sorted(Counter(j["category"] for j in jobs).items())),
        "design_spec": {
            "language": "English", "aspect_ratio": "16:9", "original_reference_dimensions": [1672, 941], "delivery_dimensions": [960, 540],
            "palette": {"cream": "#FAF7EE", "forest_green": "#103F2D", "sage": "#DCE8C8", "lime": "#BFE35B"},
            "composition": "Large short method name, one short input-to-output or core-method caption, one concrete conceptual scene/diagram. Readable at 316px. No paragraphs, result tables or benchmark numbers.",
            "listing_fallback": "Use the complete existing visual summary with contain and its original aspect ratio until approved dedicated art exists. Never use a text-only replacement.",
            "scientific_review": "Read the matching original paper before selecting inputs, outputs and core contribution. Separate pre-training, inference and downstream fine-tuning. Conceptual diagrams are not measured outputs. Resolve recorded source issues before making content claims.",
            "source_preservation": "Keep all full-size visual summaries and note bodies. Create new landscape art, never a portrait-poster crop. Preserve generated PNG bytes and register a separate no-crop optimized WebP derivative with hashes.",
            "coordination": "Claim a canonical record_id before generation, record owner/batch outside this unassigned snapshot, and exclude every already_handled ID. Check current migrations and thumbnail manifest before importing. Do not overwrite another worker's asset.",
        }, "jobs": jobs,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = ROOT / "data/thumbnail-production-inventory.json"
    value = json.dumps(produce(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != value:
            raise SystemExit("Thumbnail production inventory is stale.")
    else:
        output.write_text(value, encoding="utf-8")
    print("Thumbnail production inventory: " + str(len(produce()["jobs"])) + " unassigned; no images generated.")

if __name__ == "__main__":
    main()
