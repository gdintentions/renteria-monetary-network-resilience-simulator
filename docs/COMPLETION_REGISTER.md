# Portfolio completion register

Release baseline: Governed RAG's synthetic recruiter workflow, not its uncompleted organizational production validation. Scope applies to all connected repositories and the nested ArgusLoop/EvidenceWeave projects. Shared requirements are working behavior, input/failure controls, reproducible checks, inspectable evidence, a safe demonstration, recovery appropriate to the runtime, and explicit limitations. Tests of authored examples are never independent quality studies.

## Implemented and verified

- Governed RAG: supervised service hardening, labeled evaluation scaffolding, held-out NFCorpus report, and a deployed synthetic reviewer miniature. Its nine contract checks and mobile browser checks passed before release.
- Context Atlas, Notes Evidence RAG, Workbench and Ledger: local request/state/backup hardening plus merged real Chromium workflows. Synthetic browser integration passed in each repository; artifacts contain a screenshot and JSON checks. No model output was simulated or mislabeled as real inference.
- Monetary Simulator, ArgusLoop and EvidenceWeave: their existing external/controlled evaluation reports and published failures remain intact.

## Remaining work by product

| Component | Next implementation or validation | Input still required for real-use completion |
|---|---|---|
| Governed RAG | Independent answer/no-answer/conflict/injection holdout; host recovery/capacity study | Permitted real policy corpus, independent reviewers and actual operator thresholds |
| Context Atlas | Independently judged note links and import/update/delete quality | Permitted representative notes and independently assigned relevance judgments |
| Notes Evidence RAG | Claim support, conflict and adversarial source study | Independent answers/citation labels; installed local model for generated-mode evaluation |
| Local Model Workbench | Repeated model task/latency/availability study | Capable host, permitted installed model versions, model provenance and fixed task labels |
| Personal Assistant Ledger | Actual multi-day uptime drill after the passed synthetic clock/recovery study | Intended operator/host; delivery adapters remain separate from draft-only scope |
| Polyglot Relay | Provider-independent adapter and measured quality evaluation | Chosen permitted translation/speech provider, credentials and independent language reviewers |
| Monetary Simulator | More historical intervals/observables and identifiability analysis | Frozen historical data/provenance and defined observable-to-model mappings |
| ArgusLoop | Actual disposable GUI tasks with completion/false-block categories | Isolated desktop with synthetic accounts; fake-adapter pass is not GUI success |
| EvidenceWeave | Distinguish exclusive versus multi-valued relations; separately evaluate text extraction | Frozen development/test split and independently labeled free-text contradictions |
| Legacy RAG demo | Maintain as a frozen instructional baseline; test links and boundaries | No automatic promotion to the new service or real-policy quality claim |
| RAG model lab v2 | Retrieval comparison on a frozen external holdout | Separate development labels and held-out judgments; five authored cases remain a miniature |

This register is a work queue, not a completion certificate. None of these pending studies is replaced by a README edit or a green synthetic test. Production status remains governed by RELEASE_GATES.json. A public demonstration can be complete for its stated synthetic scope while real deployment remains unfinished.

## How a release closes

The PR states a bounded use case and acceptance checks. Run the relevant unit/integration/domain checks on the exact revision; retain failures and evidence artifacts. Merge after required checks pass. Verify deployment when the change affects a hosted demo. Update the snapshot with the measured scope and link to the tested revision. Keep remaining provider, data, quality and operator gates explicit.

Follow-up releases: Atlas and Notes RAG PR 3 close stale-query/late-response bugs under real browser regression. Ledger PR 3 passes 18 unit tests and browser integration, including a synthetic three-day recovery/DST-offset/concurrency drill. Actual wall-clock uptime, named-zone recurrence, delivery adapters and production acceptance remain separate open gates.

## October 9, 2026 UTC follow-up

[Measured retrieval improvement, expanded historical comparisons, conflict-coverage audit and disposable GUI integration](evaluations/VALIDATION_FOLLOWUP_2026-10-09.md). Original evaluation results remain preserved; new regression evidence does not close independent production gates.

## Reliability projects — v0.2.0

TraceLens, ContinuityRouter and SourceGate now have an actual-Python browser lab,
project-specific end-to-end acceptance checks, preserved original failures and
explicit completion gates. [Release evidence](RELIABILITY_RELEASE.md) records the
bounded synthetic portfolio scope and the separate real-use limits.
