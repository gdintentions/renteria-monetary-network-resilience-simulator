#!/usr/bin/env python3
"""No-token developer-fixture audit for SourceGate and TraceLens.

This is a repeatable offline protocol, NOT external independent validation.
Case and expected-label files are separate. The program never calls models
or search providers and does not transmit data to a third party.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "portfolio_projects/renteria-sourcegate"))
sys.path.insert(0, str(ROOT / "portfolio_projects/renteria-tracelens"))

from sourcegate import Evidence, run as sourcegate_run  # noqa: E402
from tracelens import diagnose  # noqa: E402


def run_cases(cases: dict, labels: dict) -> dict:
    entries = cases.get("cases")
    judgments = labels.get("labels")
    if not isinstance(entries, list) or not isinstance(judgments, list) or len(entries) < 2:
        raise ValueError("At least two evaluation cases and labels are needed")
    ids = [c.get("id") for c in entries]
    expected_ids = [l.get("id") for l in judgments]
    if (len(ids) != len(set(ids)) or len(expected_ids) != len(set(expected_ids))
            or set(ids) != set(expected_ids)
            or any(not isinstance(i, str) or not i for i in ids + expected_ids)):
        raise ValueError("Case IDs must be unique, nonempty, and identical to label IDs")
    if any("expected" in c or "gold_status" in c for c in entries):
        raise ValueError("Expected outcomes must be in the separate labels file")
    truth = {}
    for row in judgments:
        if not isinstance(row.get("status"), str) or not row["status"]:
            raise ValueError("Invalid expected status label")
        truth[row["id"]] = row["status"]
    observed = []
    for entry in entries:
        project = entry.get("project")
        data = entry.get("input")
        if project == "tracelens":
            result = diagnose(data)
            status = result["status"]
            detail = result.get("basis", result.get("reason", ""))
        elif project == "sourcegate":
            if not isinstance(data, dict):
                raise ValueError("SourceGate input must be an object")
            records = [Evidence(**doc) for doc in data.get("evidence", [])]
            result = sourcegate_run(
                "Fictional policy question for offline review",
                data.get("required_claims", []),
                lambda _: records,
                lambda _, docs: {doc.id: "relevant" for doc in docs},
                lambda _: [],
                allowed_hosts={"policy.example"},
                today=date(2026, 11, 16),
                web_allowed=False,
            )
            status = result["status"]
            detail = result.get("reason", result.get("basis", ""))
        else:
            raise ValueError(f"Unknown validation project: {project!r}")
        # SourceGate assessment labels can distinguish fail-closed reason.
        observed_status = f"{status}/{detail}" if status == "NEEDS_REVIEW" else status
        observed.append({
            "id": entry["id"],
            "project": project,
            "expected": truth[entry["id"]],
            "actual": observed_status,
            "match": observed_status == truth[entry["id"]],
        })
    breakdown = {}
    for project in ("sourcegate", "tracelens"):
        subset = [x for x in observed if x["project"] == project]
        if not subset:
            raise ValueError(f"Missing required project: {project}")
        breakdown[project] = {"n": len(subset), "matches": sum(x["match"] for x in subset)}
    return {
        "scope": "developer-authored offline fixtures only; not independent factual or diagnosis validation",
        "independent_review": False,
        "model_inference": False,
        "provider_tokens_used": 0,
        "results": observed,
        "summary": breakdown,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=Path, required=True)
    ap.add_argument("--labels", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    opts = ap.parse_args()
    raw_cases = opts.cases.read_bytes()
    raw_labels = opts.labels.read_bytes()
    report = run_cases(json.loads(raw_cases), json.loads(raw_labels))
    report["inputs_sha256"] = {
        "cases": hashlib.sha256(raw_cases).hexdigest(),
        "labels": hashlib.sha256(raw_labels).hexdigest(),
    }
    opts.out.parent.mkdir(parents=True, exist_ok=True)
    opts.out.write_text(json.dumps(report, indent=2) + "\n")
    print("Offline developer fixtures only:", report["summary"])
    if any(not row["match"] for row in report["results"]):
        raise SystemExit("Developer fixture regression detected")


if __name__ == "__main__":
    main()
