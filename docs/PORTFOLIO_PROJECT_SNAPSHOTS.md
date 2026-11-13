# Renteria AI Systems Portfolio — Recruiter Project Snapshots

This page gives recruiters and reviewers a public, non-sensitive overview of projects whose working source repositories are currently private. It is intentionally factual: capabilities listed here are limited to behavior implemented in the corresponding repository and verified by its checked-in tests or documented demo boundaries.

## Current verification — November 7, 2026 Pacific

This additive update supersedes the older test-count summaries below, without deleting their historical evidence. See the [current evidence register](CURRENT_EVIDENCE_2026-11-07.md) for tested revisions, CI links, failures, and the distinction between mainline and experimental work. Private-source links remain access-controlled; publishing this summary does not publish private source, identities, labels, or credentials.

| Component | Latest inspected evidence | Boundary still open |
|---|---|---|
| Governed RAG service v2.1.0 | **114 tests passed** on Python 3.11 and 3.12 at `9b7aafb08a1971031bdb65d1ee7ac510fde68de4`; [run 42349259829](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/42349259829). Separate November 6 development drill: 16 checks and 40/40 synthetic requests. | Fresh independent policy labels/judgments, selected organizational host/operator acceptance, and production readiness remain open. |
| Governed RAG Demo v1 | **6 local tests**, four bounded replay/restore checks; [verification](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag-demo/blob/cfc15e92/artifacts/engineering-2026-11-06/verification.txt). | Synthetic stateless demo, not the authenticated service or independent policy evaluation. |
| Governed RAG Demo v2 | **6 local tests**, four bounded replay/restore checks; [verification](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag-recruiter-demo-v2/blob/82f2771c/artifacts/engineering-2026-11-06/verification.txt). | Five authored comparison cases are not an external or blind benchmark. |
| Polyglot Relay | **4 local tests**; repaired risk-word detection, input bounds, build and dependency-audit output; [verification](https://github.com/gdintentions/renteria-polglot-relay/blob/347f0a62/artifacts/engineering-2026-11-06/verification.txt). | Translation remains a sample dictionary; quality/latency formulas are not provider measurements. |
| Context Atlas | **15 local tests**, eight bounded recovery/rate checks; [verification](https://github.com/gdintentions/renteria-context-atlas/blob/ca20e5fe/artifacts/engineering-2026-11-06/verification.txt). | Link usefulness and observed human workflow have not been independently validated. |
| Local Model Workbench | **16 local tests**, eight bounded recovery/rate checks; [verification](https://github.com/gdintentions/renteria-local-model-workbench/blob/e59a3774/artifacts/engineering-2026-11-06/verification.txt). | The drill exercised unavailable-model failure, not successful inference or model quality. |
| Notes Evidence RAG | **15 local tests**, eight bounded recovery/rate checks; [verification](https://github.com/gdintentions/renteria-notes-evidence-rag/blob/73bf3d51/artifacts/engineering-2026-11-06/verification.txt). | Extraction/no-match checks do not establish independently judged support or optional generation quality. |
| Personal Assistant Ledger | **19 local tests**, eight bounded recovery/rate checks; [verification](https://github.com/gdintentions/renteria-personal-assistant-ledger/blob/e190c0a3/artifacts/engineering-2026-11-06/verification.txt). | Approved external drafts are not delivered; actual multi-day/operator acceptance remains open. |

The counts above are not pooled into an accuracy percentage. Local artifact results, CI executions, synthetic framework UI sessions, independent human evaluation, and production evidence are distinct categories. The November 6 rollout has zero human participants. Original baseline reports and failures remain intact.

## Project specifications

### November 12, 2026 Pacific

**JEV-Routed GenAI Support Desk** · [Browser demo](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/jev-support-desk/) · [Project specification](../portfolio_projects/jev-routed-genai-support-desk/README.md). The offline prototype routes synthetic retail tickets, prepares evidence-bound drafts, and records agent review decisions. The archived v0.1.1 run routed 33 of 35 authored development cases correctly after tuning on the same set. Two paraphrases still went to clarification. Live-provider evaluation, independent review, selected-host checks, and operator acceptance remain open.

### Guardrails Evaluation Lab

[Open the Guardrails Evaluation Lab](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/guardrails-lab/) · Governed RAG extension. The offline run compares four cumulative configurations across seven authored synthetic cases. Input screening falsely blocks one legitimate correction. Output redaction reduces synthetic contact disclosures from one to zero. Application permissions deny the unauthorized fee waiver in every configuration. The final configuration matches six of seven expected outcomes. The browser displays recorded results. Live service integration and independent validation remain open.

## Historical snapshots and implemented scope

The dated hardening counts below describe their original releases, not the current test totals. Capability descriptions retain their stated prototype limits.

## Enterprise AI Chatbot — Governed RAG

[Run the reduced public demo](../demo_safe/governed-rag/README.md)

**Role:** evidence-grounded policy Q&A and AI governance reference implementation.

**Implemented:** section-aware chunking, TF-IDF/cosine retrieval, source citations, heuristic confidence scoring, safe/review/block routing, FastAPI endpoints, durable SQLite evidence/review/audit records, bearer client/reviewer roles, withheld drafts, deterministic evaluation, and a Streamlit recruiter dashboard.

**Verified boundary (refreshed October 27, 2026 Pacific):** the dependency-patched core passed **64 tests on Python 3.11 and 3.12**, retaining one Starlette/httpx deprecation warning. [Exact tested revision 1254c7a](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/40622442553) · [merged fix PR 13](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/pull/13). The separate original NFCorpus retrieval evaluation reports: MRR@10 0.4830, nDCG@10 0.2943, mean Recall@10 0.1464, and 108 complete top-10 misses among 323 queries. These results do not measure real-policy answer correctness. Independent policy labels and organizational deployment validation remain pending. The [live synthetic reviewer miniature](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/#governed-rag) uses different JavaScript retrieval logic and simulated approval; it is not the authenticated Python service.

The October 14 lexical regression comparison reproduced all 646 published cosine/BM25 top-10 lists. BM25 remains evaluation-only (MRR@10 0.5131; 99/323 misses; 56 reciprocal-rank improvements and 34 regressions). Indexed cosine remains default. These reused biomedical results are not fresh blind policy validation. [Comparison report](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/blob/main/docs/evaluations/RETRIEVAL_COMPARISON_2026-10-14.md).

The October 26 dependency audit finding for opentelemetry-api 1.45.0 is retained in [failed run 40347780711](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/40347780711). PR 13 updates it to 1.45.1; the [patched audit](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/40622442460) reports no known vulnerabilities in the listed lockfile packages, and the [container build/smoke](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag/actions/runs/40622443022) passed on the same revision. This is not comprehensive security certification or production deployment.

## Governed RAG Demo

[Run the reduced public demo](../demo_safe/governed-rag/README.md)

**Role:** compact recruiter walkthrough of the governed-RAG control loop.

**Implemented:** sample-policy retrieval, evidence ranking, citation-first answers, confidence/governance routing, benchmark evaluation, and a synthetic controls stress test.

**Verified boundary:** the benchmark contains four hand-authored questions over a tiny sample corpus. The demo now abstains on weak single-term matches rather than forcing an answer.

## Governed RAG Recruiter Demo v2

[Run the reduced public model lab](../demo_safe/governed-rag-model-lab/README.md)

**Role:** retrieval-model comparison and robustness lab.

**Implemented:** Jaccard, TF-IDF cosine, character-trigram Dice, and hybrid retrieval; Top-1, MRR, Hit@3, synthetic corruption tests, and governance-threshold simulation.

**Verified boundary:** results describe five sample sections and five authored benchmark questions only. They do not establish model quality on an external corpus.

## Renteria Polyglot Relay

[Run the reduced public demo](../demo_safe/polyglot-relay/README.md)

**Role:** governed multilingual interaction and accessibility prototype.

**Implemented:** React/Vite interface, browser speech input/output where supported, controlled sample translations, quality/risk/latency formulas, route decisions, transcript export, analytics, and deterministic simulation.

**Verified boundary:** unrestricted translation is not implemented. Built-in translations cover only listed English source phrases; production translation requires a provider adapter. Quality and latency metrics are illustrative formulas, not measured service-level results.

## Renteria Context Atlas

[Run the reduced public demo](../demo_safe/context-atlas/README.md)

**Role:** explainable personal-knowledge graph prototype.

**Implemented:** Markdown/text import, explicit wikilinks, broken-link detection, lexical connection suggestions, source hashes, current-content retrieval, SQLite persistence, and a loopback web interface.

**Verification:** 14 automated tests passed in the hardening release, including local HTTP process tests for session-token enforcement, Host/Origin rejection, path boundaries, graph behavior, deletion behavior, and revision hashes. GitHub Actions completed successfully on September 28, 2026.

**Boundary:** graph suggestions are lexical overlap, not semantic truth. The application is local-only and is not a hosted service.

## Renteria Local Model Workbench

[Run the reduced public demo](../demo_safe/local-model-workbench/README.md)

**Role:** repeatable local-model comparison harness.

**Implemented:** discovery of locally installed Ollama models, one-to-three-model prompt comparison, runtime/error/token recording, opt-in experiment persistence, export/delete, and loopback-only adapter restrictions.

**Verification:** 15 automated tests passed in the hardening release, including local HTTP tests, explicit failure handling, unknown-model rejection, redirect rejection, and cloud-tag rejection. GitHub Actions completed successfully on September 28, 2026.

**Boundary:** no model is bundled, and real-model inference was not exercised in the release evidence. Wall time is not a controlled quality benchmark.

## Renteria Notes Evidence RAG

[Run the reduced public demo](../demo_safe/notes-evidence-rag/README.md)

**Role:** source-first Q&A for small Markdown/text collections.

**Implemented:** note import/edit/delete/export, lexical passage ranking, line-numbered excerpts, content hashes, no-match abstention, extractive mode, optional local-model generation, and citation-ID validation.

**Verification:** 14 automated tests passed in the hardening release, including no-evidence abstention, citation gating, deletion behavior, session controls, Host/Origin rejection, and local HTTP behavior. GitHub Actions completed successfully on September 28, 2026.

**Boundary:** citation-ID validation proves that a cited source identifier exists; it does not prove entailment or factual correctness. Generated output remains a human-review draft.

## Renteria Personal Assistant Ledger

[Run the reduced public demo](../demo_safe/personal-assistant-ledger/README.md)

**Role:** local memory and task-state-machine prototype.

**Implemented:** SQLite-backed editable memory, timezone-aware reminders, restart catch-up, idempotent local notices, external-action draft/approval/cancellation states, and an audit trail that omits memory values.

**Verification:** 15 automated tests passed in the hardening release, including timezone handling, idempotent reminders, cancellation, approval constraints, audit-value omission, local HTTP controls, and session protection. GitHub Actions completed successfully on September 28, 2026.

**Boundary:** there is no external message delivery, autonomous tool use, or cloud scheduler. Approved external actions remain drafts.

## How to interpret these projects

These are working prototypes and inspectable engineering demonstrations, not claims of production deployment, market demand, calibrated model accuracy, or commercial readiness. The portfolio intentionally distinguishes implemented behavior, synthetic/modelled evidence, and validation work that remains to be done.

## Browser verification added October 5, 2026 (Pacific)

All four local apps also passed real Chromium integration against their actual Python loopback servers with disposable synthetic state. [Atlas PR 2](https://github.com/gdintentions/renteria-context-atlas/pull/2), [Workbench PR 2](https://github.com/gdintentions/renteria-local-model-workbench/pull/2), [Notes RAG PR 2](https://github.com/gdintentions/renteria-notes-evidence-rag/pull/2), and [Ledger PR 2](https://github.com/gdintentions/renteria-personal-assistant-ledger/pull/2) are merged. Tests include export/reload persistence and mobile viewport checks. Workbench tested unavailable-runtime handling, not actual model inference. This closes the specified synthetic browser checks, not independent quality or production deployment gates.

See [the completion register](COMPLETION_REGISTER.md) for remaining work and [sharing guidance](PUBLIC_SHARING.md) for factual introductions.

### Follow-up evidence

[Atlas PR 3](https://github.com/gdintentions/renteria-context-atlas/pull/3) and [Notes RAG PR 3](https://github.com/gdintentions/renteria-notes-evidence-rag/pull/3) fix stale evidence after changed inputs and discard late responses; actual delayed-response browser regressions and unit suites passed. [Ledger PR 3](https://github.com/gdintentions/renteria-personal-assistant-ledger/pull/3) adds a synthetic three-day backup/reopen and explicit DST-offset drill plus concurrent exactly-once local notices; all 18 unit tests and browser integration passed. This accelerated clock study is not actual multi-day uptime.
