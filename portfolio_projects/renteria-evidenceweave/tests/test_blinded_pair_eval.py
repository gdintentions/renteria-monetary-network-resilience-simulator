import copy
import unittest

from blinded_pair_eval import evaluate_cases


def input_cases():
    return {"cases": [
        {"id": "positive", "claims": [
            {"subject": "A", "predicate": "capital", "value": "East"},
            {"subject": "West", "predicate": "capital_of", "value": "A"}]},
        {"id": "control", "claims": [
            {"subject": "A", "predicate": "spoken_language", "value": "English"},
            {"subject": "A", "predicate": "spoken_language", "value": "French"}]},
    ]}


def labels():
    return {"labels": [{"id": "positive", "is_conflict": True},
                       {"id": "control", "is_conflict": False}]}


CONFIG = {"functional_predicates": ["capital"], "inverse_predicates": {"capital_of": "capital"}}


class BlindedPairEvaluationTests(unittest.TestCase):
    def test_replay_both_methods(self):
        result = evaluate_cases(input_cases(), labels(), CONFIG)
        self.assertEqual(result["exact_key"]["fn"], 1)
        self.assertEqual(result["semantic_challenger"]["tp"], 1)
        self.assertEqual(result["semantic_challenger"]["fp"], 0)
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["label_provenance_status"] if "label_provenance_status" in result else "NOT_INDEPENDENTLY_VERIFIED",
                         "NOT_INDEPENDENTLY_VERIFIED")

    def test_reject_leaked_labels(self):
        cases = input_cases()
        cases["cases"][0]["expected_conflict"] = True
        with self.assertRaisesRegex(ValueError, "Gold labels"):
            evaluate_cases(cases, labels(), CONFIG)

    def test_reject_duplicated_ids(self):
        cases = input_cases()
        cases["cases"][1]["id"] = "positive"
        with self.assertRaisesRegex(ValueError, "ID mismatch"):
            evaluate_cases(cases, labels(), CONFIG)

    def test_reject_missing_label(self):
        with self.assertRaisesRegex(ValueError, "ID mismatch"):
            evaluate_cases(input_cases(), {"labels": labels()["labels"][:1]}, CONFIG)

    def test_reject_single_class_labels(self):
        test_labels = copy.deepcopy(labels())
        test_labels["labels"][1]["is_conflict"] = True
        with self.assertRaisesRegex(ValueError, "Both positive"):
            evaluate_cases(input_cases(), test_labels, CONFIG)


if __name__ == "__main__":
    unittest.main()
