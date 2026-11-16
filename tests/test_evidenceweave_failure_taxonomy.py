import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "evidenceweave_failure_taxonomy.py"
spec = importlib.util.spec_from_file_location("taxonomy", SCRIPT)
taxonomy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(taxonomy)


class FailureTaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            **taxonomy.EXPECTED,
            "failures": [
                *({"id": f"m{i}", "failure_category": "missed-conflict",
                   "conflicting_triples": ["(subject, relation.example, value)"]}
                  for i in range(258)),
                *({"id": f"f{i}", "failure_category": "false-positive-conflict",
                   "positive_triples": ["(subject, relation.example, value)"]}
                  for i in range(4)),
            ],
        }

    def test_exact_published_counts(self):
        report = taxonomy.build_report(self.payload)
        self.assertEqual(report["failure_categories"]["missed-conflict"], 258)
        self.assertEqual(report["failure_categories"]["false-positive-conflict"], 4)
        self.assertEqual(report["predicates"][0]["predicate"], "relation.example")

    def test_reject_duplicate_ids(self):
        self.payload["failures"][0]["id"] = "m1"
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            taxonomy.build_report(self.payload)

    def test_reject_baseline_drift(self):
        self.payload["false_negative"] = 257
        with self.assertRaisesRegex(ValueError, "baseline mismatch"):
            taxonomy.build_report(self.payload)

    def test_reject_missing_failure(self):
        self.payload["failures"].pop()
        with self.assertRaisesRegex(ValueError, "Failure list"):
            taxonomy.build_report(self.payload)

    def test_predicate_malformed(self):
        self.assertEqual(taxonomy.predicate("invalid"), "<malformed>")


if __name__ == "__main__":
    unittest.main()
