import unittest

from semantic_development_eval import evaluate


class SemanticDevelopmentEvalTests(unittest.TestCase):
    def test_developer_authored_cases_compare_both_methods(self):
        result = evaluate()
        self.assertEqual(result["baseline"], {"tp": 1, "fp": 2, "tn": 3, "fn": 2})
        self.assertEqual(result["challenger"], {"tp": 3, "fp": 0, "tn": 5, "fn": 0})
        self.assertEqual(len(result["cases"]), 8)
        self.assertIn("author-labeled synthetic", result["scope"])

    def test_not_external_conflictqa(self):
        result = evaluate()
        self.assertNotIn("ConflictQA", result["scope"])
        self.assertTrue(all("expected_conflict" in case for case in result["cases"]))


if __name__ == "__main__":
    unittest.main()
