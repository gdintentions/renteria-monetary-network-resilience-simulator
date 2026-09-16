from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Risk(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Action(BaseModel):
    """Exactly one proposed desktop action; coordinates use a 0..1000 grid."""

    reasoning: str = Field(min_length=1, max_length=500)
    action: Literal["click", "type", "scroll", "press_key", "wait", "done"]
    x: int | None = Field(default=None, ge=0, le=1000)
    y: int | None = Field(default=None, ge=0, le=1000)
    text: str | None = Field(default=None, max_length=2000)
    direction: Literal["up", "down"] | None = None
    key: str | None = Field(default=None, max_length=30)
    risk: Risk = Risk.low
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    expected_effect: str = Field(default="", max_length=300)

    @model_validator(mode="after")
    def validate_payload(self) -> Action:
        required = {
            "click": self.x is not None and self.y is not None,
            "type": self.text is not None,
            "scroll": self.direction is not None,
            "press_key": self.key is not None,
            "wait": True,
            "done": True,
        }
        if not required[self.action]:
            raise ValueError(f"missing fields for action={self.action}")
        return self


class StepRecord(BaseModel):
    step: int
    action: Action
    status: Literal["proposed", "executed", "blocked", "failed", "complete"]
    observation_hash: str
    latency_ms: float
    message: str = ""
