# Demo-Safe Portfolio Showcase

This directory contains **public, reduced-function demonstrations** of selected private portfolio projects.

These demos are intentionally **not source mirrors**. They use synthetic data, simplified logic, and no credentials, private prompts, personal records, proprietary integrations, or production configuration. Their purpose is to let academics, recruiters, hiring managers, and technical reviewers inspect the engineering pattern without exposing the fuller private implementation.

## Demo-safe projects

- [Governed RAG](governed-rag/README.md)
- [Governed RAG Model Lab](governed-rag-model-lab/README.md)
- [Polyglot Relay](polyglot-relay/README.md)
- [Context Atlas](context-atlas/README.md)
- [Local Model Workbench](local-model-workbench/README.md)
- [Notes Evidence RAG](notes-evidence-rag/README.md)
- [Personal Assistant Ledger](personal-assistant-ledger/README.md)

## Already-public projects

The Monetary Network Resilience Simulator, ArgusLoop, and EvidenceWeave already use public/synthetic portfolio material inside this repository, so separate reduced copies are not required.

## Safety boundary

Each demo follows four rules:

1. synthetic fixtures only;
2. no network credentials or secrets;
3. no private repository source copied verbatim;
4. results are demonstrations, not claims of production readiness or external model accuracy.

Run all public showcase smoke tests with:

```bash
python demo_safe/smoke_test.py
```
