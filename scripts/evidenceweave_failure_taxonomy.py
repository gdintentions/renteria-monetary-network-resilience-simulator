#!/usr/bin/env python3
"""Reproduce and stratify the published EvidenceWeave ConflictQA failure ledger.

This is analysis of an ALREADY INSPECTED regression benchmark, not a new blind
evaluation or a change to the conflict detector. Standard-library only.
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

EXPECTED = {"paired_items": 430, "true_positive": 172, "false_positive": 4,
            "true_negative": 426, "false_negative": 258, "failure_count": 262}


def predicate(triple):
    # Plain triples can include commas in subjects. Extract the predicate
    # using the first comma; report malformed rows rather than guessing.
    if not isinstance(triple, str) or not triple.startswith("(") or ", " not in triple:
        return "<malformed>"
    rest = triple.split(", ", 1)[1]
    return rest.split(", ", 1)[0] if ", " in rest else "<malformed>"


def build_report(doc):
    for key, expected in EXPECTED.items():
        if doc.get(key) != expected:
            raise ValueError(f"Published baseline mismatch: {key}={doc.get(key)!r}, expected {expected}")
    failures = doc.get("failures")
    if not isinstance(failures, list) or len(failures) != EXPECTED["failure_count"]:
        raise ValueError("Failure list is missing or inconsistent")
    ids = [row.get("id") for row in failures]
    if len(ids) != len(set(ids)) or not all(isinstance(i, str) and i for i in ids):
        raise ValueError("Duplicate or missing case IDs")

    kinds = collections.Counter(row.get("failure_category") for row in failures)
    if kinds != {"missed-conflict": 258, "false-positive-conflict": 4}:
        raise ValueError(f"Unexpected failure categories: {dict(kinds)}")
    categories = collections.defaultdict(lambda: {"missed-conflict": 0, "false-positive-conflict": 0, "example_ids": []})
    for row in failures:
        kind = row["failure_category"]
        triples = row.get("conflicting_triples") or row.get("positive_triples") or []
        preds = sorted({predicate(t) for t in triples})
        if not preds:
            preds = ["<no-triple>"]
        # Count each failure once per predicate, NOT as unique case totals.
        for pred in preds:
            entry = categories[pred]
            entry[kind] += 1
            if len(entry["example_ids"]) < 3:
                entry["example_ids"].append(row["id"])
    return {
        "scope": "already-inspected ConflictQA structured-triple failures; NOT blind or free-text validation",
        "baseline": {key: doc[key] for key in EXPECTED},
        "failure_categories": dict(sorted(kinds.items())),
        "predicate_counts_overlap": True,
        "predicates": [{"predicate": k, **v} for k, v in sorted(categories.items())],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("portfolio_projects/renteria-evidenceweave/artifacts/conflictqa-external-eval.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    doc = json.loads(raw)
    report = build_report(doc)
    report["input_sha256"] = hashlib.sha256(raw).hexdigest()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "failure_taxonomy.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    with (args.output_dir / "failure_taxonomy.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["predicate", "missed_conflict", "false_positive_conflict", "example_ids"])
        for item in report["predicates"]:
            writer.writerow([item["predicate"], item["missed-conflict"], item["false-positive-conflict"], ";".join(item["example_ids"])])
    print(f"Baseline confirmed: 258 misses, 4 false positives; {len(report['predicates'])} predicate categories")
    print("Predicate counts overlap; do not add them to infer a unique failure count.")


if __name__ == "__main__":
    main()
