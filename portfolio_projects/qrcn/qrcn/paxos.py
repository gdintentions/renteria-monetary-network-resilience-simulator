"""Educational crash-recoverable single-decree Paxos per transaction identifier.

Three acceptors own independent SQLite files. Prepare/promise and accept state
is committed before reply. NOT a replicated total-order log, full Paxos stack,
Byzantine consensus, quantum network, or payment clearing system.
"""
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Callable


def canonical_value(tx_id: str, cents: int, payer: str="payer", payee: str="payee") -> str:
    if not tx_id or not payer or not payee or payer == payee:
        raise ValueError("Invalid parties or transaction ID")
    if type(cents) is not int or cents <= 0:
        raise ValueError("Positive integer cents required")
    return json.dumps({"tx_id": tx_id, "cents": cents, "payer": payer, "payee": payee},
                      sort_keys=True, separators=(",", ":"))


class Acceptor:
    """Independent durable single-decree acceptor, one SQLite DB per node."""
    def __init__(self, node_id: str, path: str | Path):
        if not node_id: raise ValueError("node_id required")
        self.node_id = node_id
        self.path = str(path)
        if self.path == ":memory:": raise ValueError("File-backed state required")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._open() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS slots (
                slot TEXT PRIMARY KEY, promised INTEGER NOT NULL DEFAULT -1,
                accepted_ballot INTEGER, accepted_value TEXT)""")

    @contextmanager
    def _open(self):
        conn = sqlite3.connect(self.path, timeout=15)
        try:
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("PRAGMA busy_timeout=15000")
            with conn:
                yield conn
        finally:
            conn.close()

    def prepare(self, slot: str, ballot: int) -> dict:
        if not slot or type(ballot) is not int or ballot < 0:
            raise ValueError("Bad ballot or slot")
        with self._open() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO slots(slot) VALUES (?)", (slot,))
            p, a, v = db.execute("SELECT promised, accepted_ballot, accepted_value "
                                 "FROM slots WHERE slot=?", (slot,)).fetchone()
            ok = ballot >= p
            if ok:
                db.execute("UPDATE slots SET promised=? WHERE slot=?", (ballot, slot))
            return {"node": self.node_id, "ok": ok, "promised": max(p, ballot) if ok else p,
                    "accepted_ballot": a, "accepted_value": v}

    def accept(self, slot: str, ballot: int, value: str) -> dict:
        if not slot or type(ballot) is not int or ballot < 0:
            raise ValueError("Bad ballot or slot")
        data = json.loads(value)
        if data.get("tx_id") != slot or canonical_value(data["tx_id"], data["cents"],
                                      data["payer"], data["payee"]) != value:
            raise ValueError("Noncanonical value or mismatched slot")
        with self._open() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO slots(slot) VALUES (?)", (slot,))
            p, a, v = db.execute("SELECT promised, accepted_ballot, accepted_value "
                                 "FROM slots WHERE slot=?", (slot,)).fetchone()
            # A single ballot cannot accept two distinct values.
            ok = ballot >= p and not (a == ballot and v != value)
            if ok:
                db.execute("UPDATE slots SET promised=?, accepted_ballot=?, accepted_value=? "
                           "WHERE slot=?", (ballot, ballot, value, slot))
            return {"node": self.node_id, "ok": ok, "promised": max(p, ballot) if ok else p}

    def inspect(self, slot: str) -> dict | None:
        with self._open() as db:
            row = db.execute("SELECT promised, accepted_ballot, accepted_value FROM slots "
                             "WHERE slot=?", (slot,)).fetchone()
        return None if row is None else {"promised": row[0], "accepted_ballot": row[1],
                                         "accepted_value": row[2]}


@dataclass(frozen=True)
class Decision:
    status: str
    requested_value: str
    chosen_value: str | None
    ballot: int
    prepare_acks: tuple[str, ...]
    accept_acks: tuple[str, ...]
    adopted_prior: bool


class Proposer:
    """Two-phase single-decree Paxos using externally unique caller ballots.

    No automatic retries or leader election. Preemption fails closed.
    """
    def __init__(self, members: tuple[str, ...], rpc: Callable[[str,str,str,int,str|None],dict]):
        if len(members) < 3 or len(members) % 2 != 1 or len(set(members)) != len(members):
            raise ValueError("Odd distinct membership >=3 required")
        self.members, self.rpc = members, rpc

    def propose(self, slot: str, ballot: int, value: str) -> Decision:
        if json.loads(value)["tx_id"] != slot:
            raise ValueError("Requested slot and value mismatch")
        majority = len(self.members)//2 + 1
        promises = []
        for node in self.members:
            try:
                reply = self.rpc(node, "prepare", slot, ballot, None)
                if reply["ok"]: promises.append(reply)
            except (ConnectionError, TimeoutError, OSError):
                continue
        ack1 = tuple(r["node"] for r in promises)
        if len(promises) < majority:
            return Decision("no_prepare_quorum",value,None,ballot,ack1,(),False)
        prior = [r for r in promises if r["accepted_ballot"] is not None]
        adopted = max(prior, key=lambda r:r["accepted_ballot"])["accepted_value"] if prior else value
        ack2=[]
        for node in self.members:
            try:
                reply = self.rpc(node,"accept",slot,ballot,adopted)
                if reply["ok"]: ack2.append(reply["node"])
            except (ConnectionError, TimeoutError, OSError):
                continue
        if len(ack2) < majority:
            return Decision("no_accept_quorum",value,None,ballot,ack1,tuple(ack2),adopted!=value)
        return Decision("adopted_prior" if adopted!=value else "chosen",
                        value,adopted,ballot,ack1,tuple(ack2),adopted!=value)


class PartitionNetwork:
    """Deterministic transport with independent acceptor files and drop rules."""
    def __init__(self, nodes: dict[str, Acceptor]):
        self.nodes=nodes
        self.reachable=set(nodes)
        self.drop_accept=set()
        self.trace=[]
    def call(self, node: str, op: str, slot: str, ballot: int, value: str|None) -> dict:
        if node not in self.reachable or (op=="accept" and node in self.drop_accept):
            self.trace.append({"node":node,"op":op,"outcome":"dropped"})
            raise ConnectionError("simulated partition")
        response=(self.nodes[node].prepare(slot,ballot) if op=="prepare"
                  else self.nodes[node].accept(slot,ballot,value))
        self.trace.append({"node":node,"op":op,"outcome":"ok" if response["ok"] else "rejected"})
        return response
