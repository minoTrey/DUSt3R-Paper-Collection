"""Card completion requires matching review evidence and recorded publication."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import build_card_inventory as inventory


class CardProgressTests(unittest.TestCase):
    def audit_with(self, **changes):
        progress_path = inventory.DEST / "paper-card-progress.jsonl"
        read_text = Path.read_text
        records = [json.loads(line) for line in progress_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        records = copy.deepcopy(records)
        record = records[-1]
        record.update(production_status="ready", status="visual_reviewed", publication_status="pending_main", published_commit=None)
        record.update(changes)
        replacement = "\n".join(json.dumps(row) for row in records)

        def read(path, *args, **kwargs):
            return replacement if path == progress_path else read_text(path, *args, **kwargs)

        with patch.object(Path, "read_text", read):
            _, audit = inventory.produce()
        return audit

    def assert_issue(self, expected, **changes):
        issues = self.audit_with(**changes)["progress_findings"]["invalid_records"]
        self.assertTrue(any(expected in row["issue"] for row in issues), issues)

    def test_reviewed_ready_record_is_valid(self):
        self.assertEqual(self.audit_with()["blocking_findings"], [])

    def test_complete_requires_publication(self):
        self.assert_issue("requires verified main publication", production_status="complete")

    def test_ready_requires_matching_asset(self):
        self.assert_issue("matching source, asset or review evidence", asset_sha256="0" * 64)

    def test_ready_requires_matching_note(self):
        self.assert_issue("matching source, asset or review evidence", source_note_sha256="0" * 64)

    def test_published_requires_commit(self):
        self.assert_issue("published state lacks a commit", publication_status="published")


if __name__ == "__main__":
    unittest.main()
