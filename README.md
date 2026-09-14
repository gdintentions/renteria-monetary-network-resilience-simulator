# Monetary Network Resilience Simulator

A portfolio-grade scenario simulator for exploring how competing global monetary and payment networks could evolve over a 10–15 year horizon under geopolitical, fiscal, cyber, commodity, and digital-currency shocks.

The repository now contains two connected interfaces:

- `app.py` — original lean simulator dashboard
- `demo/recruiter_app.py` — hardened recruiter/public demo built on the same core engine

## What this project models

The core scenario tracks six network actors:

- U.S. / USD network
- BRICS settlement network
- Europe / EUR network
- Gold
- Bitcoin & stablecoins
- Neutral / multi-aligned states

The baseline scenario includes five major shocks:

1. BRICS launches a gold-linked settlement unit
2. Partial oil de-dollarization
3. U.S. debt-confidence crisis
4. Cyberattack on payments infrastructure
5. Rapid digital-currency adoption

The model is intentionally stylized. It is designed for scenario exploration, comparative resilience analysis, systems-modeling demonstration, and portfolio review—not as a prediction engine or financial-advice system.

## Recruiter demo hardening

The `demo/recruiter_app.py` build combines the original model with:

- Monte Carlo uncertainty analysis
- 10th / median / 90th percentile bands
- 12 country-level agents
- country-to-network graph visualization
- historically anchored calibration
- concentration and diversification diagnostics
- transparent model-card disclosures
- reproducible seeds
- downloadable Monte Carlo outputs
- deployment-ready Streamlit configuration
- CI test workflow

### Historical calibration

The calibration layer uses public institutional data as **signals**, not as direct substitutes for the simulator's internal `share` variable.

**IMF COFER — 2025Q4**
- USD: 56.77%
- EUR: 20.25%
- CNY: 1.95%
- Source: https://data.imf.org/en/news/imf%20data%20brief%20march%2027

**BIS Triennial FX Survey — 2025**
- USD: 89.2% of FX trades (one side)
- EUR: 28.9%
- CNY: 8.5%
- Source: https://www.bis.org/publications/202509-commentary-otc-derivatives

Reference rows are stored in `demo/data/calibration_reference.csv`.

## Architecture

```text
.
├── app.py                              # Original Streamlit dashboard
├── simulator.py                        # Core simulation engine
├── demo/
│   ├── recruiter_app.py                # Hardened recruiter/public demo
│   ├── hardening.py                    # Monte Carlo, calibration, country agents
│   ├── README.md                       # Recruiter demo documentation
│   ├── DEPLOYMENT.md                   # Public deployment checklist
│   └── data/
│       └── calibration_reference.csv   # Public historical anchors
├── tests/
│   ├── test_simulator.py               # Core-model tests
│   └── test_recruiter_demo.py          # Advanced-layer tests
├── .streamlit/
│   └── config.toml                     # Cloud/app configuration
├── .github/workflows/
│   └── demo-tests.yml                  # CI
├── pytest.ini
├── requirements.txt
├── .gitignore
└── README.md
```

The architecture intentionally separates model mechanics from the public presentation layer. The recruiter demo calls the original engine directly rather than maintaining a second simulation implementation.

## Quick start

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/gdintentions/renteria-monetary-network-resilience-simulator.git
cd renteria-monetary-network-resilience-simulator
python -m venv .venv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the original dashboard:

```bash
streamlit run app.py
```

Run the recruiter/public demo:

```bash
streamlit run demo/recruiter_app.py
```

Run the core model from the command line:

```bash
python simulator.py
```

Run all tests:

```bash
pytest -q
```

## Modeling approach

Each network has four primary characteristics:

- baseline share
- structural growth rate
- resilience score
- volatility

For each simulated year, the engine combines structural growth, lingering shock effects, any newly activated shocks, and seeded stochastic variation. The resulting relative weights are normalized to 100%.

A shock can affect multiple networks differently. For example, partial oil de-dollarization can increase modeled BRICS and neutral-network attractiveness while reducing USD-network attractiveness.

### Monte Carlo layer

The hardened demo repeatedly executes the original engine with reproducible independent seeds. For each network/year pair, it reports the 10th percentile, median, mean, and 90th percentile across runs.

These bands describe uncertainty **inside the scenario model**. They are not frequentist confidence intervals for real-world monetary outcomes.

### Country-agent layer

Twelve country agents use explicit scenario affinities plus modeled network states to produce normalized exposure profiles. The strongest links are rendered as a network graph.

The country affinities are inspectable assumptions. They are not inferred confidential reserve holdings or claims about official policy.

## Important interpretation note

The variable called `share` is a model-internal relative attractiveness/usage share. It is **not** intended to equal official reserve-currency composition, SWIFT payment share, trade-invoicing share, BIS FX turnover, or any single real-world metric.

The historical calibration is therefore deliberately light-touch and documented.

## Public demo deployment

The recruiter build is organized for Streamlit Community Cloud:

- Repository: `gdintentions/renteria-monetary-network-resilience-simulator`
- Branch: `main`
- Entrypoint: `demo/recruiter_app.py`

See `demo/DEPLOYMENT.md` for the final account-side deployment steps.

## Portfolio value

This project demonstrates:

- Python modeling
- scenario design
- Monte Carlo simulation
- agent-based modeling concepts
- graph/network analysis
- public-data calibration
- model-governance disclosure
- reproducibility
- test-driven implementation
- CI
- interactive data applications

## Remaining research extensions

- historical backtesting against multiple vintages
- Bayesian parameter calibration
- trade and energy network datasets
- sanctions and debt-service channels
- CBDC versus stablecoin submodels
- cyber-contagion propagation
- LLM-generated scenario narratives tied to simulation outputs

## Disclaimer

This repository is an educational and research-oriented simulation. It does not provide investment, legal, economic-policy, or financial advice, and its outputs should not be interpreted as forecasts.
