# Demo-Safe Governed RAG

A synthetic, reduced-function demonstration of the portfolio's evidence-and-governance pattern.

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
