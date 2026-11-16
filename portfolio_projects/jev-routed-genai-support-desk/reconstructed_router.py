"""Clean-room, synthetic JEV routing reconstruction; NOT archived v0.1.1 code.

No model API, messages sent, account lookup, refunds, approvals or user data.
Classification is a deterministic *candidate disposition* only.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass

TRACK = re.compile(
    r"\b(?:track(?:ing)?|locate|find|where(?:'s| is)|status|update)\b.{0,90}\b(?:order|package|parcel|shipment|delivery)\b"
    r"|\b(?:order|package|parcel|shipment|delivery)\b.{0,90}\b(?:track(?:ing)?|where|status|location|update)\b",
    re.I,
)
EXCHANGE = re.compile(
    r"\b(?:exchange|swap|trade|replace)\b.{0,90}\b(?:size|color|item|product|shirt|jacket)\b"
    r"|\b(?:size|color|item|product|shirt|jacket)\b.{0,90}\b(?:exchange|swap|different)\b",
    re.I,
)
HUMAN = re.compile(r"\b(?:human|person|representative|agent|supervisor)\b", re.I)
SENSITIVE = re.compile(
    r"\b(?:fraud|identity theft|account locked|chargeback|billing dispute|stolen card|card (?:was |is )?stolen|compromised account)\b",
    re.I,
)
RETURN = re.compile(r"\b(?:return|refund)\b", re.I)
PROMISE = re.compile(r"\b(?:guarantee|guaranteed|guaranteed refund|refund approved|credit issued|we have refunded)\b", re.I)


@dataclass(frozen=True)
class Disposition:
    route: str
    reason: str
    release_authorized: bool = False
    verified_order: bool = False

    def record(self) -> dict:
        return asdict(self)


def route_ticket(
    text: str,
    *,
    order_verified: bool = False,
    exchange_policy_verified: bool = False,
) -> Disposition:
    """Fail closed. Verified flags are supplied only by a trusted external adapter.

    These flags are simulation controls, not actual identity/ownership verification.
    """
    if not isinstance(text, str) or not text.strip() or len(text) > 2000:
        return Disposition("clarify", "invalid_input")
    if type(order_verified) is not bool or type(exchange_policy_verified) is not bool:
        return Disposition("human", "invalid_verification_flag")
    if HUMAN.search(text) or SENSITIVE.search(text):
        return Disposition("human", "human_or_sensitive")
    tracking, exchange = bool(TRACK.search(text)), bool(EXCHANGE.search(text))
    if (tracking and exchange) or (exchange and RETURN.search(text)):
        return Disposition("clarify", "mixed_intent")
    if exchange:
        if not order_verified or not exchange_policy_verified:
            return Disposition("clarify", "exchange_evidence_missing")
        return Disposition("agent_review", "exchange_candidate_with_evidence", verified_order=True)
    if tracking:
        if not order_verified:
            return Disposition("clarify", "order_ownership_unverified")
        return Disposition("read_only_order_lookup", "verified_order_candidate", verified_order=True)
    if RETURN.search(text):
        return Disposition("human", "return_or_refund_requires_review")
    return Disposition("clarify", "unrecognized")


def guard_draft(draft: str, *, source_ids: list[str], approved_ids: set[str]) -> Disposition:
    """Never approves delivery. A passing guard means only agent review is possible."""
    if not isinstance(draft, str) or not draft.strip() or len(draft) > 4000:
        return Disposition("hold", "bad_draft")
    if not source_ids or len(set(source_ids)) != len(source_ids):
        return Disposition("hold", "source_ids_missing_or_duplicate")
    if not set(source_ids).issubset(approved_ids):
        return Disposition("hold", "unapproved_source_id")
    if PROMISE.search(draft):
        return Disposition("hold", "unauthorized_promise")
    return Disposition("agent_review", "candidate_draft_screened_not_semantically_verified")
