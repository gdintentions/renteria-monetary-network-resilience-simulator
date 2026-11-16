import unittest
from datetime import date

from literal_support import run_literal_supported
from sourcegate import Evidence


def doc(id, text, claims, source="https://policy.example/a"):
    return Evidence(id, text, source, "2099-01-01", claims)


class LiteralBindingTests(unittest.TestCase):
    def evaluate(self, docs, claims=("approver",)):
        return run_literal_supported(
            "Who approves access?", list(claims), docs,
            allowed_hosts={"policy.example"}, today=date(2026, 11, 16),
        )

    def test_exact_value_supported_in_text(self):
        result = self.evaluate([doc("policy", "An access sponsor approves.", {"approver": "sponsor"})])
        self.assertEqual(result["status"], "CITED_EXTRACTS")
        self.assertEqual([r["citation"] for r in result["answer"]], ["policy"])

    def test_unmentioned_value_does_not_count_as_evidence(self):
        result = self.evaluate([doc("policy", "Access rules vary.", {"approver": "sponsor"})])
        self.assertEqual(result["status"], "NEEDS_REVIEW")
        self.assertEqual(result["reason"], "MISSING_EVIDENCE")
        self.assertEqual(result["literal_binding"]["unbound_claims"],
                         [{"evidence_id": "policy", "claim_key": "approver"}])

    def test_numeric_token_does_not_match_inside_larger_number(self):
        result = self.evaluate([doc("policy", "Duration 314 days.", {"duration": 14})],
                               claims=("duration",))
        self.assertEqual(result["reason"], "MISSING_EVIDENCE")

    def test_valid_zero_and_false_are_not_dropped(self):
        result = self.evaluate([doc("policy", "allowed false; duration 0 days.",
                                    {"allowed": False, "duration": 0})],
                               claims=("allowed", "duration"))
        self.assertEqual(result["status"], "CITED_EXTRACTS")

    def test_partial_binding_withholds_incomplete_answer(self):
        result = self.evaluate([doc("policy", "Sponsor approval.",
                                    {"approver": "sponsor", "duration": 14})],
                               claims=("approver", "duration"))
        self.assertEqual(result["reason"], "MISSING_EVIDENCE")
        self.assertIsNone(result["answer"])

    def test_url_allowlist_still_applies(self):
        result = self.evaluate([doc("attacker", "sponsor",
                                    {"approver": "sponsor"},
                                    "https://policy.example.evil.test/policy")])
        self.assertEqual(result["reason"], "MISSING_EVIDENCE")

    def test_two_literal_values_withhold_conflict(self):
        result = self.evaluate([
            doc("one", "Sponsor approves.", {"approver": "sponsor"}),
            doc("two", "IT approves.", {"approver": "IT"}),
        ])
        self.assertEqual(result["reason"], "CONFLICT")

    def test_structured_value_is_not_sufficient(self):
        result = self.evaluate([doc("policy", "Approver sponsor.",
                                    {"approver": {"name": "sponsor"}})])
        self.assertEqual(result["reason"], "MISSING_EVIDENCE")

    def test_empty_value_is_not_sufficient(self):
        result = self.evaluate([doc("policy", "Approval required.", {"approver": " "})])
        self.assertEqual(result["reason"], "MISSING_EVIDENCE")

    def test_invalid_document_fails_closed(self):
        result = self.evaluate([None])
        self.assertEqual(result["reason"], "STRICT_BINDING_FAILURE")
        self.assertIsNone(result["answer"])


if __name__ == "__main__":
    unittest.main()
