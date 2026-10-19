"""Resolve flattened historical paths and validate canonical notes and PNG aliases."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
REDIRECT = re.compile(r"\A<!-- PAPER-REDIRECT: (docs/[a-z0-9-]+/[a-z0-9-]+\.md) -->\n")


def redirect_target(text: str) -> str | None:
    match = REDIRECT.match(text)
    return match.group(1) if match else None


def migration_data(root: Path = ROOT) -> dict:
    path = root / "data/paper-path-migrations.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"migrations": []}


def resolve(value: str, field: str = "record_id", root: Path = ROOT) -> str:
    """Map an exact legacy identity/path; unlisted values remain unchanged."""
    for row in migration_data(root)["migrations"]:
        if value == row["old_" + field]:
            return row["new_" + field]
    return value


def migration_errors(root: Path, records: list[dict]) -> list[str]:
    data = migration_data(root)
    rows = data["migrations"]
    if not rows:
        return []
    errors = []
    canonical = {row["file"]: row for row in records}
    expected_redirects = {row["old_note_path"] for row in rows if row.get("legacy_note_retained", True)}
    # Several historical identities can resolve to one canonical paper after
    # multiple moves. Historical keys must be unique; final targets may repeat.
    for key in ("old_record_id", "old_note_path", "old_card_path"):
        values = [row[key] for row in rows]
        if len(values) != len(set(values)):
            errors.append("duplicate migration " + key)
    for field in ("record_id", "note_path", "card_path"):
        old_values = {row["old_" + field] for row in rows}
        if any(row["new_" + field] in old_values for row in rows):
            errors.append("migration targets must be flattened: " + field)
    by_target: dict[str, set[str]] = {}
    for row in rows:
        by_target.setdefault(row["new_note_path"], set()).add(row["paper_source_identity"])
    if any(len(identities) != 1 for identities in by_target.values()):
        errors.append("historical aliases disagree on canonical source identity")
    for row in rows:
        old, new = row["old_note_path"], row["new_note_path"]
        old_path, new_path = root / old, root / new
        if row.get("legacy_note_retained", True):
            if not old_path.is_file() or redirect_target(old_path.read_text(encoding="utf-8")) != new:
                errors.append("missing or mismatched compatibility notice: " + old)
        elif old_path.exists():
            errors.append("retired compatibility notice still present: " + old)
        if old in canonical or new not in canonical or not new_path.is_file():
            errors.append("migration must have one canonical note: " + new)
            continue
        rec = canonical[new]
        if "arxiv:" + str(rec["arxiv_id"]) != row["paper_source_identity"]:
            errors.append("migration changes paper identity: " + new)
        if row["card_present_at_migration"]:
            for field in ("old_card_path", "new_card_path"):
                asset = root / row[field]
                if not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != row["card_sha256"]:
                    errors.append("missing or changed canonical/legacy card: " + row[field])
    for path in root.glob("docs/*/*.md"):
        if path.name != "README.md" and redirect_target(path.read_text(encoding="utf-8")):
            if path.relative_to(root).as_posix() not in expected_redirects:
                errors.append("unregistered compatibility notice: " + path.relative_to(root).as_posix())
    if data.get("category_directory_policy") == "canonical_only":
        expected = set(canonical) | {"docs/" + row["cat"] + "/README.md" for row in records}
        actual = {path.relative_to(root).as_posix() for path in root.glob("docs/*/*.md")}
        if actual != expected:
            errors.append("category directories must contain canonical notes and README only")
    foundation = {r["file"][5:-3] for r in records if r["cat"] == "foundation"}
    if foundation != set(data["core_foundation_record_ids"]):
        errors.append("Foundation must match the approved core-model set")
    if data.get("foundation_directory_policy") == "canonical_only":
        expected = {Path("docs/" + rid + ".md").name for rid in foundation} | {"README.md"}
        actual = {path.name for path in (root / "docs/foundation").iterdir()}
        if actual != expected:
            errors.append("Foundation directory must contain only core notes and README")
    return errors
