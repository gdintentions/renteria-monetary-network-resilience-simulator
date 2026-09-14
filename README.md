# Monetary Network Resilience Simulator

A portfolio-grade scenario simulator for exploring how competing global monetary and payment networks could evolve over a 10–15 year horizon under geopolitical, fiscal, cyber, commodity, and digital-currency shocks.

## What this project models

The default scenario tracks six actors:

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

The model is intentionally stylized. It is designed for scenario exploration, comparative resilience analysis, and portfolio demonstration—not as a prediction engine or financial-advice system.

## Key features

- Deterministic runs using a configurable random seed
- 10–15 year simulation horizon
- Shock persistence and resilience effects
- Structural growth and volatility by network
- Normalized modeled market/network shares
- Interactive Streamlit dashboard
- Downloadable CSV output
- Unit tests for normalization, reproducibility, ranking, and validation

## Architecture

```text
.
├── app.py                  # Streamlit dashboard
├── simulator.py            # Core simulation engine
├── requirements.txt        # Python dependencies
├── tests/
│   └── test_simulator.py   # Unit tests
├── .gitignore
└── README.md
```

The simulation engine is separated from the interface so it can later be reused in notebooks, APIs, agent systems, Monte Carlo studies, or model-comparison workflows.

## Quick start

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/gdintentions/renteria-monetary-network-resilience-simulator.git
cd renteria-monetary-network-resilience-simulator
python -m venv .venv
```

Activate it, then install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

Run the core model from the command line:

```bash
python simulator.py
```

Run tests:

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

## Important interpretation note

The variable called `share` is a model-internal relative attractiveness/usage share. It is **not** intended to equal official reserve-currency composition, SWIFT market share, trade-invoicing share, or any single real-world metric.

## Possible next-stage extensions

- Monte Carlo confidence bands across thousands of runs
- Agent-based strategic response functions
- Country-level nodes and alliance switching
- Trade, energy, debt, sanctions, and reserve datasets
- Network-graph visualization
- Stablecoin versus CBDC submodels
- Cyber-resilience and settlement-contagion modeling
- Historical backtesting
- Bayesian calibration
- LLM-generated scenario narratives tied to simulation results

## Portfolio value

This project demonstrates:

- Python modeling
- scenario design
- geopolitical/economic systems thinking
- simulation architecture
- reproducibility
- test-driven implementation
- interactive data applications

## Disclaimer

This repository is an educational and research-oriented simulation. It does not provide investment, legal, economic-policy, or financial advice, and its outputs should not be interpreted as forecasts.
