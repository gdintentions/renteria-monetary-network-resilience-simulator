"""Fixed-parameter historical proxy replay with an explicit persistence comparator."""

import hashlib
import json
from pathlib import Path
from statistics import mean
from simulator import Agent, DEFAULT_AGENTS, run_simulation
from demo.validation import normalize, PROXY_MAP


def replay(start, end, growth_shift=0.0):
    before = normalize({c: start[c] for c in PROXY_MAP})
    actual = normalize({c: end[c] for c in PROXY_MAP})
    defaults = {a.name: a for a in DEFAULT_AGENTS}
    agents = [
        Agent(
            n,
            before[c],
            defaults[n].structural_growth + growth_shift,
            defaults[n].resilience,
            0.0,
        )
        for c, n in PROXY_MAP.items()
    ]
    rows = run_simulation(
        years=end["year"] - start["year"],
        start_year=start["year"],
        seed=42,
        agents=agents,
        shocks=[],
    )
    final = {r["agent"]: r["share"] for r in rows if r["year"] == end["year"]}
    predicted = {c: final[n] for c, n in PROXY_MAP.items()}
    return before, actual, predicted


def evaluate(path=Path("demo/data/bis_fx_history.json")):
    raw = path.read_bytes()
    data = json.loads(raw)
    observations = data["observations"]
    windows = []
    for start, end in zip(observations, observations[1:]):
        before, actual, predicted = replay(start, end)
        _, _, shifted = replay(start, end, growth_shift=0.1)
        errors = {c: abs(predicted[c] - actual[c]) * 100 for c in PROXY_MAP}
        persistence = {c: abs(before[c] - actual[c]) * 100 for c in PROXY_MAP}
        hits = {
            c: (predicted[c] - before[c]) * (actual[c] - before[c]) > 0
            for c in PROXY_MAP
        }
        windows.append(
            {
                "start_year": start["year"],
                "end_year": end["year"],
                "predicted_normalized_shares": predicted,
                "observed_normalized_shares": actual,
                "model_errors_pp": errors,
                "persistence_errors_pp": persistence,
                "model_mae_pp": mean(errors.values()),
                "persistence_mae_pp": mean(persistence.values()),
                "direction_correct": hits,
                "common_growth_shift_max_difference": max(
                    abs(shifted[c] - predicted[c]) for c in PROXY_MAP
                ),
            }
        )
    return {
        "scope": "Retrospective fixed-parameter proxy replays, not forecasts made at those dates; not independent periods or causal validation. CNY is not a BRICS settlement network.",
        "source_file_sha256": hashlib.sha256(raw).hexdigest(),
        "windows": windows,
        "summary": {
            "window_count": len(windows),
            "target_count": len(windows) * 3,
            "model_mae_pp": mean(w["model_mae_pp"] for w in windows),
            "persistence_mae_pp": mean(w["persistence_mae_pp"] for w in windows),
            "model_wins_vs_persistence": sum(
                w["model_mae_pp"] < w["persistence_mae_pp"] for w in windows
            ),
            "direction_accuracy": sum(
                sum(w["direction_correct"].values()) for w in windows
            )
            / (3 * len(windows)),
        },
        "identifiability": "A common additive shift of +0.1 to every structural growth cancels during share normalization. Absolute growth levels are not identifiable from normalized shares alone. Resilience is unidentifiable in this no-shock replay. No parameters were fitted to these targets.",
    }


if __name__ == "__main__":
    result = evaluate()
    Path("artifacts/historical_windows_2026-10-09.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result["summary"], indent=2))
