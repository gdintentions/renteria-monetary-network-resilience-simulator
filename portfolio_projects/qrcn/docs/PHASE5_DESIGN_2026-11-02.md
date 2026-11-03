# QRCN Phase 5 — Ballot allocation and adversarial interleavings

Date: 2026-11-02 (Pacific). **Prototype-only, synthetic transactions.** This branch starts from the Phase 4 experimental branch and leaves its previous code, evidence, and draft PR unchanged.

## Scope actually implemented

- `qrcn/ballots.py`: persistent SQLite ballot counter, transactionally incremented under `BEGIN IMMEDIATE`, with a fixed ordered proposer-identity namespace. Ballots are `round * membership_width + proposer_index`, giving different configured identities different residues. After restart the same identity continues from its stored round. A caller can request a ballot greater than an observed ballot to recover from preemption.
- `tests/test_phase5.py`: 9 deterministic checks for identity separation, restart, higher-ballot recovery, incorrect namespace reuse, input rejection, selected higher/lower proposer interleavings, acceptor restart/partition, and minority safety. The existing Phase 1–4 test suites are retained.

## Important assumptions and unclosed gaps

1. Each proposer has a **unique, correctly configured identity** from the **same fixed ordered tuple**, and a single persistent allocator database is never cloned across independent instances. The code does **not** provide distributed identity registration or leased ownership. Two processes using the same copied DB or independently configured identities can produce duplicate ballots.
2. This allocator is a helper; Phase 4 `Proposer.propose(..., ballot, ...)` still accepts externally provided ballots. Integration into a producer-facing coordinator and automated retry on preemption are **not implemented**.
3. Tests exercise hand-selected synchronous nested-call schedules, **not exhaustive model checking** or real asynchronous networking. No formally established linearizability or liveness guarantee.
4. Persisting an allocator counter is not a durable chosen-value learner, certificate, ordered replicated log, or state-machine replay. These remain Phase 5 follow-on milestones.
5. No Byzantine tolerance, live financial integrations, authenticated RPC, quantum network, or post-quantum protected transport. The loopback TCP demonstration remains unauthenticated. No production/security claims.

## Local verification

From `portfolio_projects/qrcn` run:

```bash
python -m unittest discover -s tests -v
python -m unittest tests.test_phase5 -v
```

The second command requires a package-style tests directory; if unavailable use:

```bash
python -m unittest discover -s tests -p 'test_phase5.py' -v
```

CI outcome should be recorded with a separate dated evidence artifact after its job completes; source publication alone is not a passing test. Retain test failures rather than rewriting historical records.

## Acceptance gates

- [x] New isolated branch from Phase 4.
- [x] Durable fixed-membership allocator plus nine targeted regression scenarios committed.
- [ ] GitHub CI confirms runs on Python 3.11 and 3.12.
- [ ] Independent review of concurrent proposer ballot uniqueness and safety assumptions.
- [ ] Durable learner and chosen-value evidence protocol.
- [ ] Ordered replicated log with crash-safe state-machine replay.
- [ ] Scheduler-driven dropped/reordered message testing and observable process churn.
- [ ] Independent distributed-systems/security review and production-readiness gates: **OPEN**.

These are incremental research results, not certification of a financial clearing network.
