import unittest
from datetime import date
from unittest.mock import Mock

from sourcegate import Evidence, run


def evidence(pid, claims, origin="kb", host="policy.example"):
    return Evidence(pid, f"Fictional policy extract {pid}.", f"https://{host}/{pid}",
                    "2099-01-01", claims, origin)


class ClaimCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.question = "What is the fictional approval process and access duration?"
        self.local = evidence("approval", {"approver": "sponsor"})
        self.fallback = evidence("duration", {"duration": 14}, "web")
        self.search = Mock(side_effect=AssertionError("raw question must not go to fallback"))
        self.search_missing = Mock(return_value=[self.fallback])

    def evaluate(self, local, *, web_allowed=True):
        return run(
            self.question, ["approver", "duration"], lambda _: local,
            lambda _, docs: {doc.id: "partial" for doc in docs},
            self.search, allowed_hosts={"policy.example"}, today=date(2026, 11, 12),
            web_allowed=web_allowed, search_missing=self.search_missing,
        )

    def test_requests_only_the_missing_claim_and_preserves_exact_provenance(self):
        result = self.evaluate([self.local])
        self.search_missing.assert_called_once_with(("duration",))
        self.search.assert_not_called()
        self.assertEqual(result["status"], "CITED_EXTRACTS")
        self.assertEqual(result["correction"]["requested"], ["duration"])
        self.assertEqual(
            [(row["citation"], row["url"]) for row in result["answer"]],
            [("approval", self.local.source), ("duration", self.fallback.source)],
        )

    def test_disabled_complete_and_conflicting_local_evidence_do_not_search(self):
        off = self.evaluate([self.local], web_allowed=False)
        self.assertEqual(off["reason"], "MISSING_EVIDENCE")
        self.assertEqual(off["correction"], {"missing_local": ["duration"], "requested": []})
        complete = self.evaluate([self.local, evidence("local-duration", {"duration": 14})])
        self.assertEqual(complete["status"], "CITED_EXTRACTS")
        conflict = self.evaluate([self.local, evidence("other-approval", {"approver": "IT"})])
        self.assertEqual(conflict["reason"], "CONFLICT")
        self.assertIsNone(conflict["answer"])
        self.search_missing.assert_not_called()
        self.search.assert_not_called()

    def test_drops_out_of_scope_and_wrong_origin_results(self):
        self.search_missing.return_value = [
            evidence("extra", {"approver": "IT"}, "web"),
            evidence("wrong-origin", {"duration": 30}),
            self.fallback,
        ]
        result = self.evaluate([self.local])
        self.assertEqual([row["citation"] for row in result["answer"]], ["approval", "duration"])
        self.assertEqual(result["correction"]["out_of_scope_ids"], ["extra"])
        self.assertEqual(result["rejected_ids"], ["wrong-origin"])

    def test_in_scope_conflict_still_withholds_the_answer(self):
        self.search_missing.return_value = [
            evidence("mixed", {"duration": 14, "approver": "IT"}, "web")
        ]
        result = self.evaluate([self.local])
        self.assertEqual(result["reason"], "CONFLICT")
        self.assertIsNone(result["answer"])

    def test_unavailable_search_withholds_and_preserves_attempt_record(self):
        self.search_missing.side_effect = TimeoutError
        result = self.evaluate([self.local])
        self.assertEqual(result["reason"], "ADAPTER_OR_SCHEMA_FAILURE")
        self.assertEqual(result["correction"]["requested"], ["duration"])
        self.assertIsNone(result["answer"])
