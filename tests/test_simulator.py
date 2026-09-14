from simulator import run_simulation, summarize_final_state


def test_shares_sum_to_one_each_year():
    rows = run_simulation(years=12, start_year=2026, seed=7)
    years = sorted({int(r["year"]) for r in rows})
    for year in years:
        total = sum(float(r["share"]) for r in rows if int(r["year"]) == year)
        assert abs(total - 1.0) < 1e-5


def test_simulation_is_reproducible_for_same_seed():
    first = run_simulation(years=10, seed=123)
    second = run_simulation(years=10, seed=123)
    assert first == second


def test_summary_contains_all_agents():
    rows = run_simulation(years=10)
    summary = summarize_final_state(rows)
    assert len(summary) == 6
    assert summary[0]["rank"] == 1
    assert summary[-1]["rank"] == 6


def test_horizon_validation():
    try:
        run_simulation(years=0)
    except ValueError as exc:
        assert "years must be >= 1" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
