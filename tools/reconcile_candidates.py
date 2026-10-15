#!/usr/bin/env python3
"""Reconcile discovery status with exact arXiv IDs and the preserved historical triage.

This check does not infer relevance or PDF verification from titles. Name collisions
are review hints only. Run without arguments to inspect, --write to update the queue
and audit, or --check to fail on stale status/audit data.
"""
from __future__ import annotations

import argparse
import collections
import csv
import io
import json
import pathlib
import re

from extract_meta import papers, parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "candidates/queue.jsonl"
AUDIT = ROOT / "candidates/reconciliation.tsv"


def name(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.split(":", 1)[0].lower())


def reconcile() -> tuple[str, str, collections.Counter]:
    queue = [json.loads(line) for line in QUEUE.read_text(encoding="utf-8").splitlines()]
    ids = [r["arxiv_id"] for r in queue]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate arXiv ID in queue. Review before changing status.")
    triage = {}
    for line in (ROOT / "candidates/triage.tsv").read_text(encoding="utf-8").splitlines():
        aid, decision, category = line.split("|")
        if decision not in {"IN", "OUT"} or aid in triage:
            raise ValueError(f"Invalid historical triage row: {line}")
        triage[aid] = decision
    if set(triage) - set(ids):
        raise ValueError("Historical triage IDs are missing from the queue.")

    evidence_path = ROOT / "raw/curation_evidence_2026-10-15.json"
    reviewed = set()
    if evidence_path.exists():
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        reviewed = {r["arxiv_id"] for r in evidence["papers"] if r.get("pdf_reviewed")}

    by_id, by_name = collections.defaultdict(list), collections.defaultdict(list)
    for rec in (parse(p) for p in papers()):
        by_id[rec["arxiv_id"]].append(rec["file"].replace("\\", "/"))
        by_name[name(rec["h1"])].append(rec)

    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(["arxiv_id", "status", "historical_triage", "document",
                     "possible_name_collision", "content_review"])
    counts = collections.Counter()
    for row in queue:
        aid = row["arxiv_id"]
        matches = by_id.get(aid, [])
        historical = triage.get(aid, "")
        if len(matches) > 1:
            raise ValueError(f"Multiple documents for arXiv {aid}: {matches}")
        if historical == "OUT" and matches:
            raise ValueError(f"Historical OUT now has a document: {aid}. Review manually.")
        if historical == "IN" and not matches:
            raise ValueError(f"Historical IN has no matching document: {aid}")
        # Keep deliberate future review decisions. Discovery's stale 'new' cannot
        # override a document or a historical exclusion.
        status = "added" if matches else "rejected" if historical == "OUT" else row["status"]
        if status == "added" and not matches:
            raise ValueError(f"Added candidate has no document: {aid}")
        row["status"] = status
        collisions = [r["file"].replace("\\", "/") for r in by_name.get(name(row["title"]), [])
                      if r["arxiv_id"] != aid]
        review = ("historical inclusion; not revalidated in this batch" if historical == "IN"
                  else "historical exclusion; reason not recorded; not re-evaluated" if historical == "OUT"
                  else "PDF reviewed 2026-10-15; see summary and raw/curation_evidence_2026-10-15.json" if aid in reviewed
                  else "existing document; PDF review not recorded in this batch" if matches
                  else "UNVERIFIED: full text and relevance pending")
        writer.writerow([aid, status, historical, ";".join(matches), ";".join(collisions), review])
        counts[status] += 1
    text = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in queue)
    return text, stream.getvalue(), counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    queue, audit, counts = reconcile()
    print("Candidate states:", dict(sorted(counts.items())))
    # Compare decoded JSON, so discovery's JSON whitespace does not affect status checks.
    old = [json.loads(line) for line in QUEUE.read_text(encoding="utf-8").splitlines()]
    new = [json.loads(line) for line in queue.splitlines()]
    stale = old != new or not AUDIT.exists() or AUDIT.read_text(encoding="utf-8") != audit
    if args.write:
        QUEUE.write_text(queue, encoding="utf-8", newline="\n")
        AUDIT.write_text(audit, encoding="utf-8", newline="\n")
    elif args.check and stale:
        print("Queue or audit is stale. Run python tools/reconcile_candidates.py --write.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
