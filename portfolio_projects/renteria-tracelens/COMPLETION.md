# TraceLens — v0.2.0 completion gates

Scope: synthetic portfolio demonstration with actual Python execution.

| Gate | Observable acceptance condition | Evidence | Status |
|---|---|---|---|
| Retrieval-to-diagnosis | Authored lexical ranking, candidate miss, selection loss, top-k replay | `test_trace_ranking_selection_replay` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed: local + CI |
| Evidence uncertainty | Corpus unknown/unavailable and judge/gold disagreement | `test_trace_unknown_and_disagreement` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed: local + CI |
| Input boundary | Malformed/duplicate IDs rejected; source hashes exported | `test_trace_malformed_candidate_is_validation_error` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed: local + CI |
| Browser demonstration | Run, inspect, export, change/reset inputs, reload; mobile and desktop layouts | [35 Chromium checks](../../artifacts/reliability/browser/results.json) | Passed: local + CI |
| Published failures | Original failures retained alongside fixes and observed negative scenarios | [Release report](../../docs/RELIABILITY_RELEASE.md#published-failures--before-and-after) | Recorded |
| CI and hosted release | Acceptance workflows pass, Pages deploys, live browser checks pass on published bundle | Release verification below | Passed: deployed + live checks |

## Separate real-use gates

Independent corpus annotations, representative retrieval traces, independently judged answer support and comparison to a stronger retriever. Production-ready status remains **false**. Synthetic case success does not close these gates.

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
