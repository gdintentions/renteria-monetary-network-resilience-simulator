"""Phase 2 QRCN: local SQLite durability and explicit partition audit.

Single-host, trusted-process educational design. No distributed consensus or
quantum security. Phase 1 in-memory implementation remains unchanged.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import hmac
import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .core import ClearingNetwork, Result, Transaction


@dataclass(frozen=True)
class CommitRecord:
    tx_id: str
    payload_hash: str
    cents: int
    epoch: int


class SQLiteJournal:
    """A transactional single-file journal; all coordinated writers share one DB."""

    def __init__(self, file: str | Path):
        self.file = str(file)
        if self.file == ":memory:":
            raise ValueError("Use a file-backed journal to test durability")
        Path(self.file).parent.mkdir(parents=True, exist_ok=True)
        with self._open() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS committed (
                tx_id TEXT PRIMARY KEY NOT NULL,
                payload_hash TEXT NOT NULL,
                cents INTEGER NOT NULL CHECK(cents > 0),
                epoch INTEGER NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS coordinator (
                singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                epoch INTEGER NOT NULL CHECK(epoch >= 0))""")
            db.execute("INSERT OR IGNORE INTO coordinator(singleton, epoch) VALUES (1, 0)")

    def _open(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.file, timeout=15, isolation_level=None)
        db.execute("PRAGMA busy_timeout=15000")
        db.execute("PRAGMA synchronous=FULL")
        db.execute("PRAGMA journal_mode=WAL")
        return db

    def current_epoch(self) -> int:
        with self._open() as db:
            row = db.execute("SELECT epoch FROM coordinator WHERE singleton=1").fetchone()
            return int(row[0])

    def advance_epoch(self) -> int:
        with self._open() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute("UPDATE coordinator SET epoch=epoch+1 WHERE singleton=1")
                epoch = self._read_epoch(db)
                db.commit()
                return epoch
            except BaseException:
                db.rollback()
                raise

    @staticmethod
    def _read_epoch(db: sqlite3.Connection) -> int:
        row = db.execute("SELECT epoch FROM coordinator WHERE singleton=1").fetchone()
        if row is None:
            raise RuntimeError("Missing coordinator epoch")
        return int(row[0])

    def commit_once(self, tx: Transaction, *, expected_epoch: int) -> str:
        """Return accepted, duplicate_rejected, or stale_writer_rejected.

        Unique ID and fencing epoch checked together under BEGIN IMMEDIATE.
        This is not a consensus protocol across disconnected databases.
        """
        payload_hash = hashlib.sha256(tx.encode()).hexdigest()
        with self._open() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                row = db.execute(
                    "SELECT payload_hash FROM committed WHERE tx_id=?", (tx.tx_id,)
                ).fetchone()
                if row is not None:
                    outcome = "duplicate_rejected"
                elif self._read_epoch(db) != expected_epoch:
                    outcome = "stale_writer_rejected"
                else:
                    db.execute(
                        "INSERT INTO committed(tx_id,payload_hash,cents,epoch) VALUES (?,?,?,?)",
                        (tx.tx_id, payload_hash, tx.cents, expected_epoch)
                    )
                    outcome = "accepted"
                db.commit()
                return outcome
            except BaseException:
                db.rollback()
                raise

    def records(self) -> tuple[CommitRecord, ...]:
        with self._open() as db:
            rows = db.execute(
                "SELECT tx_id,payload_hash,cents,epoch FROM committed ORDER BY tx_id"
            ).fetchall()
        return tuple(CommitRecord(*r) for r in rows)

    def snapshot(self) -> dict[str, int]:
        with self._open() as db:
            count, cents = db.execute(
                "SELECT COUNT(*),COALESCE(SUM(cents),0) FROM committed"
            ).fetchone()
            epoch = self._read_epoch(db)
        return {"accepted_count": count, "accepted_cents": cents,
                "unique_ids": count, "coordinator_epoch": epoch}


class DurableClearingNetwork(ClearingNetwork):
    """Authenticates a simulated message then journals it atomically in SQLite."""

    def __init__(self, journal: SQLiteJournal, *, nodes=("alpha", "beta", "gamma"),
                 key: bytes | None = None, writer_epoch: int | None = None):
        super().__init__(nodes=nodes, key=key)
        self.journal = journal
        self.writer_epoch = journal.current_epoch() if writer_epoch is None else writer_epoch

    def clear(self, tx: Transaction, *, attack: str = "none") -> Result:
        if not isinstance(tx.cents, int) or isinstance(tx.cents, bool) or tx.cents <= 0:
            raise ValueError("Transaction amount must be positive integer cents")
        if not all((tx.tx_id, tx.payer, tx.payee)) or tx.payer == tx.payee:
            raise ValueError("Transaction identifiers and distinct parties required")
        if attack not in ("none", "tamper", "stale_tag", "crash_before_commit",
                          "drop_after_commit"):
            raise ValueError("Unrecognized simulation fault")

        payload = tx.encode()
        route = []
        events = []
        for node in self.nodes:
            if node in self.outage:
                events.append("node_unavailable:" + node)
                continue
            route.append(node)
            signed = self._tag(node, payload)
            delivered = payload
            if attack == "tamper":
                delivered = payload + b"!"
            if attack == "stale_tag":
                old_epoch = self.key_epoch - 1
                derived = hmac.new(
                    self.key, ("qrcn-demo/hmac/" + node + "/" + str(old_epoch)).encode(),
                    hashlib.sha256
                ).digest()
                signed = hmac.new(derived, payload, hashlib.sha256).digest()
            if not hmac.compare_digest(self._tag(node, delivered), signed):
                events.append("tamper_detected" if attack == "tamper"
                              else "stale_authentication")
                return Result("rejected_integrity", tx.tx_id, tuple(route), tuple(events))
            events.append("authenticated:" + node)
            break
        if not route:
            return Result("unavailable", tx.tx_id, (), tuple(events + ["no_healthy_node"]))

        if attack == "crash_before_commit":
            return Result("interrupted_before_commit", tx.tx_id, tuple(route),
                          tuple(events + ["no_journal_write"]))

        outcome = self.journal.commit_once(tx, expected_epoch=self.writer_epoch)
        if outcome != "accepted":
            return Result(outcome, tx.tx_id, tuple(route), tuple(events + [outcome]))
        events.append("durably_committed")
        if attack == "drop_after_commit":
            events.append("acknowledgment_lost")
        return Result("accepted", tx.tx_id, tuple(route), tuple(events), tx.cents)


def audit_partitions(journals: Iterable[SQLiteJournal]) -> dict:
    """Read-only comparison. Never silently merges partition journals."""
    observed: dict[str, list[dict]] = {}
    for index, journal in enumerate(journals):
        for record in journal.records():
            observed.setdefault(record.tx_id, []).append({
                "partition": index, **asdict(record)
            })
    duplicate_ids = sorted(k for k, v in observed.items() if len(v) > 1)
    conflicting_ids = sorted(
        k for k in duplicate_ids
        if len({r["payload_hash"] for r in observed[k]}) > 1
    )
    return {"unique_ids_observed": len(observed),
            "duplicate_ids": duplicate_ids, "conflicting_ids": conflicting_ids,
            "requires_adjudication": bool(duplicate_ids),
            "evidence": {k: observed[k] for k in duplicate_ids},
            "automatic_merge_performed": False}
