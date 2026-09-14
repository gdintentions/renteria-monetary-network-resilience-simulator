# Recruiter / Public Demo

`demo/recruiter_app.py` is the hardened portfolio entry point for the Monetary Network Resilience Simulator.

It **reuses the original `simulator.py` engine** and adds a presentation and analytics layer designed for technical reviewers, recruiters, and portfolio demonstrations.

## Added capabilities

- Monte Carlo simulation with 10th / median / 90th percentile bands
- 12 country-level agents with explicit, inspectable behavioral affinities
- Country-to-network graph visualization
- Historically anchored USD / EUR / CNY calibration
- Concentration, diversification, and effective-network diagnostics
- Public-facing model card and limitations
- CSV export of Monte Carlo results
- Reproducible random seeds
- Streamlit Community Cloud-ready structure

## Historical anchors

The calibration layer uses two public institutional datasets as **signals**, not as direct equivalents of the model's internal `share` variable:

1. **IMF COFER** — Currency Composition of Official Foreign Exchange Reserves
   - 2025Q4: USD 56.77%, EUR 20.25%, CNY 1.95%
   - Source: https://data.imf.org/en/news/imf%20data%20brief%20march%2027
   - COFER dataset: https://data.imf.org/Datasets/COFER

2. **BIS Triennial Central Bank Survey** — OTC FX turnover
   - 2025: USD 89.2%, EUR 28.9%, CNY 8.5% (currency appears on one side of trades)
   - Source: https://www.bis.org/publications/202509-commentary-otc-derivatives

The raw reference rows used by the demo are stored in:

`demo/data/calibration_reference.csv`

### Why the calibration is deliberately light-touch

COFER is a reserve-asset dataset. BIS FX turnover is a trading-activity dataset. The original simulator's `share` variable is a normalized scenario-level attractiveness/usage measure. These are **not the same construct**.

The recruiter build therefore blends the historical signals only into the USD/EUR/BRICS currency-network subset and keeps gold, digital assets, and neutral-state behavior as explicit scenario assumptions.

## Country agents

The demo includes:

- United States
- China
- India
- Brazil
- Russia
- Germany
- Saudi Arabia
- United Arab Emirates
- Japan
- Switzerland
- Singapore
- South Africa

Country-agent affinities are transparent scenario parameters, not claims about confidential reserve allocations or official government policy.

## Run locally

From the repository root:

```bash
pip install -r requirements.txt
streamlit run demo/recruiter_app.py
```

Run the complete test suite:

```bash
pytest -q
```

## Deployment target

The project is structured for **Streamlit Community Cloud**. Use:

- Repository: `gdintentions/renteria-monetary-network-resilience-simulator`
- Branch: `main`
- Entrypoint: `demo/recruiter_app.py`

See `demo/DEPLOYMENT.md` for the deployment checklist.

## Portfolio positioning

This version demonstrates a broader engineering stack than the original prototype:

- scenario simulation
- agent-based modeling concepts
- Monte Carlo uncertainty analysis
- graph/network analysis
- public-data calibration
- reproducibility
- model governance and limitation disclosure
- interactive application design
- CI-ready automated testing
