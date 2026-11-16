"""Optional, conservative SourceGate literal-evidence binding.

Exact value mention is a minimal *syntactic* evidence check. It cannot prove
semantic support or source authority. Run this alongside—not in place of—
independent factual review. Does not alter the baseline SourceGate API.
"""
from __future__ import annotations

import json
import re
from dataclasses import replace
from datetime import date

from sourcegate import Evidence, run


def _scalar_token(value: object) -> str | None:
    if value is None or isinstance(value, (list, dict)):
        return None
    if isinstance(value, str):
        return value.strip().casefold() or None
    if isinstance(value, (bool, int, float)):
        return json.dumps(value, allow_nan=False).casefold()
    return None


def _literal_mentioned(text: str, value: object) -> bool:
    token = _scalar_token(value)
    if token is None:
        return False
    # Word-character boundaries prevent 14 matching 314, or "IT" in item.
    return bool(re.search(r"(?<!\w)" + re.escape(token) + r"(?!\w)", text.casefold()))


def run_literal_supported(
    question: str,
    required_claims: list[str],
    docs: list[Evidence],
    *,
    allowed_hosts: set[str],
    today: date,
) -> dict:
    """Refuse all required claims that lack a value literally present in text.

    This intentionally causes false holds on paraphrases and does NOT certify
    textual entailment. No web fallback or model evaluator is invoked.
    """
    try:
        if not isinstance(docs, list) or any(not isinstance(doc, Evidence) for doc in docs):
            raise TypeError("Evidence records required")
        unsupported = []
        filtered = []
        for doc in docs:
            if not isinstance(doc.claims, dict) or not isinstance(doc.text, str):
                raise TypeError("Claim object and text required")
            claims = {}
            for key, value in doc.claims.items():
                if _literal_mentioned(doc.text, value):
                    claims[key] = value
                else:
                    unsupported.append({"evidence_id": doc.id, "claim_key": key})
            filtered.append(replace(doc, claims=claims))
        result = run(
            question, required_claims,
            lambda _: filtered,
            lambda _, evidence: {item.id: "relevant" for item in evidence},
            lambda _: [],
            allowed_hosts=allowed_hosts,
            today=today,
            web_allowed=False,
        )
        result["literal_binding"] = {
            "status": "SYNTACTIC_ONLY_NO_SEMANTIC_ENTAILMENT",
            "unbound_claims": unsupported,
        }
        return result
    except (ValueError, TypeError, OverflowError) as error:
        return {
            "status": "NEEDS_REVIEW",
            "reason": "STRICT_BINDING_FAILURE",
            "error_type": type(error).__name__,
            "answer": None,
            "literal_binding": {"status": "INVALID_INPUT"},
        }
