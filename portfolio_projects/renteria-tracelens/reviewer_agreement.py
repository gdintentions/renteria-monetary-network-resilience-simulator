"""TraceLens two-reviewer alignment and disagreement queue.

Works on reviewer-supplied ID/label mappings; no inference or private passage
text is transmitted. Agreement is NOT accuracy, and reviewer independence
cannot be established automatically by this module.
"""
from __future__ import annotations

from collections import Counter

LABELS = {"answers", "partial", "unrelated"}


def compare_reviewers(candidate_ids: list[str], reviewer_a: dict, reviewer_b: dict) -> dict:
    if not isinstance(candidate_ids, list) or len(candidate_ids) < 2:
        raise ValueError("At least two candidate IDs required")
    if any(not isinstance(cid, str) or not cid for cid in candidate_ids):
        raise ValueError("Nonempty IDs required")
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ValueError("Duplicate candidate IDs")
    reference = set(candidate_ids)
    for review in (reviewer_a, reviewer_b):
        if not isinstance(review, dict) or set(review) != reference:
            raise ValueError("Each reviewer must label exactly the same candidate IDs")
        if any(type(label) is not str or label not in LABELS for label in review.values()):
            raise ValueError("Reviewer labels must be answers, partial or unrelated")
    same = sum(reviewer_a[cid] == reviewer_b[cid] for cid in candidate_ids)
    n = len(candidate_ids)
    freq_a, freq_b = Counter(reviewer_a.values()), Counter(reviewer_b.values())
    expected = sum(freq_a[k] * freq_b[k] for k in LABELS) / (n * n)
    observed = same / n
    kappa = (observed - expected) / (1 - expected) if expected < 1 else None
    disagreements = [
        {"id": cid, "reviewer_a": reviewer_a[cid], "reviewer_b": reviewer_b[cid]}
        for cid in candidate_ids if reviewer_a[cid] != reviewer_b[cid]
    ]
    return {
        "cases": n,
        "raw_agreement": observed,
        "cohen_kappa": kappa,
        "degenerate_single_label": expected == 1,
        "disagreement_count": len(disagreements),
        "needs_adjudication": disagreements,
        "consensus_ids": [cid for cid in candidate_ids if reviewer_a[cid] == reviewer_b[cid]],
        "independent_review_verified": False,
        "accuracy_measured": False,
        "evaluation_boundary": "Agreement between provided labels only; does not certify relevance or truth.",
    }
