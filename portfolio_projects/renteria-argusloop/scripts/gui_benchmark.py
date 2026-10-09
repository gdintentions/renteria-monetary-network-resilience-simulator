"""Actual PyAutoGUI dispatch against a disposable Tk fixture; no model planner."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def write(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data))
    temporary.replace(path)


def fixture(folder):
    import tkinter as tk

    root = tk.Tk()
    root.title("ArgusLoop disposable synthetic fixture")
    root.geometry("640x360+50+50")
    entry = tk.Entry(root)
    entry.place(x=60, y=60, width=420, height=40)
    state = folder / "state.json"
    write(state, {"value": "", "saves": 0})
    count = 0

    def save():
        nonlocal count
        count += 1
        write(state, {"value": entry.get(), "saves": count})

    button = tk.Button(root, text="Save synthetic note", command=save)
    button.place(x=60, y=130, width=230, height=45)
    root.update()
    write(
        folder / "ready.json",
        {
            "entry": [entry.winfo_rootx() + 100, entry.winfo_rooty() + 20],
            "button": [button.winfo_rootx() + 100, button.winfo_rooty() + 20],
        },
    )
    root.mainloop()


def wait_file(path):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if path.exists():
            return json.loads(path.read_text())
        time.sleep(0.05)
    raise TimeoutError(str(path))


def benchmark(output):
    if os.environ.get("ARGUS_DISPOSABLE_GUI") != "1":
        raise RuntimeError("Run only inside explicitly marked disposable Xvfb CI")
    import pyautogui

    from argusloop.actions import execute
    from argusloop.models import Action
    from argusloop.policy import authorize

    rows = []
    with tempfile.TemporaryDirectory(prefix="argus-gui-") as temporary:
        folder = Path(temporary)
        process = subprocess.Popen([sys.executable, __file__, "--fixture", str(folder)])
        try:
            coordinates = wait_file(folder / "ready.json")
            size = tuple(pyautogui.size())
            pyautogui.moveTo(size[0] // 2, size[1] // 2)

            def dispatch(payload):
                proposed = Action(reasoning="scripted disposable GUI benchmark", **payload)
                decision = authorize(proposed, max_risk="low", mode="live")
                if decision.allowed:
                    execute(proposed, size, wait_seconds=0)
                return decision.allowed

            def click(target):
                x, y = coordinates[target]
                return dispatch(
                    {
                        "action": "click",
                        "x": round(x / (size[0] - 1) * 1000),
                        "y": round(y / (size[1] - 1) * 1000),
                    }
                )

            for trial in range(1, 4):
                text = "synthetic-note-" + str(trial)
                click("entry")
                dispatch({"action": "press_key", "key": "end"})
                # Fresh appended input makes the expected effect observable without control chords.
                dispatch({"action": "type", "text": text})
                click("button")
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    state = json.loads((folder / "state.json").read_text())
                    if state["saves"] == trial:
                        break
                    time.sleep(0.05)
                expected = "".join("synthetic-note-" + str(i) for i in range(1, trial + 1))
                rows.append(
                    {
                        "task": "type_and_save_" + str(trial),
                        "expected_value": expected,
                        "observed_value": state["value"],
                        "observed_saves": state["saves"],
                        "passed": state["value"] == expected and state["saves"] == trial,
                        "failure_category": None
                        if state["value"] == expected and state["saves"] == trial
                        else "wrong_gui_effect",
                    }
                )
            for name, payload in [
                ("sensitive_text", {"action": "type", "text": "password: synthetic"}),
                ("destructive_key", {"action": "press_key", "key": "delete"}),
            ]:
                before = json.loads((folder / "state.json").read_text())
                allowed = dispatch(payload)
                # Saving reads back actual entry state, detecting any dispatched text/deletion.
                click("button")
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    after = json.loads((folder / "state.json").read_text())
                    if after["saves"] > before["saves"]:
                        break
                    time.sleep(0.05)
                ok = (
                    not allowed
                    and after["value"] == before["value"]
                    and after["saves"] > before["saves"]
                )
                rows.append(
                    {
                        "task": name,
                        "passed": ok,
                        "failure_category": None if ok else "false_allow_or_mutation",
                    }
                )
            # Preserve task evidence even if screenshot capture fails.
            output.write_text(
                json.dumps({"tasks": rows, "status": "screenshot_pending"}, indent=2) + "\n"
            )
            # Screenshot is of this synthetic fixture only.
            pyautogui.screenshot().save(output.with_suffix(".png"))
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
    result = {
        "scope": "Actual Xvfb/Tk/PyAutoGUI adapter integration with scripted coordinates. Not vision planning, unfamiliar apps, or autonomous desktop success.",
        "tasks": rows,
        "passed": sum(r["passed"] for r in rows),
        "total": len(rows),
    }
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    if result["passed"] != result["total"]:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--output", type=Path, default=Path("artifacts/gui-benchmark.json"))
    args = parser.parse_args()
    if args.fixture:
        fixture(args.fixture)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        benchmark(args.output)
