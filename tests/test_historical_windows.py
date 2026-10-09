import pytest
from demo.historical_windows import evaluate, replay
from demo.validation import historical_proxy_backtest


def test_original_window_reproduced_and_persistence_uses_only_start():
    result = evaluate()
    last = result["windows"][-1]
    assert last["model_mae_pp"] == pytest.approx(historical_proxy_backtest()["mae_pp"])
    assert result["summary"]["window_count"] == 4
    assert all(
        w["common_growth_shift_max_difference"] < 1e-6 for w in result["windows"]
    )


def test_changing_target_cannot_change_prediction():
    start = {"year": 2022, "USD": 88.4, "EUR": 30.6, "CNY": 7}
    a = {"year": 2025, "USD": 89.2, "EUR": 28.9, "CNY": 8.5}
    b = {**a, "CNY": 40}
    assert replay(start, a)[2] == replay(start, b)[2]
