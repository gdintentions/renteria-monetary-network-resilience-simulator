from __future__ import annotations

from collections import Counter

from .graph import ClaimGraph
from .models import Answer, Claim, EvidenceBlock, Modality, Source
from .scoring import cosine_text, evidence_integrity


class EvidenceWeave:
    def __init__(self) -> None:
        self.sources: dict[str, Source] = {}
        self.blocks: dict[str, EvidenceBlock] = {}
        self.graph = ClaimGraph()

    def add_source(self, source: Source) -> None:
        self.sources[source.source_id] = source

    def add_block(self, block: EvidenceBlock) -> None:
        if block.source_id not in self.sources:
            raise KeyError(f"unknown source: {block.source_id}")
        self.blocks[block.block_id] = block

    def add_claim(self, claim: Claim) -> None:
        missing = [item for item in claim.evidence_ids if item not in self.blocks]
        if missing:
            raise KeyError(f"unknown evidence blocks: {missing}")
        self.graph.add(claim)

    def query(self, query: str, limit: int = 4) -> Answer:
        ranked = sorted(
            self.blocks.values(),
            key=lambda block: cosine_text(query, block.content),
            reverse=True,
        )[:limit]
        ranked_ids = {block.block_id for block in ranked}
        claims = [
            claim
            for claim in self.graph.claims.values()
            if ranked_ids.intersection(claim.evidence_ids)
        ]
        conflicts = self.graph.conflicts(claims)
        modalities = {block.modality for block in ranked}
        source_ids = {block.source_id for block in ranked}

        semantic = sum(cosine_text(query, block.content) for block in ranked) / max(len(ranked), 1)
        graph_support = min(1.0, sum(len(claim.evidence_ids) for claim in claims) / 4)
        cross_modal = min(1.0, len(modalities) / 3)
        reliability = sum(self.sources[s].authority for s in source_ids) / max(len(source_ids), 1)
        freshness = sum(self.sources[s].freshness for s in source_ids) / max(len(source_ids), 1)
        contradiction = min(1.0, len(conflicts) / max(len(claims), 1))
        ambiguity = 1.0 if not claims else max(0.0, 1 - min(1.0, len(claims) / 3))
        score = evidence_integrity(
            semantic=semantic,
            graph_support=graph_support,
            cross_modal=cross_modal,
            source_reliability=reliability,
            freshness=freshness,
            contradiction=contradiction,
            ambiguity=ambiguity,
        )

        summary = self._summarize(claims, conflicts)
        return Answer(query, summary, tuple(claims), tuple(ranked), score, tuple(conflicts))

    @staticmethod
    def _summarize(claims: list[Claim], conflicts: list[str]) -> str:
        if not claims:
            return "The indexed evidence does not support a defensible answer."
        grouped: Counter[tuple[str, str, str]] = Counter(
            (claim.subject, claim.predicate, claim.value) for claim in claims
        )
        statements = [
            f"{subject} {predicate} {value}"
            for (subject, predicate, value), _count in grouped.most_common(3)
        ]
        answer = "; ".join(statements) + "."
        if conflicts:
            answer += " Conflicting evidence was detected and should be reviewed."
        return answer

    def dashboard_metrics(self) -> dict[str, int]:
        return {
            "sources": len(self.sources),
            "evidence_blocks": len(self.blocks),
            "claims": len(self.graph.claims),
            "conflicts": len(self.graph.conflicts()),
            "modalities": len({block.modality for block in self.blocks.values()}),
        }


def modality_label(modality: Modality) -> str:
    return modality.value.title()

