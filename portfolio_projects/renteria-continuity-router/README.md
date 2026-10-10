# Renteria ContinuityRouter

**v0.1.0 · Runnable Python prototype · AI infrastructure & resilience**

An asynchronous router accepts provider callables, applies classification allowlists, retries transient failures, opens failed-provider circuits, permits a single recovery probe, and enforces a total wall-clock request budget.

## Original contribution

Failover is authorized per data classification. A restricted request cannot silently move to a public-only provider. The router propagates cancellation and programming errors, omits prompts from event logs, and returns a review-required state rather than promising that a human has been notified.

## Run

Python 3.11 or newer; standard library only. From this project directory:

```bash
python continuity_router.py
python -m unittest discover -v
```

See [sample results](DEMO_RESULTS.json) and [executed tests](TEST_RESULTS.txt).
Tests were run in the development environment on October 10, 2026 UTC.
These are authored synthetic contract tests, not independent real-world validation.

## Architecture and formulas

Retry delay is uniform(0, min(1 second, 0.05 × 2^attempt)), unless retry_after is supplied. A retry that cannot fit the remaining request budget is skipped. Circuit failure counts exhausted provider calls, not each retry. Authorization is checked before invoking a provider.

The architecture uses explicit control flow. A free-running agent is unnecessary
for these bounded tasks. Provider, evaluator and search adapters can be replaced
without moving policy decisions into prompts.

## Boundaries and next validation

Bundled providers simulate outages and responses. No live SDK integration or vendor reliability has been tested. A provider adapter must normalize its own errors to ProviderFailure and disable hidden SDK retries. Callables must be cancellation-cooperative async functions. Use one event loop; breaker state is in memory, not shared between processes. No cost reservation, distributed rate limiter, authentication or durable review queue is implemented. Provider output correctness and safety require downstream validation.

Before broader release, run independently labeled cases, record failures and
compare against a simple baseline. Live integrations and production deployment
are **not validated** by this release. The original tutorial's timing, dependency
versions, and claimed outputs are not adopted as measured results.

## Attribution

Conceptual starting point: @datasciencebrain, “Build an LLM Router That Survives Provider Outages,”
from screenshots supplied by the portfolio owner. Architecture selection was also
informed by their “AI Agent Architectures — And When to Choose Which” guide.
Source creator: https://www.instagram.com/datasciencebrain/

Implementation, enterprise fixtures, interfaces, tests and documentation in this
project were written for the Renteria portfolio. This is an adaptation of established
patterns, not a claim to have invented RAG, circuit breakers or corrective retrieval.
Tutorial screenshots and original code are not redistributed here.

## Portfolio placement

This standalone project sits in `portfolio_projects/renteria-continuity-router` in the existing
public portfolio repository. It has its own manifest and tests and can later be
extracted into a separate repository. It does not alter the private Governed RAG
service. [Portfolio index](../../START_HERE.md).
