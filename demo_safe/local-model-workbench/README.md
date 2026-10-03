# Demo-Safe Local Model Workbench

A deterministic simulation of the experiment-ledger pattern used by the private local-model workbench.

No local model, Ollama runtime, provider endpoint, prompt history, or private response data is exposed here.

## Demonstrates

- repeatable same-prompt comparison
- explicit success/error recording
- opt-in result retention concept
- separation of latency measurement from quality claims

All sample outputs and timings are synthetic.

Run:

```bash
python demo.py
python demo.py --self-test
```
