import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("novelty", Path(__file__).resolve().parents[1] / "scripts" / "evidenceweave_novelty_analysis.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class NoveltyTests(unittest.TestCase):
    def test_addition_is_only_candidate_anomaly(self):
        x = mod.analyze({"failures": [{"id": "x", "failure_category": "missed-conflict",
            "positive_triples": ["(a, p, x)"], "conflicting_triples": ["(a, p, x)", "(b, q, y)"]}]})
        self.assertEqual(x["cases_with_novel_claims"], 1)
        self.assertEqual(x["anomalies"][0]["new_triples"], ["(b, q, y)"])
        self.assertIn("not validation", x["scope"])
    def test_positive_control_is_not_counted_as_miss(self):
        x = mod.analyze({"failures": [{"id": "x", "failure_category": "false-positive-conflict"}]})
        self.assertEqual(x["cases"], 0)
    def test_identical_triples_not_anomaly(self):
        x = mod.analyze({"failures": [{"id": "x", "failure_category": "missed-conflict",
            "positive_triples": ["a"], "conflicting_triples": ["a"]}]})
        self.assertEqual(x["cases_without_novel_claims"], 1)

if __name__ == "__main__":
    unittest.main()
