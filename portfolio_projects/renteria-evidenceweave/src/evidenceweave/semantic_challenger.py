"""Opt-in, rule-scoped semantic candidate detector.

Adds explicit entity equivalence and *declared* inverse relation normalization.
Neither a new triple nor an inferred multi-hop association implies contradiction.
Every emitted conflict must contain two unequal facts for a configured functional
property of the same resolved subject, with attributable claim IDs.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from .models import Claim


def norm(text: str) -> str:
    return " ".join(text.casefold().split())


@dataclass(frozen=True)
class SemanticCandidate:
    subject: str
    predicate: str
    left_claim_id: str
    right_claim_id: str
    left_value: str
    right_value: str
    rationale: str


def semantic_candidates(
    claims: Iterable[Claim],
    *,
    functional_predicates: Iterable[str],
    inverse_predicates: dict[str, str] | None = None,
    equivalence_predicate: str = "same_as",
) -> list[SemanticCandidate]:
    """Only author-specified equivalences and inverse relations are followed."""
    items = list(claims)
    parent: dict[str, str] = {}

    def root(x: str) -> str:
        x = norm(x)
        parent.setdefault(x, x)
        while parent[x] != x:
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        a, b = root(a), root(b)
        if a != b:
            parent[max(a, b)] = min(a, b)

    # No fuzzy, generated, or transitive semantic inference beyond explicit
    # equivalence assertions. A chain of these is valid union-find equality.
    for claim in items:
        if norm(claim.predicate) == norm(equivalence_predicate):
            union(claim.subject, claim.value)

    inverse = {norm(k): norm(v) for k, v in (inverse_predicates or {}).items()}
    functional = {norm(v) for v in functional_predicates}
    buckets: dict[tuple[str, str], list[tuple[Claim, str, str]]] = defaultdict(list)
    for claim in items:
        predicate = norm(claim.predicate)
        if predicate == norm(equivalence_predicate):
            continue
        subject, value = claim.subject, claim.value
        rationale = "direct"
        if predicate in inverse:
            subject, value = value, subject
            predicate = inverse[predicate]
            rationale = "declared_inverse"
        if predicate not in functional:
            continue
        buckets[(root(subject), predicate)].append((claim, root(value), rationale))

    found = []
    for (subject, predicate), facts in sorted(buckets.items()):
        for idx, (left, left_value, left_reason) in enumerate(facts):
            for right, right_value, right_reason in facts[idx + 1 :]:
                if left_value == right_value:
                    continue
                found.append(
                    SemanticCandidate(
                        subject, predicate, left.claim_id, right.claim_id,
                        left.value, right.value,
                        "declared_inverse" if "declared_inverse" in (left_reason, right_reason) else "explicit_equivalence_or_direct",
                    )
                )
    return found
