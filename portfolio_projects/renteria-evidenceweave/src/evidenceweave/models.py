from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Modality(str, Enum):
    text = "text"
    table = "table"
    chart = "chart"
    equation = "equation"
    image = "image"


@dataclass(frozen=True)
class Source:
    source_id: str
    title: str
    authority: float = 0.7
    freshness: float = 0.8
    uri: str = ""

    def __post_init__(self) -> None:
        if not 0 <= self.authority <= 1 or not 0 <= self.freshness <= 1:
            raise ValueError("authority and freshness must be in [0, 1]")


@dataclass(frozen=True)
class EvidenceBlock:
    block_id: str
    source_id: str
    modality: Modality
    content: str
    page: int | None = None
    confidence: float = 0.8

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("evidence content cannot be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be in [0, 1]")


@dataclass
class Claim:
    claim_id: str
    subject: str
    predicate: str
    value: str
    evidence_ids: list[str] = field(default_factory=list)

    @property
    def key(self) -> tuple[str, str]:
        return self.subject.casefold(), self.predicate.casefold()


@dataclass(frozen=True)
class ScoreBreakdown:
    semantic: float
    graph_support: float
    cross_modal: float
    source_reliability: float
    freshness: float
    contradiction: float
    ambiguity: float
    integrity: float


@dataclass(frozen=True)
class Answer:
    query: str
    summary: str
    claims: tuple[Claim, ...]
    evidence: tuple[EvidenceBlock, ...]
    score: ScoreBreakdown
    conflicts: tuple[str, ...]

