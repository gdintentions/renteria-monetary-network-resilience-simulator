# TraceLens — v0.2.0 completion gates

Scope: synthetic portfolio demonstration with actual Python execution.

| Gate | Observable acceptance condition | Evidence | Status |
|---|---|---|---|
| Retrieval-to-diagnosis | Authored lexical ranking, candidate miss, selection loss, top-k replay | `test_trace_ranking_selection_replay` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed locally |
| Evidence uncertainty | Corpus unknown/unavailable and judge/gold disagreement | `test_trace_unknown_and_disagreement` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed locally |
| Input boundary | Malformed/duplicate IDs rejected; source hashes exported | `test_trace_malformed_candidate_is_validation_error` and [Python evidence](../../artifacts/reliability/python_results.json) | Passed locally |
| Browser demonstration | Run, inspect, export, change/reset inputs, reload; mobile and desktop layouts | [35 Chromium checks](../../artifacts/reliability/browser/results.json) | Passed locally |
| Published failures | Original failures retained alongside fixes and observed negative scenarios | [Release report](../../docs/RELIABILITY_RELEASE.md#published-failures--before-and-after) | Recorded |
| CI and hosted release | Acceptance workflows pass, Pages deploys, live browser checks pass on published bundle | Release verification below | Pending publication verification |

## Separate real-use gates

Independent corpus annotations, representative retrieval traces, independently judged answer support and comparison to a stronger retriever. Production-ready status remains **false**. Synthetic case success does not close these gates.

## Release verification

Local Python and Chromium checks passed. CI, deployment and live URL verification will be recorded after publication.
