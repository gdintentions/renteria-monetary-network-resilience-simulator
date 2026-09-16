from __future__ import annotations

import argparse
import json
from pathlib import Path


def wilson(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    spread = z * ((p * (1 - p) / total + z * z / (4 * total * total)) ** 0.5) / denominator
    return center - spread, center + spread


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path, help="JSONL rows with success, steps, latency_ms")
    parser.add_argument("--chart", type=Path, default=Path("artifacts/benchmark.png"))
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.results.read_text().splitlines() if line.strip()]
    successes = sum(bool(row["success"]) for row in rows)
    low, high = wilson(successes, len(rows))
    summary = {
        "tasks": len(rows),
        "success_rate": successes / len(rows) if rows else 0,
        "success_95pct_wilson": [low, high],
        "mean_steps": sum(row["steps"] for row in rows) / len(rows) if rows else 0,
        "mean_latency_ms": sum(row["latency_ms"] for row in rows) / len(rows) if rows else 0,
    }
    print(json.dumps(summary, indent=2))
    try:
        import matplotlib.pyplot as plt

        args.chart.parent.mkdir(parents=True, exist_ok=True)
        labels = ["Success %", "Avg steps", "Latency (s)"]
        values = [summary["success_rate"] * 100, summary["mean_steps"], summary["mean_latency_ms"] / 1000]
        fig, ax = plt.subplots(figsize=(8, 4.5))
        bars = ax.bar(labels, values, color=["#6d5dfc", "#22c55e", "#f59e0b"])
        ax.bar_label(bars, fmt="%.2f")
        ax.set_title("Renteria ArgusLoop Evaluation")
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(args.chart, dpi=160)
    except ImportError:
        pass


if __name__ == "__main__":
    main()

