# Current evidence and open acceptance gates — November 20, 2026 Pacific

This additive register replaces no historical source, labels, reports or failure artifacts. It separates merged engineering, experimental branches, human validation and organizational acceptance. Private-source links remain access-controlled.

## Inventory

**14 distinct systems across nine accessible owned repositories, plus two related RAG demo variants.** The eight systems sharing this public repository are Monetary Simulator, ArgusLoop, EvidenceWeave, TraceLens, ContinuityRouter, SourceGate, QRCN and JEV Support Desk. Six further systems are Governed RAG, Polyglot Relay, Context Atlas, Local Model Workbench, Notes Evidence RAG and Personal Assistant Ledger. The RAG v1/v2 demo repositories are related variants, not additional independent systems; Guardrails is a RAG extension. Reflexion remains an unfinished paused reference, not an active system.

The [project index](../START_HERE.md), [private-project snapshots](PORTFOLIO_PROJECT_SNAPSHOTS.md), and [machine-readable production gates](RELEASE_GATES.json) must be read together. The release manifest has fifteen entries: fourteen systems and one combined gate group for the two RAG variants. All production-ready flags remain false. JEV now has its own five pending gates. Accessible repository inventory does not establish the existence or status of inaccessible repositories.

## Governed RAG dependency revalidation

**Bounded correction verified and merged**, [RAG PR #21](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/pull/21), merge `f272e0ace6446e40bea24cfb65694e9d17866832`. Private RAG baseline was `8a0c896efef531042f675c3be22ff0d69fa86f20`; the authenticated supervised Python service remains v2.1.0, with application code and policy behavior unchanged.

The [November 16 audit failure](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/43931212837) reported `opentelemetry-api==1.45.1`, CVE-2026-126360. The upstream [advisory](https://github.com/open-telemetry/opentelemetry-python/security/advisories/GHSA-mf5v-w3w3-f6cg) identifies 1.45.2 as patched. [RAG PR #21](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/pull/21) changes only that service pin and adds safe CI evidence retention plus predeclared revalidation criteria. Its application code, corpora, labels and benchmarks are unchanged. An edit alone is not a passing audit or release. No actual exploitation is asserted.

The [private revalidation report](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/blob/f272e0ace6446e40bea24cfb65694e9d17866832/docs/evaluations/SERVICE_DEPENDENCY_REVALIDATION_2026-11-20.md) retains the failed baseline and inspected before/after receipts. At candidate `023c2457`, audit [44843617797](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/44843617797) reported **zero known vulnerabilities across all fourteen listed service pins**. [Tests 44843617723](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/44843617723) passed **125 tests on each of Python 3.11 and 3.12**, zero failures/errors/skips, with one existing warning each. [Container smoke 44843617749](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/44843617749) passed. JSON, JUnit, resolved environments, source/lock hashes and image/corpus identifiers were inspected and retained privately. The actual PR test-merge tree was verified byte-identical to that candidate tree.

The final evidence-only head `56e09b5a` then passed [audit 44844088267](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/44844088267), [tests 44844088240](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/44844088240), and [container 44844088258](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/44844088258) before merge. This closes only the dated dependency/compatibility gate, not every supply-chain issue: future advisory changes, image/OS scanning and base-image digest approval remain separate. No suppressions were added. The original failed run and benchmark bytes are preserved.

## Released companion engineering

Hub mainline before this documentation change: `7519f4d113ba0a92fbcf2d1bc660e0ac028d30c8`, [merged PR #24](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/24), November 16 UTC / November 15 Pacific.

- **SourceGate:** null and blank claim values no longer count as facts; meaningful zero/false values remain valid and conflicts still withhold. Six new fixed-date regressions are in [test_missing_evidence_regressions.py](../portfolio_projects/renteria-sourcegate/test_missing_evidence_regressions.py). This establishes supplied structured-claim handling, not semantic truth or external source authority.
- **EvidenceWeave:** [failure-taxonomy CI 43821666386](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43821666386) passed five tests and regenerated diagnostics from the unchanged failure ledger. Original ConflictQA remains 172 TP, 4 FP, 426 TN, 258 FN across 430 paired items; recall 0.4000. A diagnostic is not improved recall.
- **Browser release:** [Pages run 43821666524](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43821666524) verified published Python bytes, 42 live browser acceptance checks and Guardrails browser checks at that revision. This register does not claim a new interactive or accessibility run.

## Experimental work — not released or independently validated

| Draft | What is actually measured | What must not be inferred |
|---|---|---|
| [EvidenceWeave PR #25](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/25), `77e95b11` | [CI 43844110462](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43844110462): functional-schema replay recovered **0 of 258** exposed misses. A separate semantic candidate on eight authored fixtures changed 1 TP / 2 FP / 3 TN / 2 FN to 3 TP / 0 FP / 5 TN / 0 FN. | No fresh external recall, free-text understanding or default conflict-model upgrade. Negative result and baseline remain preserved. |
| [JEV PR #28](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/28), `f8e11093` | [CI 43844163415](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43844163415): 25 reconstruction tests and 12/12 author-labeled tickets. Earlier refund-guarantee and stolen-card failures are retained in branch history. | This is a clean-room reconstruction, not the archived v0.1.1 source or its 35-case benchmark. Historical 33/35 is not superseded; no provider, account or customer delivery is tested. |
| [SourceGate / TraceLens PR #29](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/29), `a1ce5130` | [CI 43844300132](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/43844300132): 31 SourceGate tests, 21 TraceLens tests, four harness tests; separate files for seven SourceGate and six TraceLens developer cases. | Separate label files are not independent labeling. Literal value mention is not entailment; computed agreement is not truth. No independent human review received. |

Research PRs #14–18 and planning PR #23 remain separately scoped; this update does not merge them or silently transfer their capabilities to mainline.

## Historical evaluations retained

RAG's October 28 twelve-case exposed development study, its cafeteria-scope failure, and the October 9/14 reused NFCorpus comparisons are unchanged. NFCorpus MRR@10 0.4830 and 108/323 top-ten misses remain retrieval evidence, not policy accuracy. BM25 remains evaluation-only with 56 improvements and 34 regressions. Local retrieval timings are not API capacity or production latency. The [historical November 7 register](CURRENT_EVIDENCE_2026-11-07.md) retains detailed provenance.

Monetary proxy results remain seven correct directions out of twelve and only two of four windows beating persistence. ArgusLoop's scripted 5/5 and earlier 3/5 remain controlled GUI evidence, not unfamiliar vision-planner validation. No new numerical capability gain is claimed for either.

Context Atlas (15 local tests), Workbench (16), Notes Evidence RAG (15), Ledger (19), Polyglot Relay (4), and both RAG demo variants (6 each) retain their November 6 evidence and original limits. Workbench's drill did not demonstrate successful model inference; Polyglot uses sample translations; approved Ledger external actions remain drafts.

## Recruiter execution boundaries

- [Public RAG miniature](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/#governed-rag): synthetic JavaScript simulation, not the authenticated private Python service.
- [Public Python RAG samples](../demo_safe/governed-rag/README.md): reduced synthetic examples, not private-service parity or independent policy accuracy.
- [Guardrails Lab](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/guardrails-lab/): recorded seven-case offline outputs; final stage matches 6/7 authored expectations with one false block. No live account or payment connection.
- [Reliability Lab](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/reliability/): actual Python TraceLens/ContinuityRouter/SourceGate cores through Pyodide, using synthetic adapters/data.
- [JEV walkthrough](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/jev-support-desk/): six recorded static cases, not an executing support engine or live provider.
- [QRCN browser](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/qrcn/): JavaScript scenario fixtures, not released consensus/PQC/financial clearing.

## Independent review and selected-host acceptance: OPEN

No human judgments, independence attestations, reviewer times, owner-competence scores, organizations or acceptance signatures are created by this adjustment. New protocol tooling and authored fixtures are preparation only. A reviewer/custodian must verify competence, independence, scope and permissions before freezing fresh holdout labels and thresholds. Keep original labels, disagreements, failed/missing outputs and separately dated verdicts. Neither self-review nor another AI agent closes this gate.

Selected organizational host, operator, approved workload, TLS/identity lifecycle, retention, load/capacity, recovery/rollback, monitoring and incident responsibilities remain unresolved. Development/container checks cannot supply organizational approval. The current RAG service has no outbound model call; provider-dependent projects need separately authorized real-model testing before making provider-quality claims.

## Next decisions

1. Keep the scheduled RAG audit and preserved receipts current; the bounded dependency correction has passed, while independent policy and selected-host gates remain open.
2. Obtain qualified independent reviewers and agreed criteria for a small frozen batch; do not invent participants or convert the current developer labels into a blind holdout.
3. Select one personal or organizational pilot host/operator and budget before any provisioning or real data transfer. Keep that pilot's acceptance distinct from independent policy validation.

No paid inference, service deployment, reviewer outreach or visibility change is part of this documentation adjustment.
