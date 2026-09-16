from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("ARGUSLOOP_MODEL", "gemini-2.5-flash")
    mode: str = os.getenv("ARGUSLOOP_MODE", "dry-run")
    max_steps: int = int(os.getenv("ARGUSLOOP_MAX_STEPS", "12"))
    max_risk: str = os.getenv("ARGUSLOOP_MAX_RISK", "medium")
    screenshot_width: int = int(os.getenv("ARGUSLOOP_SCREENSHOT_WIDTH", "1280"))
    wait_seconds: float = float(os.getenv("ARGUSLOOP_WAIT_SECONDS", "1.0"))
    audit_dir: Path = Path(os.getenv("ARGUSLOOP_AUDIT_DIR", "audit"))

    def validate(self) -> None:
        if self.mode not in {"dry-run", "live"}:
            raise ValueError("ARGUSLOOP_MODE must be dry-run or live")
        if not 1 <= self.max_steps <= 50:
            raise ValueError("ARGUSLOOP_MAX_STEPS must be in [1, 50]")
        if self.max_risk not in {"low", "medium", "high", "critical"}:
            raise ValueError("invalid ARGUSLOOP_MAX_RISK")
