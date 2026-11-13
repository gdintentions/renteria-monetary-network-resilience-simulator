import json
import unittest
from pathlib import Path

from tracelens import diagnose, sweep, sweep_scores


class GovernedObservations(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).with_name("governed_rag_examples.json")
        self.examples = json.loads(path.read_text(encoding="utf-8"))["examples"]

    def test_locates_four_distinct_failure_stages(self):
        expected = {
            "governed-rank": "below_rank_cutoff",
            "governed-candidate": "outside_candidate_pool",
            "governed-score": "below_score_cutoff",
            "governed-unused": "selected_not_used",
        }
        for case, stage in expected.items():
            with self.subTest(case=case):
                result = diagnose(self.examples[case]["trace"])
                self.assertEqual(result["evidence_stages"]["supporting_passages"]["sponsor"], stage)
                self.assertNotIn("judge_false_positive_ids", result["gold_metrics"])

    def test_rank_replay_does_not_carry_over_observed_answer_use(self):
        replay = sweep(self.examples["governed-rank"]["trace"], [1, 2, 3])
        diagnoses = [row["diagnosis"] for row in replay]
        self.assertEqual([row["gold_metrics"]["selected_recall"] for row in diagnoses], [0, 1, 1])
        self.assertEqual([len(row["cells"]["noise"]) for row in diagnoses], [1, 1, 2])
        self.assertEqual(diagnoses[1]["evidence_stages"]["supporting_passages"]["sponsor"], "selected")

    def test_score_replay_preserves_budget_and_excludes_zero_score(self):
        trace = self.examples["governed-rank"]["trace"]
        replay = sweep_scores(trace, [0.0, 0.15, 0.45])
        self.assertEqual([row["diagnosis"]["cells"]["noise"] for row in replay], [["directory"], ["directory"], []])
        replay = sweep_scores(self.examples["governed-score"]["trace"], [0.0])
        self.assertEqual(replay[0]["diagnosis"]["evidence_stages"]["supporting_passages"]["sponsor"], "below_score_cutoff")

    def test_rejects_inconsistent_or_invalid_observations(self):
        trace = self.examples["governed-rank"]["trace"]
        with self.assertRaises(ValueError):
            diagnose(dict(trace, used_ids=["sponsor"]))
        with self.assertRaises(ValueError):
            diagnose(dict(trace, kept_ids=["sponsor"]))
        with self.assertRaises(ValueError):
            sweep_scores(trace, [float("nan")])

    def test_early_stop_is_not_a_candidate_miss(self):
        trace = {"retrieval_ran": False, "candidates": [], "kept_ids": [], "used_ids": [], "gold_ids": ["policy"]}
        self.assertEqual(diagnose(trace)["status"], "RETRIEVAL_NOT_RUN")
        self.assertEqual(sweep(trace, [1, 2]), [])
