import unittest

from evidenceweave.models import Claim
from evidenceweave.scoped_semantic import FactScope, scoped_conflict_candidates


def claim(cid, subject, predicate, value):
    return Claim(cid, subject, predicate, value, [cid + "-evidence"])


def evaluate(claims, contexts, **other):
    return scoped_conflict_candidates(
        claims,
        contexts=contexts,
        functional_predicates={"capital"},
        inverse_predicates={"capital_of": "capital"},
        **other,
    )


class ScopedSemanticTests(unittest.TestCase):
    def test_same_time_competing_functional_facts(self):
        claims = [claim("a", "Aurora", "capital", "East"), claim("b", "Aurora", "capital", "West")]
        contexts = {id: FactScope("country-facts", "2026-01-01", "2026-12-31") for id in ("a", "b")}
        self.assertEqual(len(evaluate(claims, contexts)), 1)

    def test_successive_capitals_do_not_conflict(self):
        claims = [claim("a", "Aurora", "capital", "East"), claim("b", "Aurora", "capital", "West")]
        contexts = {"a": FactScope("country-facts", "2000-01-01", "2009-12-31"),
                    "b": FactScope("country-facts", "2010-01-01", "2026-12-31")}
        self.assertEqual(evaluate(claims, contexts), [])

    def test_overlapping_validity_is_a_candidate(self):
        claims = [claim("a", "Aurora", "capital", "East"), claim("b", "Aurora", "capital", "West")]
        contexts = {"a": FactScope("country-facts", "2020-01-01", "2025-01-01"),
                    "b": FactScope("country-facts", "2024-01-01", "2026-12-31")}
        self.assertEqual(len(evaluate(claims, contexts)), 1)

    def test_separate_scopes_are_not_compared(self):
        claims = [claim("a", "Aurora", "capital", "East"), claim("b", "Aurora", "capital", "West")]
        contexts = {"a": FactScope("fiction-world-1"), "b": FactScope("fiction-world-2")}
        self.assertFalse(evaluate(claims, contexts))

    def test_unreviewed_identity_edge_does_not_merge_entities(self):
        claims = [
            claim("same", "Aurora", "same_as", "Republic of Aurora"),
            claim("a", "Aurora", "capital", "East"),
            claim("b", "Republic of Aurora", "capital", "West"),
        ]
        contexts = {item.claim_id: FactScope("example-world") for item in claims}
        self.assertEqual(evaluate(claims, contexts), [])
        self.assertEqual(
            len(evaluate(claims, contexts, approved_equivalence_ids={"same"})), 1,
        )

    def test_inverse_relations_require_same_scope(self):
        claims = [claim("a", "Aurora", "capital", "East"),
                  claim("b", "West", "capital_of", "Aurora")]
        contexts = {"a": FactScope("fiction-A"), "b": FactScope("fiction-B")}
        self.assertFalse(evaluate(claims, contexts))

    def test_missing_context_fails_closed(self):
        claims = [claim("a", "Aurora", "capital", "East")]
        with self.assertRaisesRegex(ValueError, "context"):
            evaluate(claims, {})

    def test_duplicate_claim_ids_fail_closed(self):
        claims = [claim("a", "Aurora", "capital", "East"),
                  claim("a", "Aurora", "capital", "West")]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            evaluate(claims, {"a": FactScope("fiction")})

    def test_invalid_scope_or_date_is_rejected(self):
        with self.assertRaises(ValueError):
            FactScope("")
        with self.assertRaises(ValueError):
            FactScope("fiction", "2026-99-01")
        with self.assertRaises(ValueError):
            FactScope("fiction", "2026-02-01", "2026-01-01")
        with self.assertRaisesRegex(ValueError, "canonical"):
            FactScope("fiction", "20260101")

    def test_reviewed_alias_does_not_cross_policy_domain(self):
        claims = [
            claim("eq", "Aurora", "same_as", "Republic of Aurora"),
            claim("a", "Aurora", "capital", "East"),
            claim("b", "Republic of Aurora", "capital", "West"),
        ]
        # The alias was reviewed for domain A only; the conflicting facts
        # are both about domain B, where that alias is unapproved.
        contexts = {"eq": FactScope("domain-A"),
                    "a": FactScope("domain-B"),
                    "b": FactScope("domain-B")}
        self.assertFalse(evaluate(claims, contexts, approved_equivalence_ids={"eq"}))

    def test_time_bounded_alias_is_rejected_not_applied_globally(self):
        claims = [
            claim("eq", "Aurora", "same_as", "A"),
            claim("a", "Aurora", "capital", "East"),
            claim("b", "A", "capital", "West"),
        ]
        contexts = {"eq": FactScope("fiction", "2010-01-01", "2010-12-31"),
                    "a": FactScope("fiction", "2026-01-01"),
                    "b": FactScope("fiction", "2026-01-01")}
        with self.assertRaisesRegex(ValueError, "Time-scoped equivalence"):
            evaluate(claims, contexts, approved_equivalence_ids={"eq"})

    def test_approval_cannot_turn_ordinary_claim_into_identity(self):
        claims = [claim("a", "Aurora", "capital", "East")]
        with self.assertRaisesRegex(ValueError, "Only identity assertions"):
            evaluate(claims, {"a": FactScope("fiction")}, approved_equivalence_ids={"a"})

    def test_unknown_alias_approval_fails(self):
        claims = [claim("a", "Aurora", "capital", "East")]
        with self.assertRaisesRegex(ValueError, "unknown"):
            evaluate(claims, {"a": FactScope("fiction")}, approved_equivalence_ids={"missing"})


if __name__ == "__main__":
    unittest.main()
