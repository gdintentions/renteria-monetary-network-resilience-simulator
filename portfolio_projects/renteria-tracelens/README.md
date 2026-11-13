# Renteria TraceLens

**v0.2.0 · Python core + browser portfolio release · Retrieval observability & evaluation**

Accepts a ranked retrieval trace, selected passage IDs, and supplied judge labels. Produces a hit/noise/miss/cut matrix, stage-specific diagnosis, optional gold-label recall, and top-k counterfactual replay.

## Original contribution

A bounded judge pool cannot prove that the entire corpus lacks an answer. TraceLens requires exhaustive corpus annotations to confirm that diagnosis, reports judge disagreement, and preserves unknown states. Exported reports contain passage IDs rather than raw text.

## Run

Python 3.11 or newer; standard library only. From this project directory:

```bash
python tracelens.py sample_trace.json --sweep 1 2 3
python -m unittest discover -v
```

See [sample results](DEMO_RESULTS.json) and [executed tests](TEST_RESULTS.txt).
Tests were run in the development environment on October 10, 2026 UTC.
These are authored synthetic contract tests, not independent real-world validation.

## Architecture and formulas

candidate recall = |gold ∩ candidates| / |gold|; selected recall = |gold ∩ kept| / |gold|. Empty gold sets yield null recall. Counterfactual replay changes only top-k selection; it does not measure answer improvement.

The architecture uses explicit control flow. A free-running agent is unnecessary
for these bounded tasks. Provider, evaluator and search adapters can be replaced
without moving policy decisions into prompts.

## Governed RAG trace integration

The browser demo includes four recorded traces from the Governed RAG Python engine on a four-passage fictional policy corpus. The examples distinguish evidence outside the candidate pool, cut by rank, cut by score, and selected but unused in the extracted answer. The trace records which passages contributed text to the answer separately from the citation list.

In the sponsor-policy case, the correct passage ranks second. Top-2 includes it in the observed answer. Top-3 adds one more distractor without changing the answer. TraceLens can also replay rank budgets or score thresholds on the recorded pool. Only the offline engine reruns produce new answers.

The [recorded examples](governed_rag_examples.json) include the engine file hash and authored labels. These are synthetic development results. Independent policy review and live service tracing remain open.

## Boundaries and next validation

This trace-analysis engine can use observations from an existing retriever. Preserve candidate rank order and supply independently evaluated labels for domain validation. Gold labels must be exhaustive for the corpus version; the program cannot verify that promise. IDs may themselves be sensitive. Judge support does not prove the generated answer is correct.

Before broader release, run independently labeled cases, record failures and
compare against a simple baseline. Live integrations and production deployment
are **not validated** by this release. The original tutorial's timing, dependency
versions, and claimed outputs are not adopted as measured results.

## Attribution

Conceptual starting point: @datasciencebrain, “Build a RAG Debugger That Shows Why Retrieval Failed,”
from screenshots supplied by the portfolio owner. Architecture selection was also
informed by their “AI Agent Architectures — And When to Choose Which” guide.
Source creator: https://www.instagram.com/datasciencebrain/

Implementation, enterprise fixtures, interfaces, tests and documentation in this
project were written for the Renteria portfolio. This is an adaptation of established
patterns, not a claim to have invented RAG, circuit breakers or corrective retrieval.
Tutorial screenshots and original code are not redistributed here.

## Portfolio placement

This standalone project sits in `portfolio_projects/renteria-tracelens` in the existing
public portfolio repository. It has its own manifest and tests and can later be
extracted into a separate repository. The private Governed RAG engine provides an opt-in offline trace export. [Portfolio index](../../START_HERE.md).

## Browser release v0.2.0

[Run TraceLens in your browser](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/reliability/#tracelens).
This executes this repository's Python core inside a Web Worker with Pyodide 0.27.7;
it is not a separate JavaScript imitation. No account, local installation or API key is required.
The hosted runtime and bundled Python are rebuilt and tested before Pages deployment.

[Project-specific completion gates](COMPLETION.md) ·
[Shared release evidence and reproduced failures](../../docs/RELIABILITY_RELEASE.md) ·
[Observed synthetic scenario outputs](../../artifacts/reliability/scenario_outputs.json).

The v0.2.0 scope is a complete, inspectable synthetic portfolio demonstration.
Independent real-world labels, live providers and production acceptance remain separate gates.
