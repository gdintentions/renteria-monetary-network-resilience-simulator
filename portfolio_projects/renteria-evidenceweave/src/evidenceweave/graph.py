from __future__ import annotations

from collections import defaultdict

from .models import Claim


class ClaimGraph:
    """Small dependency-free graph optimized for provenance inspection."""

    def __init__(self) -> None:
        self.claims: dict[str, Claim] = {}
        self.by_key: dict[tuple[str, str], list[str]] = defaultdict(list)

    def add(self, claim: Claim) -> None:
        self.claims[claim.claim_id] = claim
        self.by_key[claim.key].append(claim.claim_id)

    def competing(self, claim: Claim) -> list[Claim]:
        return [
            self.claims[claim_id]
            for claim_id in self.by_key.get(claim.key, [])
            if self.claims[claim_id].value.casefold() != claim.value.casefold()
        ]

    def conflicts(self, claims: list[Claim] | None = None) -> list[str]:
        selected = claims or list(self.claims.values())
        messages: set[str] = set()
        for claim in selected:
            for other in self.competing(claim):
                values = sorted({claim.value, other.value})
                messages.add(f"{claim.subject} · {claim.predicate}: {' vs '.join(values)}")
        return sorted(messages)

    def edges(self) -> list[tuple[str, str, str]]:
        edges: list[tuple[str, str, str]] = []
        for claim in self.claims.values():
            edges.append((claim.subject, claim.value, claim.predicate))
        return edges

