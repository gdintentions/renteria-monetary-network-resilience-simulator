# QRCN validation and failure ledger

Date: 2026-11-02
Status: implementation and tests present; GitHub CI status must be separately checked. **No independent validation.**

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
