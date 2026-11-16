"""Deterministic author-labeled development fixtures (NOT a holdout).

Measure paired detection and false alarms on built-in synthetic scenarios.
These examples test mechanics only; they do not establish ConflictQA recall.
"""
from __future__ import annotations

import json
from pathlib import Path

from evidenceweave.graph import ClaimGraph
from evidenceweave.models import Claim
from evidenceweave.semantic_challenger import semantic_candidates


def c(label: str, subject: str, predicate: str, value: str) -> Claim:
    return Claim(label, subject, predicate, value, [label + "-ev"])


SCENARIOS = [
    ("direct_conflict", True, [c("a1", "Aurora", "capital", "Eastport"), c("a2", "Aurora", "capital", "Westport")]),
    ("inverse_conflict", True, [c("b1", "Aurora", "capital", "Eastport"), c("b2", "Westport", "capital_of", "Aurora")]),
    ("two_hop_alias_conflict", True, [c("c1", "Aurora", "same_as", "A"), c("c2", "A", "same_as", "B"),
                                      c("c3", "Aurora", "capital", "Eastport"), c("c4", "B", "capital", "Westport")]),
    ("no_conflict_indirect", False, [c("d1", "Aurora", "neighbor", "Borealis"), c("d2", "Borealis", "capital", "Northport")]),
    ("no_conflict_multivalued", False, [c("e1", "Aurora", "spoken_language", "French"), c("e2", "Aurora", "spoken_language", "English")]),
    ("no_conflict_matching_inverse", False, [c("f1", "Aurora", "capital", "Eastport"), c("f2", "Eastport", "capital_of", "Aurora")]),
    ("no_conflict_alias_value", False, [c("g1", "Eastport", "same_as", "City of Eastport"),
                                         c("g2", "Aurora", "capital", "Eastport"), c("g3", "Aurora", "capital", "City of Eastport")]),
    ("no_conflict_separate_entities", False, [c("h1", "Aurora", "capital", "Eastport"),
                                               c("h2", "Borealis", "capital", "Westport")]),
]


def evaluate() -> dict:
    results = []
    for name, expected, claims in SCENARIOS:
        graph = ClaimGraph()
        for item in claims:
            graph.add(item)
        baseline = bool(graph.conflicts())
        challenger = bool(semantic_candidates(
            claims, functional_predicates={"capital"},
            inverse_predicates={"capital_of": "capital"}))
        results.append({"id": name, "expected_conflict": expected, "baseline": baseline, "challenger": challenger})
    def counts(key):
        return {
            "tp": sum(v["expected_conflict"] and v[key] for v in results),
            "fp": sum(not v["expected_conflict"] and v[key] for v in results),
            "tn": sum(not v["expected_conflict"] and not v[key] for v in results),
            "fn": sum(v["expected_conflict"] and not v[key] for v in results),
        }
    return {"scope": "author-labeled synthetic development fixtures; no independent or external accuracy claim",
            "baseline": counts("baseline"), "challenger": counts("challenger"), "cases": results}


if __name__ == "__main__":
    output = evaluate()
    path = Path("artifacts/semantic-challenger-development.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
