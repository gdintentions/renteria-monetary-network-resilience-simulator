import unittest
from datetime import date
from sourcegate import Evidence, run

TODAY = date(2026, 11, 15)
def doc(ident, claims, *, expires="2099-01-01", origin="kb"):
    return Evidence(ident, "Fictional approved policy extract.",
                    "https://policy.example/" + ident, expires, claims, origin)

def execute(records, required=("approver", "duration"), web_allowed=False):
    return run("What are the approval and duration requirements?", list(required),
               lambda q: records, lambda q, rs: {r.id: "partial" for r in rs},
               lambda q: [], allowed_hosts={"policy.example"}, today=TODAY,
               web_allowed=web_allowed)

class MeaningfulCoverageTests(unittest.TestCase):
    def test_null_claim_does_not_claim_coverage(self):
        result = execute([doc("empty", {"approver": None}), doc("time", {"duration": 14})])
        self.assertEqual(result["reason"], "MISSING_EVIDENCE")
        self.assertEqual(result["missing"], ["approver"])
        self.assertIsNone(result["answer"])

    def test_blank_claim_does_not_claim_coverage(self):
        result = execute([doc("blank", {"approver": "  ", "duration": 14})])
        self.assertEqual(result["reason"], "MISSING_EVIDENCE")
        self.assertEqual(result["missing"], ["approver"])

    def test_zero_and_false_are_valid_facts(self):
        result = execute([doc("valid", {"approver": False, "duration": 0})])
        self.assertEqual(result["status"], "CITED_EXTRACTS")

    def test_expired_evidence_not_counted(self):
        result = execute([doc("stale", {"approver": "sponsor"}, expires="2026-11-14"),
                          doc("duration", {"duration": 14})])
        self.assertEqual(result["reason"], "MISSING_EVIDENCE")
        self.assertIn("stale", result["rejected_ids"])

    def test_partial_claims_without_fallback_withhold(self):
        result = execute([doc("partial", {"approver": "sponsor"})])
        self.assertEqual(result["missing"], ["duration"])
        self.assertEqual(result["events"], ["RETRIEVE", "GRADE"])

    def test_conflicting_meaningful_values_withhold(self):
        result = execute([doc("one", {"approver": "sponsor", "duration": 14}),
                          doc("two", {"approver": "IT"})])
        self.assertEqual(result["reason"], "CONFLICT")
        self.assertEqual(result["conflicts"], ["approver"])

if __name__ == "__main__":
    unittest.main()
