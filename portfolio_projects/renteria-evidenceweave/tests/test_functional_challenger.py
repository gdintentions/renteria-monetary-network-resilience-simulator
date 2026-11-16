import unittest

from evidenceweave.models import Claim
from evidenceweave.functional_challenger import functional_conflict_candidates


class FunctionalChallengerTests(unittest.TestCase):
    def make(self, id, subj, pred, value):
        return Claim(id, subj, pred, value, [id + ":e"])

    def test_alias_catches_previous_exact_key_miss(self):
        claims = [
            self.make("a", "Example Republic", "location.country.capital", "North City"),
            self.make("b", "Example Republic", "base.aareas.schema.administrative_area.capital", "South City"),
        ]
        result = functional_conflict_candidates(
            claims,
            functional_predicates={"location.country.capital"},
            predicate_aliases={"base.aareas.schema.administrative_area.capital": "location.country.capital"},
        )
        self.assertEqual([(x.first_claim_id, x.second_claim_id) for x in result], [("a", "b")])

    def test_multi_valued_attributes_not_marked_conflict(self):
        claims = [self.make("a", "Example Person", "people.person.children", "Child A"),
                  self.make("b", "Example Person", "people.person.children", "Child B")]
        self.assertEqual(functional_conflict_candidates(
            claims, functional_predicates={"location.country.capital"}), [])

    def test_functional_competing_values_detected(self):
        claims = [self.make("a", "Example Republic", "location.country.capital", "North City"),
                  self.make("b", "Example Republic", "location.country.capital", "South City")]
        self.assertEqual(len(functional_conflict_candidates(
            claims, functional_predicates={"location.country.capital"})), 1)

    def test_value_normalization_avoids_false_alert(self):
        claims = [self.make("a", "Example Republic", "location.country.capital", "North City"),
                  self.make("b", "example republic", "location.country.capital", " north   CITY ")]
        self.assertFalse(functional_conflict_candidates(
            claims, functional_predicates={"location.country.capital"}))

    def test_explicit_entity_alias_only(self):
        claims = [self.make("a", "Example Republic", "location.country.capital", "North City"),
                  self.make("b", "ER", "location.country.capital", "South City")]
        self.assertFalse(functional_conflict_candidates(
            claims, functional_predicates={"location.country.capital"}))
        self.assertEqual(len(functional_conflict_candidates(
            claims, functional_predicates={"location.country.capital"},
            entity_aliases={"ER": "Example Republic"})), 1)

    def test_alias_cycle_fails_closed(self):
        claims = [self.make("a", "x", "p1", "v")]
        with self.assertRaisesRegex(ValueError, "cycle"):
            functional_conflict_candidates(claims, functional_predicates={"p1"},
                predicate_aliases={"p1": "p2", "p2": "p1"})

    def test_no_schema_no_conflict_promotion(self):
        claims = [self.make("a", "x", "p", "v1"), self.make("b", "x", "p", "v2")]
        self.assertFalse(functional_conflict_candidates(claims, functional_predicates=set()))


if __name__ == "__main__":
    unittest.main()
