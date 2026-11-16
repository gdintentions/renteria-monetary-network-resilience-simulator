"""JEV routing paired assessment with separately stored labels.

No archived v0.1.1 router available: this script evaluates only the new
clean-room reconstruction on synthetic, developer-written tickets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from reconstructed_router import route_ticket

ROUTES = {"human", "clarify", "agent_review", "read_only_order_lookup"}


def evaluate(cases: dict, labels: dict) -> dict:
    entries = cases.get("tickets", [])
    judgments = labels.get("labels", [])
    if not isinstance(entries, list) or not isinstance(judgments, list) or len(entries) < 2:
        raise ValueError("Tickets and judgments are required")
    ids = [x.get("id") for x in entries]
    ids2 = [x.get("id") for x in judgments]
    if (len(set(ids)) != len(ids) or len(set(ids2)) != len(ids2)
            or set(ids) != set(ids2) or not all(isinstance(i, str) and i for i in ids + ids2)):
        raise ValueError("Mismatched, missing or duplicate case IDs")
    if any("route" in x or "label" in x or "expected" in x for x in entries):
        raise ValueError("Evaluation labels leaked into ticket records")
    expected = {}
    for x in judgments:
        if x.get("route") not in ROUTES:
            raise ValueError("Invalid expected route")
        expected[x["id"]] = x["route"]
    records = []
    for x in entries:
        if not isinstance(x.get("text"), str):
            raise ValueError("Ticket text must be a string")
        if any(type(x.get(k, False)) is not bool for k in ("order_verified", "exchange_policy_verified")):
            raise ValueError("Verification flags must be booleans")
        got = route_ticket(
            x["text"],
            order_verified=x.get("order_verified", False),
            exchange_policy_verified=x.get("exchange_policy_verified", False))
        if got.release_authorized:
            raise ValueError("Any customer delivery authorization blocks evaluation")
        records.append({"id": x["id"], "expected": expected[x["id"]],
                        "actual": got.route, "reason": got.reason,
                        "match": got.route == expected[x["id"]]})
    handoffs = [r for r in records if r["expected"] == "human"]
    non_handoffs = [r for r in records if r["expected"] != "human"]
    return {
        "scope": "DEVELOPER-authored synthetic routing reconstruction, not v0.1.1 comparison",
        "tickets": len(records),
        "correct": sum(r["match"] for r in records),
        "handoff_recall": (
            sum(r["actual"] == "human" for r in handoffs) / len(handoffs)
            if handoffs else None),
        "false_handoffs": sum(r["actual"] == "human" for r in non_handoffs),
        "raw": records,
        "original_router_available": False,
        "original_33_of_35_unchanged": True,
        "independent_review": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickets", type=Path, required=True)
    ap.add_argument("--labels", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    raw_tickets, raw_labels = args.tickets.read_bytes(), args.labels.read_bytes()
    report = evaluate(json.loads(raw_tickets), json.loads(raw_labels))
    report["sha256"] = {
        "tickets": hashlib.sha256(raw_tickets).hexdigest(),
        "labels": hashlib.sha256(raw_labels).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Reconstruction {report['correct']}/{report['tickets']} development routes; "
          "original v0.1.1 result UNCHANGED")


if __name__ == "__main__":
    main()
