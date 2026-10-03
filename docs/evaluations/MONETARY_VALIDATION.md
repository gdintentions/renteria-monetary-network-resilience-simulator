# Monetary Simulator Validation — Sensitivity + Historical Proxy Backtest

This report deliberately includes model failures and instability. It is not a forecast-validation claim.

## Sensitivity analysis

- Scenario runs: 25
- Seeds: [1, 7, 42, 99, 314]
- Calibration weights: [0.0, 0.15, 0.3, 0.45, 0.6]
- Final-year leader counts: {'BRICS settlement network': 18, 'US / USD network': 7}

| Network | Min final share | Max final share | Range |
|---|---:|---:|---:|
| US / USD network | 17.37% | 23.43% | 6.06 pp |
| BRICS settlement network | 15.73% | 31.57% | 15.83 pp |
| Europe / EUR network | 15.15% | 19.92% | 4.77 pp |
| Gold | 16.54% | 20.87% | 4.33 pp |
| Bitcoin & stablecoins | 6.31% | 10.53% | 4.22 pp |
| Neutral / multi-aligned states | 9.72% | 12.89% | 3.17 pp |

## Historical proxy backtest

- Definition: BIS 2022→2025 normalized USD/EUR/CNY subset; zero-volatility, no-shock structural-growth replay
- Direction accuracy: 33.3%
- Mean absolute error: 1.001 percentage points on the normalized three-currency subset

| Currency/proxy | 2022 start | 2025 observed | 2025 predicted | Direction correct? | Absolute error |
|---|---:|---:|---:|---|---:|
| USD | 70.16% | 70.46% | 69.87% | FAIL | 0.592 pp |
| EUR | 24.29% | 22.83% | 24.33% | FAIL | 1.502 pp |
| CNY | 5.56% | 6.71% | 5.80% | PASS | 0.910 pp |

## Published limitations / failure interpretation

- BIS turnover shares are not reserve shares and sum to 200% across all currencies because each trade has two sides.
- The comparison normalizes only USD/EUR/CNY to a three-currency subset.
- CNY is mapped to the BRICS settlement network as a coarse proxy; they are not equivalent.
- Only one 2022→2025 interval is evaluated, so this is a sanity check rather than evidence of forecasting skill.
- A wrong direction is published as a model failure, not tuned away.
- Large seed/calibration ranges are published as sensitivity, not hidden behind a single preferred run.

## Public data anchors

- BIS 2022 FX turnover: USD 88.4%, EUR 30.6%, CNY 7.0% (one side of trades).
- BIS 2025 FX turnover: USD 89.2%, EUR 28.9%, CNY 8.5% (one side of trades).
- These are market-usage signals, not the simulator's internal six-network share variable.