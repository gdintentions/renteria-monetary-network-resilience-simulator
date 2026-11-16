import unittest

from reviewer_agreement import compare_reviewers


class ReviewerAgreementTests(unittest.TestCase):
    def test_disagreement_queue_and_kappa(self):
        ids = ["a", "b", "c", "d"]
        one = {"a": "answers", "b": "partial", "c": "unrelated", "d": "answers"}
        two = {"a": "answers", "b": "unrelated", "c": "unrelated", "d": "partial"}
        result = compare_reviewers(ids, one, two)
        self.assertEqual(result["raw_agreement"], 0.5)
        self.assertAlmostEqual(result["cohen_kappa"], 0.2727272727272727)
        self.assertEqual([row["id"] for row in result["needs_adjudication"]], ["b", "d"])
        self.assertFalse(result["independent_review_verified"])
        self.assertFalse(result["accuracy_measured"])

    def test_perfect_non_degenerate_agreement(self):
        ids = ["a", "b"]
        labels = {"a": "answers", "b": "unrelated"}
        result = compare_reviewers(ids, labels, labels)
        self.assertEqual(result["raw_agreement"], 1.0)
        self.assertEqual(result["cohen_kappa"], 1.0)
        self.assertEqual(result["needs_adjudication"], [])

    def test_single_label_is_not_informative_for_kappa(self):
        result = compare_reviewers(["a", "b"],
                                   {"a": "answers", "b": "answers"},
                                   {"a": "answers", "b": "answers"})
        self.assertEqual(result["raw_agreement"], 1.0)
        self.assertIsNone(result["cohen_kappa"])
        self.assertTrue(result["degenerate_single_label"])

    def test_missing_reviewer_annotation_not_counted_as_negative(self):
        with self.assertRaisesRegex(ValueError, "exactly"):
            compare_reviewers(["a", "b"],
                              {"a": "answers", "b": "partial"},
                              {"a": "answers"})

    def test_duplicate_candidate_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            compare_reviewers(["a", "a"], {"a": "answers"}, {"a": "answers"})

    def test_invalid_labels_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be"):
            compare_reviewers(["a", "b"],
                              {"a": "answers", "b": "maybe"},
                              {"a": "answers", "b": "partial"})

    def test_input_not_modified(self):
        ids = ["a", "b"]
        one = {"a": "answers", "b": "partial"}
        two = {"a": "answers", "b": "unrelated"}
        compare_reviewers(ids, one, two)
        self.assertEqual(ids, ["a", "b"])
        self.assertEqual(one["b"], "partial")
        self.assertEqual(two["b"], "unrelated")


if __name__ == "__main__":
    unittest.main()
