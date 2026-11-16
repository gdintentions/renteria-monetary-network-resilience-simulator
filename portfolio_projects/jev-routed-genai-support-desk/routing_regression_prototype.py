"""Synthetic JEV routing precheck prototype; NOT the archived v0.1.1 router.

Only returns candidate intents when a single explicit phrase is present.
Never authorizes order disclosure, draft approval, refund or customer delivery.
"""
import re

TRACK = re.compile(r"\b(?:track(?:ing)?|where(?:'s| is)|locate)\b.*\b(?:order|parcel|package|shipment)\b|\b(?:order|parcel|package|shipment)\b.*\b(?:track(?:ing)?|where|status|location)\b", re.I)
EXCHANGE = re.compile(r"\b(?:exchange|swap|trade)\b.*\b(?:size|color|item|product)\b|\b(?:size|color|item|product)\b.*\b(?:exchange|swap)\b", re.I)
HUMAN = re.compile(r"\b(?:human|person|representative|agent)\b", re.I)
SENSITIVE = re.compile(r"\b(?:fraud|account locked|billing dispute|stolen card|chargeback)\b", re.I)


def propose_intent(text):
    if not isinstance(text, str) or not 1 <= len(text) <= 2000:
        return {"route": "clarify", "reason": "invalid_input"}
    if HUMAN.search(text) or SENSITIVE.search(text):
        return {"route": "human", "reason": "explicit_handoff"}
    hit_tracking = bool(TRACK.search(text))
    hit_exchange = bool(EXCHANGE.search(text))
    if hit_tracking and hit_exchange:
        return {"route": "clarify", "reason": "mixed_intent"}
    if hit_tracking:
        return {"route": "candidate_order_lookup", "reason": "requires_account_verification"}
    if hit_exchange:
        return {"route": "candidate_exchange", "reason": "requires_policy_and_order_evidence"}
    return {"route": "clarify", "reason": "unrecognized"}

