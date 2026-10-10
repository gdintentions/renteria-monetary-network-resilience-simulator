import unittest
from tracelens import diagnose,sweep
class Tests(unittest.TestCase):
 def trace(self):return {"candidates":[{"id":"noise"},{"id":"answer"}],"kept_ids":["noise"],"judge_labels":{"noise":"unrelated","answer":"answers"},"gold_ids":["answer"]}
 def test_selection_loss(self):self.assertEqual(diagnose(self.trace())["status"],"SELECTION_MISS")
 def test_counterfactual(self):self.assertEqual(sweep(self.trace(),[1,2])[1]["diagnosis"]["gold_metrics"]["selected_recall"],1)
 def test_unknown_is_not_gap(self):
  t=self.trace();t.pop("gold_ids");t["judge_labels"]["answer"]="partial"
  self.assertEqual(diagnose(t)["status"],"INSUFFICIENT_EVIDENCE")
 def test_exhaustive_gap(self):
  t=self.trace();t["gold_ids"]=[];t["judge_labels"]["answer"]="unrelated"
  self.assertEqual(diagnose(t)["status"],"CORPUS_GAP_CONFIRMED")
 def test_judge_failure(self):
  t=self.trace();t["judge_labels"].pop("answer")
  self.assertEqual(diagnose(t)["status"],"JUDGE_UNAVAILABLE")
 def test_miss_outside_pool(self):
  t=self.trace();t["gold_ids"]=["absent"];t["judge_labels"]["answer"]="unrelated"
  self.assertEqual(diagnose(t)["status"],"CANDIDATE_MISS")
 def test_bad_kept(self):
  t=self.trace();t["kept_ids"]=["absent"]
  with self.assertRaises(ValueError):diagnose(t)
 def test_duplicates(self):
  t=self.trace();t["candidates"].append({"id":"answer"})
  with self.assertRaises(ValueError):diagnose(t)
 def test_judge_false_positive_visible(self):
  t=self.trace();t["gold_ids"]=[]
  self.assertEqual(diagnose(t)["gold_metrics"]["judge_false_positive_ids"],["answer"])
if __name__=="__main__":unittest.main()
