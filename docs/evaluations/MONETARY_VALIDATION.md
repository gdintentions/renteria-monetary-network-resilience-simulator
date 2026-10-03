# Monetary Simulator Validation — Sensitivity + Historical Proxy Backtest

**Evaluation date:** 2026-10-03

This report deliberately includes model failures and instability. It is not a forecast-validation claim.

## Sensitivity analysis

- Scenario runs: 25
- Seeds: `[1, 7, 42, 99, 314]`
- Calibration weights: `[0.0, 0.15, 0.30, 0.45, 0.60]`
- Final-year leader counts: BRICS settlement network **18/25**; US / USD network **7/25**

| Network | Min final share | Max final share | Range |
|---|---:|---:|---:|
| US / USD network | 17.37% | 23.43% | 6.06 pp |
| BRICS settlement network | 15.73% | 31.57% | 15.83 pp |
| Europe / EUR network | 15.15% | 19.92% | 4.77 pp |
| Gold | 16.54% | 20.87% | 4.33 pp |
| Bitcoin & stablecoins | 6.31% | 10.53% | 4.22 pp |
| Neutral / multi-aligned states | 9.72% | 12.89% | 3.17 pp |

The BRICS settlement network is the most sensitivity-dependent final share in this grid. That instability is published rather than hidden behind a preferred seed or calibration setting.

## Historical proxy backtest

- Definition: BIS 2022→2025 normalized USD/EUR/CNY subset; zero-volatility, no-shock structural-growth replay
- Direction accuracy: **33.3% (1/3)**
- Mean absolute error: **1.001 percentage points** on the normalized three-currency subset

| Currency/proxy | 2022 start | 2025 observed | 2025 predicted | Direction correct? | Absolute error |
|---|---:|---:|---:|---|---:|
| USD | 70.16% | 70.46% | 69.87% | **FAIL** | 0.592 pp |
| EUR | 24.29% | 22.83% | 24.33% | **FAIL** | 1.502 pp |
| CNY | 5.56% | 6.71% | 5.80% | PASS | 0.910 pp |

## Published failures

### USD direction failure

Observed BIS-subset direction: **up** (+0.299 pp).  
Model proxy direction: **down** (-0.293 pp).

### EUR direction failure

Observed BIS-subset direction: **down** (-1.458 pp).  
Model proxy direction: **up** (+0.044 pp).

These failures are not tuned away. They show that the current structural-growth assumptions do not reproduce two of the three observed 2022→2025 directions in this deliberately narrow replay.

## Limitations / interpretation

- BIS turnover shares are not reserve shares and sum to 200% across all currencies because each trade has two sides.
- The comparison normalizes only USD/EUR/CNY to a three-currency subset.
- CNY is mapped to the BRICS settlement network as a coarse proxy; they are **not equivalent**.
- Only one 2022→2025 interval is evaluated, so this is a sanity check rather than evidence of forecasting skill.
- Large seed/calibration ranges are sensitivity evidence, not uncertainty estimates for the real world.
- A wrong direction is published as a model failure, not reclassified as an acceptable scenario.

## Public data anchors

- BIS 2022 FX turnover: USD 88.4%, EUR 30.6%, CNY 7.0% (one side of trades).
- BIS 2025 FX turnover: USD 89.2%, EUR 28.9%, CNY 8.5% (one side of trades).
- These are market-usage signals, not the simulator's internal six-network share variable.

## Reproduce

```bash
python -m demo.validation
```

CI workflow: `.github/workflows/monetary-validation.yml`
