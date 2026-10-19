"""Chronology, editorial selection and complete-index regression checks."""
import copy
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import build_papers_list as index


def record(slug, venue, cat="extensions", verification="UNKNOWN (2029-01-01)"):
    return {"cat": cat, "slug": slug, "file": f"docs/{cat}/{slug}.md",
            "h1": f"{slug}: Example method (arXiv 2030)",
            "fields": {"Venue": venue, "Verification": verification}}


class ChronologyTests(unittest.TestCase):
    def test_overview_venue_beats_h1_and_verification_year(self):
        self.assertEqual(index.paper_year(record("a", "CVPR 2024")), 2024)
        self.assertEqual(index.paper_year(record("a", "arXiv preprint (2025-11)")), 2025)
        self.assertEqual(index.paper_year(record("a", "RA-L 2024 (ICRA 2025 presentation)")), 2024)

    def test_unknown_year_does_not_borrow_a_verification_or_h1_date(self):
        self.assertEqual(index.paper_year(record("a", "arXiv preprint")), 0)
        self.assertEqual(index.paper_year(record("a", "")), 0)

    def test_years_descend_with_stable_slug_ties_and_unknown_last(self):
        recs = [record("z", "2026"), record("b", "2025"),
                record("a", "2026"), record("unknown", "")]
        groups = index.year_groups(recs)
        self.assertEqual([year for year, _ in groups], [2026, 2025, 0])
        self.assertEqual([r["slug"] for r in groups[0][1]], ["a", "z"])
        self.assertEqual(index.build(recs), index.build(list(reversed(recs))))

    def test_unknown_category_fails_instead_of_silently_omitting_notes(self):
        with self.assertRaises(ValueError):
            index.build([record("a", "2026", cat="unregistered")])


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()
        self.patch = patch.object(index, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.recs = [record("recent", "arXiv preprint (2026-09)"),
                     record("classic", "CVPR 2024", verification="CONFIRMED (2026-10-19)")]
        self.config = {"schema_version": 1, "reviewed_on": "2026-10-19", "categories": {
            "extensions": [
                {"record_id": "extensions/recent", "selection": "recent", "reason": "New method."},
                {"record_id": "extensions/classic", "selection": "representative", "reason": "Starting point."},
            ]}}
        self.write_config(self.config)
        (self.root / "data/category-groups.json").write_text(json.dumps({"categories": {}}))

    def write_config(self, config):
        (self.root / "data/category-featured.json").write_text(json.dumps(config))

    def test_unknown_preprint_is_explicitly_labeled_and_retains_curated_order(self):
        config = index.load_featured(self.recs)
        block = index.featured_block(self.recs, config)
        self.assertLess(block.index("(recent.md)"), block.index("(classic.md)"))
        self.assertIn("**Preprint**", block)
        self.assertIn("**Recent:** New method.", block)
        self.assertNotIn("Venue unconfirmed", block)
        self.assertIn("reviewed 2026-10-19", block)

    def test_likely_venue_is_not_presented_as_confirmed(self):
        self.recs[0]["fields"] = {"Venue": "ECCV 2026", "Verification": "LIKELY (2026-10-19)"}
        block = index.featured_block(self.recs, self.config)
        self.assertIn("**Venue unconfirmed**", block)
        self.assertNotIn("**Preprint**", block)

    def test_provisional_choices_remain_visibly_pending(self):
        self.config["selection_status"] = "provisional_pending_primary_contribution_classification_review"
        self.write_config(self.config)
        config = index.load_featured(self.recs)
        block = index.featured_block(self.recs, config)
        self.assertIn("**Provisional choices: primary-contribution classification review is pending.**", block)
        self.assertNotIn("\n\n> **Curated", block)
        config["selection_status"] = "unrecognized"
        self.write_config(config)
        with self.assertRaises(ValueError):
            index.load_featured(self.recs)

    def test_missing_category_invalid_member_duplicate_and_missing_reason_fail(self):
        cases = []
        config = copy.deepcopy(self.config)
        config["categories"] = {}
        cases.append(config)
        config = copy.deepcopy(self.config)
        config["categories"]["extensions"][0]["record_id"] = "pose/recent"
        cases.append(config)
        config = copy.deepcopy(self.config)
        config["categories"]["extensions"][1] = copy.deepcopy(config["categories"]["extensions"][0])
        cases.append(config)
        for field, value in [("reason", ""), ("reason", "two\nlines"), ("selection", "best")]:
            config = copy.deepcopy(self.config)
            config["categories"]["extensions"][0][field] = value
            cases.append(config)
        for config in cases:
            with self.subTest(config=config):
                self.write_config(config)
                with self.assertRaises(ValueError):
                    index.load_featured(self.recs)

    def test_topics_are_nested_below_year_and_members_are_not_duplicated(self):
        config = {"categories": {"extensions": [
            {"title": "Efficiency", "record_ids": ["extensions/classic", "extensions/recent"]}
        ]}}
        (self.root / "data/category-groups.json").write_text(json.dumps(config))
        block = index.category_block(self.recs)
        self.assertLess(block.index("### 2026"), block.index("#### Efficiency"))
        self.assertLess(block.index("(recent.md)"), block.index("### 2024"))
        self.assertEqual(block.count("#### Efficiency"), 2)
        self.assertEqual(block.count("(recent.md)"), 1)
        self.assertEqual(block.count("(classic.md)"), 1)
        config["categories"]["extensions"][0]["record_ids"].append("extensions/recent")
        (self.root / "data/category-groups.json").write_text(json.dumps(config))
        with self.assertRaises(ValueError):
            index.category_block(self.recs)

    def test_check_does_not_write_and_generation_preserves_surrounding_content(self):
        folder = self.root / "docs/extensions"
        folder.mkdir(parents=True)
        path = folder / "README.md"
        prefix, suffix = "# Existing design\n\n", "\n\nExisting image and footer.\n"
        original = (prefix + index.FEAT_BEGIN + "\nOld feature\n" + index.FEAT_END +
                    "\n\n" + index.CAT_BEGIN + "\nOld list\n" + index.CAT_END + suffix)
        path.write_text(original)
        self.assertEqual(index.apply_category(self.recs, True)[0], 1)
        self.assertEqual(path.read_text(), original)
        self.assertEqual(index.apply_category(self.recs, False)[0], 1)
        updated = path.read_text()
        self.assertTrue(updated.startswith(prefix) and updated.endswith(suffix))
        self.assertEqual(index.apply_category(self.recs, True)[0], 0)
        self.assertEqual(index.apply_category(self.recs, False)[0], 0)


class CollectionIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recs = index.load()
        cls.config = index.load_featured(cls.recs)

    def test_every_note_occurs_once_under_its_recorded_year_in_both_complete_indexes(self):
        complete = index.build(self.recs)
        all_links = re.findall(r"^- \[\*\*.*?\*\*\]\(([^)]+)\)", complete, re.M)
        self.assertEqual(len(all_links), len(self.recs))
        self.assertEqual(set(all_links), {f"{r['cat']}/{r['slug']}.md" for r in self.recs})
        for cat, _ in index.CATEGORY_ORDER:
            recs = [r for r in self.recs if r["cat"] == cat]
            block = index.category_block(recs)
            years = [int(y) for y in re.findall(r"^### (20\d{2})$", block, re.M)]
            self.assertEqual(years, sorted(set(years), reverse=True))
            year, found = None, []
            by_slug = {r["slug"]: r for r in recs}
            for line in block.splitlines():
                if line.startswith("### "):
                    year = int(line[4:])
                match = re.match(r"^- \[\*\*.*?\*\*\]\(([^)]+)\.md\)", line)
                if match:
                    slug = match.group(1)
                    found.append(slug)
                    self.assertEqual(index.paper_year(by_slug[slug]), year)
            self.assertEqual(len(found), len(recs))
            self.assertEqual(set(found), set(by_slug))

    def test_foundation_stays_the_five_core_models_and_all_featured_links_resolve(self):
        foundation = {r["slug"] for r in self.recs if r["cat"] == "foundation"}
        self.assertEqual(foundation, {"croco", "croco-v2", "dust3r", "mast3r", "vggt"})
        selected = self.config["categories"]["foundation"]
        self.assertEqual({e["record_id"].split("/")[1] for e in selected}, foundation)
        for cat, selections in self.config["categories"].items():
            for entry in selections:
                self.assertTrue((index.ROOT / f"docs/{entry['record_id']}.md").is_file())


if __name__ == "__main__":
    unittest.main()
