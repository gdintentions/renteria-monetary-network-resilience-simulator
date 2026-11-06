# Portfolio engineering rollout — 2026-11-06

The Governed RAG method is now implemented across the other 14 inventoried components: bounded tests, explicit recovery contracts, additive reports, failures preserved, source binding, CI reruns and independent-review handoffs. The current RAG reference is service v2.1.0, merged at `6c510c8a0319cc452ebbb7a57d6ef789d077f2f6` in its private PR #19. This update adds engineering evidence; it does not transfer RAG domain accuracy, observed user evidence, identities, or production acceptance to other projects.

The prior [planning draft](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/19) is historical. The user's November 6 instruction authorizes development in parallel with open independent validation. No production or independent-validation gate is closed by that instruction.

## Actual scope

| Component | Development/recovery workflow | Remaining limitation |
|---|---|---|
| Monetary Simulator | 5-year seeded scenario replay; bounded horizon | Historical validity, forecasting and identifiability unchanged |
| TraceLens | Restore structured trace/config; reproduce diagnosis and replay | Supplied labels are not independent truth |
| Continuity Router | Restore routing config; injected failover and restricted classification | Synthetic adapters; no provider SLO or persistent circuit-state claim |
| SourceGate | Restore supplied evidence/config; conflict abstention | No semantic truth certification or live-web quality claim |
| EvidenceWeave | Private provenance checkpoint; missing references and duplicate IDs rejected | ConflictQA recall/misses remain unchanged |
| ArgusLoop | Private unique metadata-only audit files; deterministic policy/dispatch replay | No live desktop replay, vision-planner acceptance or human observation |
| QRCN | Authenticated checkpoint; recovered duplicate IDs cannot commit twice | Single-process toy HMAC; no real payment, PQC/QKD or distributed durability |
| [Context Atlas](https://github.com/gdintentions/renteria-context-atlas/blob/main/ENGINEERING_STANDARD.md) | SQLite restore, evidence search and links | Independent review and observed human workflow open; see repository limits |
| [Local Model Workbench](https://github.com/gdintentions/renteria-local-model-workbench/blob/main/ENGINEERING_STANDARD.md) | SQLite restore and honest unavailable-model failure | Independent review and observed human workflow open; see repository limits |
| [Notes Evidence RAG](https://github.com/gdintentions/renteria-notes-evidence-rag/blob/main/ENGINEERING_STANDARD.md) | SQLite restore, extraction and no-match abstention | Independent review and observed human workflow open; see repository limits |
| [Personal Assistant Ledger](https://github.com/gdintentions/renteria-personal-assistant-ledger/blob/main/ENGINEERING_STANDARD.md) | SQLite restore, draft approval and durable denial | Independent review and observed human workflow open; see repository limits |
| [Polyglot Relay](https://github.com/gdintentions/renteria-polglot-relay/blob/main/ENGINEERING_STANDARD.md) | Bounded heuristic replay; risk-detector and dependency fixes | Independent review and observed human workflow open; see repository limits |
| [RAG Demo v1](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag-demo/blob/main/ENGINEERING_STANDARD.md) | Lexical/config replay and Streamlit workflow | Independent review and observed human workflow open; see repository limits |
| [RAG Demo v2](https://github.com/gdintentions/enterprise-ai-chatbot-governed-rag-recruiter-demo-v2/blob/main/ENGINEERING_STANDARD.md) | Lexical/config replay and Streamlit abstention workflow | Independent review and observed human workflow open; see repository limits |

## Reproduce the public components

```sh
python -m pip install -r requirements.txt
python -m pytest -q
python engineering.py --project qrcn --output-dir artifacts/my-qrcn-reproduction --source-revision "$(git rev-parse HEAD)"
```

Choose any of: `monetary-simulator`, `tracelens`, `continuity-router`, `sourcegate`, `evidenceweave`, `argusloop`, `qrcn`. Use a NEW output directory each time. The final reports are in `artifacts/engineering-2026-11-06-r2/PROJECT/report.json`. A 30-second wall deadline, 20 CPU seconds, 2 GiB process address space and 1 MB checkpoint bound constrain each child. The four generic checks are overwrite rejection, separate-process replay equality, altered-checkpoint rejection and separate-destination restore equality. Component-specific assertions are recorded inside `observed_result`. This is bounded synthetic development execution, not capacity testing.

Reports pin an implementation commit and SHA-256 hashes of measured source files. A subsequent evidence-only commit adds the reports without changing that measured code; CI runs on its own checkout SHA and uploads new artifacts. Preserve old reports and compare deterministic outcomes, not generated timestamps or timings. `source_revision` is supplied by the runner; verify the hash map against the named checkout before treating it as bound evidence.

The generic checkpoint restores invented inputs/configuration, then reruns actual Python cores. It does not recover a live provider session, browser speech state, authenticated identity, or execute a desktop action. SHA-256 only detects changes relative to a separately trusted receipt; it does not authenticate the author. QRCN additionally authenticates its toy journal with a separately retained key; the fixture key is public synthetic test material, never a production credential. Restoring an old valid QRCN checkpoint can lose transactions after that checkpoint: there is no automatic crash-safe journal, consensus or anti-rollback service.

EvidenceWeave exposes `evidenceweave.checkpoint.save(weave, path)` and `restore(path, retained_sha256)`. Restore validates into a new graph and never mutates the original on failure. ArgusLoop's new audit schema retains action/status metadata and a record digest while omitting typed text, arbitrary messages and planner reasoning; it is not an immutable remote audit service. Existing raw historical artifacts are preserved and require their own retention/privacy decisions.

## Honest failures and validation boundaries

Original numerical evaluation reports remain unchanged: monetary validity limitations and EvidenceWeave's ConflictQA misses are not improved by restore tests. No real translation provider, successful local-model inference, independent reviewer or human workflow is claimed. All new automated workflows have **zero human participants**. Browser installation locally failed on a truncated download; available CI browser checks remain separate evidence. Streamlit AppTest checks are framework-level UI sessions, not observed human or real-device tests.

During development, an invalid-request audit initially violated the old mutation-free framing contract in the four local tools; dispatch-only logging fixed that regression while retaining the original tests. A stricter horizon initially changed a tested error message; the original message contract was retained while adding the upper bound. The production-gate inventory check was updated from ten grouped entries to an explicit fourteen-entry set after adding the four previously unlisted components (the two recruiter demos share a production-gate entry). New test harness path/indentation/import setup failures were corrected before final runs. These were development failures, not silently removed benchmark cases.

## Independent review handoff

No independent review is complete. A reviewer should use the pinned source, verify hashes, rerun ordinary/invalid/fault/restore workflows, inspect denial/abstention and corruption behavior, then create a NEW signed/identified review receipt with commands, assistance, timings actually measured, failures and verdict. Until that exists, independent validation stays OPEN. A separate observed-user session must record who acted, assistance, interruption/replay and whether the workflow was unassisted.

For production, select an actual host and operator; validate its trust boundary, resource/capacity/recovery, retention and incident responsibilities. [Production gates](RELEASE_GATES.json) stay pending. Recruiter-safe claim: “Implemented and reproduced bounded synthetic engineering/recovery checks across the portfolio; independent and production validation remain open.”
