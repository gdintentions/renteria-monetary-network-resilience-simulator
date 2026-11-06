from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .models import StepRecord


class AuditLog:
    """Private metadata-only journal; never replays desktop actions on recovery."""

    def __init__(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = directory / f"run-{uuid4().hex}.jsonl"
        fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)

    def append(self, record: StepRecord) -> None:
        # Typed text, planner reasoning, effects, and arbitrary messages can contain
        # secrets. Retain a digest for correlation, never their raw values.
        raw = record.model_dump(mode="json")
        event = {
            "schema": 1,
            "timestamp": datetime.now(UTC).isoformat(),
            "step": record.step,
            "status": record.status,
            "action": record.action.action,
            "risk": record.action.risk.value,
            "confidence": record.action.confidence,
            "latency_ms": record.latency_ms,
            "observation_hash": hashlib.sha256(record.observation_hash.encode()).hexdigest(),
            "record_sha256": hashlib.sha256(
                json.dumps(raw, sort_keys=True, allow_nan=False).encode()
            ).hexdigest(),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
