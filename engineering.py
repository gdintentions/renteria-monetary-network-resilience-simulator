"""Bounded synthetic replay and private checkpoints; never restores external side effects."""

import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

MAX_BYTES = 1_000_000


def canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()


def save(path, payload):
    raw = canonical({"version": 1, "payload": payload})
    if len(raw) > MAX_BYTES:
        raise ValueError("Checkpoint size limit")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return hashlib.sha256(raw).hexdigest()


def load(path, expected_sha256):
    with open(path, "rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES or hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError(
            "Checkpoint does not match separately retained SHA-256 receipt"
        )
    value = json.loads(
        raw,
        parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Non-finite JSON")),
    )
    if set(value) != {"version", "payload"} or value["version"] != 1:
        raise ValueError("Checkpoint version/schema")
    return value["payload"]


def child_limits():
    resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))


def replay(root, project, fixture):
    proc = subprocess.run(
        [sys.executable, str(root / "engineering.py"), "--child", project],
        input=canonical(fixture),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=root,
        timeout=30,
        preexec_fn=child_limits,
    )
    if proc.returncode:
        raise RuntimeError("Bounded child failed: " + proc.stderr.decode()[-800:])
    if len(proc.stdout) > MAX_BYTES:
        raise ValueError("Output limit")
    return json.loads(proc.stdout)


def drill(root, project, fixture, output, revision):
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    result = {
        "project": project,
        "source_revision": revision,
        "scope": "authored synthetic process/replay/restore drill",
        "human_participants": 0,
        "independent_review_completed": False,
        "production_ready": False,
        "bounds": {
            "wall_seconds_per_process": 30,
            "cpu_seconds": 20,
            "memory_bytes": 2 * 1024**3,
            "checkpoint_bytes": MAX_BYTES,
        },
        "checks": [],
        "source_hashes": {},
    }
    # Include local project sources and harness; exclude environment, generated evidence, dependencies.
    for p in sorted(root.rglob("*")):
        if (
            not p.is_file()
            or p.suffix not in (".py", ".js", ".jsx")
            and p.name not in ("package.json", "package-lock.json")
        ):
            continue
        if any(
            x in p.parts
            for x in (
                "node_modules",
                ".git",
                "artifacts",
                "__pycache__",
                ".pytest_cache",
                "dist",
                "vendor",
            )
        ):
            continue
        if p.stat().st_size > MAX_BYTES:
            continue
        result["source_hashes"][str(p.relative_to(root))] = hashlib.sha256(
            p.read_bytes()
        ).hexdigest()

    def check(name, passed):
        result["checks"].append({"name": name, "passed": bool(passed)})
        if not passed:
            raise RuntimeError(name)

    start = time.monotonic()
    try:
        first = replay(root, project, fixture)
        with tempfile.TemporaryDirectory(prefix="portfolio-checkpoint-") as temp:
            path = Path(temp) / "snapshot.json"
            receipt = save(path, fixture)
            try:
                save(path, fixture)
            except FileExistsError:
                check("overwrite_refused", True)
            else:
                check("overwrite_refused", False)
            restored = load(path, receipt)
            check(
                "separate_process_replay_matches",
                replay(root, project, restored) == first,
            )
            raw = path.read_bytes()
            path.write_bytes(raw + b" ")
            try:
                load(path, receipt)
            except ValueError:
                check("tamper_rejected", True)
            else:
                check("tamper_rejected", False)
            destination = Path(temp) / "restored.json"
            save(destination, restored)
            check(
                "separate_destination_restore_matches",
                replay(root, project, load(destination, receipt)) == first,
            )
        result["observed_result"] = first
        result["checkpoint_receipt_sha256"] = receipt
        result["status"] = "passed"
    except Exception as exc:
        result["status"] = "failed"
        result["failure"] = {"type": type(exc).__name__, "message": str(exc)[:1000]}
    result["elapsed_seconds"] = time.monotonic() - start
    (output / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "project": project,
                "status": result["status"],
                "checks": len(result["checks"]),
            }
        )
    )
    return result


if __name__ == "__main__":
    from engineering_scenarios import FIXTURES, execute

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child")
    parser.add_argument("--project")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--source-revision")
    a = parser.parse_args()
    root = Path(__file__).resolve().parent
    if a.child:
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Input limit")
        print(
            json.dumps(
                execute(a.child, json.loads(raw)), sort_keys=True, allow_nan=False
            )
        )
    else:
        if not a.output_dir or not a.source_revision or a.project not in FIXTURES:
            parser.error("project, new output-dir and source-revision required")
        report = drill(
            root, a.project, FIXTURES[a.project], a.output_dir, a.source_revision
        )
        sys.exit(report["status"] != "passed")
