"""Replay an explicitly scoped functional-conflict challenger against historical misses.

This is an exposed development benchmark, not independent semantic validation.
Only the reported false-negative entries are available; original control
triples for four false positives are not reconstructed here.
"""
from __future__ import annotations
import json
from pathlib import Path

from evidenceweave.external_eval import parse_triple
from evidenceweave.functional_challenger import functional_conflict_candidates
from evidenceweave.models import Claim

# Explicit schema sample: no automated guess that other predicates are functional.
FUNCTIONAL = {"location.country.capital"}
PREDICATE_ALIASES = {
    "base.aareas.schema.administrative_area.capital": "location.country.capital"
}

def evaluate_failures(data):
    examined = 0
    recovered = []
    malformed = 0
    for row in data["failures"]:
        if row["failure_category"] != "missed-conflict":
            continue
        examined += 1
        triples = row.get("conflicting_triples", [])
        claims = []
        for i, raw in enumerate(triples):
            parsed = parse_triple(raw)
            if parsed is None:
                malformed += 1
                continue
            claims.append(Claim(f"{row['id']}:{i}", *parsed))
        conflicts = functional_conflict_candidates(
            claims, functional_predicates=FUNCTIONAL,
            predicate_aliases=PREDICATE_ALIASES)
        if conflicts:
            recovered.append(row["id"])
    if examined != 258:
        raise ValueError(f"Historical miss count drifted: {examined}")
    return {
        "scope": "already-seen failure-only replay; not full paired precision or independent validation",
        "misses_inspected": examined,
        "schema_candidate_alarms_on_misses": len(recovered),
        "alarm_ids": recovered,
        "unparsed_triples": malformed,
        "historical_recall": 0.4,
        "full_test_precision": None,
        "full_test_recall": None,
        "claim": "No external accuracy improvement asserted",
    }


def main():
    path = Path("artifacts/conflictqa-external-eval.json")
    data = json.loads(path.read_text())
    report = evaluate_failures(data)
    destination = Path("artifacts/challenger-schema-replay.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "alarm_ids"}, indent=2))


if __name__ == "__main__":
    main()
