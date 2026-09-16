from __future__ import annotations

import re
from dataclasses import dataclass

from .models import Action, Risk

RANK = {Risk.low: 0, Risk.medium: 1, Risk.high: 2, Risk.critical: 3}
SENSITIVE = re.compile(r"(?i)(password|passcode|api[_ -]?key|secret|seed phrase|ssn|credit card)")
DANGEROUS_KEYS = {"delete", "f4"}


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


def authorize(action: Action, max_risk: str, mode: str) -> Decision:
    if action.risk == Risk.critical:
        return Decision(False, "critical actions are never automated")
    if RANK[action.risk] > RANK[Risk(max_risk)]:
        return Decision(False, f"risk {action.risk.value} exceeds policy ceiling {max_risk}")
    if action.text and SENSITIVE.search(action.text):
        return Decision(False, "possible secret or sensitive credential detected")
    if action.action == "press_key" and (action.key or "").lower() in DANGEROUS_KEYS:
        return Decision(False, "destructive/system key is blocked")
    if mode == "dry-run" and action.action not in {"wait", "done"}:
        return Decision(False, "dry-run: proposed action recorded but not executed")
    return Decision(True, "policy approved")

