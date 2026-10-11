# TraceLens, ContinuityRouter and SourceGate — portfolio release v0.2.0

Date: October 11, 2026 UTC. Original base: `57feaab29032b3d1d4e8392325df244d71c7464c`.

## Release scope

Three browser-runnable, inspectable **synthetic portfolio demonstrations**, with the
actual Python cores, end-to-end checks, retained failure evidence and project-specific
acceptance gates. No independent domain study or production deployment is asserted.
The user requested this completion standard before beginning another project.

- [TraceLens](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/reliability/#tracelens)
- [ContinuityRouter](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/reliability/#continuity-router)
- [SourceGate](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/reliability/#sourcegate)

The browser downloads a pinned Pyodide 0.27.7 runtime from the same GitHub Pages
origin, verifies SHA-256 hashes of the bundled Python files and executes them in a
Web Worker. No user code is evaluated. TraceLens accepts bounded JSON; the other
projects expose bounded scenario controls. No question or document is sent to an API.
Output JSON includes source hashes and synthetic scope. The runtime is about 14 MB;
initial load needs network access. In-memory state clears on reload; exports are opt-in.
Source hashes prove file parity, not authorship, safety or independent correctness.

## What changed

| Project | Completed implementation | Demonstrated end-to-end behavior |
|---|---|---|
| TraceLens | Bounded input schema; disagreement takes precedence over a misleading supported status, with original judge diagnosis retained | Lexical fixture ranking → selection → diagnosis → top-k replay → evidence export; unknown and unavailable judgments remain explicit |
| ContinuityRouter | Finite bounded budgets/timeouts; integer retry limits; provider/classification validation | Actual async fixture outage → authorized backup → open-circuit skip → timed recovery probe; restricted data invokes neither provider; total deadline withholds output |
| SourceGate | Strict evidence metadata and finite JSON claims; malformed evidence fails closed | Local retrieval → grading → explicitly permitted fixture search → source/freshness/coverage/conflict gates → exact cited extracts or withholding |

## Executed evidence

- **28 existing Python tests** (9 TraceLens, 9 ContinuityRouter, 10 SourceGate).
- **15 added regression/end-to-end tests**, with additional scenario subcases.
- **35 Chromium browser acceptance checks** at mobile 390×844 and desktop 1440×1000:
  actual Python execution, successful and withheld results, provenance export,
  malformed input, text-only rendering, stale-output clearing, keyboard operation,
  no horizontal overflow, reload reset, and resource-failure/restart recovery.
- **19 observed scenario outputs**, including expected failure/withholding paths.

[Python run and source hashes](../artifacts/reliability/python_results.json) ·
[Browser checks](../artifacts/reliability/browser/results.json) ·
[Browser source hashes](../artifacts/reliability/browser/source-manifest.json) ·
[Observed scenarios](../artifacts/reliability/scenario_outputs.json).

Screenshots: [TraceLens mobile](../artifacts/reliability/browser/tracelens-mobile.png),
[ContinuityRouter mobile](../artifacts/reliability/browser/continuity-router-mobile.png),
[SourceGate mobile](../artifacts/reliability/browser/sourcegate-mobile.png),
[SourceGate desktop](../artifacts/reliability/browser/sourcegate-desktop.png).

These authored fixtures test behavior; their scores are not independently labeled
retrieval, semantic quality, uptime or safety metrics. Browser coverage is Chromium;
iOS Safari and assistive-technology compatibility have not been independently tested.

## Published failures — before and after

The first boundary run on the original cores had **4 assertion failures, 1 error,
and 1 passing case**. The original log is preserved in
[initial_boundary_failures.txt](../artifacts/reliability/initial_boundary_failures.txt).

| Reproduced failure | Correction | Regression evidence |
|---|---|---|
| TraceLens missing candidate ID raised KeyError | Validate candidate schema with explicit ValueError | `test_trace_malformed_candidate_is_validation_error` |
| TraceLens said SUPPORTED_CONTEXT despite supplied gold contradiction | Report JUDGE_DISAGREEMENT; preserve observed judge status and metrics | `test_trace_gold_disagreement_not_supported` |
| Router accepted NaN timeout | Require finite bounded numeric limits | `test_router_nonfinite_timeout_rejected` |
| Router accepted fractional retries | Validate integer retry bounds | `test_router_fractional_retries_rejected` |
| SourceGate released extracts backed by NaN claim metadata | Reject non-finite JSON metadata before coverage/conflict decisions | `test_sourcegate_nonfinite_claims_fail_closed` |

The `claims=None` case already failed closed; it remains a passing control, not a claimed fix.
All six cases now pass. The first browser harness also failed because its polling
helper attempted eval under the restrictive content-security policy. The harness
now waits on locators; the page policy was **not weakened**.
[Preserved harness failure](../artifacts/reliability/browser_harness_csp_failure.json).

Expected failures are also visible interactively: absent candidates, unavailable
judges, unknown corpus coverage, policy-prohibited failover, deadline expiry,
conflicts, expired/look-alike sources and bad evaluator metadata. They are not
hidden by an aggregate success score. The demo intentionally preserves baseline
weaknesses: top-1 lexical ranking drops a needed answer; local-only SourceGate lacks
a duration claim; a primary-only call cannot answer through the injected outage.

## Acceptance gates

- [TraceLens gates](../portfolio_projects/renteria-tracelens/COMPLETION.md)
- [ContinuityRouter gates](../portfolio_projects/renteria-continuity-router/COMPLETION.md)
- [SourceGate gates](../portfolio_projects/renteria-sourcegate/COMPLETION.md)

The CI workflow runs Python 3.11 and 3.12 checks and the actual Python browser lab.
Pages separately runs the acceptance suite before deployment. A failed acceptance
check prevents replacing the live Pages artifact. Source/runtime changes rebuild
the bundle; generated runtime binaries are not committed. The npm lockfile pins
package integrity. Browser evidence is attached to CI runs, including failures.

## Reproduce locally

```sh
python scripts/verify_reliability.py
python scripts/export_reliability_cases.py
npm ci --prefix reliability_lab --ignore-scripts
python scripts/build_reliability_browser.py
npm install --prefix /tmp/reliability-browser playwright@1.51.1
/tmp/reliability-browser/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/reliability-browser/node_modules node scripts/reliability_browser_smoke.cjs
python -m http.server 8000 --bind 127.0.0.1 --directory hosted_demo
```

Open `http://127.0.0.1:8000/reliability/`. To run the same checks against a deployed
release, set `RELIABILITY_BASE_URL` to the URL ending in `/reliability/`; use a
separate `RELIABILITY_ARTIFACTS` directory to retain local and deployed evidence.

## Remaining real-use boundaries

TraceLens cannot establish corpus completeness or answer truth from guessed labels.
ContinuityRouter uses cooperative async fixtures and in-memory, single-loop breaker
state; it does not measure vendor uptime or implement production identity/cost controls.
SourceGate compares supplied structured claims, not arbitrary natural-language meaning;
its allowed domains and freshness checks do not establish truth. Live adapters require
separate authorization, timeout/error handling and independent evaluation.
All production-ready flags remain false. This release closes the stated synthetic
portfolio demonstration scope only.
