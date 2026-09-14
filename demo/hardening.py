from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple
import math

from simulator import Agent, DEFAULT_AGENTS, run_simulation


NETWORKS = [a.name for a in DEFAULT_AGENTS]


@dataclass(frozen=True)
class CountryAgent:
    country: str
    region: str
    policy_flexibility: float
    digital_readiness: float
    commodity_exporter: float
    affinities: Dict[str, float]


# These are scenario-level behavioral affinities, not measured reserve allocations.
DEFAULT_COUNTRIES: List[CountryAgent] = [
    CountryAgent("United States", "North America", 0.88, 0.88, 0.35, {
        "US / USD network": 1.00, "Europe / EUR network": 0.18,
        "Bitcoin & stablecoins": 0.22, "Gold": 0.12,
        "BRICS settlement network": 0.04, "Neutral / multi-aligned states": 0.08,
    }),
    CountryAgent("China", "East Asia", 0.82, 0.93, 0.42, {
        "BRICS settlement network": 1.00, "Gold": 0.45,
        "US / USD network": 0.24, "Neutral / multi-aligned states": 0.34,
        "Bitcoin & stablecoins": 0.12, "Europe / EUR network": 0.18,
    }),
    CountryAgent("India", "South Asia", 0.90, 0.79, 0.40, {
        "Neutral / multi-aligned states": 0.92, "BRICS settlement network": 0.67,
        "US / USD network": 0.62, "Gold": 0.52,
        "Europe / EUR network": 0.28, "Bitcoin & stablecoins": 0.22,
    }),
    CountryAgent("Brazil", "Latin America", 0.77, 0.73, 0.72, {
        "BRICS settlement network": 0.82, "US / USD network": 0.58,
        "Neutral / multi-aligned states": 0.66, "Gold": 0.27,
        "Europe / EUR network": 0.24, "Bitcoin & stablecoins": 0.24,
    }),
    CountryAgent("Russia", "Eurasia", 0.60, 0.70, 0.88, {
        "BRICS settlement network": 1.00, "Gold": 0.78,
        "Neutral / multi-aligned states": 0.54, "Bitcoin & stablecoins": 0.25,
        "Europe / EUR network": 0.10, "US / USD network": 0.06,
    }),
    CountryAgent("Germany", "Europe", 0.76, 0.87, 0.28, {
        "Europe / EUR network": 1.00, "US / USD network": 0.54,
        "Gold": 0.30, "Neutral / multi-aligned states": 0.18,
        "Bitcoin & stablecoins": 0.16, "BRICS settlement network": 0.12,
    }),
    CountryAgent("Saudi Arabia", "Middle East", 0.72, 0.82, 1.00, {
        "US / USD network": 0.72, "BRICS settlement network": 0.52,
        "Neutral / multi-aligned states": 0.62, "Gold": 0.40,
        "Europe / EUR network": 0.24, "Bitcoin & stablecoins": 0.18,
    }),
    CountryAgent("United Arab Emirates", "Middle East", 0.86, 0.94, 0.90, {
        "Neutral / multi-aligned states": 0.80, "US / USD network": 0.66,
        "BRICS settlement network": 0.58, "Bitcoin & stablecoins": 0.48,
        "Gold": 0.34, "Europe / EUR network": 0.30,
    }),
    CountryAgent("Japan", "East Asia", 0.73, 0.91, 0.18, {
        "US / USD network": 0.88, "Neutral / multi-aligned states": 0.40,
        "Europe / EUR network": 0.25, "Gold": 0.18,
        "Bitcoin & stablecoins": 0.18, "BRICS settlement network": 0.14,
    }),
    CountryAgent("Switzerland", "Europe", 0.90, 0.92, 0.12, {
        "Gold": 0.86, "Neutral / multi-aligned states": 0.78,
        "US / USD network": 0.60, "Europe / EUR network": 0.52,
        "Bitcoin & stablecoins": 0.36, "BRICS settlement network": 0.18,
    }),
    CountryAgent("Singapore", "Southeast Asia", 0.95, 0.98, 0.12, {
        "Neutral / multi-aligned states": 0.92, "US / USD network": 0.72,
        "Bitcoin & stablecoins": 0.62, "BRICS settlement network": 0.50,
        "Europe / EUR network": 0.34, "Gold": 0.22,
    }),
    CountryAgent("South Africa", "Africa", 0.68, 0.70, 0.78, {
        "BRICS settlement network": 0.82, "Neutral / multi-aligned states": 0.64,
        "US / USD network": 0.48, "Gold": 0.38,
        "Europe / EUR network": 0.27, "Bitcoin & stablecoins": 0.20,
    }),
]


# Public institutional anchors used for a light-touch calibration of the
# currency-network subset. COFER excludes monetary gold, and BIS FX turnover
# is not a reserve-share measure, so both are treated as signals rather than
# direct replacements for model shares.
OBSERVED_CALIBRATION = {
    "reserve_2024q4": {"USD": 57.79, "EUR": 19.84, "CNY": 2.18},
    "reserve_2025q4": {"USD": 56.77, "EUR": 20.25, "CNY": 1.95},
    "fx_2022": {"USD": 88.4, "EUR": 30.6, "CNY": 7.0},
    "fx_2025": {"USD": 89.2, "EUR": 28.9, "CNY": 8.5},
}


def _clone_agents(agents: Iterable[Agent]) -> List[Agent]:
    return [
        Agent(
            name=a.name,
            share=a.share,
            structural_growth=a.structural_growth,
            resilience=a.resilience,
            volatility=a.volatility,
            shock_memory=a.shock_memory,
            metadata=dict(a.metadata),
        )
        for a in agents
    ]


def _normalize(values: Dict[str, float]) -> Dict[str, float]:
    total = sum(max(v, 0.0) for v in values.values())
    if total <= 0:
        raise ValueError("Cannot normalize a non-positive vector")
    return {k: max(v, 0.0) / total for k, v in values.items()}


def calibrated_agents(calibration_weight: float = 0.30) -> List[Agent]:
    """Return the original agent set with a transparent, light-touch calibration.

    `calibration_weight=0` reproduces the original starting shares. Higher values
    blend the USD/EUR/BRICS subset toward a composite of IMF COFER reserve shares
    and BIS FX-turnover signals. Non-currency networks retain their original
    shares and are re-normalized with the currency subset.
    """
    if not 0.0 <= calibration_weight <= 1.0:
        raise ValueError("calibration_weight must be between 0 and 1")

    agents = _clone_agents(DEFAULT_AGENTS)
    if calibration_weight == 0.0:
        return agents
    by_name = {a.name: a for a in agents}

    reserve = OBSERVED_CALIBRATION["reserve_2025q4"]
    fx = OBSERVED_CALIBRATION["fx_2025"]
    reserve_norm = _normalize(reserve)
    fx_norm = _normalize(fx)

    composite = {
        "USD": 0.65 * reserve_norm["USD"] + 0.35 * fx_norm["USD"],
        "EUR": 0.65 * reserve_norm["EUR"] + 0.35 * fx_norm["EUR"],
        "CNY": 0.65 * reserve_norm["CNY"] + 0.35 * fx_norm["CNY"],
    }
    composite = _normalize(composite)

    mapping = {
        "USD": "US / USD network",
        "EUR": "Europe / EUR network",
        "CNY": "BRICS settlement network",
    }
    original_subset_total = sum(by_name[mapping[k]].share for k in mapping)
    original_subset = _normalize({k: by_name[mapping[k]].share for k in mapping})

    blended = {
        k: (1.0 - calibration_weight) * original_subset[k]
        + calibration_weight * composite[k]
        for k in mapping
    }
    blended = _normalize(blended)
    for key, network in mapping.items():
        by_name[network].share = blended[key] * original_subset_total

    # Momentum adjustments are deliberately small. They only nudge structural
    # growth using the direction of recent reserve and FX changes.
    reserve_delta = {
        k: OBSERVED_CALIBRATION["reserve_2025q4"][k]
        - OBSERVED_CALIBRATION["reserve_2024q4"][k]
        for k in ("USD", "EUR", "CNY")
    }
    fx_delta = {
        k: OBSERVED_CALIBRATION["fx_2025"][k]
        - OBSERVED_CALIBRATION["fx_2022"][k]
        for k in ("USD", "EUR", "CNY")
    }
    for key, network in mapping.items():
        momentum = 0.0008 * reserve_delta[key] + 0.00025 * fx_delta[key]
        by_name[network].structural_growth += calibration_weight * max(-0.003, min(0.003, momentum))

    # Final normalization protects the original six-network invariant.
    shares = _normalize({a.name: a.share for a in agents})
    for a in agents:
        a.share = shares[a.name]
    return agents


def _quantile(sorted_values: List[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("quantile requires at least one value")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return sorted_values[lo]
    fraction = pos - lo
    return sorted_values[lo] * (1.0 - fraction) + sorted_values[hi] * fraction


def run_monte_carlo(
    runs: int = 300,
    years: int = 15,
    start_year: int = 2026,
    seed: int = 42,
    calibration_weight: float = 0.30,
) -> List[Dict[str, float | int | str]]:
    """Run repeated versions of the original model and return 10/50/90 bands."""
    if runs < 20:
        raise ValueError("runs must be >= 20 for stable percentile bands")

    agents = calibrated_agents(calibration_weight)
    samples: Dict[Tuple[int, str], List[float]] = defaultdict(list)

    for i in range(runs):
        run_seed = seed + i * 7919
        rows = run_simulation(
            years=years,
            start_year=start_year,
            seed=run_seed,
            agents=agents,
        )
        for row in rows:
            samples[(int(row["year"]), str(row["agent"]))].append(float(row["share_pct"]))

    result: List[Dict[str, float | int | str]] = []
    for (year, agent), values in sorted(samples.items()):
        values.sort()
        result.append({
            "year": year,
            "agent": agent,
            "p10": round(_quantile(values, 0.10), 4),
            "median": round(_quantile(values, 0.50), 4),
            "p90": round(_quantile(values, 0.90), 4),
            "mean": round(sum(values) / len(values), 4),
        })
    return result


def country_exposures(
    network_rows: List[Dict[str, float | int | str]],
    countries: Iterable[CountryAgent] = DEFAULT_COUNTRIES,
) -> List[Dict[str, float | str]]:
    """Translate a modeled network state into country-level scenario exposures."""
    latest_year = max(int(r["year"]) for r in network_rows)
    shares = {
        str(r["agent"]): float(r["share"])
        for r in network_rows
        if int(r["year"]) == latest_year
    }

    rows: List[Dict[str, float | str]] = []
    for country in countries:
        raw: Dict[str, float] = {}
        for network, affinity in country.affinities.items():
            network_share = shares.get(network, 0.0)
            adaptability = 0.80 + 0.20 * country.policy_flexibility
            digital_boost = 1.0
            if network == "Bitcoin & stablecoins":
                digital_boost += 0.25 * country.digital_readiness
            commodity_boost = 1.0
            if network in {"Gold", "BRICS settlement network"}:
                commodity_boost += 0.12 * country.commodity_exporter
            raw[network] = (
                affinity
                * (0.30 + network_share)
                * adaptability
                * digital_boost
                * commodity_boost
            )
        normalized = _normalize(raw)
        ordered = sorted(normalized.items(), key=lambda item: item[1], reverse=True)
        top_network, top_share = ordered[0]
        for network, exposure in ordered:
            rows.append({
                "country": country.country,
                "region": country.region,
                "network": network,
                "exposure": round(exposure, 6),
                "exposure_pct": round(exposure * 100, 2),
                "top_network": top_network,
                "top_network_pct": round(top_share * 100, 2),
            })
    return rows


def network_edges(
    exposure_rows: List[Dict[str, float | str]],
    top_n: int = 2,
) -> List[Dict[str, float | str]]:
    """Return the strongest country-to-network links for graph rendering."""
    grouped: Dict[str, List[Dict[str, float | str]]] = defaultdict(list)
    for row in exposure_rows:
        grouped[str(row["country"])].append(row)

    edges: List[Dict[str, float | str]] = []
    for country, rows in grouped.items():
        ranked = sorted(rows, key=lambda r: float(r["exposure"]), reverse=True)[:top_n]
        for row in ranked:
            edges.append({
                "source": country,
                "target": str(row["network"]),
                "weight": float(row["exposure"]),
                "weight_pct": float(row["exposure_pct"]),
            })
    return edges


def concentration_metrics(
    network_rows: List[Dict[str, float | int | str]],
) -> Dict[str, float]:
    latest_year = max(int(r["year"]) for r in network_rows)
    shares = [
        float(r["share"])
        for r in network_rows
        if int(r["year"]) == latest_year
    ]
    hhi = sum(s * s for s in shares)
    entropy = -sum(s * math.log(s) for s in shares if s > 0)
    max_entropy = math.log(len(shares))
    diversification = entropy / max_entropy if max_entropy else 0.0
    return {
        "hhi": round(hhi, 4),
        "diversification_index": round(diversification, 4),
        "effective_networks": round(math.exp(entropy), 2),
    }
