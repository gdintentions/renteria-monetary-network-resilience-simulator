# Evidence Integrity mathematics

EvidenceWeave separates retrieval relevance from answer integrity. A relevant passage can still
be stale, weakly sourced, ambiguous, or contradicted by another document.

For a candidate answer, the Evidence Integrity Score is:

```text
EIS = σ(1.50S + 1.20G + 1.10X + 1.00R + 0.60F - 1.80K - 0.90A - 1.40)
σ(z) = 1 / (1 + e^-z)
```

| Symbol | Component | Interpretation |
|---|---|---|
| `S` | Semantic relevance | Query-to-evidence cosine similarity |
| `G` | Graph support | Density of provenance-backed claim links |
| `X` | Cross-modal agreement | Support from text, table, chart, equation, or image channels |
| `R` | Source reliability | Configured authority of contributing sources |
| `F` | Freshness | Time-sensitive source currency signal |
| `K` | Contradiction | Competing values for the same subject–predicate pair |
| `A` | Ambiguity | Missing or insufficiently specific claim support |

Weights are explicit product assumptions, not learned truth probabilities. They must be calibrated
against a labeled evaluation set before operational use.

Text relevance uses cosine similarity over deterministic token-frequency vectors:

```text
cos(q,d) = (q · d) / (||q||₂ ||d||₂)
```

