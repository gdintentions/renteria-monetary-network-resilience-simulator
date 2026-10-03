# Renteria AI Systems Portfolio — Recruiter Project Snapshots

This page gives recruiters and reviewers a public, non-sensitive overview of projects whose working source repositories are currently private. It is intentionally factual: capabilities listed here are limited to behavior implemented in the corresponding repository and verified by its checked-in tests or documented demo boundaries.

## Enterprise AI Chatbot — Governed RAG

[Run the reduced public demo](../demo_safe/governed-rag/README.md)

**Role:** evidence-grounded policy Q&A and AI governance reference implementation.

**Implemented:** section-aware chunking, TF-IDF/cosine retrieval, source citations, heuristic confidence scoring, safe/review/block routing, FastAPI endpoints, an in-memory human-review queue, deterministic evaluation, and a Streamlit recruiter dashboard.

**Verified boundary:** the corpus and benchmark cases are authored fixtures. Confidence is a heuristic score, not a calibrated probability. The review queue is not durable and authentication is not implemented.

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

**Verification:** 11 automated tests passed in the release evidence record, including local HTTP process tests for session-token enforcement, Host/Origin rejection, path boundaries, graph behavior, deletion behavior, and revision hashes. GitHub Actions completed successfully on September 28, 2026.

**Boundary:** graph suggestions are lexical overlap, not semantic truth. The application is local-only and is not a hosted service.

## Renteria Local Model Workbench

[Run the reduced public demo](../demo_safe/local-model-workbench/README.md)

**Role:** repeatable local-model comparison harness.

**Implemented:** discovery of locally installed Ollama models, one-to-three-model prompt comparison, runtime/error/token recording, opt-in experiment persistence, export/delete, and loopback-only adapter restrictions.

**Verification:** 12 automated tests passed in the release evidence record, including local HTTP tests, explicit failure handling, unknown-model rejection, redirect rejection, and cloud-tag rejection. GitHub Actions completed successfully on September 28, 2026.

**Boundary:** no model is bundled, and real-model inference was not exercised in the release evidence. Wall time is not a controlled quality benchmark.

## Renteria Notes Evidence RAG

[Run the reduced public demo](../demo_safe/notes-evidence-rag/README.md)

**Role:** source-first Q&A for small Markdown/text collections.

**Implemented:** note import/edit/delete/export, lexical passage ranking, line-numbered excerpts, content hashes, no-match abstention, extractive mode, optional local-model generation, and citation-ID validation.

**Verification:** 11 automated tests passed in the release evidence record, including no-evidence abstention, citation gating, deletion behavior, session controls, Host/Origin rejection, and local HTTP behavior. GitHub Actions completed successfully on September 28, 2026.

**Boundary:** citation-ID validation proves that a cited source identifier exists; it does not prove entailment or factual correctness. Generated output remains a human-review draft.

## Renteria Personal Assistant Ledger

[Run the reduced public demo](../demo_safe/personal-assistant-ledger/README.md)

**Role:** local memory and task-state-machine prototype.

**Implemented:** SQLite-backed editable memory, timezone-aware reminders, restart catch-up, idempotent local notices, external-action draft/approval/cancellation states, and an audit trail that omits memory values.

**Verification:** 12 automated tests passed in the release evidence record, including timezone handling, idempotent reminders, cancellation, approval constraints, audit-value omission, local HTTP controls, and session protection. GitHub Actions completed successfully on September 28, 2026.

**Boundary:** there is no external message delivery, autonomous tool use, or cloud scheduler. Approved external actions remain drafts.

## How to interpret these projects

These are working prototypes and inspectable engineering demonstrations, not claims of production deployment, market demand, calibrated model accuracy, or commercial readiness. The portfolio intentionally distinguishes implemented behavior, synthetic/modelled evidence, and validation work that remains to be done.
