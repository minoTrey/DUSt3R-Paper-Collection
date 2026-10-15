"""Prettier-equivalent padding must pass; changed evidence must fail."""
import contextlib
import io
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import build_candidate_review as report
import verify_internal_links as links


class CandidateReportTests(unittest.TestCase):
    def check(self, generated, saved):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / 'report.md'
            path.write_text(saved, encoding='utf-8')
            with patch.object(report, 'OUT', path), patch.object(report, 'build', return_value=generated), \
                    patch('sys.argv', ['build_candidate_review.py', '--check']), contextlib.redirect_stdout(io.StringIO()):
                return report.main()

    def test_prettier_padding_preserves_content(self):
        self.assertEqual(self.check('| Paper | State |\n| --- | --- |\n| [A](a.md) | added |',
                                    '| Paper       | State |\n| ----------- | ----- |\n| [A](a.md)   | added |\n'), 0)

    def test_changed_state_fails(self):
        self.assertEqual(self.check('| A | added |', '| A | reviewed |'), 1)

    def test_changed_link_fails(self):
        self.assertEqual(self.check('| [A](a.md) |', '| [A](b.md) |'), 1)

    def test_changed_reason_fails(self):
        self.assertEqual(self.check('| reason one |', '| reason two |'), 1)

    def test_missing_row_fails(self):
        self.assertEqual(self.check('| A |\n| B |', '| A |'), 1)

    def test_changed_prose_fails(self):
        self.assertEqual(self.check('Count: 76', 'Count: 75'), 1)

    def test_local_links_are_case_sensitive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root/'target.md').write_text('# Target', encoding='utf-8')
            source=root/'README.md'
            source.write_text('[ok](target.md#target)', encoding='utf-8')
            self.assertEqual(links.errors(root), [])
            source.write_text('[bad](Target.md)', encoding='utf-8')
            self.assertEqual(len(links.errors(root)), 1)
            source.write_text('[bad](missing.md)', encoding='utf-8')
            self.assertEqual(len(links.errors(root)), 1)


if __name__ == '__main__':
    unittest.main()
