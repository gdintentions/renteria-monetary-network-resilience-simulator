# QRCN validation and failure ledger

Date: 2026-11-02
Status: **Core CI verified on Python 3.11 and 3.12.** No independent validation or production-readiness certification.

## Contract tests

- Valid transaction yields one accepted local journal entry
- Duplicate ID with same or different contents cannot increment journal twice
- Modified payload fails HMAC verification without committing
- Stale epoch tag fails
- Primary outage selects alternate node
- Total outage returns unavailable and does not commit
- Dropped acknowledgment followed by retry cannot duplicate local settlement
- Invalid negative/zero/non-integer amounts rejected
- Invalid node or key configuration rejected

## Executed automated evidence

- [Successful GitHub Actions run #41574438714](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/41574438714): both Python 3.11 and 3.12 executed the full project unittest suite, sample scenario runner and Python compilation without reported errors.
- Six scenario outputs from the Python 3.11 run were [archived separately](../artifacts/scenario_results_2026-11-02.json), without modifying test inputs.
- Scenario outcomes: normal transaction **accepted**; tampering **rejected**; stale authentication tag **rejected**; primary outage **rerouted to beta and accepted**; all-node outage **unavailable**; dropped acknowledgment **accepted once with retry rejected as duplicate**.
- Source-control snapshot is synthetic and in-memory. CI pass establishes only the checked contracts; no browser automation, independent security review, network threat experiment, QKD/PQC implementation, or real finance integration was executed.

## Intentionally unclosed failures / scientific limits

- Single-process journal loses state on restart. This prevents a claim of durable exactly-once clearing.
- Failover is simulated and cannot establish distributed consensus or protection from split brain.
- The rotating HMAC system authenticates but never encrypts payloads; confidentiality is untested.
- No actual post-quantum cryptography or QKD is present.
- No throughput, p50/p95 latency, concurrency, availability, cyber resilience or production cost targets measured.
- Browser demonstration uses visibly labeled predefined scenario outputs, not the real Python engine.

## Completion gates

1. Automated local and CI suite pass on supported Python versions; retain raw CI URL and commit SHA.
2. Add durable journaling, crash/restart and concurrent retry stress tests.
3. Define trust architecture / authenticated inter-node connections and idempotent settlement semantics.
4. Commission independent cryptographic/distributed-systems review and adversarial evaluation.
5. Only after all above consider production or regulated-finance deployment claims.

Failures should remain published, not overwritten with presentation-only success evidence.
