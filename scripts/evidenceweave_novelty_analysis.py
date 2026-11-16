#!/usr/bin/env python3
"""Analyze novel claims in already-inspected EvidenceWeave ConflictQA failures.

Novel triples are NOT automatically contradictions; report a separate candidate
signal without changing or relabeling published ConflictQA metrics.
"""
import argparse
import json
from pathlib import Path

def analyze(payload):
    failures = payload["failures"]
    out = []
    for row in failures:
        if row["failure_category"] != "missed-conflict":
            continue
        old = set(row.get("positive_triples", []))
        new = set(row.get("conflicting_triples", []))
        added = sorted(new - old)
        removed = sorted(old - new)
        out.append({"id": row["id"], "new_triples": added,
                    "removed_triples": removed, "has_novel_claim": bool(added)})
    return {
        "scope": "already-exposed missed-conflict examples, novelty only; not validation of true contradiction",
        "cases": len(out),
        "cases_with_novel_claims": sum(x["has_novel_claim"] for x in out),
        "cases_without_novel_claims": sum(not x["has_novel_claim"] for x in out),
        "anomalies": out,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("portfolio_projects/renteria-evidenceweave/artifacts/conflictqa-external-eval.json"))
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = analyze(json.loads(a.input.read_text()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Previously missed rows: {result['cases']}; with added claims: {result['cases_with_novel_claims']}")
    print("Novel claims are not contradictions; unchanged 0.4000 historical recall.")

if __name__ == "__main__":
    main()
