# Threat model

## Assets

- User data visible on screen
- Credentials and API keys
- Files, messages, purchases, and account permissions
- Integrity of the host operating system
- Audit evidence

## Trust boundaries

The vision model is an untrusted planner. Web pages and documents are untrusted observations.
Only the deterministic policy module may authorize an operating-system action.

| Threat | Example | Control | Residual risk |
|---|---|---|---|
| Prompt injection | Page says “ignore the user” | Screen text declared untrusted; schema + gate | Model may still misclassify |
| Secret leakage | Planner types an API key | Sensitive-text deny rule; no credential action | Visual secrets can still be observed |
| Destructive action | Delete or submit | Risk ceiling; blocked keys; dry-run default | Mouse clicks can be ambiguous |
| Runaway loop | Repeating clicks | Hard step cap; history; fail-fast | Wasted API calls below cap |
| Coordinate error | Display scaling | Logical-screen transform; bounds clamp | Multi-monitor layouts need adapters |
| Audit tampering | Edited JSONL | Hash each observation | Log signing is future work |

## Explicit non-goals

ArgusLoop is not intended for autonomous purchasing, financial transactions, authentication,
security-setting changes, medical decisions, or unsupervised operation on sensitive systems.

