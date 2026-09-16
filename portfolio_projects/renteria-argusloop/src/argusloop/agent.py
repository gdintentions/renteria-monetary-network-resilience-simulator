from __future__ import annotations

import os
from time import perf_counter

from google import genai

from .actions import execute
from .audit import AuditLog
from .brain import decide_action
from .config import Settings
from .models import StepRecord
from .policy import authorize
from .screen import capture_screen


def run(task: str, settings: Settings | None = None) -> list[StepRecord]:
    cfg = settings or Settings()
    cfg.validate()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required")
    client = genai.Client(api_key=api_key)
    audit = AuditLog(cfg.audit_dir)
    records: list[StepRecord] = []
    history: list[str] = []

    for step in range(1, cfg.max_steps + 1):
        observation = capture_screen(cfg.screenshot_width)
        started = perf_counter()
        action = decide_action(client, cfg.model, task, observation.image, history)
        latency_ms = (perf_counter() - started) * 1000
        decision = authorize(action, cfg.max_risk, cfg.mode)
        status = "blocked"
        message = decision.reason
        if action.action == "done":
            status, message = "complete", "model reports visible completion"
        elif decision.allowed:
            try:
                message = execute(action, observation.logical_size, cfg.wait_seconds)
                status = "executed"
            except (RuntimeError, OSError, ValueError) as exc:
                status, message = "failed", f"{type(exc).__name__}: {exc}"
        record = StepRecord(
            step=step,
            action=action,
            status=status,
            observation_hash=observation.sha256,
            latency_ms=latency_ms,
            message=message,
        )
        audit.append(record)
        records.append(record)
        history.append(f"step {step}: {action.action} -> {status}: {message}")
        if status in {"complete", "blocked", "failed"}:
            break
    return records
