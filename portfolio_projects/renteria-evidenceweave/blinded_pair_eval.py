"""Blinded-label, reproducible EvidenceWeave benchmark runner.

The case file must NOT contain gold labels; labels are supplied separately after
the rules are frozen. Matching hashes prove input identity, not independence.
No evaluation is inherently independent just because this script runs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from evidenceweave.graph import ClaimGraph
from evidenceweave.models import Claim
from evidenceweave.semantic_challenger import semantic_candidates


def _read(path: Path):
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def evaluate_cases(case_doc: dict, label_doc: dict, config: dict) -> dict:
    cases = case_doc.get("cases")
    labels = label_doc.get("labels")
    if not isinstance(cases, list) or not isinstance(labels, list) or len(cases) < 2:
        raise ValueError("At least two cases and matching labels are required")
    if not isinstance(config.get("functional_predicates"), list) or not config["functional_predicates"]:
        raise ValueError("Explicit functional predicate schema is required")
    if not isinstance(config.get("inverse_predicates", {}), dict):
        raise TypeError("Inverse mappings must be a dictionary")
    ids = [c.get("id") for c in cases]
    label_ids = [l.get("id") for l in labels]
    if any(not isinstance(i, str) or not i for i in ids + label_ids):
        raise ValueError("Every case and label must have a nonempty ID")
    if len(ids) != len(set(ids)) or len(label_ids) != len(set(label_ids)) or set(ids) != set(label_ids):
        raise ValueError("Case/label ID mismatch or duplication")
    if any("label" in c or "expected_conflict" in c or "gold" in c for c in cases):
        raise ValueError("Gold labels must not be bundled with test cases")
    by_label = {}
    for label in labels:
        if type(label.get("is_conflict")) is not bool:
            raise ValueError("Labels must be explicit booleans, not strings or model scores")
        by_label[label["id"]] = label["is_conflict"]
    if len(set(by_label.values())) != 2:
        raise ValueError("Both positive and negative examples are required")
    records = []
    for case in cases:
        source = case.get("claims")
        if not isinstance(source, list) or not source:
            raise ValueError("Each case needs at least one claim")
        claims = []
        for index, item in enumerate(source):
            if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k].strip()
                                                  for k in ("subject", "predicate", "value")):
                raise ValueError("Claims require nonempty subject, predicate and value strings")
            claims.append(Claim(f"{case['id']}:{index}", item["subject"], item["predicate"], item["value"]))
        graph = ClaimGraph()
        for claim in claims:
            graph.add(claim)
        baseline = bool(graph.conflicts())
        challenger = bool(semantic_candidates(
            claims, functional_predicates=config["functional_predicates"],
            inverse_predicates=config.get("inverse_predicates", {})))
        records.append({"id": case["id"], "gold_conflict": by_label[case["id"]],
                        "exact_key": baseline, "semantic_challenger": challenger})
    def matrix(name):
        tp = sum(x[name] and x["gold_conflict"] for x in records)
        fp = sum(x[name] and not x["gold_conflict"] for x in records)
        fn = sum(not x[name] and x["gold_conflict"] for x in records)
        tn = sum(not x[name] and not x["gold_conflict"] for x in records)
        return {"tp": tp, "fp": fp, "tn": tn, "fn": fn,
                "recall": tp / (tp + fn) if tp + fn else None,
                "false_positive_rate": fp / (fp + tn) if fp + tn else None,
                "precision": tp / (tp + fp) if tp + fp else None}
    return {"scope": "paired evaluation on supplied case labels, independence NOT verified",
            "label_provenance_status": "NOT_INDEPENDENTLY_VERIFIED",
            "count": len(records), "exact_key": matrix("exact_key"),
            "semantic_challenger": matrix("semantic_challenger"), "cases": records}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cases", type=Path, required=True)
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    case_doc, case_hash = _read(a.cases)
    label_doc, label_hash = _read(a.labels)
    config, config_hash = _read(a.config)
    report = evaluate_cases(case_doc, label_doc, config)
    report["sha256"] = {"cases": case_hash, "labels": label_hash, "config": config_hash}
    report["label_provenance_status"] = "NOT_INDEPENDENTLY_VERIFIED"
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Paired benchmark: {report['count']} supplied cases; independence not verified")
    print(f"Exact: {report['exact_key']}\nChallenger: {report['semantic_challenger']}")


if __name__ == "__main__":
    main()
