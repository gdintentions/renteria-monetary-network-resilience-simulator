# QRCN threat model — research scope

**Assets:** transaction bytes, sender/recipient/amount invariants, integrity tags, local journal, transaction identifiers and audit events.

**Adversary:** may alter a simulated transit payload, replay a transaction, withhold an acknowledgment, or cause node unavailability. In the current prototype, the adversary **cannot** read the in-process master secret, modify the journal, or compromise multiple hosts; no real untrusted network exists.

**Security controls simulated:** HMAC-SHA256 with node- and epoch-specific derived secret, constant-time tag compare, unique transaction-ID journal, explicit rejection on tag mismatch, alternate-node selection on outage.

**Excluded / not solved:** endpoint compromise, secret exfiltration, colluding validators, Byzantine consensus, arbitrary network partitions, distributed double spend, key negotiation or revocation, packet confidentiality, timing side channels, actual QKD, production-grade PQC, ledger recovery, regulatory settlement rules.

**Failure decisions:**
- Payload tamper: reject; do not treat rerouting as an excuse to skip integrity validation.
- Stale authentication tag: reject. Epoch is local; no consensus-based key rotation.
- Node outage: try another simulated node, but reject/unavailable when all nodes fail.
- Duplicate identifier: reject regardless of whether its message bytes match.
- Lost acknowledgment after commit: retry must not increment committed total.

**Known limitations:** HMAC tags are not encryption; local memory is not durable; a changed payload signed by an insider holding the key would verify; key epochs do not magically prevent interception; nodes are simulated entries not independent parties. This prototype does not establish quantum resistance. The design is a laboratory for evidence-driven engineering, not a security product.

**Next attack tests:** concurrent duplicate requests, restart/recovery, replay under rotated epochs, compromised keys, split-brain journals, authentic-but-conflicting writes, and denial of service. No claims until measured.
