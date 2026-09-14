from demo.hardening import (
    DEFAULT_COUNTRIES,
    calibrated_agents,
    concentration_metrics,
    country_exposures,
    network_edges,
    run_monte_carlo,
)
from simulator import DEFAULT_AGENTS, run_simulation


def test_zero_weight_preserves_original_starting_shares():
    calibrated = calibrated_agents(0.0)
    assert [round(a.share, 8) for a in calibrated] == [
        round(a.share, 8) for a in DEFAULT_AGENTS
    ]


def test_calibrated_shares_stay_normalized():
    calibrated = calibrated_agents(0.30)
    assert abs(sum(a.share for a in calibrated) - 1.0) < 1e-12


def test_monte_carlo_band_ordering_and_shape():
    bands = run_monte_carlo(runs=20, years=10, start_year=2026, seed=7)
    assert len(bands) == (10 + 1) * len(DEFAULT_AGENTS)
    for row in bands:
        assert row["p10"] <= row["median"] <= row["p90"]


def test_country_exposures_normalize_per_country():
    rows = run_simulation(years=10, start_year=2026, seed=42)
    exposures = country_exposures(rows)
    assert len({row["country"] for row in exposures}) == len(DEFAULT_COUNTRIES)
    for country in {row["country"] for row in exposures}:
        total = sum(
            float(row["exposure"])
            for row in exposures
            if row["country"] == country
        )
        assert abs(total - 1.0) < 1e-5


def test_network_graph_edges_use_valid_nodes():
    rows = run_simulation(years=10, start_year=2026, seed=42)
    exposures = country_exposures(rows)
    edges = network_edges(exposures, top_n=2)
    assert len(edges) == len(DEFAULT_COUNTRIES) * 2
    assert all(float(edge["weight"]) > 0 for edge in edges)


def test_concentration_metrics_are_bounded():
    rows = run_simulation(years=10, start_year=2026, seed=42)
    metrics = concentration_metrics(rows)
    assert 0 < metrics["hhi"] <= 1
    assert 0 <= metrics["diversification_index"] <= 1
    assert metrics["effective_networks"] >= 1
