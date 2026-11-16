"""Strict JEV preview composer; draft-screening is NOT semantic certification.

Unlike source-ID-only guard checks, this composer accepts a restricted,
human-reviewed fact vocabulary and emits fixed text only. It does not send to
customers, execute order actions, or certify the verifier's identity.
"""
from __future__ import annotations

from dataclasses import dataclass

from reconstructed_router import Disposition


@dataclass(frozen=True)
class VerifiedFact:
    key: str
    value: str
    source_id: str
    verified: bool


@dataclass(frozen=True)
class AgentPreview:
    status: str
    text: str | None
    reason: str
    source_ids: tuple[str, ...]
    release_authorized: bool = False


ORDER_STATUSES = {
    "processing": "The order is processing.",
    "shipped": "The order has shipped.",
    "in_transit": "The order is in transit.",
    "delivered": "The order is marked delivered.",
    "delayed": "The order is delayed.",
}
EXCHANGE_STATES = {
    "requires_review": "The exchange requires review.",
    "eligible_for_review": "The exchange may be eligible for review.",
    "not_eligible": "The exchange appears outside the stated policy.",
}


def compose_agent_preview(
    decision: Disposition,
    facts: list[VerifiedFact],
    *,
    approved_sources: set[str],
) -> AgentPreview:
    """Only typed, verified, allowlisted facts may enter the preview."""
    def hold(reason: str) -> AgentPreview:
        return AgentPreview("HOLD", None, reason, ())

    if not isinstance(decision, Disposition) or decision.release_authorized:
        return hold("invalid_or_released_decision")
    if decision.route not in {"read_only_order_lookup", "agent_review"}:
        return hold("not_a_reviewable_route")
    if decision.verified_order is not True:
        return hold("order_ownership_not_verified")
    if not isinstance(facts, list) or len(facts) != 1 or not isinstance(facts[0], VerifiedFact):
        return hold("exactly_one_typed_fact_required")
    fact = facts[0]
    if type(fact.verified) is not bool or not fact.verified:
        return hold("unverified_fact")
    if not isinstance(fact.source_id, str) or not fact.source_id or fact.source_id not in approved_sources:
        return hold("unapproved_fact_source")
    if decision.route == "read_only_order_lookup":
        if fact.key != "order_status" or fact.value not in ORDER_STATUSES:
            return hold("unsupported_status_value")
        text = ORDER_STATUSES[fact.value]
    else:
        if fact.key != "exchange_policy" or fact.value not in EXCHANGE_STATES:
            return hold("unsupported_exchange_value")
        text = EXCHANGE_STATES[fact.value]
    return AgentPreview("PENDING_AGENT_REVIEW", text, "fixed_template_from_verified_fact", (fact.source_id,))
