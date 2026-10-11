# SourceGate — v0.2.0 completion gates

Scope: synthetic portfolio demonstration with actual Python execution.

| Gate | Observable acceptance condition | Evidence | Status |
|---|---|---|---|
| Permission and provenance | No search without opt-in; exact evidence IDs and URLs on extracts | `test_source_permission_and_citations` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed locally |
| Negative evidence paths | Conflict, expiry, look-alike host, bad grade and invalid claim metadata withhold answers | `test_source_negative_cases_withhold` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed locally |
| Corrective end-to-end path | Retrieve, grade, permitted fixture search, coverage and citations | `test_source_permission_and_citations` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed locally |
| Browser demonstration | Run, inspect, export, change/reset inputs, reload; mobile and desktop layouts | [35 Chromium checks](../../artifacts/reliability/browser/results.json) | Passed locally |
| Published failures | Original failures retained alongside fixes and observed negative scenarios | [Release report](../../docs/RELIABILITY_RELEASE.md#published-failures--before-and-after) | Recorded |
| CI and hosted release | Acceptance workflows pass, Pages deploys, live browser checks pass on published bundle | Release verification below | Pending publication verification |

## Separate real-use gates

Independent text/claim relevance and contradiction judgments; permitted real corpus and live search adapter; adapter deadlines, scope/authority handling and human acceptance. Production-ready status remains **false**. Synthetic case success does not close these gates.

## Release verification

Local Python and Chromium checks passed. CI, deployment and live URL verification will be recorded after publication.
