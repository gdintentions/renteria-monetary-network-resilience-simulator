# QRCN — Project Record and Development Continuity

**Established:** November 2, 2026 (Pacific). **Status:** standalone, self-contained GitHub portfolio research project, with subsequent phases retained as isolated drafts. This file is a durable index of existing evidence, not a new claim of validation.

## Original research concept

The initial screenshot-based concept imagined a decentralized transaction-clearing system with moving credentials/code, compromise detection, alternate routes and quantum protection. Technical review separated valid testable ideas—message integrity, replay protection, idempotency, failover, persistency and agreement—from unsupported claims that code mutation makes interception useless or that entanglement detects all intrusions.

The working name **Quantum-Resilient Clearing Network (QRCN)** was retained as a research label. The current system does **not** deploy quantum hardware or implement a PQC-protected production network.

## Phase 1 — Transaction-integrity laboratory

**Code:** [core.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/qrcn/core.py)  
**Tests:** [test_core.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/tests/test_core.py)  
**Runner:** [run_demo.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/scripts/run_demo.py)  
**Documentation:** [Threat model](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/docs/THREAT_MODEL.md), [baseline validation](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/docs/VALIDATION.md)  
**Results:** [Original scenario results](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/artifacts/scenario_results_2026-11-02.json)

Delivered an HMAC-SHA256 integrity demonstration with illustrative key epochs, tampering and stale-tag rejection, local duplicate rejection, alternate-node selection and acknowledgment-loss replay rejection. The initial project had nine automated tests; both Python 3.11 and Python 3.12 passed CI. A separate public browser uses synthetic JavaScript fixtures, never the Python clearing engine.

**Failure boundary:** In-memory single-process journal, no confidentiality, no authenticated network protocol, no real settlement.

## Phase 2 — Durability, crash recovery and concurrency

**Code:** [durable.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/qrcn/durable.py)  
**Tests:** [test_durable.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/tests/test_durable.py)  
**Runner:** [run_phase2.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/scripts/run_phase2.py)  
**Results:** [Phase 2 evidence](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/artifacts/phase2_scenarios_2026-11-02.json)  
**Report:** [Phase 2 validation](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/docs/PHASE2_VALIDATION_2026-11-02.md)  
**PR:** [#15](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/15)

Added file-backed SQLite transaction journaling and atomic transaction-ID uniqueness across threads that share one journal, a coordinator epoch, crash-before-commit and crash-after-commit tests, and post-restart retry checks. The development tests passed **23/23 on Python 3.11 and 3.12**; six client-side browser choices were also checked in Chromium.

**Published real failure:** Initial Python 3.11 concurrency CI hit `sqlite3.OperationalError: database is locked` during repeated WAL mode initialization. Removing per-connection mode switching and closing connections correctly fixed the tested issue; the failing CI run remains in GitHub. More importantly, two independently partitioned databases can still each commit a conflicting transaction; the audit detects the conflict afterward, **not** before the commits.

## Phase 3 — Quorum admission and post-quantum API tests

**Code:** [quorum.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/qrcn/quorum.py)  
**Tests:** [test_quorum.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/tests/test_quorum.py), [optional PQC tests](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/tests/test_pqc_optional.py)  
**Runners:** [run_phase3.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/scripts/run_phase3.py), [run_pqc.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/scripts/run_pqc.py)  
**Results:** [quorum](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/artifacts/phase3_quorum_results_2026-11-02.json), [PQC](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/artifacts/phase3_pqc_results_2026-11-02.json)  
**Report:** [Phase 3 validation](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/docs/PHASE3_VALIDATION_2026-11-02.md)  
**PR:** [#16](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/16)

Simulated an availability majority gate (2/3 required) while still using a shared journal for transaction uniqueness. Separately exercised third-party ML-KEM-768 encapsulation/decapsulation and ML-DSA-65 signature verification/tampering detection with `pqcrypto==1.0.0`.

The core Python 3.11 log reported **34 tests: 33 passed and one optional PQC test skipped**; optional PQC CI passed independently on both Python versions. Measured on one CPU runner: ML-KEM encapsulation 0.0702 ms median, ML-DSA sign 8.9829 ms, ML-DSA verify 0.1915 ms, each over 12 warm calls.

**Failure boundary:** The majority decision is a local gate, not independently maintained consensus. The ML-KEM/ML-DSA evaluation is **not integrated** into transport, has no authenticated handshake/KDF/AEAD or certificate validation, and does not establish FIPS 140 certification.

## Phase 4 — Independent persistent acceptors and Paxos-style messaging

**Code:** [paxos.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/qrcn/paxos.py), [tcpnode.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/qrcn/tcpnode.py)  
**Tests:** [test_paxos.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/tests/test_paxos.py), [test_tcp_nodes.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/tests/test_tcp_nodes.py)  
**Runner:** [run_phase4.py](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/scripts/run_phase4.py)  
**Results:** [Phase 4 raw evidence](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/artifacts/phase4_paxos_results_2026-11-02.json)  
**Report:** [Phase 4 validation](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/docs/PHASE4_VALIDATION_2026-11-02.md)  
**PR:** [#17](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/17)

Implemented independent acceptors, each with their **own SQLite file** storing ballot promises and accepted values. A single-decree proposer uses prepare/promise and accept exchanges, chooses a value only when a majority responds appropriately, and adopts previously accepted values in later ballots. A loopback-only, unauthenticated TCP JSON-RPC demonstration exercises **three distinct OS processes** and node restart.

GitHub CI passed on Python **3.11 and 3.12**, with **45 tests executed, one optional PQC test skipped** in the standard-only configuration; the synthetic Phase 4 raw output records minority refusal, majority choice, recovery after restart and conflict adoption.

**Published local failure:** An initial local implementation closed a connection without committing; the persistence bug was fixed before GitHub commit. No claim is made that a complete replicated log, automatic ballot election, concurrent adversarial schedule model, authenticated transport, Byzantine safety or real clearing exists.

## Next engineering and independent-review gates

1. Explicitly model competing proposers with globally unique ballots; add controlled scheduling and state-space/property testing.
2. Add durable learner/decision recording and an ordered replicated log or use and benchmark a mature consensus implementation.
3. Test ungraceful process death, restart, traffic delays/reordering and independent partitions with trace capture and invariant checks.
4. Separately design a reviewed authenticated key-establishment channel, then opt-in PQC/hybrid experiments with identity binding and AEAD; never invent encryption.
5. Obtain independent distributed-systems and cryptographic review before treating this as anything beyond a prototype.

## Preservation policy

Older source and benchmarks must not be overwritten. New results receive separate paths, commit references, tests and documented failures. Every draft PR remains open until reviewed. This project record is stored on `main` solely as a portfolio index to the research branches; it is **not** the release of experimental Phases 2–4.
