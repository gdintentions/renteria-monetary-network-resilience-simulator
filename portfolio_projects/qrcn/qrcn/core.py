"""Quantum-Resilient Clearing Network (QRCN) research miniature.

Uses per-hop HMAC with deterministic key epochs for demonstration only.
No QKD, PQC, encryption, authenticated networking, distributed consensus,
external money movement, or production security claims.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import json
import secrets
from typing import Literal


@dataclass(frozen=True)
class Transaction:
    tx_id: str
    payer: str
    payee: str
    cents: int

    def encode(self) -> bytes:
        return json.dumps(
            {"tx_id": self.tx_id, "payer": self.payer,
             "payee": self.payee, "cents": self.cents},
            sort_keys=True, separators=(",", ":")
        ).encode("utf-8")


@dataclass(frozen=True)
class Result:
    status: str
    tx_id: str
    route: tuple[str, ...]
    events: tuple[str, ...]
    accepted_cents: int = 0


class ClearingNetwork:
    """Single-process simulation, NOT an actual decentralized clearing house."""

    def __init__(self, nodes=("alpha", "beta", "gamma"), key: bytes | None = None):
        if len(set(nodes)) != len(nodes) or len(nodes) < 2:
            raise ValueError("At least two uniquely named nodes are required")
        self.nodes = tuple(nodes)
        self.key = key if key is not None else secrets.token_bytes(32)
        if len(self.key) < 16:
            raise ValueError("Key must have at least 16 bytes")
        self.committed: dict[str, bytes] = {}
        self.outage: set[str] = set()
        self.key_epoch = 0
        self.accepted_count = 0
        self.accepted_cents = 0

    def rotate_keys(self) -> int:
        self.key_epoch += 1
        return self.key_epoch

    def _hop_key(self, node: str) -> bytes:
        msg = ("qrcn-demo/hmac/" + node + "/" + str(self.key_epoch)).encode()
        return hmac.new(self.key, msg, hashlib.sha256).digest()

    def _tag(self, node: str, payload: bytes) -> bytes:
        return hmac.new(self._hop_key(node), payload, hashlib.sha256).digest()

    def clear(self, tx: Transaction, *, attack: Literal[
        "none", "tamper", "stale_tag", "drop_after_commit"
    ] = "none") -> Result:
        if not isinstance(tx.cents, int) or isinstance(tx.cents, bool) or tx.cents <= 0:
            raise ValueError("Transaction must contain a positive integer number of cents")
        if not all((tx.tx_id, tx.payer, tx.payee)) or tx.payer == tx.payee:
            raise ValueError("Transaction identifiers and distinct parties are required")
        if attack not in ("none", "tamper", "stale_tag", "drop_after_commit"):
            raise ValueError("Unrecognized simulated fault")

        encoded = tx.encode()
        if tx.tx_id in self.committed:
            # A duplicate identifier is rejected whether identical or conflicting.
            return Result("duplicate_rejected", tx.tx_id, (), ("replay_detected",))

        route: list[str] = []
        events: list[str] = []
        for node in self.nodes:
            if node in self.outage:
                events.append("node_unavailable:" + node)
                continue
            route.append(node)
            # Authentication requires a trusted channel/key agreement in a real
            # network. This sample uses an in-process shared secret.
            signed = self._tag(node, encoded)
            delivered = encoded
            if attack == "tamper" and not any(e == "tamper_detected" for e in events):
                delivered = encoded + b"!"
            if attack == "stale_tag" and not any(e == "stale_authentication" for e in events):
                prior = hmac.new(
                    hmac.new(self.key, ("qrcn-demo/hmac/" + node + "/" + str(self.key_epoch - 1)).encode(),
                             hashlib.sha256).digest(),
                    encoded, hashlib.sha256
                ).digest()
                signed = prior
            if not hmac.compare_digest(self._tag(node, delivered), signed):
                label = "tamper_detected" if attack == "tamper" else "stale_authentication"
                events.append(label)
                return Result("rejected_integrity", tx.tx_id, tuple(route), tuple(events))
            events.append("authenticated:" + node)
            break

        if not route:
            return Result("unavailable", tx.tx_id, (), tuple(events + ["no_healthy_node"]))

        self.committed[tx.tx_id] = hashlib.sha256(encoded).digest()
        self.accepted_count += 1
        self.accepted_cents += tx.cents
        events.append("committed_once")
        if attack == "drop_after_commit":
            # A lost acknowledgment must never cause a second settlement.
            events.append("acknowledgment_lost")
        return Result("accepted", tx.tx_id, tuple(route), tuple(events), tx.cents)

    def snapshot(self) -> dict[str, int]:
        return {"accepted_count": self.accepted_count,
                "accepted_cents": self.accepted_cents, "unique_ids": len(self.committed),
                "key_epoch": self.key_epoch}
