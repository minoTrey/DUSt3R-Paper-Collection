"""Category counts must remain distinct from the collection total."""
import unittest

import update_stats


class CategoryCountTests(unittest.TestCase):
    def setUp(self):
        self.stats = {"total": 337, "categories": {"foundation": 5, "extensions": 23}, "years": {}}

    def test_both_directory_link_styles_are_updated(self):
        text = "[Foundation](docs/foundation) (30 papers)\n[Extensions](docs/extensions/) (0 papers)\n337 papers\n"
        result, _ = update_stats.apply(text, self.stats)
        self.assertIn("(docs/foundation) (5 papers)", result)
        self.assertIn("(docs/extensions/) (23 papers)", result)
        self.assertEqual(update_stats.category_errors(result, self.stats), [])

    def test_missing_category_is_rejected(self):
        self.assertTrue(update_stats.category_errors("[Foundation](docs/foundation/) (5 papers)", self.stats))

    def test_duplicate_category_is_rejected(self):
        text = "[Foundation](docs/foundation/) (5 papers)\n" * 2 + "[Extensions](docs/extensions/) (23 papers)"
        self.assertTrue(update_stats.category_errors(text, self.stats))

    def test_collection_total_cannot_stand_in_for_category_counts(self):
        text = "[Foundation](docs/foundation) (337 papers)\n[Extensions](docs/extensions/) (337 papers)"
        self.assertTrue(update_stats.category_errors(text, self.stats))
        fixed, _ = update_stats.apply(text, self.stats)
        self.assertEqual(update_stats.category_errors(fixed, self.stats), [])


if __name__ == "__main__":
    unittest.main()
