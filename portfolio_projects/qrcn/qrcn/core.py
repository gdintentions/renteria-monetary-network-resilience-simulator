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
        if not 2 <= len(nodes) <= 12 or any(not isinstance(n,str) or not 1 <= len(n) <= 200 for n in nodes) or len(set(nodes)) != len(nodes):
            raise ValueError("At least two uniquely named nodes are required")
        self.nodes = tuple(nodes)
        self.key = key if key is not None else secrets.token_bytes(32)
        if not isinstance(self.key,bytes) or not 16 <= len(self.key) <= 64:
            raise ValueError("Key must have at least 16 bytes")
        self.committed: dict[str, bytes] = {}
        self.records: list[dict] = []
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

        if any(not isinstance(v,str) or not 1 <= len(v) <= 200 for v in (tx.tx_id,tx.payer,tx.payee)):raise ValueError("Identifiers must contain 1..200 characters")
        encoded = tx.encode()
        if tx.tx_id in self.committed:
            # A duplicate identifier is rejected whether identical or conflicting.
            return Result("duplicate_rejected", tx.tx_id, (), ("replay_detected",))

        if len(self.committed)>=1000:raise ValueError("Toy ledger limit: 1000 accepted records")
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
        self.records.append({"tx_id":tx.tx_id,"payer":tx.payer,"payee":tx.payee,"cents":tx.cents})
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

    def checkpoint(self) -> bytes:
        """Authenticated toy journal; key must be retained separately. No key export."""
        payload={'version':1,'nodes':self.nodes,'records':self.records,
                 'key_epoch':self.key_epoch,'outage':sorted(self.outage)}
        raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
        return json.dumps({'payload':payload,'mac':hmac.new(self.key,raw,hashlib.sha256).hexdigest()},sort_keys=True).encode()

    @classmethod
    def restore(cls,raw:bytes,*,key:bytes):
        if len(raw)>1_000_000:raise ValueError("Checkpoint size limit")
        data=json.loads(raw)
        if set(data)!={'payload','mac'}:raise ValueError("Checkpoint schema")
        payload=data['payload'];encoded=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
        if not hmac.compare_digest(hmac.new(key,encoded,hashlib.sha256).hexdigest(),data['mac']):raise ValueError("Checkpoint authentication failed")
        if set(payload)!={'version','nodes','records','key_epoch','outage'} or payload['version']!=1:raise ValueError("Checkpoint version/schema")
        if type(payload['key_epoch']) is not int or not 0 <= payload['key_epoch'] <= 1_000_000:raise ValueError("Key epoch")
        if not isinstance(payload['records'],list) or len(payload['records'])>1000:raise ValueError("Journal bound")
        network=cls(tuple(payload['nodes']),key=key)
        for record in payload['records']:
            if network.clear(Transaction(**record)).status!='accepted':raise ValueError("Duplicate recovered transaction")
        if not set(payload['outage']) <= set(network.nodes):raise ValueError("Unknown recovered node")
        network.key_epoch=payload['key_epoch'];network.outage=set(payload['outage'])
        return network
