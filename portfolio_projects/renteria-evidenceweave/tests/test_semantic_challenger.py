import unittest

from evidenceweave.models import Claim
from evidenceweave.semantic_challenger import semantic_candidates


def c(label, subject, predicate, value):
    return Claim(label, subject, predicate, value, [label + "-evidence"])


CONFIG = {"functional_predicates": {"capital"},
          "inverse_predicates": {"capital_of": "capital"}}


class SemanticChallengerTests(unittest.TestCase):
    def test_explicit_transitive_entity_equivalence(self):
        claims = [c("eq1", "A", "same_as", "B"),
                  c("eq2", "B", "same_as", "C"),
                  c("one", "A", "capital", "Eastport"),
                  c("two", "C", "capital", "Westport")]
        found = semantic_candidates(claims, **CONFIG)
        self.assertEqual(len(found), 1)
        self.assertEqual({found[0].left_claim_id, found[0].right_claim_id}, {"one", "two"})

    def test_declared_inverse_relation_exposes_competing_capitals(self):
        claims = [c("a", "Aurora", "capital", "Eastport"),
                  c("b", "Westport", "capital_of", "Aurora")]
        found = semantic_candidates(claims, **CONFIG)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].rationale, "declared_inverse")

    def test_indirect_chain_without_functional_disagreement_is_not_conflict(self):
        claims = [c("a", "Aurora", "neighbor", "Borealis"),
                  c("b", "Borealis", "capital", "Northport")]
        self.assertFalse(semantic_candidates(claims, **CONFIG))

    def test_multivalued_language_is_not_functional(self):
        claims = [c("a", "Aurora", "spoken_language", "French"),
                  c("b", "Aurora", "spoken_language", "English")]
        self.assertFalse(semantic_candidates(claims, **CONFIG))

    def test_identical_facts_do_not_false_alarm(self):
        claims = [c("a", "Aurora", "capital", "Eastport"),
                  c("b", "Aurora", "capital", " eastport ")]
        self.assertFalse(semantic_candidates(claims, **CONFIG))

    def test_no_alias_fabrication(self):
        claims = [c("a", "Aurora", "capital", "Eastport"),
                  c("b", "Republic of Aurora", "capital", "Westport")]
        self.assertFalse(semantic_candidates(claims, **CONFIG))

    def test_explicit_value_alias_prevents_false_alarm(self):
        claims = [c("e", "Eastport", "same_as", "City of Eastport"),
                  c("a", "Aurora", "capital", "Eastport"),
                  c("b", "Aurora", "capital", "City of Eastport")]
        self.assertFalse(semantic_candidates(claims, **CONFIG))

    def test_no_configured_functional_predicate(self):
        claims = [c("a", "Aurora", "capital", "Eastport"),
                  c("b", "Aurora", "capital", "Westport")]
        self.assertFalse(semantic_candidates(
            claims, functional_predicates=(), inverse_predicates={}))


if __name__ == "__main__":
    unittest.main()
