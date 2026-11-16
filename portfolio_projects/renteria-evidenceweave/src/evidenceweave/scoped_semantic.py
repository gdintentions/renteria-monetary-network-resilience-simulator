"""Review-bound semantic conflict candidates for the experimental EvidenceWeave layer.

A functional property can change over time, and two entities may only be aliases
if a reviewer approves the identity relation. This wrapper adds those safeguards
WITHOUT changing the published exact-key graph baseline or default answer path.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date

from .models import Claim
from .semantic_challenger import SemanticCandidate, norm, semantic_candidates


@dataclass(frozen=True)
class FactScope:
    """Inclusive time bounds and explicit policy/domain boundary."""

    domain: str
    valid_from: str | None = None
    valid_to: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.domain, str) or not self.domain.strip():
            raise ValueError("A nonempty domain scope is required")
        for value in (self.valid_from, self.valid_to):
            if value is not None:
                if not isinstance(value, str):
                    raise ValueError("Dates must be ISO date strings")
                date.fromisoformat(value)
        if self.valid_from and self.valid_to and self.valid_from > self.valid_to:
            raise ValueError("Validity interval end precedes start")


def _overlaps(left: FactScope, right: FactScope) -> bool:
    if norm(left.domain) != norm(right.domain):
        return False
    if left.valid_to is not None and right.valid_from is not None and left.valid_to < right.valid_from:
        return False
    return not (right.valid_to is not None and left.valid_from is not None and right.valid_to < left.valid_from)


def scoped_conflict_candidates(
    claims: Iterable[Claim],
    *,
    contexts: Mapping[str, FactScope],
    functional_predicates: Iterable[str],
    inverse_predicates: Mapping[str, str] | None = None,
    approved_equivalence_ids: Iterable[str] = (),
    equivalence_predicate: str = "same_as",
) -> list[SemanticCandidate]:
    """Return only same-domain, overlapping fact conflicts.

    Equivalence edges require claim-ID approval. Missing contexts fail closed;
    approval is local review metadata, never evidence that an alias is true.
    """
    items = list(claims)
    ids = [item.claim_id for item in items]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate claim IDs")
    if set(ids) != set(contexts) or not all(isinstance(contexts[x], FactScope) for x in ids):
        raise ValueError("All claims must have exactly one validated context")
    approved = set(approved_equivalence_ids)
    if not approved.issubset(set(ids)):
        raise ValueError("Approved aliases reference unknown claim IDs")
    usable: list[Claim] = []
    for claim in items:
        if norm(claim.predicate) != norm(equivalence_predicate):
            usable.append(claim)
        elif claim.claim_id in approved:
            usable.append(claim)
    candidates = semantic_candidates(
        usable,
        functional_predicates=functional_predicates,
        inverse_predicates=dict(inverse_predicates or {}),
        equivalence_predicate=equivalence_predicate,
    )
    return [
        candidate for candidate in candidates
        if _overlaps(contexts[candidate.left_claim_id], contexts[candidate.right_claim_id])
    ]
