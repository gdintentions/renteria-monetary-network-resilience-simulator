# Demo-Safe Governed RAG

A synthetic, reduced-function demonstration of the portfolio's evidence-and-governance pattern.

[**Run the public browser reviewer demo**](https://gdintentions.github.io/renteria-monetary-network-resilience-simulator/#governed-rag) · [Inspect Python miniature](demo.py) · [Read the public source guide](../../PUBLIC_SOURCE_GUIDE.md) · [Read release tests and limitations](../../hosted_demo/RECRUITER_RELEASE.md)

**Disclosure:** this Python miniature and the separately implemented JavaScript browser reviewer are public teaching/demo implementations; neither is a copy of the private authenticated FastAPI application. Its synthetic cases, heuristic scores and simulated approvals do not establish real-world policy accuracy or staffed governance. The private development service stays private.

It contains no private documents, API keys, proprietary prompts, production integrations, or source copied from the private implementation.

## Demonstrates

- lexical evidence retrieval
- source visibility
- abstention on weak evidence
- heuristic confidence
- `safe / review / block` routing
- explicit escalation for legal-policy questions

Run:

```bash
python demo.py
python demo.py --self-test
```

The confidence value is a demo heuristic, not a calibrated probability.
