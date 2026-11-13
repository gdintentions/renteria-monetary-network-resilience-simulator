"""TraceLens: diagnose observed retrieval stages without claiming unseen truth."""
import argparse
import json
from pathlib import Path

LABELS = {"answers", "partial", "unrelated"}

def _scored_selection(candidates, top_k, min_score):
    if type(top_k) is not int or not 1 <= top_k <= 1000:
        raise ValueError("top_k must be an integer between 1 and 1000")
    if type(min_score) not in (int, float) or not 0 <= min_score <= 1:
        raise ValueError("min_score must be between 0 and 1")
    for candidate in candidates:
        score = candidate.get("score")
        if type(score) not in (int, float) or not 0 <= score <= 1.000000000001:
            raise ValueError("candidate score must be a finite cosine similarity in [0, 1]")
    # Governed RAG applies the rank budget first, then filters by score.
    return [row["id"] for row in candidates[:top_k] if row["score"] > min_score]


def _observed_evidence(trace, candidates, kept, gold):
    """Describe the observed stage of each annotated supporting passage."""
    if trace.get("retrieval_ran") is not True:
        if trace.get("retrieval_ran") is not False or candidates or kept or trace.get("used_ids") != []:
            raise ValueError("invalid retrieval observation")
        return {"status": "RETRIEVAL_NOT_RUN"}
    top_k, threshold = trace.get("top_k"), trace.get("min_score")
    if _scored_selection(candidates, top_k, threshold) != kept:
        raise ValueError("kept_ids must match the observed rank and score policy")
    used = trace.get("used_ids")
    if used is not None and (
        not isinstance(used, list) or any(not isinstance(pid, str) for pid in used)
        or len(set(used)) != len(used) or not set(used) <= set(kept)
    ):
        raise ValueError("used_ids must be unique IDs selected by the retrieval policy")
    if gold is None:
        return {"status": "UNLABELED_EVIDENCE"}
    ranked = {row["id"]: (rank, row["score"]) for rank, row in enumerate(candidates, 1)}
    stages = {}
    for pid in gold:
        if pid not in ranked:
            stages[pid] = "outside_candidate_pool"
            continue
        rank, score = ranked[pid]
        if rank > top_k:
            stages[pid] = "below_rank_cutoff"
        elif score <= threshold:
            stages[pid] = "below_score_cutoff"
        elif used is None:
            stages[pid] = "selected"
        else:
            stages[pid] = "used_in_answer" if pid in used else "selected_not_used"
    return {"status": "OBSERVED", "supporting_passages": stages}


def diagnose(trace):
    """Input contains IDs only; passage text is intentionally absent from reports.

    Gold labels are optional, exhaustive corpus annotations, never model guesses.
    Judge labels must cover every candidate exactly once to support a diagnosis.
    """
    if not isinstance(trace, dict): raise ValueError("trace must be an object")
    candidates = trace.get("candidates")
    kept = trace.get("kept_ids")
    def valid_id(value): return isinstance(value, str) and 0 < len(value) <= 200
    if not isinstance(candidates, list) or len(candidates) > 1000:
        raise ValueError("candidates must be a list of at most 1000 entries")
    if any(not isinstance(c, dict) or not valid_id(c.get("id")) for c in candidates):
        raise ValueError("candidate needs a nonempty string ID (at most 200 characters)")
    if not isinstance(kept, list) or any(not valid_id(x) for x in kept):
        raise ValueError("kept_ids must be a list of string IDs")
    ids = [c["id"] for c in candidates]
    kept = trace["kept_ids"]
    if len(set(ids)) != len(ids) or len(set(kept)) != len(kept):
        raise ValueError("duplicate IDs")
    if not set(kept) <= set(ids):
        raise ValueError("kept passage absent from candidate pool")
    for c in candidates:
        if not isinstance(c["id"], str) or not c["id"]:
            raise ValueError("nonempty string ID required")
    labels = trace.get("judge_labels", {})
    valid = isinstance(labels, dict) and set(labels) == set(ids) and all(isinstance(v, str) and v in LABELS for v in labels.values())
    gold = trace.get("gold_ids")
    if gold is not None and (not isinstance(gold, list) or any(not valid_id(x) for x in gold)):
        raise ValueError("gold_ids must be an exhaustive list or omitted")
    if gold is not None and len(set(gold)) != len(gold):
        raise ValueError("duplicate gold IDs")
    observed = _observed_evidence(trace, candidates, kept, gold) if "retrieval_ran" in trace else None
    if observed and observed["status"] == "RETRIEVAL_NOT_RUN":
        return {"status": "RETRIEVAL_NOT_RUN", "kept_ids": kept, "evidence_stages": observed}
    gold_only = observed is not None and gold is not None and "judge_labels" not in trace
    if gold_only:
        supported = set(gold) & set(ids)
    elif valid:
        supported = {pid for pid, label in labels.items() if label == "answers"}
    else:
        result = {"status": "JUDGE_UNAVAILABLE", "kept_ids": kept,
                  "reason": "Missing, extra or invalid judge labels; do not infer a corpus gap."}
        if observed is not None:
            result["evidence_stages"] = observed
        return result
    selected = set(kept)
    cells = {name: [] for name in ("hit", "noise", "miss", "cut")}
    for pid in ids:
        cell = ("hit" if pid in supported else "noise") if pid in selected else ("miss" if pid in supported else "cut")
        cells[cell].append(pid)
    if not ids:
        status = "CORPUS_GAP_CONFIRMED" if gold == [] else ("CANDIDATE_MISS" if gold else "INSUFFICIENT_EVIDENCE")
    elif cells["hit"]:
        status = "NOISY_CONTEXT" if cells["noise"] else "SUPPORTED_CONTEXT"
    elif cells["miss"]:
        status = "SELECTION_MISS"
    elif gold is not None:
        status = "CORPUS_GAP_CONFIRMED" if not gold else ("CANDIDATE_MISS" if not set(gold)&set(ids) else "JUDGE_DISAGREEMENT")
    else:
        status = "INSUFFICIENT_EVIDENCE"
    basis = "supplied judge labels; not answer correctness"
    if gold_only:
        basis = "authored corpus annotations; no judge or answer correctness measurement"
    result = {"status": status, "cells": cells, "basis": basis}
    if observed is not None:
        result["evidence_stages"] = observed
    if gold is not None:
        g=set(gold)
        result["gold_metrics"] = {
            "candidate_recall": len(g&set(ids))/len(g) if g else None,
            "selected_recall": len(g&selected)/len(g) if g else None}
        if not gold_only:
            result["gold_metrics"]["judge_false_positive_ids"] = sorted(supported-g)
            result["gold_metrics"]["judge_false_negative_ids"] = sorted((g&set(ids))-supported)
        if not gold_only and (supported-g or (g&set(ids))-supported):
            result["observed_judge_status"] = status
            result["status"] = "JUDGE_DISAGREEMENT"
    return result

def sweep(trace, budgets):
    """Counterfactual top-k replay, preserving input rank order and judge labels."""
    if "retrieval_ran" in trace:
        baseline = diagnose(trace)
        if baseline["status"] == "RETRIEVAL_NOT_RUN":
            return []
        return [
            {"top_k": k, "diagnosis": diagnose(dict(
                trace, top_k=k, used_ids=None,
                kept_ids=_scored_selection(trace["candidates"], k, trace["min_score"]),
            ))}
            for k in budgets
        ]
    out=[]
    for k in budgets:
        if type(k) is not int or k < 1: raise ValueError("positive integer budget required")
        replay=dict(trace, kept_ids=[c["id"] for c in trace["candidates"][:k]])
        out.append({"top_k":k, "diagnosis":diagnose(replay)})
    return out


def sweep_scores(trace, thresholds):
    """Replay the score threshold while keeping the original top-k budget."""
    baseline = diagnose(trace)
    if "evidence_stages" not in baseline:
        raise ValueError("score replay requires a scored retrieval observation")
    if baseline["status"] == "RETRIEVAL_NOT_RUN":
        return []
    return [
        {"min_score": threshold, "diagnosis": diagnose(dict(
            trace, min_score=threshold, used_ids=None,
            kept_ids=_scored_selection(trace["candidates"], trace["top_k"], threshold),
        ))}
        for threshold in thresholds
    ]


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    replay = parser.add_mutually_exclusive_group()
    replay.add_argument("--sweep", nargs="+", type=int)
    replay.add_argument("--score-sweep", nargs="+", type=float)
    args=parser.parse_args()
    trace=json.loads(args.trace.read_text())
    if args.sweep:
        result = sweep(trace, args.sweep)
    elif args.score_sweep:
        result = sweep_scores(trace, args.score_sweep)
    else:
        result = diagnose(trace)
    print(json.dumps(result, indent=2))
