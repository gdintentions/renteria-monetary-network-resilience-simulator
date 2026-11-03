"""Phase 5 experimental crash-durable ballot allocator for fixed Paxos membership.

Distinct configured proposer IDs must be assigned distinct indices from the
SAME fixed membership tuple. No dynamic membership, distributed ID leasing,
or protection against cloning an allocator database.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3


class DurableBallots:
    def __init__(self, proposer_id: str, members: tuple[str, ...], path: str | Path):
        if not proposer_id or len(members) < 2 or len(set(members)) != len(members):
            raise ValueError("Distinct configured proposer identities required")
        if proposer_id not in members:
            raise ValueError("Proposer must be a member of the fixed identity namespace")
        self.proposer_id = proposer_id
        self.members = members
        self.path = str(path)
        if self.path == ":memory:":
            raise ValueError("Ballot counter must be file-backed")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS allocator (id INTEGER PRIMARY KEY CHECK(id=1), proposer TEXT NOT NULL, namespace TEXT NOT NULL, round INTEGER NOT NULL)")
            existing = db.execute("SELECT proposer, namespace FROM allocator WHERE id=1").fetchone()
            namespace = "\\x1f".join(members)
            if existing is None:
                db.execute("INSERT INTO allocator (id, proposer, namespace, round) VALUES (1, ?, ?, 0)", (proposer_id, namespace))
            elif existing != (proposer_id, namespace):
                raise ValueError("Database already belongs to another identity or membership namespace")

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.execute("PRAGMA synchronous=FULL")
        db.execute("PRAGMA busy_timeout=15000")
        return db

    def next_ballot(self, greater_than: int = -1) -> int:
        if type(greater_than) is not int or greater_than < -1:
            raise ValueError("Invalid observed ballot")
        db = self._connect()
        try:
            with db:
                db.execute("BEGIN IMMEDIATE")
                current = db.execute("SELECT round FROM allocator WHERE id=1").fetchone()[0]
                index = self.members.index(self.proposer_id)
                width = len(self.members)
                next_round = max(current + 1, (greater_than - index) // width + 1, 1)
                ballot = next_round * width + index
                db.execute("UPDATE allocator SET round=? WHERE id=1", (next_round,))
            return ballot
        finally:
            db.close()
