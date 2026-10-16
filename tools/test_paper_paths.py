"""Legacy note notices must resolve to one canonical paper without lost cards."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import extract_meta
import paper_paths


class PaperPathTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.row = {
            "old_record_id": "foundation/example", "new_record_id": "extensions/example",
            "old_note_path": "docs/foundation/example.md", "new_note_path": "docs/extensions/example.md",
            "old_card_path": "assets/paper-cards/en/foundation/example.png",
            "new_card_path": "assets/paper-cards/en/extensions/example.png",
            "paper_source_identity": "arxiv:2601.00001", "card_present_at_migration": True,
            "card_sha256": hashlib.sha256(b"reviewed pixels").hexdigest(),
        }
        self.data = {"migrations": [self.row], "core_foundation_record_ids": ["foundation/core"]}
        self.write("data/paper-path-migrations.json", json.dumps(self.data))
        self.write(self.row["old_note_path"], "<!-- PAPER-REDIRECT: docs/extensions/example.md -->\n\n# Moved\n")
        self.write(self.row["new_note_path"], "# Example\n")
        self.write("docs/foundation/core.md", "# Core\n")
        for key in ("old_card_path", "new_card_path"):
            self.write(self.row[key], "reviewed pixels")
        self.records = [
            {"file": "docs/extensions/example.md", "cat": "extensions", "arxiv_id": "2601.00001"},
            {"file": "docs/foundation/core.md", "cat": "foundation", "arxiv_id": "2601.00002"},
        ]

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")

    def test_resolve_exact_identity_and_paths(self):
        for field in ("record_id", "note_path", "card_path"):
            self.assertEqual(paper_paths.resolve(self.row["old_" + field], field, self.root), self.row["new_" + field])
        self.assertEqual(paper_paths.resolve("foundation/core", root=self.root), "foundation/core")

    def test_notice_is_excluded_from_papers(self):
        with patch.object(extract_meta, "ROOT", self.root):
            self.assertEqual(len(list(extract_meta.papers())), 2)
        self.assertEqual(paper_paths.migration_errors(self.root, self.records), [])

    def test_wrong_notice_target_fails(self):
        self.write(self.row["old_note_path"], "<!-- PAPER-REDIRECT: docs/extensions/wrong.md -->\n")
        self.assertTrue(any("compatibility notice" in e for e in paper_paths.migration_errors(self.root, self.records)))

    def test_changed_legacy_card_fails(self):
        self.write(self.row["old_card_path"], "different pixels")
        self.assertTrue(any("canonical/legacy card" in e for e in paper_paths.migration_errors(self.root, self.records)))

    def test_changed_source_identity_fails(self):
        self.records[0]["arxiv_id"] = "2601.99999"
        self.assertTrue(any("paper identity" in e for e in paper_paths.migration_errors(self.root, self.records)))

    def test_unregistered_notice_fails(self):
        self.write("docs/foundation/unregistered.md", "<!-- PAPER-REDIRECT: docs/extensions/example.md -->\n")
        self.assertTrue(any("unregistered" in e for e in paper_paths.migration_errors(self.root, self.records)))

    def test_unapproved_foundation_member_fails(self):
        self.records.append({"file": "docs/foundation/extra.md", "cat": "foundation", "arxiv_id": "2601.00003"})
        self.assertTrue(any("approved core-model set" in e for e in paper_paths.migration_errors(self.root, self.records)))

    def test_retired_notice_is_absent_and_mapping_still_resolves(self):
        self.row["legacy_note_retained"] = False
        self.data["foundation_directory_policy"] = "canonical_only"
        self.write("data/paper-path-migrations.json", json.dumps(self.data))
        self.write("docs/foundation/README.md", "# Core models\n")
        self.assertTrue(any("retired compatibility" in e for e in paper_paths.migration_errors(self.root, self.records)))
        (self.root / self.row["old_note_path"]).unlink()
        self.assertEqual(paper_paths.migration_errors(self.root, self.records), [])
        self.assertEqual(paper_paths.resolve("foundation/example", root=self.root), "extensions/example")


if __name__ == "__main__":
    unittest.main()
