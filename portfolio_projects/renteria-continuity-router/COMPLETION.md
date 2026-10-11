# ContinuityRouter — v0.2.0 completion gates

Scope: synthetic portfolio demonstration with actual Python execution.

| Gate | Observable acceptance condition | Evidence | Status |
|---|---|---|---|
| Authorized failover | Restricted data calls neither provider; internal data cannot reach public backup | `test_router_authorization_blocks_every_call` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed locally |
| Failure and recovery | Actual async outage, open-circuit skip, timed recovery probe | `test_router_recovery_sequence` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed locally |
| Bounded execution | Deadline withholds output; cancellation propagates; finite budgets and integer retries | `test_router_deadline_withholds` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed locally |
| Browser demonstration | Run, inspect, export, change/reset inputs, reload; mobile and desktop layouts | [35 Chromium checks](../../artifacts/reliability/browser/results.json) | Passed locally |
| Published failures | Original failures retained alongside fixes and observed negative scenarios | [Release report](../../docs/RELIABILITY_RELEASE.md#published-failures--before-and-after) | Recorded |
| CI and hosted release | Acceptance workflows pass, Pages deploys, live browser checks pass on published bundle | Release verification below | Pending publication verification |

## Separate real-use gates

Authorized live provider adapters, independent outage/load study, distributed state if needed, identity/cost controls, and intended-host/operator acceptance. Production-ready status remains **false**. Synthetic case success does not close these gates.

## Release verification

Local Python and Chromium checks passed. CI, deployment and live URL verification will be recorded after publication.
