from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .models import StepRecord


class AuditLog:
    def __init__(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        self.path = directory / f"run-{stamp}.jsonl"

    def append(self, record: StepRecord) -> None:
        event = {"timestamp": datetime.now(UTC).isoformat(), **record.model_dump(mode="json")}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

