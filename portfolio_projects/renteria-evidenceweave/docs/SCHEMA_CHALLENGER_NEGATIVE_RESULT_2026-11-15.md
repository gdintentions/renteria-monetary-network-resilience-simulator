# EvidenceWeave schema challenger — measured negative result

**Date:** November 15, 2026 Pacific  
**Scope:** Opt-in controlled experiment on an already-inspected ConflictQA failure ledger. This is not independent blind evaluation or a production model upgrade.

## Verified engineering

- Schema-bound, explicit functional-predicate and entity/predicate alias comparison implemented in `src/evidenceweave/functional_challenger.py`.
- Seven synthetic tests cover alias conflict, explicitly multi-valued attributes, case/whitespace normalization, refusal to infer aliases, cycle rejection and empty schema. The challenger is not wired into `ClaimGraph.conflicts()`, service answer release, or public recruiter demos.
- [GitHub Actions challenger replay run #43822121136](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43822121136): lint, tests, exposed failure-only replay, scope assertions and artifact upload passed. The initial import lint errors were fixed without suppressing the lint checks.

## Actual observed result

- Historical ConflictQA baseline (unchanged): 172 TP, 4 FP, 426 TN, 258 FN; precision 0.9773 and recall 0.4000.
- Challenger inspected all **258 previously missed** exposed entries: **0** new schema-bound conflict alerts on these cases.
- This is **not** a claim of no false positives or a full dataset score. The replay did not evaluate the complete controls for this challenger; full precision and recall remain **not measured**.
- The earlier novelty analysis found additions among missed entries, but an added relation is not by itself a contradictory fact. Calling all additions conflicts would exploit the benchmark's paired construction and overstate semantic quality.

## Release decision

**REJECT as a recall improvement.** Retain as isolated investigative code, not a replacement or extension of default detection. Do not merge PR #25 into stable `main` on the grounds of improved recall.

## Next genuinely substantive experiment

Before any further tuning, choose a separate, permission-cleared dataset containing independently adjudicated semantic conflict and nonconflict pairs, including multi-valued facts and indirect/multi-hop contradictions. Freeze the evaluation split. Keep historical ConflictQA labels for regression-only investigation. Compare baseline exact-key, opt-in challenger and a genuinely different graph/entailment method on identical unseen cases. Publish paired TP/FP/TN/FN, uncertainty, per-case outcomes, rubric, model/version/cost and abstention, with no false-positive budget inferred after inspecting the test output. Independent human domain review and selected organizational acceptance remain OPEN.

JEV historical router integration remains blocked until its archived runnable v0.1.1 code and preserved fixtures are available; the existing standalone routing miniature cannot substitute for that measurement.
