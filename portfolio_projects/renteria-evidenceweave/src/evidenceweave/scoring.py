from __future__ import annotations

import math
import re
from collections import Counter

from .models import ScoreBreakdown

TOKEN = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> list[str]:
    return TOKEN.findall(text.casefold())


def cosine_text(left: str, right: str) -> float:
    a, b = Counter(tokens(left)), Counter(tokens(right))
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(term, 0) for term, value in a.items())
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    return dot / (norm_a * norm_b)


def sigmoid(value: float) -> float:
    return 1 / (1 + math.exp(-value))


def evidence_integrity(
    *,
    semantic: float,
    graph_support: float,
    cross_modal: float,
    source_reliability: float,
    freshness: float,
    contradiction: float,
    ambiguity: float,
) -> ScoreBreakdown:
    """Return the Evidence Integrity Score and its inspectable components."""
    logit = (
        1.50 * semantic
        + 1.20 * graph_support
        + 1.10 * cross_modal
        + 1.00 * source_reliability
        + 0.60 * freshness
        - 1.80 * contradiction
        - 0.90 * ambiguity
        - 1.40
    )
    return ScoreBreakdown(
        semantic=semantic,
        graph_support=graph_support,
        cross_modal=cross_modal,
        source_reliability=source_reliability,
        freshness=freshness,
        contradiction=contradiction,
        ambiguity=ambiguity,
        integrity=sigmoid(logit),
    )

