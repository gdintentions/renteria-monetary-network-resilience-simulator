from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
DEMOS = [
    "governed-rag",
    "governed-rag-model-lab",
    "polyglot-relay",
    "context-atlas",
    "local-model-workbench",
    "notes-evidence-rag",
    "personal-assistant-ledger",
]

def main() -> None:
    failures = []
    for name in DEMOS:
        script = ROOT / name / "demo.py"
        compile_result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            capture_output=True, text=True
        )
        if compile_result.returncode:
            failures.append((name, "compile", compile_result.stderr))
            continue
        result = subprocess.run(
            [sys.executable, str(script), "--self-test"],
            capture_output=True, text=True
        )
        print(result.stdout.strip())
        if result.returncode:
            failures.append((name, "self-test", result.stderr or result.stdout))
    if failures:
        for failure in failures:
            print("FAIL:", failure, file=sys.stderr)
        raise SystemExit(1)
    print(f"demo-safe showcase: PASS ({len(DEMOS)} demos)")

if __name__ == "__main__":
    main()
