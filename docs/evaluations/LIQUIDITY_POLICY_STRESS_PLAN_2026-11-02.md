# Liquidity, endogenous policy and shock-model experiment plan
Date: 2026-11-02
Status: PROPOSED EXPERIMENT; baseline preserved.

## Grounded initial audit
The current simulator.py has seeded Gaussian stochastic terms, persistent exogenous shock memory, exponential weight transitions and share normalization. The README documents Monte Carlo ensembles, uncertainty bands and a published sensitivity analysis and limited historical proxy backtest. It is therefore incorrect to characterize this implementation as purely deterministic or lacking Monte Carlo.
The variable `share` is an **internal relative attractiveness/usage measure**, not the real value of liquidity, FX market turnover or a reserve percentage. Normalization to sum to 1 is appropriate to that definition. A separate absolute state is needed to represent liquidity destruction or settlement outages.

Preserved baseline: docs/evaluations/MONETARY_VALIDATION.md
Previously reported: 25 sensitivity runs, 33.3% direction accuracy in narrow 2022-to-2025 USD/EUR/CNY historical proxy. This is **not** a validated forecast.

## Step-by-step experiment
1. Pin original main revision, simulator.py hash, parameter table, seeds, current CSV inputs and historic output artifacts. Never overwrite baseline.
2. Define units and equations before coding: relative attractiveness shares versus absolute settlement capacity, realized transaction volume, failed settlement fraction and system-wide liquidity. Avoid giving a unitless variable a real-world interpretation.
3. Add a separate optional state channel for liquidity and settlement capacity; the original share engine must remain reproducible and unchanged by default. Define non-negativity, conservation/accounting assumptions and failure modes.
4. Design exogenous stresses (payment-infrastructure outage, withdrawal of liquidity, liquidity hoarding, cyber contagion). Model both system-level contraction and conditional cross-network substitution instead of assuming all lost USD transactions transfer to competitors.
5. Prototype a transparent **configurable** policy-response rule with explicit triggers, lag, capacity, duration and intervention type. Document that responses are scenario assumptions, not historically verified policy predictions.
6. Compare original Gaussian shocks against optional jump and regime-switching alternatives. Do not adopt geometric Brownian motion or arbitrary volatility caps merely for sophistication; check domain appropriateness and behavior near zero.
7. Run reproducible seeded paired simulations for no shock, moderate shock, severe systemic collapse, synchronized counterparty disruption, successful intervention and adverse intervention. Add parameter sweeps and numerical invariants.
8. Measure tail losses, system-wide transaction collapse, recovery time, concentration, settlement failure, sensitivity, calibration bounds, numerical stability and runtime. Separate model-internal dispersion from real-world predictive uncertainty.
9. Revisit observable choices and historical calibration carefully. Preserve the old BIS proxy failures; BIS turnover, reserve composition, payments and internal network shares are not interchangeable.
10. Publish a distinct dated successor report with raw inputs, exact code revision, seeds, equations, results, counterexamples, regressions and limitations. Seek expert independent review before stronger scientific or production claims.

## Acceptance / stop gates
- Original simulator outputs reproduce for same seed and assumptions when new mode is disabled.
- Never silently normalize away loss in absolute liquidity or settlement capacity.
- Scenario outcomes remain exploratory, not probabilistic world forecasts.
- Untested or uncalibrated policy feedback assumptions are visibly labeled.
- Production-readiness and independent validation remain separate OPEN gates.
- No merge into main until implementation, tests, evidence review and approval.

## Initial status
Planning document only. No engine, equations, calibration sources, or historical artifacts changed. No new simulation run or validation claim.
