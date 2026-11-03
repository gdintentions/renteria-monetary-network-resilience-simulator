# QRCN — Quantum-Resilient Clearing Network
**Portfolio project home • Versioned research archive • November 2, 2026**

> **Research prototype only. Not a secure financial clearinghouse, production payment platform, actual quantum network, or independently validated security product.**

This is the canonical **QRCN** project entry in the Renteria AI Systems Portfolio. It gathers the original concept, four successive implementation phases, runnable source, automated test evidence, browser visualization, preserved failures, and next-stage engineering decisions **without copying, overwriting, or merging the experimental code**.

## Quick access

| Destination | What you will find |
|---|---|
| [Complete Phase 4 project source](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/tree/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn) | All Python source, tests, scripts, validation reports, historical artifacts |
| [Current consolidated project README](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/README.md) | Installation, execution, architectural boundaries, phases |
| [Development chronology](PROJECT_RECORD.md) | What happened in each phase, verified claims, unsolved problems |
| [Phase 1 public browser demo](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/qrcn/) | Interactive **synthetic** scenarios, not a live settlement/consensus service |
| [Phase 4 draft PR #17](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/17) | Latest experimental work, stacked on earlier review branches |
| [Phase 4 validation report](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/docs/PHASE4_VALIDATION_2026-11-02.md) | Test coverage and explicit outstanding security/consensus gates |

## Project mission

Investigate how synthetic transaction messages behave under tampering, replay, node outages, crash/restart, concurrent duplicate attempts, isolated partitions, and competing agreement proposals. Test standard post-quantum APIs in a **separate controlled experiment**, with all controls, results, and failures independently inspectable.

## Four phases and current engineering status

| Phase | Concrete implementation | Evidence | Limitations |
|---|---|---|---|
| **1 — Local integrity and failover** | HMAC-authenticated transaction message, per-node key epoch, replay rejection, local in-memory idempotency and simulated rerouting | [Phase 1 validation](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/docs/VALIDATION.md) · [scenario outputs](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/artifacts/scenario_results_2026-11-02.json) | In-memory state and one process; no quantum security, encrypted transport or genuine distributed coordination |
| **2 — Durable transaction journal** | SQLite atomic ID check+insert, writer fencing, multi-threaded attempts, crash recovery, partition comparison | [Phase 2 report](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/docs/PHASE2_VALIDATION_2026-11-02.md) · [raw outputs](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/artifacts/phase2_scenarios_2026-11-02.json) | Same-file consistency only; **isolated split-brain databases can both accept** |
| **3 — Majority gate and isolated PQC experiment** | Simulated majority admission with shared file; optional ML-KEM-768 and ML-DSA-65 API tests | [Phase 3 report](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/docs/PHASE3_VALIDATION_2026-11-02.md) · [quorum JSON](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/artifacts/phase3_quorum_results_2026-11-02.json) · [PQC JSON](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/artifacts/phase3_pqc_results_2026-11-02.json) | Majority gate is **not** independent-node consensus; cryptography not integrated with transport |
| **4 — Independent acceptors / single-decree Paxos** | Three separately persisted SQLite acceptors, prepare/accept proposals, observed majority choice, localhost three-process test | [Phase 4 report](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/docs/PHASE4_VALIDATION_2026-11-02.md) · [raw outputs](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/blob/experiment/qrcn-phase4-paxos-prototype-2026-11/portfolio_projects/qrcn/artifacts/phase4_paxos_results_2026-11-02.json) | Not a full replicated log, authenticated transport, automatic leader election, Byzantine security or financial settlement |

## How to run the source

Clone the portfolio repository and run these commands in `portfolio_projects/qrcn` **after checking out the Phase 4 branch**:

```bash
python -m unittest discover -s tests -v
python -m scripts.run_demo
python -m scripts.run_phase2
python -m scripts.run_phase3
python -m scripts.run_phase4
```

Standard tests are Python standard-library-only. The **optional** experimental ML-KEM / ML-DSA example requires `python -m pip install -r requirements-pqc-experiment.txt` followed by `python -m scripts.run_pqc`; use a disposable virtual environment. No secret keys or production systems are required.

## Evidence-based project quality standard

Every phase keeps original implementation material, separately versioned new work, runnable tests, raw results, a dated validation report, explicit failures, and a documented **independent-validation gate**. CI passing demonstrates only the behavior of the checked-in code under the tested cases.

**Open gates:** independent distributed-systems reviewer; authenticated transport design; durable ordered replication/leader and membership protocols; independent adversarial schedules and chaos tests; post-quantum handshake/key lifecycle analysis; sustained concurrency/latency measurements; security/legal/regulatory assessment before any claims beyond a research prototype.

## Preservation and GitHub review structure

- The publicly deployed source on `main` is the **Phase 1 demonstration**; no Phase 2–4 experimental release has been merged.
- [Phase 2 draft PR #15](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/15) — separate durable local-journal branch.
- [Phase 3 draft PR #16](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/16) — stacked on Phase 2.
- [Phase 4 draft PR #17](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/pull/17) — stacked on Phase 3.
- This root `QRCN/` directory is a **discoverability/index layer**. The authoritative implementation is still under `portfolio_projects/qrcn/` on the appropriate development branch. Creating this index does not duplicate code or imply an unapproved merge.

## Research positioning

The prototype investigates **distributed-systems safety and cryptographic API integration**, not the claim that changing packets or quantum entanglement makes hacking impossible. QRCN is designed to publish what works **and** what fails.
