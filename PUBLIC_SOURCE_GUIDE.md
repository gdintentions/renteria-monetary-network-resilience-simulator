# Public Engineering Portfolio — Recruiter Source Guide

**Public entry point:** [Interactive demo showcase](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/) · [Portfolio map](START_HERE.md) · [Validation matrix](docs/VALIDATION_MATRIX.md).

This is the **public, bounded engineering portfolio**. Recruiters can inspect actual source, run tests and explore browser demos without receiving access to the original private development repositories. The materials are intentionally synthetic and educational; the public source is not a mirror of the private applications.

## Four projects to review first

| Project | Run in browser | Inspect implementation | Tests, evidence and limitations |
| --- | --- | --- | --- |
| **Governed RAG (curated Python miniature)** | [Synthetic review workflow](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/#governed-rag) | [Python retrieval and governance miniature](demo_safe/governed-rag/demo.py) · [instructions](demo_safe/governed-rag/README.md) · [hosted JavaScript reviewer demo](hosted_demo/rag-demo.js) | [Synthetic recruiter release](hosted_demo/RECRUITER_RELEASE.md) · [RAG release limits](docs/COMPLETION_REGISTER.md) |
| **TraceLens** | [Retrieval diagnosis and top-k replay](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/reliability/#tracelens) | [Python engine](portfolio_projects/renteria-tracelens/tracelens.py) · [unit tests](portfolio_projects/renteria-tracelens/test_tracelens.py) | [Project README](portfolio_projects/renteria-tracelens/README.md) · [release evidence](docs/RELIABILITY_RELEASE.md) |
| **ContinuityRouter** | [Failover and circuit recovery](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/reliability/#continuity-router) | [Python engine](portfolio_projects/renteria-continuity-router/continuity_router.py) · [unit tests](portfolio_projects/renteria-continuity-router/test_router.py) | [Project README](portfolio_projects/renteria-continuity-router/README.md) · [release evidence](docs/RELIABILITY_RELEASE.md) |
| **SourceGate** | [Corrective evidence workflow](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/reliability/#sourcegate) | [Python engine](portfolio_projects/renteria-sourcegate/sourcegate.py) · [unit tests](portfolio_projects/renteria-sourcegate/test_sourcegate.py) | [Project README](portfolio_projects/renteria-sourcegate/README.md) · [release evidence](docs/RELIABILITY_RELEASE.md) |

### Suggested technical review (10–15 minutes)

1. Open the **Governed RAG** browser demo, test an answerable question, a no-answer example and a policy conflict. Observe the withheld draft and simulated review. The public browser demo is a *reduced JavaScript implementation*, not the private authenticated Python service; its reviewer buttons are not authenticated.
2. Open **TraceLens** and inspect a retrieval miss and the diagnosis/replay output. Read the actual Python engine and unit tests.
3. Open **SourceGate** and select a conflict or expired-source case. Observe that the workflow withholds an answer.
4. Open **ContinuityRouter** and compare authorized failover with prohibited provider routing. Inspect retry/deadline controls in the Python engine.
5. Read the [published failures, implementation coverage and limitations](docs/RELIABILITY_RELEASE.md). Each project is complete **for its stated synthetic demonstration scope**, not for general production deployment.

### Reproduce the public code locally

Requires Python 3.11+; the curated Governed RAG miniature and three reliability cores use the Python standard library.

```bash
python demo_safe/governed-rag/demo.py --self-test
python demo_safe/smoke_test.py
python scripts/verify_reliability.py
python scripts/check_public_release.py
```

For project-specific commands, see each project's README. The browser reliability lab runs these repository Python cores using Pyodide. The private production-style Governed RAG FastAPI service is **not** included here.

## Publication and security boundary

**Public:** selected source and tests; fabricated example inputs; synthetic browser workflows; architecture explanations; reproducible contract testing; measured results only where explicitly scoped; documented failures.

**Private:** full Governed RAG implementation and other private-source projects; credentials, API tokens, real user/policy documents, private prompts, operational endpoints, unreleased components and proprietary integrations.

A lightweight [public-source safety check](scripts/check_public_release.py) scans selected published text/code paths for common credential signatures and validates important source and demo references. It runs in [GitHub Actions](.github/workflows/public-release-check.yml). It is a **defense-in-depth check, not a complete secrets audit**: it does not inspect all Git history, all past artifacts, inaccessible secrets, private repositories or runtime infrastructure. Maintain GitHub secret scanning, push protection, human review and credential rotation separately as applicable.

**License:** the existing public repository is [MIT-licensed](LICENSE). Do not copy additional private code into this repository without reviewing the intended disclosure and licensing consequences. An existing MIT grant is not made confidential retroactively.

**Release discipline:** keep original private repositories private, use feature branches and reviews for public source changes, avoid real personal/enterprise data, and never call a synthetic pass an independent domain benchmark. Vulnerability reports: see [Security Policy](.github/SECURITY.md).
