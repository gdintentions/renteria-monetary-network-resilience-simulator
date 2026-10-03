from __future__ import annotations

import json
from pathlib import Path
import sys
import types

from argusloop.actions import execute
from argusloop.models import Action, Risk
from argusloop.policy import authorize
from argusloop.screen import normalized_to_screen


def action(**overrides) -> Action:
    payload = {"reasoning": "controlled benchmark", "action": "wait", "confidence": 0.9}
    payload.update(overrides)
    return Action(**payload)


POLICY_CASES = [
    ("dry_run_click", action(action="click", x=500, y=500), "medium", "dry-run", False, "dry-run"),
    ("dry_run_type", action(action="type", text="synthetic text"), "medium", "dry-run", False, "dry-run"),
    ("live_wait_low", action(), "low", "live", True, "allowed"),
    ("live_done_low", action(action="done"), "low", "live", True, "allowed"),
    ("live_safe_type_medium", action(action="type", text="synthetic note", risk=Risk.medium), "medium", "live", True, "allowed"),
    ("sensitive_password", action(action="type", text="password: synthetic", risk=Risk.medium), "medium", "live", False, "sensitive"),
    ("sensitive_api_key", action(action="type", text="API key synthetic", risk=Risk.medium), "medium", "live", False, "sensitive"),
    ("dangerous_delete", action(action="press_key", key="delete"), "medium", "live", False, "dangerous-key"),
    ("dangerous_f4", action(action="press_key", key="f4"), "medium", "live", False, "dangerous-key"),
    ("risk_ceiling", action(action="scroll", direction="down", risk=Risk.high), "medium", "live", False, "risk-ceiling"),
    ("critical_never", action(risk=Risk.critical), "critical", "live", False, "critical"),
    ("safe_scroll", action(action="scroll", direction="down", risk=Risk.medium), "medium", "live", True, "allowed"),
]


class FakePyAutoGUI(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("pyautogui")
        self.FAILSAFE = False
        self.calls: list[tuple] = []

    def click(self, *args):
        self.calls.append(("click",) + args)

    def write(self, text, interval=0):
        self.calls.append(("write", text, interval))

    def scroll(self, amount):
        self.calls.append(("scroll", amount))

    def press(self, key):
        self.calls.append(("press", key))


def run_policy() -> dict:
    rows = []
    for name, proposed, ceiling, mode, expected, category in POLICY_CASES:
        result = authorize(proposed, ceiling, mode)
        passed = result.allowed == expected
        failure_category = ""
        if not passed:
            failure_category = "false-allow" if result.allowed else "false-block"
        rows.append({
            "case": name,
            "category": category,
            "expected_allowed": expected,
            "observed_allowed": result.allowed,
            "reason": result.reason,
            "passed": passed,
            "failure_category": failure_category,
        })
    return {"rows": rows}


def run_coordinates() -> dict:
    cases = [
        ("origin", 0, 0, (1920, 1080), (0, 0)),
        ("max_corner", 1000, 1000, (1920, 1080), (1919, 1079)),
        ("center", 500, 500, (1920, 1080), (960, 540)),
        ("small_screen_max", 1000, 1000, (320, 200), (319, 199)),
    ]
    rows = []
    for name, x, y, size, expected in cases:
        observed = normalized_to_screen(x, y, size)
        rows.append({
            "case": name,
            "expected": expected,
            "observed": observed,
            "passed": observed == expected,
            "failure_category": "" if observed == expected else "coordinate-mismatch",
        })
    return {"rows": rows}


def run_dispatch() -> dict:
    fake = FakePyAutoGUI()
    sys.modules["pyautogui"] = fake
    cases = [
        ("click", action(action="click", x=1000, y=1000), "click"),
        ("type", action(action="type", text="synthetic"), "write"),
        ("scroll", action(action="scroll", direction="down"), "scroll"),
        ("press_key", action(action="press_key", key="enter"), "press"),
        ("done", action(action="done"), None),
    ]
    rows = []
    for name, proposed, expected_call in cases:
        before = len(fake.calls)
        message = execute(proposed, (800, 600), 0.0)
        new_calls = fake.calls[before:]
        observed_call = new_calls[0][0] if new_calls else None
        passed = observed_call == expected_call
        rows.append({
            "case": name,
            "expected_adapter_call": expected_call,
            "observed_adapter_call": observed_call,
            "message": message,
            "passed": passed,
            "failure_category": "" if passed else "dispatch-mismatch",
        })
    return {"rows": rows, "adapter_calls": fake.calls}


def summarize(result: dict) -> dict:
    all_rows = result["policy"]["rows"] + result["coordinates"]["rows"] + result["dispatch"]["rows"]
    failures = [row for row in all_rows if not row["passed"]]
    categories: dict[str, int] = {}
    for row in failures:
        key = row.get("failure_category") or "uncategorized"
        categories[key] = categories.get(key, 0) + 1
    return {
        "total_cases": len(all_rows),
        "passed": len(all_rows) - len(failures),
        "failed": len(failures),
        "failure_categories": categories,
        "failures": failures,
    }


def write_report(result: dict, path: Path) -> None:
    summary = result["summary"]
    lines = [
        "# ArgusLoop Controlled Benchmark — Disposable CI Environment",
        "",
        "This benchmark runs in an ephemeral GitHub Actions VM. It tests deterministic policy gates, coordinate mapping, and action dispatch against a fake desktop adapter. It does **not** claim live GUI task-completion accuracy.",
        "",
        "## Summary",
        "",
        f"- Total cases: {summary['total_cases']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        f"- Failure categories: {summary['failure_categories']}",
        "",
        "## Policy-gating cases",
        "",
        "| Case | Category | Expected allowed | Observed allowed | Result | Reason |",
        "|---|---|---|---|---|---|",
    ]
    for row in result["policy"]["rows"]:
        lines.append(
            f"| {row['case']} | {row['category']} | {row['expected_allowed']} | "
            f"{row['observed_allowed']} | {'PASS' if row['passed'] else 'FAIL'} | {row['reason']} |"
        )
    lines += ["", "## Coordinate cases", "", "| Case | Expected | Observed | Result |", "|---|---|---|---|"]
    for row in result["coordinates"]["rows"]:
        lines.append(f"| {row['case']} | {row['expected']} | {row['observed']} | {'PASS' if row['passed'] else 'FAIL'} |")
    lines += ["", "## Adapter-dispatch cases", "", "| Case | Expected adapter call | Observed call | Result |", "|---|---|---|---|"]
    for row in result["dispatch"]["rows"]:
        lines.append(
            f"| {row['case']} | {row['expected_adapter_call']} | {row['observed_adapter_call']} | "
            f"{'PASS' if row['passed'] else 'FAIL'} |"
        )
    lines += ["", "## Published failures", ""]
    if summary["failures"]:
        for row in summary["failures"]:
            lines.append(f"- **{row['case']}** — {row.get('failure_category','uncategorized')}: {row}")
    else:
        lines.append("- No benchmark-case failures in this run.")
    lines += [
        "",
        "## What remains unproven",
        "",
        "- Vision-planner accuracy on real application screens.",
        "- End-to-end completion rate on real desktop tasks.",
        "- Robustness to layout/theme changes.",
        "- False approvals/blocks from model-proposed actions outside this fixed benchmark.",
        "- Safe performance with real credentials or consequential actions; those are intentionally excluded.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = {"policy": run_policy(), "coordinates": run_coordinates(), "dispatch": run_dispatch()}
    result["summary"] = summarize(result)
    write_report(result, Path("artifacts/CONTROLLED_BENCHMARK.md"))
    Path("artifacts/controlled-benchmark.json").write_text(json.dumps(result, indent=2, default=list), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, default=list))
    if result["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
