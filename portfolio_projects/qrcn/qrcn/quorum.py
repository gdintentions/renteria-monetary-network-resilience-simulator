"""QRCN Phase 3: conservative quorum admission experiment.

This is a deterministic *simulation* of majority availability and a
coordinator epoch, backed by the Phase 2 single-file SQLite journal.
It is NOT Raft/Paxos, replicated state-machine consensus, quorum certificates,
network authentication, or a multi-host fault-tolerant payment system.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

from .core import Result, Transaction
from .durable import DurableClearingNetwork, SQLiteJournal


@dataclass(frozen=True)
class QuorumDecision:
    accepted_voters: tuple[str, ...]
    total_voters: int
    threshold: int
    admitted: bool
    epoch: int


class QuorumClearing:
    """Toy coordinator that fails closed when a majority is unavailable.

    All writer instances point at ONE trusted SQLiteJournal. Membership
    and reachability are supplied by the simulator, not established via
    real network protocol or cryptographic validator attestations.
    """

    def __init__(self, journal: SQLiteJournal, members: Iterable[str] =
                 ("alpha", "beta", "gamma"), *, key: bytes,
                 epoch: int | None = None):
        names = tuple(members)
        if len(names) < 3 or len(names) % 2 == 0 or len(names) != len(set(names)):
            raise ValueError("Require odd-sized unique membership of at least three")
        if any(not x or not isinstance(x, str) for x in names):
            raise ValueError("Member names must be non-empty strings")
        self.journal = journal
        self.members = names
        self.key = key
        self.epoch = journal.current_epoch() if epoch is None else epoch

    @property
    def majority(self) -> int:
        return len(self.members) // 2 + 1

    def vote(self, reachable: Iterable[str]) -> QuorumDecision:
        authorized = set(reachable)
        if not authorized <= set(self.members):
            raise ValueError("Unknown member in reachability set")
        voters = tuple(x for x in self.members if x in authorized)
        current = self.journal.current_epoch()
        # Check epoch before considering quorum. The DB commit repeats the
        # fence inside an atomic transaction to close local TOCTOU windows.
        return QuorumDecision(voters, len(self.members), self.majority,
                              len(voters) >= self.majority and
                              self.epoch == current, current)

    def clear(self, tx: Transaction, *, reachable: Iterable[str],
              attack: str = "none") -> Result:
        decision = self.vote(reachable)
        if not decision.admitted:
            status = ("stale_writer_rejected" if decision.epoch != self.epoch
                      else "quorum_unavailable")
            return Result(status, tx.tx_id, (), (
                "votes:" + str(len(decision.accepted_voters)) +
                "/" + str(decision.total_voters),
                "majority_required:" + str(decision.threshold),
                "journal_not_written"))
        # Selection is deterministic and tests run on one process / file.
        backend = DurableClearingNetwork(
            self.journal, nodes=self.members, key=self.key,
            writer_epoch=self.epoch)
        backend.outage.update(set(self.members) - set(decision.accepted_voters))
        result = backend.clear(tx, attack=attack)
        return Result(result.status, result.tx_id, result.route,
                      ("quorum_admitted:" +
                       str(len(decision.accepted_voters)) +
                       "/" + str(decision.total_voters),) +
                      result.events, result.accepted_cents)
