"""Explicit private provenance checkpoints with separately retained integrity receipts."""

import hashlib
import json
import os
from dataclasses import asdict

from .models import Claim, EvidenceBlock, Modality, Source
from .pipeline import EvidenceWeave

LIMIT = 1_000_000


def save(weave, path):
    payload = {
        "version": 1,
        "sources": [asdict(x) for x in weave.sources.values()],
        "blocks": [asdict(x) for x in weave.blocks.values()],
        "claims": [asdict(x) for x in weave.graph.claims.values()],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if len(raw) > LIMIT:
        raise ValueError("Checkpoint size limit")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return hashlib.sha256(raw).hexdigest()


def restore(path, expected_sha256):
    with open(path, "rb") as handle:
        raw = handle.read(LIMIT + 1)
    if len(raw) > LIMIT or hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("Checkpoint receipt mismatch")
    payload = json.loads(raw)
    if set(payload) != {"version", "sources", "blocks", "claims"} or payload["version"] != 1:
        raise ValueError("Checkpoint version/schema")
    if any(
        not isinstance(payload[k], list) or len(payload[k]) > limit
        for k, limit in [("sources", 1000), ("blocks", 5000), ("claims", 10000)]
    ):
        raise ValueError("Checkpoint collection bounds")
    # Build a new graph completely before returning it; failures never mutate the caller.
    result = EvidenceWeave()
    for x in payload["sources"]:
        result.add_source(Source(**x))
    for x in payload["blocks"]:
        item = {**x, "modality": Modality(x["modality"])}
        result.add_block(EvidenceBlock(**item))
    for x in payload["claims"]:
        result.add_claim(Claim(**x))
    return result
