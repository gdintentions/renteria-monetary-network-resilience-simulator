# Portfolio upgrade program — evidence-first release gates
**Opened:** 2026-11-15 (Pacific)  
**State:** Proposed execution plan, not completed validation or a quality-rating upgrade.  
**Scope:** 13 inventoried systems plus the JEV Support Desk; two RAG recruiter demo variants are separately verified presentation surfaces. Do not equate system count with repository count.

## Objective and non-negotiable rules

Bring each project to a consistent **recruiter-credible engineering standard**, comparable in evidence discipline to Governed RAG, rather than assigning an unearned numerical score. Keep all existing baselines, raw failures, historical artifacts, and experimental branches unchanged. Changes must be additive on isolated branches with review and reproducibility. A passing synthetic test is not an independent judgment; a browser miniature is not proof of backend parity; an assisted walkthrough is not an unassisted participant study.

No blanket production, security certification, independently verified quality, enterprise adoption, or forecasting claim. A project's declared status must reflect observed evidence and the actual deployment scope.

## Cross-project evidence gates

For every system, publish a short, source-revision-bound **release evidence packet**:

1. **Ownership:** architecture diagram; a human-readable account of decisions and trade-offs; a personally executed change or bug fix with before/after tests and AI-assistance disclosure. Owner participation not yet observed; do not manufacture it.
2. **Repeatability:** exact commands, dependency versions, commit SHA, runtime environment, input fixture hashes, test counts, CI URLs, failures and known limitations.
3. **Failure behavior:** separate pass/fail/abstain/degrade cases, denied unauthorized actions, replay/restore where stateful, and documented regressions.
4. **Domain validity:** a frozen, genuinely unseen holdout with explicitly identified labeling authority, baseline, uncertainty/error analysis and a declared metric. Keep previously inspected sets as regression datasets, not blind holdouts.
5. **Observed workflow:** task script with an actual participant, assistance status, interruptions, success/failure and timings only if measured. Do not substitute scripted UI checks or AI-operated sessions.
6. **Selected environment:** documented host and trust boundary, data permissions, secret handling, dependency/supply-chain checks, capacity, recovery, logging/retention and responsible operator. Scope this to a local prototype where appropriate.
7. **Acceptance:** named authorized domain/organizational reviewer, pre-agreed thresholds, signed/dated accept or reject result, and unresolved risks. If unavailable, report OPEN, not PASS.
8. **Recruiter surface:** concise README, 2–4 minute reproducible demo on synthetic data, explicit distinction between hosted browser miniatures and real service, evidence links, accessible captions/screens, and no sensitive inputs.

Each packet must have a machine-readable gate manifest with states `passed`, `failed`, `blocked`, `not_run`, or `not_applicable`, plus evidence pointer and timestamp. Do **not** claim a release upgrade until mandatory engineering evidence passes; independent and organizational gates stay visibly open if blocked. Scores are editorial, not measured quality metrics.

## System-specific upgrade backlog (proposed success criteria, not achieved results)

| System | Baseline / key gap | Next executable change and proof | Independent gate |
|---|---|---|---|
| Monetary Network Resilience Simulator | Four historical proxy windows; only 2/4 beat persistence; model share is not a forecasted reserve statistic | Freeze observable/proxy mappings; walk-forward on additional windows, compare persistence/naive baselines, sensitivity and identifiability sweeps; release full seeds and failures | Qualified economics/quantitative reviewer judges claims and model suitability |
| Polyglot Relay | Fixed demo dictionary and illustrative risk/quality/latency | Integrate a permitted provider on synthetic multilingual prompts with opt-in/no-storage config, timestamped latency/errors, unsupported pairs, injection and accessibility tests | Independent bilingual judgments, measured review outcomes, real-browser accessibility |
| Context Atlas | Lexical/wikilink connections; no semantic truth | Import/update/delete/restore and broken-link regression suite on a consented or synthetic corpus; measure precision of suggested edges against frozen labels | Independent graph/link relevance reviewer and observed browser tasks |
| ArgusLoop | Scripted GUI outcomes, policy gating and metadata-only audit; no live vision planner validation | Disposable sandbox task set: allowed/denied actions, injection and false-blocks, interruption, resumed state, screenshot redaction; log step-level success and assistance | Supervised real GUI operator evaluation and independent safety review |
| EvidenceWeave | ConflictQA 172 TP / 4 FP / 258 FN; 0.4000 recall on structured triples | Failure taxonomy by relation/normalization/multihop; introduce one limited challenger behind a flag; run paired benchmark with exact IDs, regression check on 4 false positives; do not tune on holdout | Fresh independently labeled conflict/provenance cases and analyst resolution time |
| TraceLens | Trace replay and judge labels not independently adjudicated | Replay frozen retrieval failures; measure stage diagnosis accuracy on hidden labels, false alarms and intervention effect; verify trace redaction | Independent retrieval-evaluation annotator and operator session |
| ContinuityRouter | Synthetic failover, no real provider SLOs | Fault-inject deadlines, retry storms and recovery within permitted test environment; measure dropped/duplicated requests, p95/p99 and fallback cost with pinned configs | Authorized operator agrees on routing, capacity and incident policy |
| SourceGate | Allowlists, expiry/conflict abstention, recent missing-claim fix | Freeze citation/coverage fixtures; run missing claims, stale sources, conflicting authority and injected text; report false accepts/rejects and replay actual Python core versus browser view | Independently labeled coverage/conflict and source authority |
| QRCN | Mainline Phase 1 toy HMAC; later journal/PQC/Paxos in separate experimental PRs | Keep branches isolated; adversarial crash/replay/partition tests, cross-process restoration and explicit downgrade/rollback proof; do not conflate Paxos toy with financial consensus | Distributed-systems/security reviewer; no real money or quantum-network claims |
| JEV Support Desk | Offline developer-authored 33/35 routing after tuning; provider adapters unmeasured | Freeze new tickets before code change; add paraphrase failures R29/R30, mixed intent, policy-version conflict, guard error and safe-hold regressions; measure route/handoff/unsafe-release and hold precision separately | Independent ticket/policy labels and observed support-agent workflows |
| Local Model Workbench | Mock inference tests; no real installed-model results | Run two permitted local Ollama models with environment hardware, seeds/config, error/latency/cost proxy and labeled task outcomes; document unavailable paths | Outside evaluator of result quality and usability |
| Notes Evidence RAG | Lexical retrieval/citation ID gating; no actual claim entailment proof | Evaluate no-answer, unsupported cited claims, changed document hashes, prompt injection and local generation separately; report citation precision and false release rate | Independent source-support adjudication on new notes/questions |
| Personal Assistant Ledger | Local persistent draft approval, no external sends | Multi-day/timezone/restart/cancel/deduplicate exercise, post-restore immutable receipt checks, privacy/retention and unauthorized delivery attempt negative tests | Human usability session and acceptance of draft-only contract |
| Governed RAG (reference) | Most mature reference, but independent real-policy labels/host acceptance OPEN | Preserve before/after + NFCorpus; complete fresh blinded policy review, owner walkthrough and selected host drill | Independent policy-owner acceptance still required |
| RAG recruiter demo v1 / v2 | Presentation variants, not separate independently validated systems | Verify frozen synthetic examples, browser accessibility, public-source disclosure and parity limits; don't claim equivalence with private service | Recruiter walk-through with comprehension feedback, not production sign-off |

## Execution order and release strategy

**Wave 1 — High-recruiter-value companion systems:** SourceGate, TraceLens, JEV, EvidenceWeave. These directly complement Governed RAG; prioritize actual tests/fixes over new demo polish.  
**Wave 2 — User-facing applications:** Polyglot Relay, Context Atlas, Notes Evidence RAG, Local Model Workbench, Assistant Ledger, ArgusLoop.  
**Wave 3 — Research and infrastructure:** Monetary Simulator, ContinuityRouter, QRCN, where independent domain and distributed-systems review are especially important.

For each wave: (a) preserve baseline with SHA and reports; (b) write a measurable hypothesis and failure taxonomy; (c) implement a bounded change on a separate branch; (d) run tests and retain raw output; (e) compare with untouched baseline; (f) peer review code and domain claims; (g) request an actual observed human/operator evaluation; (h) merge only after scoped evidence and review; (i) update public project cards with verified claims only.

## First implementation tickets

- **EW-01:** Extract the published 258 ConflictQA misses and 4 false positives into a stable, deterministic error-taxonomy report with counts and example IDs by relation; no algorithm change and no re-labeling the existing results. Acceptance: a reproducible command, exact benchmark-source revision, consistency checks that reproduce 172/4/426/258 and a separately documented data-splitting policy.
- **SG-01:** Verify the recent missing-claim correction using an added untouched test slice, compare no-claim / partial-claim / expired-policy and high-priority conflict cases, and preserve pre-fix behavior in a dated report.
- **JEV-01:** Freeze a fresh ticket holdout *before* adjusting routing rules; include the two known paraphrase misses as regression tests only, plus unseen explicit human, mixed-intent and draft guard cases.
- **TL-01:** Build a labeled trace-review rubric that distinguishes retrieval misses, wrong evidence selection, unsupported answer, contradictory inputs and judge disagreement; keep original trace records immutable.

## Reporting convention

A project may reach the proposed high-quality standard in reproducible engineering while still lacking real production applicability. Use these separate labels in every public summary: **implemented**, **automated development verified**, **independently domain validated**, **observed workflow validated**, **selected-host validated**, **organizationally accepted**. The last four remain OPEN unless an actual accountable reviewer, user, host or organization contributes the required proof.

This plan is an additive specification. It does not represent executed tests, independent decisions, a completed work sprint, or a universal 8.5/10 rating.
