# QRCN Phase 4 — Single-decree Paxos research prototype

Date: 2026-11-02 Pacific (some GitHub CI executions occur November 3 UTC). **No live financial clearing, security certification, or production deployment.** Phase 1–3 code and historical results are retained. Work is isolated on `experiment/qrcn-phase4-paxos-prototype-2026-11`.

## Important change from Phase 3

Phase 3 gates admission on a simulated majority but still relies on **one shared SQLite file**. This Phase 4 prototype adds a distinct SQLite database **per acceptor**, persisted ballot promises/accepted values, a two-round Paxos-style prepare/accept exchange, and an optional local-only TCP JSON-RPC demonstration with three independent OS processes. It no longer relies on a shared transaction journal for its prepare/accept votes.

This is **single-decree Paxos per transaction identifier**, not a full replicated log, Multi-Paxos or Raft implementation. A returned `chosen` means the test proposer observed a majority accepting the same canonical value for that ID/ballot. It does **not** mean funds moved, a payment settled, or every node learned the decision.

## Reproducibility

From `portfolio_projects/qrcn`:

```bash
python -m unittest discover -s tests -v
python -m scripts.run_phase4
```

Source:
- `qrcn/paxos.py`: independent SQLite acceptors, canonical synthetic values, single-decree proposer, deterministic partition transport
- `qrcn/tcpnode.py`: **unauthenticated loopback-only** separate process acceptor server
- `tests/test_paxos.py`: ten single-decree safety and failure cases
- `tests/test_tcp_nodes.py`: one three-process partition and persisted-restart test
- `scripts/run_phase4.py`: deterministic scenario/evidence JSON
- Existing QRCN CI executes the Phase 4 tests on Python 3.11 and 3.12; optional post-quantum API testing remains **separate** from transport.

## Required evidence cases

| Scenario | Expected observable outcome |
|---|---|
| Minority partition, only 1/3 responding | `no_prepare_quorum`, no chosen value |
| Majority, 2/3 responding | `chosen` |
| Conflicting proposal after majority acceptance | `adopted_prior`; original value selected |
| Accepted state survives acceptor recreation | Higher ballot adopts preserved value |
| Three localhost acceptor processes; kill/restart one | Previously accepted value survives restart and is adopted |
| Prepare majority but accept quorum unavailable | `no_accept_quorum`; no claim of chosen value |
| Promises for higher ballot already stored | Stale lower ballot cannot prepare majority |
| Same acceptor, same ballot, different data | Second acceptance rejected |
| Distinct transaction IDs | Independent consensus slots |
| Multiple higher sequential ballots | Chosen value unchanged |

## Failure evidence and design limitations

- In a first local iteration, the acceptor used a context manager that closed SQLite connections without an explicit commit; the tests failed to recover accepted values. Corrected by entering the SQLite transaction context before yielding. This local failure was not a GitHub CI failure and is included here to explain the fix.
- This is not a consensus proof. Tests cover selected deterministic interleavings, not all asynchronous network schedules, simultaneous competing proposers or power-loss corruption.
- **Ballot uniqueness is a caller responsibility.** An automated election/candidate numbering protocol is not implemented; reusing a ballot across competing proposers could invalidate safety assumptions.
- No total ordering or replicated log, state machine application, decision learning protocol, membership reconfiguration, quorum certificate persistence, operator rollback/recovery process, or exactly-once funds movement.
- The TCP server binds to **127.0.0.1** and is not authenticated/encrypted. It is strictly for loopback testing; never expose it to public traffic.
- No Byzantine faults or malicious acceptors; nodes are crash-fault model and process/synthetic message drop tests only.
- No ML-KEM/ML-DSA transport integration; Phase 3 post-quantum API measurements remain independent and unchanged.
- The public hosted browser demo remains synthetic Phase 1/2 presentation, **not connected to Phase 4**.
- Independent security review, distributed-protocol review, operational chaos tests and production gate remain **OPEN**.

## Next scientific work

1. Model-check or exhaustively explore small-node schedule interleavings; verify ballot uniqueness and strengthen handling of concurrent proposers.
2. Add learner/decision durability, log ordering, authenticated RPC, process churn, and network delay/instrumentation.
3. Compare against an established consensus library and published correctness tests; keep failures and regressions visible.
4. Separately design reviewed PQC-authenticated key establishment and transport *after* replicated correctness is established.
5. Do not release as secure clearing infrastructure. Only synthetic, isolated research data is permitted.

## Status

Development implementation and tests committed on the experimental branch. GitHub CI run links and raw output are authoritative evidence; no independent validation or production claim.
