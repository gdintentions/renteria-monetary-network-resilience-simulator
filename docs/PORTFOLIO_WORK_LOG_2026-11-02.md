# Portfolio work log — November 2, 2026

**Scope:** governed retrieval/evidence reliability and monetary stress-model planning. **Status:** research/development evidence, not independent certification or deployed production change.

## Governed RAG: completed on experimental branch (private source)
The project reviewed twelve third-party stress-test screenshots, checked the actual policy engine and preserved historical benchmark provenance. Two separate development branches/PRs across the portfolio isolate proposed changes from the existing `main` implementations.

In Governed RAG, the current heuristic detects narrow same-section frequency disagreements. An optional separate lightweight candidate detects additional exact negation inversions without changing live answer routing. This was tested against 20 AI-authored exposed development sentence pairs (10 conflicts, 10 non-conflicts).

A CPU-only, pinned MiniLM NLI cross-encoder was then evaluated against the same 20 pairs using both directional classifications. **Measured exposed-set results:**

| Method | True positive | False negative | False positive | True negative | Recall | Precision | Median per-pair CPU time |
|---|---:|---:|---:|---:|---:|---:|---:|
| Existing frequency heuristic | 2 | 8 | 0 | 10 | 20% | 100% | 0.030 ms |
| Lightweight experimental rules | 6 | 4 | 0 | 10 | 60% | 100% | 0.038 ms |
| Pinned MiniLM NLI | 10 | 0 | 4 | 6 | 100% | 71.4% | 102.849 ms |

These **are not population performance estimates**: the 20 cases were written by the developer, exposed during implementation, and have not been independently reviewed. `P10` has a likely mistaken non-conflict label, and `P04` has ambiguous scope. The NLI experiment had approximately 82.1 million model parameters, roughly 760 MiB maximum process RSS, and 4.655 seconds model-loading time on the runner. Timing is a CPU-only microbenchmark, not an end-to-end service SLA.

**Decision:** Do not integrate MiniLM into the governed service or claim production readiness. Test a hybrid/scope-aware selective NLI review mechanism with new blinded labels, authority and document injection cases, and end-to-end latency measures. Preserve failures.

**Internal evidence:** private Governed RAG experimental PR [#17](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/pull/17), executed [GitHub Actions NLI run](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/41567799161), per-case archived JSON at `artifacts/adversarial_conflict/2026-11-02/nli-results.json`, along with separate [development report](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/blob/experiment/adversarial-conflict-validation-2026-11/docs/evaluations/NLI_EXECUTED_COMPARISON_2026-11-02.md). The raw results and implementation are in a **private repository** and are not a public demo.

## Monetary Network Resilience Simulator: documented next experiment
An isolated draft [PR #14](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/14) holds the `docs/evaluations/LIQUIDITY_POLICY_STRESS_PLAN_2026-11-02.md` proposal. The core simulator already has seeded stochastic noise and Monte Carlo results; no redesign claim should erase that existing work. Proposed work separates **relative settlement-network shares** from absolute payment liquidity/capacity, models shocks and conditional policy feedback, and requires reproducible numerical invariants and preserved historical proxy failures. No new monetary code or simulation metrics were produced for this plan.

## Immutable evidence and status gates
- Original `main` implementations and historical reports remained unchanged during this day's experiments. Only additive work in a Governed RAG experiment branch and a monetary proposal branch was submitted.
- External screenshot claims, including an alleged 40% contradiction-miss rate, were **not confirmed** by a defined benchmark. NFCorpus 108/323 top-10 misses measures **retrieval**, not conflict-detection.
- The independent-review and production-readiness gates remain **OPEN** for both projects; CI passing is not an independent safety certification.
- Future releases must document before/after failure matrices, provenance, held-out reviewer judgments, threat-model findings, latency, reproducibility and operational readiness separately.

## Next project actions
1. Audit and adjudicate the 20 labels, then freeze an independently authored blind holdout.
2. Create an authority-aware, scope-sensitive NLI second-opinion experiment (do not silently replace heuristics).
3. Measure whole-pipeline retrieval, abstention, conflicting evidence, prompt injection, review release and p95 latency.
4. Keep baseline, successor and negative results separately versioned; seek independent adjudication before merging experimental governance changes.
5. Progress monetary liquidity/policy stress work only in its separate branch after its variable semantics and unit tests are defined.

*Published here as a recruiter-safe portfolio development summary; private RAG source and raw policy-engine records have not been made public.*
