# QRCN Phase 5 — CI evidence and open review gates

Evidence captured 2026-11-02 Pacific / 2026-11-03 UTC. Prototype only. **This document is additive and does not replace Phase 4 reports.**

## GitHub CI results

- Source commit: `037ada2d10f5652f59bb293ad72cee2acb5140f5`.
- [QRCN research prototype tests run 41585458455](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41585458455): **success** on Python 3.11 and 3.12.
- Python 3.11 [job 125749766105](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41585458455/job/125749766105): log reports **54 tests run, one optional test skipped, no failures**; all nine `test_phase5.py` tests listed as `ok`.
- Python 3.12 [job 125749765918](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41585458455/job/125749765918): completed successfully (individual count not independently transcribed).
- Existing Phase 4 tests and scenarios remain in the CI suite. Counts reflect the whole suite, not independent third-party testing.

## Interpretation

This verifies the current selected deterministic schedules and restart cases on two Python runtimes. It does **not** verify every competing-proposer schedule, failure ordering, network partition, or malformed/malicious node behavior. A successful unit suite does not establish Paxos safety formally, a durable learner, or transaction finality. Allocator uniqueness assumes correctly configured proposer identities, matching ordered membership and no database clones.

## Phase 5 follow-on gates (still open)

- Formal/interleaving model checking and independent protocol review.
- Durable chosen-value learner with quorum evidence.
- Total-order replicated log and crash-replay state machine.
- Simulated scheduler with delayed, duplicated, reordered packets and process churn.
- Transport authentication and reviewed cryptography (not part of this milestone).
- Independent validation and all production-readiness gates.
