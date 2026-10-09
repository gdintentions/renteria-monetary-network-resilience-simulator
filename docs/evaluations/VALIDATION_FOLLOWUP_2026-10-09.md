# Validation follow-up — October 9, 2026 UTC

## Governed RAG

[PR 11](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/pull/11) merged after Python 3.11/3.12, dependency-audit, container and paired-regression checks passed. Exact-ranking indexed cosine measured approximately 45x lower local median retrieval time (35.3 ms to 0.78 ms). BM25 remains evaluation-only: MRR 0.4830 to 0.5131, misses 108 to 99, 56 per-query improvements and 34 regressions. Independent real-policy human validation remains pending; a hash/quote-checking reviewer-packet CLI is now available. IBM deployment remains underway.

## Monetary Simulator: expanded retrospective comparison

Four consecutive historical proxy windows (2013–2016, 2016–2019, 2019–2022, 2022–2025), twelve currency targets, fixed original structural growth, no shocks or volatility. A persistence comparator predicts the starting normalized share without seeing the endpoint.

| Window | Model MAE (pp) | Persistence MAE (pp) | Correct directions |
|---|---:|---:|---:|
| 2013–2016 | 1.2064 | 1.1431 | 1/3 |
| 2016–2019 | 0.2002 | 0.3486 | 3/3 |
| 2019–2022 | 1.3035 | 1.4085 | 2/3 |
| 2022–2025 | 1.0013 | 0.9719 | 1/3 |

Overall model MAE is **0.9279 pp**, versus **0.9680 pp** for persistence. The model wins in **2/4** intervals and gets **7/12** directions right. No parameters were fitted to these endpoints. These retrospective comparisons use parameters devised after historical outcomes were known; they are not authentic out-of-time forecasts. Adjacent intervals and currencies are dependent. Do not infer a reliable predictive edge from this small difference.

Sources: [BIS September 2019, Table 2](https://www.bis.org/publications/201909-commentary-otc-derivatives.pdf) and [BIS September 2025 release](https://www.bis.org/publications/202509-commentary-otc-derivatives). Frozen release vintages and input SHA-256 are recorded. These are FX turnover shares normalized to a three-currency subset, not reserves or settlement shares. CNY remains an explicitly imperfect BRICS proxy. The original one-window report is preserved.

Identifiability check: adding the same +0.1 to every growth parameter leaves normalized predicted shares unchanged. Absolute growth cannot be identified from those shares; resilience cannot be identified from the no-shock replay. This is a concrete model limitation, not a solved calibration problem.

## EvidenceWeave: reproduced failures and rejected ineffective change

Pinned ConflictQA to commit `be7f9c5b7b0c9b6907aeaeeda8bb3c83e6b2e448` and verified SHA-256 for both source files. Reproduced 430 paired items: 172 true positives, 4 false positives, 258 misses. Unicode NFKC/whitespace normalization changes **zero cases**; it is not promoted as an improvement.

The missed pairs have no differing values for an identical normalized subject/predicate in the supplied triples. Some benchmark contradictions depend on additional textual evidence or multi-hop relationships, which the current graph does not reason over. All misses remain in the denominator. The next implementation needs a separately evaluated text/multi-hop layer; inventing opposing triples from the gold answer would leak labels and is not permitted.

## ArgusLoop: actual GUI integration

New disposable Xvfb/Tk/PyAutoGUI benchmark exercises the actual adapter with three type-and-save tasks and two blocked-action checks. It captures a synthetic screenshot and observed GUI state. At document creation, CI execution is pending; consult the Validation follow-up workflow for the actual result. Scripted coordinates isolate execution reliability; this is not a vision-planner benchmark or success on unfamiliar applications.

## Remaining projects and real-use blockers

| Project | Evidence retained | Missing real-use input or environment |
|---|---|---|
| Context Atlas | Existing merged browser/import/recovery regressions | Permitted representative notes and independent link judgments |
| Notes Evidence RAG | Existing citation/state/browser checks | Actual model runtime and independent claim-support labels |
| Local Model Workbench | Existing adapter/browser tests | An installed permitted model and capable inference host; Ollama is not available in this execution environment |
| Personal Assistant Ledger | Existing synthetic three-day/DST-offset recovery drill | Actual elapsed multi-day deployment on the intended host; synthetic clock advancement does not satisfy it |
| Polyglot Relay | Existing static prototype and tests | Chosen translation/speech provider, authorized credentials and bilingual reviewers |
| Legacy RAG demos | Synthetic instructional and comparison examples | Keep scope labels; do not inherit service or external-domain accuracy claims |

These are explicit blockers, not completed gates. No provider credentials, reviewer identities, policy judgments, elapsed days, or IBM deployment results were assumed. Production-ready flags remain false. No new background monitoring or recurring task was created.

## Reproduce

```sh
python -m demo.historical_windows
python scripts/evidence_coverage_audit.py --cache /tmp/conflictqa-frozen
python -m pytest -q tests
```

The disposable GUI must run in the isolated CI/Xvfb job, never on an unattended personal desktop.
