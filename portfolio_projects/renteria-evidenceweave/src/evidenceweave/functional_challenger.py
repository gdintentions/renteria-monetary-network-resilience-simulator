"""Opt-in functional-fact conflict challenger for EvidenceWeave.

Only declared single-valued predicates are compared. Alias maps are supplied by
a policy/domain owner; this module must never silently infer equivalents.
It is NOT calibrated semantic contradiction detection.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .models import Claim


def canonical(value: str) -> str:
    return " ".join(value.casefold().split())


@dataclass(frozen=True)
class ConflictCandidate:
    subject: str
    predicate: str
    first_claim_id: str
    second_claim_id: str
    first_value: str
    second_value: str


def functional_conflict_candidates(
    claims: Iterable[Claim],
    *,
    functional_predicates: Iterable[str],
    predicate_aliases: Mapping[str, str] | None = None,
    entity_aliases: Mapping[str, str] | None = None,
) -> list[ConflictCandidate]:
    """Return competing values for *declared* single-valued attributes.

    Unspecified predicates are never assumed single-valued; time-scoped claims
    should be separated before calling if facts can legitimately change.
    """
    predicates = {canonical(x) for x in functional_predicates}
    if not predicates:
        return []
    p_alias = {canonical(k): canonical(v) for k, v in (predicate_aliases or {}).items()}
    e_alias = {canonical(k): canonical(v) for k, v in (entity_aliases or {}).items()}

    def resolve(value, mapping):
        seen = set()
        current = canonical(value)
        while current in mapping:
            if current in seen:
                raise ValueError("Alias cycle detected")
            seen.add(current)
            current = mapping[current]
        return current

    buckets: dict[tuple[str, str], list[Claim]] = {}
    for claim in claims:
        if not isinstance(claim, Claim):
            raise TypeError("Expected Claim objects")
        predicate = resolve(claim.predicate, p_alias)
        if predicate not in predicates:
            continue
        key = resolve(claim.subject, e_alias), predicate
        buckets.setdefault(key, []).append(claim)

    conflicts = []
    for (subject, predicate), group in sorted(buckets.items()):
        for i, left in enumerate(group):
            for right in group[i + 1:]:
                if canonical(left.value) != canonical(right.value):
                    conflicts.append(ConflictCandidate(
                        subject, predicate, left.claim_id, right.claim_id,
                        left.value, right.value,
                    ))
    return conflicts
