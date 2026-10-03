from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from simulator import Agent, DEFAULT_AGENTS, run_simulation
from demo.hardening import calibrated_agents

BIS_2022 = {"USD": 88.4, "EUR": 30.6, "CNY": 7.0}
BIS_2025 = {"USD": 89.2, "EUR": 28.9, "CNY": 8.5}
PROXY_MAP = {
    "USD": "US / USD network",
    "EUR": "Europe / EUR network",
    "CNY": "BRICS settlement network",
}


def normalize(values: dict[str, float]) -> dict[str, float]:
    total = sum(values.values())
    return {key: value / total for key, value in values.items()}


def sensitivity_analysis() -> dict:
    seeds = [1, 7, 42, 99, 314]
    weights = [0.0, 0.15, 0.30, 0.45, 0.60]
    rows = []
    leaders = Counter()
    for weight in weights:
        for seed in seeds:
            agents = calibrated_agents(weight)
            result = run_simulation(years=15, start_year=2026, seed=seed, agents=agents)
            final_year = max(int(row["year"]) for row in result)
            final = {
                str(row["agent"]): float(row["share_pct"])
                for row in result
                if int(row["year"]) == final_year
            }
            leader = max(final, key=final.get)
            leaders[leader] += 1
            rows.append({"seed": seed, "calibration_weight": weight, "final": final, "leader": leader})

    ranges = {}
    for name in [a.name for a in DEFAULT_AGENTS]:
        vals = [row["final"][name] for row in rows]
        ranges[name] = {
            "min_pct": min(vals),
            "max_pct": max(vals),
            "range_pp": max(vals) - min(vals),
        }
    return {
        "runs": len(rows),
        "seeds": seeds,
        "calibration_weights": weights,
        "leader_counts": dict(leaders),
        "final_share_ranges": ranges,
        "runs_detail": rows,
    }


def historical_proxy_backtest() -> dict:
    """Mechanical historical sanity check, not a forecast validation.

    Uses 2022 BIS FX-turnover shares for USD/EUR/CNY as normalized starting
    weights, evolves only the mapped USD/EUR/BRICS proxy networks for three
    quiet years with zero volatility and no shocks, then compares the direction
    and normalized subset shares with BIS 2025.

    CNY is *not* equivalent to a BRICS settlement network; this mapping is
    intentionally published as a coarse proxy to expose model mismatch.
    """
    start = normalize(BIS_2022)
    target = normalize(BIS_2025)
    defaults = {a.name: a for a in DEFAULT_AGENTS}
    agents = []
    for currency, network in PROXY_MAP.items():
        base = defaults[network]
        agents.append(
            Agent(
                network,
                start[currency],
                base.structural_growth,
                base.resilience,
                0.0,
            )
        )
    rows = run_simulation(
        years=3,
        start_year=2022,
        seed=42,
        agents=agents,
        shocks=[],
    )
    final = {
        str(row["agent"]): float(row["share"])
        for row in rows
        if int(row["year"]) == 2025
    }
    inverse = {network: currency for currency, network in PROXY_MAP.items()}
    predicted = {inverse[network]: value for network, value in final.items()}

    currency_rows = []
    direction_hits = 0
    errors = []
    for currency in ("USD", "EUR", "CNY"):
        actual_change = target[currency] - start[currency]
        predicted_change = predicted[currency] - start[currency]
        direction_ok = (actual_change == 0 and abs(predicted_change) < 1e-12) or (
            actual_change * predicted_change > 0
        )
        direction_hits += int(direction_ok)
        error_pp = abs(predicted[currency] - target[currency]) * 100
        errors.append(error_pp)
        currency_rows.append({
            "currency": currency,
            "start_2022_pct_normalized": start[currency] * 100,
            "observed_2025_pct_normalized": target[currency] * 100,
            "predicted_2025_pct_normalized": predicted[currency] * 100,
            "observed_change_pp": actual_change * 100,
            "predicted_change_pp": predicted_change * 100,
            "direction_correct": direction_ok,
            "absolute_error_pp": error_pp,
        })
    return {
        "definition": "BIS 2022→2025 normalized USD/EUR/CNY subset; zero-volatility, no-shock structural-growth replay",
        "direction_accuracy": direction_hits / 3,
        "mae_pp": sum(errors) / len(errors),
        "currency_results": currency_rows,
        "limitations": [
            "BIS turnover shares are not reserve shares and sum to 200% across all currencies because each trade has two sides.",
            "The comparison normalizes only USD/EUR/CNY to a three-currency subset.",
            "CNY is mapped to the BRICS settlement network as a coarse proxy; they are not equivalent.",
            "Only one 2022→2025 interval is evaluated, so this is a sanity check rather than evidence of forecasting skill.",
        ],
    }


def write_report(result: dict, path: Path) -> None:
    sens = result["sensitivity"]
    back = result["historical_proxy_backtest"]
    lines = [
        "# Monetary Simulator Validation — Sensitivity + Historical Proxy Backtest",
        "",
        "This report deliberately includes model failures and instability. It is not a forecast-validation claim.",
        "",
        "## Sensitivity analysis",
        "",
        f"- Scenario runs: {sens['runs']}",
        f"- Seeds: {sens['seeds']}",
        f"- Calibration weights: {sens['calibration_weights']}",
        f"- Final-year leader counts: {sens['leader_counts']}",
        "",
        "| Network | Min final share | Max final share | Range |",
        "|---|---:|---:|---:|",
    ]
    for name, row in sens["final_share_ranges"].items():
        lines.append(f"| {name} | {row['min_pct']:.2f}% | {row['max_pct']:.2f}% | {row['range_pp']:.2f} pp |")
    lines += [
        "",
        "## Historical proxy backtest",
        "",
        f"- Definition: {back['definition']}",
        f"- Direction accuracy: {back['direction_accuracy']:.1%}",
        f"- Mean absolute error: {back['mae_pp']:.3f} percentage points on the normalized three-currency subset",
        "",
        "| Currency/proxy | 2022 start | 2025 observed | 2025 predicted | Direction correct? | Absolute error |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for row in back["currency_results"]:
        lines.append(
            f"| {row['currency']} | {row['start_2022_pct_normalized']:.2f}% | "
            f"{row['observed_2025_pct_normalized']:.2f}% | {row['predicted_2025_pct_normalized']:.2f}% | "
            f"{'PASS' if row['direction_correct'] else 'FAIL'} | {row['absolute_error_pp']:.3f} pp |"
        )
    lines += ["", "## Published limitations / failure interpretation", ""]
    lines.extend(f"- {item}" for item in back["limitations"])
    lines += [
        "- A wrong direction is published as a model failure, not tuned away.",
        "- Large seed/calibration ranges are published as sensitivity, not hidden behind a single preferred run.",
        "",
        "## Public data anchors",
        "",
        "- BIS 2022 FX turnover: USD 88.4%, EUR 30.6%, CNY 7.0% (one side of trades).",
        "- BIS 2025 FX turnover: USD 89.2%, EUR 28.9%, CNY 8.5% (one side of trades).",
        "- These are market-usage signals, not the simulator's internal six-network share variable.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = {
        "sensitivity": sensitivity_analysis(),
        "historical_proxy_backtest": historical_proxy_backtest(),
    }
    report = Path("docs/evaluations/MONETARY_VALIDATION.md")
    write_report(result, report)
    artifact = Path("artifacts/monetary_validation.json")
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(result, indent=2), encoding="utf-8")
    summary = {
        "sensitivity_runs": result["sensitivity"]["runs"],
        "leader_counts": result["sensitivity"]["leader_counts"],
        "direction_accuracy": result["historical_proxy_backtest"]["direction_accuracy"],
        "mae_pp": result["historical_proxy_backtest"]["mae_pp"],
        "currency_results": result["historical_proxy_backtest"]["currency_results"],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
