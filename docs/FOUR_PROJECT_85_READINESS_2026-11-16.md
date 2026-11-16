# Four-project 8.5 readiness gate — November 16, 2026

**Decision: advance the engineering baseline; DO NOT mark any of these four projects independently validated or production accepted.** No private keys, paid-model tokens, large local machine, or external live services are necessary for the current offline regression suite. GitHub Actions quotas/billing still apply.

## Verified changes, preserving the original evidence

| System | New bounded implementation | Verified current CI | Original boundary |
|---|---|---|---|
| EvidenceWeave | Experimental `scoped_semantic.py` adds reviewer-approved identity edges, policy-domain isolation, and validity-overlap comparison, failing closed on time-scoped identity links and noncanonical dates | [41 Python tests, lint, replay and artifacts succeeded](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43843858587) · [tests workflow](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43843858598) | 8 authored toy cases: challenger 3 TP, 0 FP, 5 TN, 0 FN vs exact-key 1 TP, 2 FP, 3 TN, 2 FN; original 430-item ConflictQA recall 0.4000 and 4 FP **unchanged**. Experiment in [draft PR #25](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/25) only |
| JEV Support Desk | Experimental `verified_preview.py` emits fixed agent-review templates only from strictly typed, approved, simulated verified facts; blocks prompt-injected fact values, unknown sources, absent ownership or unauthorized promises. No customer send | [25 unit tests and 12/12 author-labeled routing developer fixtures passed](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43843917077) | Original v0.1.1 source still unavailable; archived 33/35 comparison cannot be superseded. Experiment in [draft PR #28](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/28) only |
| SourceGate | Opt-in `literal_support.py` insists on literal scalar value mention in evidence text, preserves source allowlists and conflict abstention, and reports unsupported claim keys. Fails closed on blank, partial, malformed and untrusted input | [31 SourceGate tests and 7/7 author-labeled offline cases passed](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43843504918) | Exact value mention is **not semantic entailment** and may false-hold paraphrases or miss negation; SourceGate main's earlier null/blank coverage fix was merged via PR #24. Additional strict mode in draft PR #29 only |
| TraceLens | `reviewer_agreement.py` computes per-ID agreement, chance-adjusted Cohen kappa, and unresolved disagreements while declining to call consensus ground truth. Unlabeled candidates fail input validation | [21 TraceLens tests, 4 harness tests, and 6/6 authored trace cases passed](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43843504918) | No actual separate human reviews received or recorded. New alignment tooling in [draft PR #29](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/29) only |

All initial failing builds and regression histories are retained in CI; correcting them does not erase the original failures.

## Proposed evidence gates before rating 8.5

**These are suggested pre-registered evaluation conditions, not certified industry thresholds.** Agree on final thresholds with the appropriate independent reviewer before opening a holdout.

### 1. EvidenceWeave

Freeze ontology and temporal scope. Obtain fresh independently labeled conflict/nonconflict cases with at least fifty of each class as an initial target and disclose selection method. Evaluate exact-key baseline and challenger on the *same* holdout with per-class confusion matrices, precision, recall, FPR, unresolved annotation cases and error taxonomy. Block accuracy promotion if improved recall comes from uncontrolled false alarms. Document real benchmark limitations, temporal exceptions and reviewer permission.

### 2. JEV

Recover the original `Jev_Routed_GenAI_Support_Desk_v0.1.1.zip` and 35 exact original cases to make a fair old-vs-new comparison; if unavailable, explicitly retire any comparison claim and evaluate the reconstruction as an independent new prototype. Obtain at least fifty previously unseen synthetic support tickets with mixed intents, paraphrases, sensitive billing cases, absent account evidence and unsupported drafts. Record handoff recall, false handoffs, abstention, unsupported preview releases, reviewer task outcomes, and original v0.1.1 result separately. A single unsafe automatic customer release blocks approval.

### 3. SourceGate

Independent reviewer annotates actual answer-support claims, source trust, scope, date validity, and conflicts on a separate frozen set (initial target 50 varied evidence decisions). Compare mainline supplied-claim coverage to opt-in literal binding with true-support precision, false abstention and evidence leakage. **Text matching cannot substitute for independent semantic evaluation.** Selected environment authority policies, credential separation and recovery remain open.

### 4. TraceLens

Collect an agreed independent reference of relevant and irrelevant passages for at least thirty diverse real retrieval traces (proposed starting target), with two reviewers if feasible. Use `reviewer_agreement.py` to expose disagreement, then adjudicate by a separate process. Measure candidate recall, score/rank cutoff diagnosis, evidence-use attribution, judge false positives and negatives against that reference. Preserve cases with no usable gold annotations as unknown, never as confirmed corpus gaps.

## Technical-ownership and acceptance evidence

- Owner explains a newly failed case and demonstrates the minimal corrective patch plus regression.
- New code/CI report exact commit SHAs and a reproducible command with raw denominators, unchanged baselines and known failures.
- Qualified human reviewers who did not author the code submit judgments without seeing system labels in advance. CI alone cannot certify this condition.
- A selected host/operator performs a supervised synthetic workflow and signs acceptance/deferral. Private records and privileged credentials remain off the public repo.
- Provider/model inference, real latency, and hardware-specific performance remain clearly **UNTESTED** until access is arranged; zero-token CI cannot substitute for these results.

**Recommended merge policy:** Keep experimental PRs #25, #28, #29 unmerged until their domain owner has reviewed code changes, CI on the final head is green, and recruiter-facing descriptions correctly limit claimed results. Independent validation gates can remain open in a merged engineering artifact only when explicitly documented; never label that as a production or independent-accuracy release.
