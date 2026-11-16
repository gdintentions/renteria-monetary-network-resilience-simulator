# Wave 1 bounded engineering results — November 15, 2026 Pacific

This report records branch-only technical development. It does **not** close independent validation, production, or organizational acceptance gates. Keep all prior evaluations and historical failures.

## Verified CI

[Wave 1 Evidence Regressions run #43820354990](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43820354990) succeeded on the draft PR branch, including SourceGate tests, a JEV isolated precheck, EvidenceWeave novelty diagnostics, and saved artifacts. Run revisions, commands and logs are available on GitHub Actions. Passing here means the authored tests passed; it is not deployment or independent test participation.

## EvidenceWeave — no inflated recall claim

Published benchmark baseline: 172 true positives, 4 false positives, 426 true negatives, 258 false negatives; precision 0.9773, recall 0.4000. The new `scripts/evidenceweave_novelty_analysis.py` checks *already-inspected* missed rows for additions/removals in their structured triples and emits JSON. It is a **novel-claim triage signal**, not evidence that added claims contradict old claims. It does not change the conflict model, historical 0.4000 recall, or the original report. A proper conflict-recall challenger must run on independently adjudicated semantic conflict relations and report a paired false-positive comparison. Historical known misses are regression examples only.

## SourceGate — actual bounded implementation fix

The `sourcegate.py` coverage check now treats null and blank-string values as absent rather than supported facts. It still accepts legitimate zero and false values; exact conflicts remain withheld. The new `test_missing_evidence_regressions.py` checks null, blank, expired, partial and conflicting data against an explicit synthetic current date. The full SourceGate unit tests passed in CI. No independent factual accuracy or external source authority test is claimed.

## JEV — isolated synthetic precheck, not integrated archived router

`routing_regression_prototype.py` and its tests are a **separate miniature**, not the archived v0.1.1 implementation. They exercise tracking/exchange paraphrase candidates, mixed intent, explicit human requests, sensitive cases, and input bounds. Candidate routes do not authorize account data disclosure, refund, draft release or delivery. These new developer-authored sentences are *not* the archived R29/R30 examples and must not be presented as a measured improvement from the historical 33/35. To fix the real JEV router, obtain and pin the source archive, adapt the current routed implementation and rerun the 35 historical regression cases plus a truly fresh holdout.

## Merge decision

Merge to `main` **only the tested and reviewed bounded changes**: fail-closed SourceGate value checks, regression tests, EvidenceWeave diagnostic code with clear anomaly caveats, reproducible CI and the upgrade evidence program. Keep actual model-challenger experiments, JEV integration requiring unavailable archived code, post-quantum/distributed QRCN research and independent-review findings in their own branches until they meet relevant evidence gates. A merged engineering change does not imply independent or organizational acceptance. Do not squash away important provenance references or delete historical run evidence.

## Remaining gates

- ConflictQA challenger with semantic conflict adjudication and false-positive budget: OPEN.
- SourceGate fresh independently labeled authority/coverage assessment: OPEN.
- JEV archived router integration and fair before/after comparison: BLOCKED pending actual source.
- Human owner walkthrough, outside reviewer, selected host and operator acceptance: OPEN.
