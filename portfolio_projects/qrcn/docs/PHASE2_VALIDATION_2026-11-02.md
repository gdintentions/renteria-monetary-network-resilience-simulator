# QRCN Phase 2 — Durable journal, crash recovery, concurrency and split-brain

**Date:** 2026-11-02 local (CI executed November 3 UTC)  
**Status:** development evidence completed on isolated branch, **draft PR #15**. Independent review **OPEN**; production **OPEN**.

## Scope and baseline preservation

The Phase 1 `qrcn/core.py` in-memory simulation remains unchanged. Phase 2 adds an **optional** `qrcn/durable.py` file-backed SQLite implementation. All changes are confined to the branch `experiment/qrcn-durable-journal-phase2-2026-11`; nothing here is a production payment service, quantum channel, or a globally consistent multi-node clearing system.

## Implemented mechanisms

1. **Atomic single-file journal:** SQLite table with unique transaction identifiers and `BEGIN IMMEDIATE` for ID/epoch check plus insert in one transaction; transaction records persist after process/object restart. Local `synchronous=FULL` is set; there is no promise of zero data loss under all hardware/power failure modes.
2. **Idempotent rejection:** both identical and conflicting payloads that reuse a committed identifier are rejected. Accepted amounts remain integer cents; a hash of canonical payload is recorded.
3. **Local fencing epoch:** a journal-local coordinator epoch is advanced in an atomic transaction; stale writers sharing that file are rejected. **This is not a cross-database fencing service.**
4. **Crash experiments:** a precommit interruption leaves no ledger record; a lost acknowledgment after commit is safely rejected on retry. Two subprocess tests use abrupt `os._exit` to test rollback of an open SQLite transaction and persistence of a completed commit after process death.
5. **Concurrent duplicates:** 24 threaded attempts on one journal yield exactly one accepted commit and 23 rejections. Additional concurrent distinct IDs preserve the expected aggregate sum.
6. **Partition audit:** two isolated SQLite databases can each commit the same ID independently. The read-only audit detects duplicated/conflicting IDs and requires adjudication; **it does not auto-merge**.

## Executed CI

GitHub Actions: [Phase 2 successful run](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41575171078), source revision `44781d0b1cdaa86b6448e6fb1875d5b2f1c72142`.

- Python **3.11 and 3.12**: entire unittest suite passed (**23 tests per interpreter**), both scenario runners passed, compilation passed.
- CLI: `cd portfolio_projects/qrcn && python -m unittest discover -s tests -v`
- Phase 2 scenario output: `python -m scripts.run_phase2`
- [Committed raw scenario evidence](../artifacts/phase2_scenarios_2026-11-02.json). Source run's raw `qrcn-phase2.json` SHA-256: `2eca03c178fa76cb9461cd728f8fbd82592730977525b6121cbf0c48c311d133`.
- Example: lost acknowledgment then restart -> `accepted`, `duplicate_rejected`; precommit interruption then restart -> `interrupted_before_commit`, `accepted`; epoch advance -> `stale_writer_rejected`; isolated partition -> independently `accepted` and audit flags conflict `demo-001`, no merge.
- The six original Phase 1 scenarios are preserved separately, unchanged.

### Failure found and fixed (preserved)

The first 21-test run **failed on Python 3.11** with `sqlite3.OperationalError: database is locked` during concurrent initialization because the connection constructor repeatedly attempted `PRAGMA journal_mode=WAL`; Python 3.12 had passed on the same commit. See [failed run](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41574973043).

Fix: eliminate per-connection journal-mode switching and explicitly close each connection using a context manager; preserve synchronous FULL and transactional lock acquisition. Both Python versions subsequently passed. The initial failure is not deleted or rewritten.

## Explicit unclosed failures and assumptions

- **True split-brain remains unsafe**: independent databases can both accept the same ID. Audit detects it **after the fact**, not at acceptance. No distributed consensus, leader election, quorum, external fencing token or cross-partition lock has been built.
- **Security assumptions**: all simulated validators share an in-process HMAC secret; no TLS, key negotiation, secure key vault, attacker-controlled infrastructure or post-quantum cryptography.
- **Operational limitations**: no network latency, power-loss durability trials, disk-corruption recovery, high-volume load, inter-process contention benchmark, failover orchestration or adversarial third-party audit. Local SQLite on shared or network filesystems is not represented.
- **Ledger semantics**: unique-ID journal, **not** double-entry accounting, financial settlement finality or funds custody. Physical crash safety depends on database and storage configuration.
- **Evidence limits**: fixed synthetic tests, one GitHub runner environment per interpreter, no confidence intervals or externally sourced adversarial cases.
- **UI boundary**: browser demonstration is synthetic and not backed by the Python security implementation.

## Phase 2 verdict

**Development gate passed for this specified local-simulation contract. Do not claim distributed exactly-once semantics, quantum resilience, regulatory compliance, or production readiness.** Independent review and production release remain open. The next engineering gate is independent hostile testing, process-level load/stress, persistent audit-chain tampering, and an explicit consensus/failover design (or a transparent admission that the system is intentionally centralized for settlement integrity).

## Browser interface verification (successor evidence)

- [Chromium browser interaction run](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41575535402) passed on the Phase 2 branch, alongside the latest [QRCN Python CI](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41575535558) and [public-source safety check](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41575535441).
- Browser script `scripts/qrcn_browser_smoke.cjs` exercised six client-side synthetic scenarios, checked each displayed receipt/status and captured a screenshot artifact. It does **not** exercise the Python SQLite implementation or prove a deployed website is current.
- New Phase 2 browser examples are saved in `hosted_demo/qrcn/index.html` on this **unmerged experimental branch**. The existing public GitHub Pages demo may still show only Phase 1 until an approved release deploys the branch.
