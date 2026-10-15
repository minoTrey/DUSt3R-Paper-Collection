"""Guard the status reconciliation against false inclusion and silent data loss."""
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import reconcile_candidates as target


class ReconciliationTests(unittest.TestCase):
    def reconcile(self, queue, triage="", docs=()):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            candidates = root / "candidates"
            candidates.mkdir()
            source = candidates / "queue.jsonl"
            source.write_text("".join(json.dumps(r) + "\n" for r in queue), encoding="utf-8")
            (candidates / "triage.tsv").write_text(triage, encoding="utf-8")
            with patch.multiple(target, ROOT=root, QUEUE=source), patch.object(
                target, "papers", return_value=docs
            ), patch.object(target, "parse", side_effect=lambda r: r):
                text, audit, counts = target.reconcile()
                return [json.loads(line) for line in text.splitlines()], audit, counts

    def row(self, aid="2601.00001", title="Example: A paper", status="new"):
        return dict(arxiv_id=aid, title=title, status=status, via="discovery")

    def doc(self, aid="2601.00001", title="Example: A paper"):
        return dict(arxiv_id=aid, h1=title, file="docs/reconstruction/example.md")

    def test_historical_decisions_and_unreviewed_remainder(self):
        rows, audit, counts = self.reconcile(
            [self.row(), self.row("2601.00002"), self.row("2601.00003")],
            "2601.00001|IN|reconstruction\n2601.00002|OUT|robotics\n",
            [self.doc()],
        )
        self.assertEqual([r["status"] for r in rows], ["added", "rejected", "new"])
        self.assertEqual(rows[0]["via"], "discovery")
        self.assertIn("reason not recorded", audit)
        self.assertIn("UNVERIFIED", audit)
        self.assertEqual(sum(counts.values()), 3)

    def test_same_name_with_different_id_does_not_become_added(self):
        rows, audit, _ = self.reconcile([self.row()], docs=[self.doc("2501.00001")])
        self.assertEqual(rows[0]["status"], "new")
        self.assertIn("docs/reconstruction/example.md", audit)

    def test_duplicate_queue_id_fails(self):
        with self.assertRaisesRegex(ValueError, "Duplicate arXiv ID"):
            self.reconcile([self.row(), self.row()])

    def test_missing_historical_in_fails(self):
        with self.assertRaisesRegex(ValueError, "IN has no matching document"):
            self.reconcile([self.row()], "2601.00001|IN|reconstruction\n")

    def test_historical_out_with_document_fails(self):
        with self.assertRaisesRegex(ValueError, "OUT now has a document"):
            self.reconcile([self.row()], "2601.00001|OUT|reconstruction\n", [self.doc()])

    def test_missing_added_document_fails(self):
        with self.assertRaisesRegex(ValueError, "Added candidate has no document"):
            self.reconcile([self.row(status="added")])

    def test_document_does_not_imply_pdf_review(self):
        rows, audit, _ = self.reconcile([self.row()], docs=[self.doc()])
        self.assertEqual(rows[0]["status"], "added")
        self.assertIn("PDF review not recorded", audit)


if __name__ == "__main__":
    unittest.main()
