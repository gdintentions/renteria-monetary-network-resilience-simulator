import copy
import json
import unittest
from pathlib import Path

from offline_review_runner import run_cases

DIR = Path(__file__).resolve().parents[1] / "data" / "validation_protocol_demo"
CASES = json.loads((DIR / "cases.dev.json").read_text())
LABELS = json.loads((DIR / "labels.dev.json").read_text())


class OfflineReviewTests(unittest.TestCase):
    def test_repeatable_developer_cases(self):
        data = run_cases(CASES, LABELS)
        self.assertEqual(data["summary"]["sourcegate"]["n"], 7)
        self.assertEqual(data["summary"]["tracelens"]["n"], 6)
        self.assertEqual(data["provider_tokens_used"], 0)
        self.assertFalse(data["independent_review"])
        self.assertTrue(all(x["match"] for x in data["results"]))

    def test_no_label_leak(self):
        cases = copy.deepcopy(CASES)
        cases["cases"][0]["expected"] = "CITED_EXTRACTS"
        with self.assertRaisesRegex(ValueError, "separate labels"):
            run_cases(cases, LABELS)

    def test_duplicate_case_id_fails(self):
        cases = copy.deepcopy(CASES)
        cases["cases"][1]["id"] = cases["cases"][0]["id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            run_cases(cases, LABELS)

    def test_wrong_expected_status_visible_as_failure(self):
        labels = copy.deepcopy(LABELS)
        labels["labels"][0]["status"] = "UNSUPPORTED"
        data = run_cases(CASES, labels)
        self.assertFalse(data["results"][0]["match"])


if __name__ == "__main__":
    unittest.main()
