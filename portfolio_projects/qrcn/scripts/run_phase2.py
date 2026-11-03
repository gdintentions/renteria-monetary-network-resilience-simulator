"""QRCN Phase 2 reproducible durability and partition experiment.

Run from portfolio_projects/qrcn:
  python -m scripts.run_phase2
No network, real transfers or secrets. Temporary SQLite files only.
"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from qrcn.core import Transaction
from qrcn.durable import DurableClearingNetwork, SQLiteJournal, audit_partitions


def execute() -> dict:
    key = b"phase-two-demo-shared-secret-0000000"
    with TemporaryDirectory() as folder:
        root = Path(folder)
        main = SQLiteJournal(root / "primary.sqlite")
        first = DurableClearingNetwork(main, key=key)
        transaction = Transaction("demo-001", "alice", "bob", 12500)

        committed = first.clear(transaction, attack="drop_after_commit")
        recovered = DurableClearingNetwork(SQLiteJournal(root / "primary.sqlite"), key=key)
        retry = recovered.clear(transaction)

        interrupted = recovered.clear(
            Transaction("demo-002", "alice", "bob", 1500), attack="crash_before_commit"
        )
        after_restart = DurableClearingNetwork(main, key=key).clear(
            Transaction("demo-002", "alice", "bob", 1500)
        )
        stale_writer = DurableClearingNetwork(main, key=key)
        epoch = main.advance_epoch()
        fenced = stale_writer.clear(Transaction("demo-003", "alice", "bob", 300))

        isolated = SQLiteJournal(root / "split-brain.sqlite")
        competing = DurableClearingNetwork(isolated, key=key).clear(
            Transaction("demo-001", "alice", "bob", 99900)
        )
        audit = audit_partitions([main, isolated])
        return {
            "metadata": {
                "phase": 2, "demo_only": True,
                "persistence": "single-host SQLite files",
                "distributed_consensus": False,
            },
            "ack_lost_then_restart": [committed.status, retry.status],
            "interrupted_then_restart": [interrupted.status, after_restart.status],
            "fencing": {"epoch": epoch, "stale_writer": fenced.status},
            "partition": {"isolated_commit": competing.status,
                          "conflicting_ids": audit["conflicting_ids"],
                          "requires_adjudication": audit["requires_adjudication"],
                          "automatic_merge_performed": audit["automatic_merge_performed"]},
            "shared_journal": main.snapshot(),
        }


if __name__ == "__main__":
    print(json.dumps(execute(), indent=2, sort_keys=True))
