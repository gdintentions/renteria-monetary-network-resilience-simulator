from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List
import math
import random


@dataclass(frozen=True)
class Shock:
    year: int
    name: str
    effects: Dict[str, float]
    persistence: float = 0.55


@dataclass
class Agent:
    name: str
    share: float
    structural_growth: float
    resilience: float
    volatility: float
    shock_memory: float = 0.0
    metadata: Dict[str, str] = field(default_factory=dict)


DEFAULT_AGENTS: List[Agent] = [
    Agent("US / USD network", 0.47, 0.002, 0.86, 0.012),
    Agent("BRICS settlement network", 0.15, 0.018, 0.67, 0.020),
    Agent("Europe / EUR network", 0.17, 0.004, 0.76, 0.014),
    Agent("Gold", 0.08, 0.007, 0.92, 0.010),
    Agent("Bitcoin & stablecoins", 0.05, 0.022, 0.55, 0.045),
    Agent("Neutral / multi-aligned states", 0.08, 0.010, 0.73, 0.018),
]


def default_shocks(start_year: int) -> List[Shock]:
    return [
        Shock(start_year + 2, "BRICS gold-linked settlement unit", {
            "BRICS settlement network": 0.16,
            "Gold": 0.10,
            "US / USD network": -0.07,
            "Neutral / multi-aligned states": 0.04,
        }),
        Shock(start_year + 4, "Partial oil de-dollarization", {
            "BRICS settlement network": 0.11,
            "US / USD network": -0.10,
            "Gold": 0.05,
            "Neutral / multi-aligned states": 0.05,
        }),
        Shock(start_year + 6, "U.S. debt confidence crisis", {
            "US / USD network": -0.16,
            "Europe / EUR network": 0.04,
            "Gold": 0.13,
            "Bitcoin & stablecoins": 0.06,
        }),
        Shock(start_year + 8, "Cyberattack on payments infrastructure", {
            "US / USD network": -0.06,
            "BRICS settlement network": -0.05,
            "Europe / EUR network": -0.05,
            "Gold": 0.08,
            "Bitcoin & stablecoins": -0.03,
            "Neutral / multi-aligned states": 0.04,
        }),
        Shock(start_year + 10, "Rapid digital-currency adoption", {
            "Bitcoin & stablecoins": 0.14,
            "BRICS settlement network": 0.05,
            "Europe / EUR network": 0.03,
            "US / USD network": 0.02,
        }),
    ]


def _clone_agents(agents: Iterable[Agent]) -> List[Agent]:
    return [Agent(**{
        "name": a.name,
        "share": a.share,
        "structural_growth": a.structural_growth,
        "resilience": a.resilience,
        "volatility": a.volatility,
        "shock_memory": a.shock_memory,
        "metadata": dict(a.metadata),
    }) for a in agents]


def _normalize(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(max(v, 1e-9) for v in weights.values())
    return {k: max(v, 1e-9) / total for k, v in weights.items()}


def run_simulation(
    years: int = 15,
    start_year: int = 2026,
    seed: int = 42,
    agents: Iterable[Agent] | None = None,
    shocks: Iterable[Shock] | None = None,
) -> List[Dict[str, float | int | str]]:
    """Run a stylized scenario model of international settlement-network shares.

    Shares represent relative usage/attractiveness inside the model, not forecasts of
    official reserve holdings. Results are scenario-analysis outputs, not predictions.
    """
    if years < 1:
        raise ValueError("years must be >= 1")

    rng = random.Random(seed)
    model_agents = _clone_agents(DEFAULT_AGENTS if agents is None else agents)
    if not model_agents:
        raise ValueError("at least one agent is required")
    names = [agent.name for agent in model_agents]
    if len(names) != len(set(names)) or any(not name.strip() for name in names):
        raise ValueError("agent names must be unique and nonempty")
    for agent in model_agents:
        values = (agent.share, agent.structural_growth, agent.resilience, agent.volatility, agent.shock_memory)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("agent parameters must be finite")
        if agent.share <= 0 or agent.volatility < 0 or not 0 <= agent.resilience <= 1:
            raise ValueError("agent share, volatility, or resilience is out of range")
    total_share = sum(agent.share for agent in model_agents)
    if not math.isclose(total_share, 1.0, rel_tol=0, abs_tol=1e-6):
        raise ValueError("initial agent shares must sum to one")
    shock_list = list(shocks if shocks is not None else default_shocks(start_year))
    shock_by_year: Dict[int, List[Shock]] = {}
    for shock in shock_list:
        if not 0 <= shock.persistence <= 1 or not math.isfinite(shock.persistence):
            raise ValueError("shock persistence must be finite and between zero and one")
        if set(shock.effects) - set(names) or not all(math.isfinite(v) for v in shock.effects.values()):
            raise ValueError("shock effects must be finite and reference known agents")
        shock_by_year.setdefault(shock.year, []).append(shock)

    rows: List[Dict[str, float | int | str]] = []

    def append_rows(year: int, event: str) -> None:
        for agent in model_agents:
            rows.append({
                "year": year,
                "agent": agent.name,
                "share": round(agent.share, 6),
                "share_pct": round(agent.share * 100, 3),
                "event": event,
            })

    append_rows(start_year, "Baseline")

    for year in range(start_year + 1, start_year + years + 1):
        active = shock_by_year.get(year, [])
        event_label = "; ".join(s.name for s in active) if active else "No discrete shock"
        raw_weights: Dict[str, float] = {}

        for agent in model_agents:
            direct_effect = sum(s.effects.get(agent.name, 0.0) for s in active)
            if active:
                persistence = sum(s.persistence for s in active) / len(active)
                agent.shock_memory = agent.shock_memory * persistence + direct_effect
            else:
                agent.shock_memory *= 0.60

            stochastic = rng.gauss(0.0, agent.volatility)
            effective_shock = agent.shock_memory * (0.55 + 0.45 * agent.resilience)
            score = agent.structural_growth + effective_shock + stochastic
            raw_weights[agent.name] = agent.share * math.exp(score)

        normalized = _normalize(raw_weights)
        for agent in model_agents:
            agent.share = normalized[agent.name]

        append_rows(year, event_label)

    return rows


def summarize_final_state(rows: List[Dict[str, float | int | str]]) -> List[Dict[str, float | str]]:
    if not rows:
        return []
    final_year = max(int(r["year"]) for r in rows)
    final_rows = [r for r in rows if int(r["year"]) == final_year]
    ranked = sorted(final_rows, key=lambda r: float(r["share"]), reverse=True)
    return [{"rank": i + 1, "agent": r["agent"], "share_pct": r["share_pct"]} for i, r in enumerate(ranked)]


if __name__ == "__main__":
    results = run_simulation()
    for row in summarize_final_state(results):
        print(f"{row['rank']}. {row['agent']}: {row['share_pct']}%")
