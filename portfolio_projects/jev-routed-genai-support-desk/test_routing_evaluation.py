import copy
import unittest

from routing_evaluation import evaluate


CASES = {"tickets": [
    {"id": "a", "text": "Track my package"},
    {"id": "b", "text": "My card was stolen"},
]}
LABELS = {"labels": [
    {"id": "a", "route": "clarify"},
    {"id": "b", "route": "human"},
]}


class RoutingEvaluationTests(unittest.TestCase):
    def test_reconstruct_routing(self):
        r = evaluate(CASES, LABELS)
        self.assertEqual(r["correct"], 2)
        self.assertEqual(r["tickets"], 2)
        self.assertEqual(r["handoff_recall"], 1)
        self.assertEqual(r["false_handoffs"], 0)
        self.assertFalse(r["independent_review"])

    def test_no_label_leak(self):
        c = copy.deepcopy(CASES)
        c["tickets"][0]["route"] = "clarify"
        with self.assertRaisesRegex(ValueError, "leaked"):
            evaluate(c, LABELS)

    def test_no_missing_labels(self):
        with self.assertRaisesRegex(ValueError, "IDs"):
            evaluate(CASES, {"labels": [LABELS["labels"][0]]})

    def test_invalid_label(self):
        l = copy.deepcopy(LABELS)
        l["labels"][1]["route"] = "refund"
        with self.assertRaisesRegex(ValueError, "expected route"):
            evaluate(CASES, l)

    def test_bad_flag(self):
        c = copy.deepcopy(CASES)
        c["tickets"][0]["order_verified"] = "true"
        with self.assertRaisesRegex(ValueError, "booleans"):
            evaluate(c, LABELS)


if __name__ == "__main__":
    unittest.main()
