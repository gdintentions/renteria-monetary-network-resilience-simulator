# Renteria SourceGate

**v0.1.0 · Runnable Python prototype · Corrective retrieval & governed help desks**

A corrective workflow retrieves local evidence, evaluates it, optionally invokes a search adapter for missing claims, checks source allowlists and expiry, detects conflicts in structured claims, and returns cited extracts or a review-required result.

## Original contribution

Correction is constrained by explicit source permissions, fact coverage, expiry and conflict checks. Web fallback is opt-in. Every output excerpt retains an exact evidence ID and URL. Conflicting evidence blocks the answer rather than being blended into fluent text.

## Run

Python 3.11 or newer; standard library only. From this project directory:

```bash
python sourcegate.py --mode complete
python -m unittest discover -v
```

See [sample results](DEMO_RESULTS.json) and [executed tests](TEST_RESULTS.txt).
Tests were run in the development environment on October 10, 2026 UTC.
These are authored synthetic contract tests, not independent real-world validation.

## Architecture and formulas

Coverage = required claim keys ⊆ union of accepted evidence keys. A conflict exists when a required key has more than one distinct serialized value. Sources require HTTPS and exact hostname membership; expired evidence is rejected. All required claims must be covered without conflicts before returning extracts.

The architecture uses explicit control flow. A free-running agent is unnecessary
for these bounded tasks. Provider, evaluator and search adapters can be replaced
without moving policy decisions into prompts.

## Boundaries and next validation

The runnable demo uses invented enterprise-access policies, authored claim metadata and fixture grades. No live search, trained evaluator or generative answer model is bundled. The core accepts injected adapters; it does not prove semantic correctness of their labels or claims. Contradiction detection compares supplied structured values, not arbitrary natural language. Domain approval and expiry do not prove truth. Adapters need their own timeouts and input controls. The caller must authorize any external transfer of a question. Human verification remains necessary.

Before broader release, run independently labeled cases, record failures and
compare against a simple baseline. Live integrations and production deployment
are **not validated** by this release. The original tutorial's timing, dependency
versions, and claimed outputs are not adopted as measured results.

## Attribution

Conceptual starting point: @datasciencebrain, “Build a CRAG Help Desk That Checks Its Own Retrieval,”
from screenshots supplied by the portfolio owner. Architecture selection was also
informed by their “AI Agent Architectures — And When to Choose Which” guide.
Source creator: https://www.instagram.com/datasciencebrain/

Implementation, enterprise fixtures, interfaces, tests and documentation in this
project were written for the Renteria portfolio. This is an adaptation of established
patterns, not a claim to have invented RAG, circuit breakers or corrective retrieval.
Tutorial screenshots and original code are not redistributed here.

## Portfolio placement

This standalone project sits in `portfolio_projects/renteria-sourcegate` in the existing
public portfolio repository. It has its own manifest and tests and can later be
extracted into a separate repository. It does not alter the private Governed RAG
service. [Portfolio index](../../START_HERE.md).
