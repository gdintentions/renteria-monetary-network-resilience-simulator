"""TraceLens: diagnose observed retrieval stages without claiming unseen truth."""
import argparse
import json
from pathlib import Path

LABELS = {"answers", "partial", "unrelated"}

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
    if not valid:
        return {"status": "JUDGE_UNAVAILABLE", "kept_ids": kept,
                "reason": "Missing, extra or invalid judge labels; do not infer a corpus gap."}
    supported = {pid for pid, label in labels.items() if label == "answers"}
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
    result = {"status": status, "cells": cells, "basis": "supplied judge labels; not answer correctness"}
    if gold is not None:
        g=set(gold)
        result["gold_metrics"] = {
            "candidate_recall": len(g&set(ids))/len(g) if g else None,
            "selected_recall": len(g&selected)/len(g) if g else None,
            "judge_false_positive_ids": sorted(supported-g),
            "judge_false_negative_ids": sorted((g&set(ids))-supported)}
        if result["gold_metrics"]["judge_false_positive_ids"] or result["gold_metrics"]["judge_false_negative_ids"]:
            result["observed_judge_status"] = status
            result["status"] = "JUDGE_DISAGREEMENT"
    return result

def sweep(trace, budgets):
    """Counterfactual top-k replay, preserving input rank order and judge labels."""
    out=[]
    for k in budgets:
        if type(k) is not int or k < 1: raise ValueError("positive integer budget required")
        replay=dict(trace, kept_ids=[c["id"] for c in trace["candidates"][:k]])
        out.append({"top_k":k, "diagnosis":diagnose(replay)})
    return out

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--sweep", nargs="+", type=int)
    args=parser.parse_args()
    trace=json.loads(args.trace.read_text())
    print(json.dumps(sweep(trace,args.sweep) if args.sweep else diagnose(trace),indent=2))
