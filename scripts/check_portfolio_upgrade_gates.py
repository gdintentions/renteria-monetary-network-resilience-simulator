#!/usr/bin/env python3
"""Fail closed if portfolio wave states claim unsupported approvals."""
import json
import sys
from pathlib import Path

ALLOWED = {"passed", "failed", "blocked", "not_run", "not_applicable"}
EXPECTED = {1: {"SourceGate", "TraceLens", "JEV Support Desk", "EvidenceWeave"},
            2: {"Polyglot Relay", "Context Atlas", "Notes Evidence RAG", "Local Model Workbench",
                "Personal Assistant Ledger", "ArgusLoop"},
            3: {"Monetary Simulator", "ContinuityRouter", "QRCN"}}
REQUIRED = {"automated_regression", "domain_validation", "owner_walkthrough",
            "observed_workflow", "selected_host", "organizational_acceptance"}

def validate(data):
    projects = data.get("projects", [])
    if len(projects) != 13:
        raise ValueError(f"Expected 13 non-RAG system entries, got {len(projects)}")
    observed = {1: set(), 2: set(), 3: set()}
    for item in projects:
        wave = item["wave"]
        name = item["name"]
        if wave not in EXPECTED or name in observed[wave]:
            raise ValueError(f"Invalid or duplicate system: {name}")
        observed[wave].add(name)
        gates = item["gates"]
        if set(gates) != REQUIRED or any(status not in ALLOWED for status in gates.values()):
            raise ValueError(f"Missing or invalid gates for {name}")
        for gate, status in gates.items():
            if status == "passed" and not item.get("evidence", {}).get(gate):
                raise ValueError(f"Missing evidence for {name}/{gate}")
    if observed != EXPECTED:
        raise ValueError("Wave inventory drift")
    return True

if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/portfolio_upgrade_gates_2026-11-15.json")
    validate(json.loads(path.read_text()))
    print("Verified: 13 wave entries, complete gate states, evidence for all passes.")
