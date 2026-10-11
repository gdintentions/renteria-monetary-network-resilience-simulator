# SourceGate — v0.2.0 completion gates

Scope: synthetic portfolio demonstration with actual Python execution.

| Gate | Observable acceptance condition | Evidence | Status |
|---|---|---|---|
| Permission and provenance | No search without opt-in; exact evidence IDs and URLs on extracts | `test_source_permission_and_citations` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed: local + CI |
| Negative evidence paths | Conflict, expiry, look-alike host, bad grade and invalid claim metadata withhold answers | `test_source_negative_cases_withhold` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed: local + CI |
| Corrective end-to-end path | Retrieve, grade, permitted fixture search, coverage and citations | `test_source_permission_and_citations` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed: local + CI |
| Browser demonstration | Run, inspect, export, change/reset inputs, reload; mobile and desktop layouts | [35 Chromium checks](../../artifacts/reliability/browser/results.json) | Passed: local + CI |
| Published failures | Original failures retained alongside fixes and observed negative scenarios | [Release report](../../docs/RELIABILITY_RELEASE.md#published-failures--before-and-after) | Recorded |
| CI and hosted release | Acceptance workflows pass, Pages deploys, live browser checks pass on published bundle | Release verification below | Passed: deployed + live checks |

## Separate real-use gates

Independent text/claim relevance and contradiction judgments; permitted real corpus and live search adapter; adapter deadlines, scope/authority handling and human acceptance. Production-ready status remains **false**. Synthetic case success does not close these gates.

## Release verification

**Complete for the stated synthetic portfolio demonstration scope.**

- Release revision: `8e62f9be308c60f9139f91b4c9662ca6dedf0aa9`.
- [Build, deployment and live verification](https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/actions/runs/38122746290) all succeeded.
- 46 Python tests pass; all 35 Chromium checks pass against the **public URL**.
- [Served Python bytes match the tested checkout](../../artifacts/reliability/live/live-source-parity.json).
- [Live browser results](../../artifacts/reliability/live/results.json) retain the deliberately injected
  `Source manifest unavailable` fault; failure withholding and restart recovery both pass.
- [Machine-readable completion record](../../artifacts/reliability/COMPLETION.json).

Verified October 11, 2026 at 07:52 UTC. The real-use gates above remain open;
this completion statement does not assert independent domain quality or production readiness.
