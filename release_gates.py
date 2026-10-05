"""Manifest checks for honest portfolio release claims, not production certification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {"domain_validation", "security_boundary", "recovery", "deployment", "operator_acceptance"}


def validate(manifest: dict) -> list[dict]:
    if manifest.get("schema_version") != "1.0" or not isinstance(manifest.get("projects"), list):
        raise ValueError("Expected schema_version 1.0 and project list")
    if not manifest["projects"]:
        raise ValueError("Project list must not be empty")
    ids, reports = set(), []
    for project in manifest["projects"]:
        project_id = project.get("id")
        if not isinstance(project_id, str) or not project_id or project_id in ids:
            raise ValueError("Project IDs must be distinct nonempty strings")
        ids.add(project_id)
        gates = project.get("gates", [])
        if not isinstance(gates, list):
            raise ValueError("Gates must be a list")
        gate_ids = [g.get("id") for g in gates]
        if len(gate_ids) != len(set(gate_ids)) or set(gate_ids) != REQUIRED:
            raise ValueError("Every project requires each release gate exactly once")
        pending = []
        for gate in gates:
            if gate.get("status") not in {"pending", "passed"}:
                raise ValueError("Gate status must be pending or passed")
            if not isinstance(gate.get("requirement"), str) or not gate["requirement"].strip():
                raise ValueError("Each gate needs a concrete requirement")
            evidence = gate.get("evidence")
            if not isinstance(evidence, list) or any(not isinstance(e, str) or not e.strip() for e in evidence):
                raise ValueError("Evidence must be a list of nonempty references")
            if gate["status"] == "passed" and not evidence:
                raise ValueError("A passed gate requires evidence references")
            if gate["status"] == "pending":
                pending.append(gate["id"])
        eligible = not pending
        if type(project.get("production_ready")) is not bool or project["production_ready"] != eligible:
            raise ValueError("Readiness claim must match gate state")
        reports.append({"id": project_id, "production_ready": eligible, "pending": pending})
    return reports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path(__file__).parent / "docs" / "RELEASE_GATES.json")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    reports = validate(json.loads(args.manifest.read_text()))
    print(json.dumps(reports, indent=2))
    if args.require_ready and any(not row["production_ready"] for row in reports):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
