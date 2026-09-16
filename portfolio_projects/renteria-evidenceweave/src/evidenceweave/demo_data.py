from __future__ import annotations

from .models import Claim, EvidenceBlock, Modality, Source
from .pipeline import EvidenceWeave


def build_demo() -> EvidenceWeave:
    weave = EvidenceWeave()
    weave.add_source(Source("report", "Q2 Retrieval Benchmark", 0.92, 0.95, "benchmark.pdf"))
    weave.add_source(Source("memo", "Engineering Review Memo", 0.78, 0.90, "review.pdf"))
    blocks = [
        EvidenceBlock(
            "b1", "report", Modality.text,
            "BGE-M3 was selected as the production embedding model after the Q2 evaluation.", 1, 0.98,
        ),
        EvidenceBlock(
            "b2", "report", Modality.chart,
            "The accuracy chart shows BGE-M3 at 0.91, E5-large at 0.89, and MiniLM at 0.86.", 1, 0.93,
        ),
        EvidenceBlock(
            "b3", "report", Modality.table,
            "The comparison table lists BGE-M3: 1024 dimensions, 0.91 accuracy, 42 ms latency.", 1, 0.99,
        ),
        EvidenceBlock(
            "b4", "memo", Modality.text,
            "The engineering memo reports BGE-M3 accuracy as 0.88 after a revised holdout test.", 2, 0.90,
        ),
        EvidenceBlock(
            "b5", "memo", Modality.equation,
            "Utility equals accuracy minus 0.001 times latency; BGE-M3 utility is 0.838.", 2, 0.88,
        ),
    ]
    for block in blocks:
        weave.add_block(block)
    claims = [
        Claim("c1", "BGE-M3", "was selected as", "production model", ["b1"]),
        Claim("c2", "BGE-M3", "has accuracy", "0.91", ["b2", "b3"]),
        Claim("c3", "BGE-M3", "has latency", "42 ms", ["b3"]),
        Claim("c4", "BGE-M3", "has accuracy", "0.88", ["b4"]),
        Claim("c5", "BGE-M3", "has utility", "0.838", ["b5"]),
    ]
    for claim in claims:
        weave.add_claim(claim)
    return weave

