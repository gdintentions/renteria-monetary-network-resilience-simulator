# QRCN Phase 3 — Quorum-admission and post-quantum API comparison

Date: 2026-11-02 America/Los_Angeles (workflow executed November 3 UTC). **Development experiment only**.
Independent security validation: **OPEN**. Production readiness: **OPEN**. Original Phase 1 and Phase 2 evidence preserved.

## Scope and architecture decisions

The earlier proposal recommended genuinely multi-node coordination and standardized PQC. This phase establishes a **quorum-admission simulation**, not an actual independent-node consensus protocol:

- Optional `qrcn/quorum.py` simulates an odd-size validator membership list, majority availability gating and journal epoch fencing. Fewer than a majority denies a request; same-file journal atomically enforces duplicate ID rejection.
- It does **not** implement Raft, Paxos, verified votes, durable replicated logs, leader election, independent validator machines, cluster membership changes, or network partitions with asynchronous messages. Real distributed finality remains **unachieved**.
- `qrcn/durable.py` (Phase 2) remains the single trusted SQLite journal. Its split-brain limitation involving *separate* databases is still unresolved.
- Optional `scripts/run_pqc.py` uses `pqcrypto==1.0.0` for an **isolated local API evaluation** of ML-KEM-768 and ML-DSA-65. The experiment is neither transport integration nor a security-certified payment system.

## Executed reproducible tests

- [QRCN core Python CI run](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41577695549) passed on **Python 3.11 and 3.12**. The 3.11 log reports **34 tests, 1 optional PQC test skipped** because its dependency is deliberately absent from the standard-library-only core suite. All non-skipped tests passed.
- [Optional PQC CI run](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41577655089) passed for both Python versions with `pqcrypto==1.0.0` installed. No private keys or shared secrets logged.
- Original Phase 2 [published failure and repair](PHASE2_VALIDATION_2026-11-02.md) retained, with original 3.11 SQLite locking incident.
- [Quorum per-scenario JSON](../artifacts/phase3_quorum_results_2026-11-02.json) archived; raw GitHub artifact file SHA-256 `7e0e46dce39443684e0187fde671371ec49379cff64d32c557853b35e086516e`.
- [PQC per-experiment JSON](../artifacts/phase3_pqc_results_2026-11-02.json) archived; raw GitHub artifact file SHA-256 `56b7c581a61d12fc2423cdd60ee0fe697bc47ac7da819065857f1500407e041d`.

### Quorum admission (simulator observations)

| Scenario | Result |
|---|---|
| 1/3 nodes available | `quorum_unavailable` (no write) |
| 2/3 nodes available | `accepted` |
| Overlapping majority replay of same transaction ID | `duplicate_rejected` |
| Older writer after coordinator epoch advance | `stale_writer_rejected` |
| New writer at current epoch | `accepted` |

The quorum runner's final journal shows two committed unique IDs and 2,000 cents total, corresponding to different authorized sample payments. It does not model inter-host timing, coordinated compromise or Byzantine clients.

### Optional ML-KEM and ML-DSA measurements

From actual CPU GitHub Actions evidence (12 repeated warm API calls, not service latency):

| Operation | Observed median |
|---|---:|
| ML-KEM-768 encapsulation | 0.0702 ms |
| ML-DSA-65 sign | 8.9829 ms |
| ML-DSA-65 verify | 0.1915 ms |

- ML-KEM-768 key pair successfully established matching 32-byte shared secrets through encapsulation/decapsulation. Modifying ciphertext produced a different shared secret in this sample, **not** a replacement for authenticated key agreement or AEAD.
- ML-DSA-65 valid signature verified; changing the signed payload was rejected. Signature length measured **3,309 bytes**; public key **1,952 bytes**, secret key **4,032 bytes**.
- This third-party crypto wrapper states it has not had independent formal security audit. No FIPS 140 module validation or production hardening is claimed. Library behavior and timing are tied to the CI runner and installed package revision.

## Safety and completion gates — explicit failures

- **Still fails distributed split-brain prevention** with independent databases. Simulated majority admission with one shared journal is not independent durable voting; no authentic multi-node consensus is built.
- No realistic network, mutually authenticated channels, quorum proofs, asynchronous delay, Byzantine faults, partition healing, crash-recovery election, or formally verified safety property.
- PQC API is isolated; no identity binding, hybrid key establishment, KDF, AEAD packet encryption, transcript binding, lifecycle controls, key vault or audited cryptographic deployment.
- No real money, exchange or banking integration. The public browser demo is synthetic and remains on Phase 1 until an approved release.
- This work is **not** an independent security assessment; all evaluation cases are developer-authored.

## Next technical milestone (Phase 4 candidate)

1. Design a true replicated-log protocol with explicit terms, quorum-confirmed votes and persistent per-node storage, or use a mature consensus library/service; test asynchronous partitions and replay under crashes.
2. Keep transaction idempotency and finality semantics distinct from session-key handshake and message authentication.
3. Add independently reviewed ML-KEM handshake + authenticated identity + KDF and ML-DSA signing only behind a separate opt-in adapter; avoid rolling custom cryptography.
4. Publish cross-platform latency, chaos testing, adversarial failure evidence, threat model and external reviewer decisions.
5. No merge, deployment or production safety claim before these gates.

**Verdict:** The quorum admission and standard PQC API experiments are executed and reproducible. The larger request of true distributed consensus and quantum-resilient transaction transport remains an **open design and validation task**, not a completed feature.
