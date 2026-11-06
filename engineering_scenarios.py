"""Allowlisted invented workflows. No provider credentials or live desktop actions."""

import asyncio
import hashlib
import importlib.util
import json
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for name in ("renteria-tracelens", "renteria-continuity-router", "renteria-sourcegate"):
    sys.path.insert(0, str(ROOT / "portfolio_projects" / name))
sys.path.insert(0, str(ROOT / "reliability_lab"))
for name in ("renteria-evidenceweave", "renteria-argusloop"):
    sys.path.insert(0, str(ROOT / "portfolio_projects" / name / "src"))
sys.path.insert(0, str(ROOT / "portfolio_projects/qrcn"))
FIXTURES = {
    "monetary-simulator": {"years": 5, "seed": 42},
    "tracelens": {"project": "tracelens", "scenario": "selection-miss"},
    "continuity-router": {
        "project": "continuity-router",
        "scenario": "failover",
        "classification": "public",
        "budget": 0.08,
    },
    "sourcegate": {
        "project": "sourcegate",
        "scenario": "conflict",
        "web_allowed": True,
    },
    "evidenceweave": {"query": "BGE-M3 accuracy"},
    "argusloop": {"text": "synthetic-password-not-a-real-secret"},
    "qrcn": {
        "transactions": [
            {"tx_id": "invented-1", "payer": "alpha", "payee": "beta", "cents": 100}
        ],
        "key_label": "public-synthetic-fixture-only",
    },
}


def stable(value):
    if isinstance(value, dict):
        return {
            k: stable(v)
            for k, v in value.items()
            if k not in {"elapsed_s", "latency_ms", "timestamp"}
        }
    if isinstance(value, (tuple, list)):
        return [stable(v) for v in value]
    return value


def execute(project, fixture):
    if project not in FIXTURES:
        raise ValueError("Unknown project")
    if project in ("tracelens", "continuity-router", "sourcegate"):
        from scenarios import execute as run

        result = stable(asyncio.run(run(fixture)))
        if project == "continuity-router":
            restricted = {**fixture, "classification": "restricted"}
            result["restricted_probe"] = stable(asyncio.run(run(restricted)))
        return result
    if project == "monetary-simulator":
        from simulator import run_simulation

        rows = run_simulation(**fixture)
        assert rows
        rejected = False
        try:
            run_simulation(years=101)
        except ValueError:
            rejected = True
        assert rejected
        return {"rows": rows, "oversize_rejected": rejected, "forecast_claim": False}
    if project == "evidenceweave":
        from evidenceweave.demo_data import build_demo
        from evidenceweave.models import Claim

        original = build_demo()
        from evidenceweave.checkpoint import restore, save

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "provenance.json"
            receipt = save(original, path)
            restored = restore(path, receipt)
            state = json.loads(path.read_text())
        answer = asdict(restored.query(fixture["query"]))
        assert (
            answer == asdict(original.query(fixture["query"])) and answer["conflicts"]
        )
        refused = False
        try:
            restored.add_claim(Claim("missing", "x", "y", "z", ["absent"]))
        except KeyError:
            refused = True
        assert refused
        return {
            "answer": answer,
            "restored_state": state,
            "missing_provenance_rejected": refused,
        }
    if project == "qrcn":
        from qrcn.core import ClearingNetwork, Transaction

        key = hashlib.sha256(fixture["key_label"].encode()).digest()
        network = ClearingNetwork(key=key)
        for row in fixture["transactions"]:
            assert (
                network.clear(Transaction(**row), attack="drop_after_commit").status
                == "accepted"
            )
        network.rotate_keys()
        network.outage.add("alpha")
        restored = ClearingNetwork.restore(network.checkpoint(), key=key)
        assert restored.snapshot() == network.snapshot()
        assert (
            restored.clear(Transaction(**fixture["transactions"][0])).status
            == "duplicate_rejected"
        )
        altered = json.loads(network.checkpoint())
        altered["payload"]["records"][0]["cents"] += 1
        refused = False
        try:
            ClearingNetwork.restore(json.dumps(altered).encode(), key=key)
        except ValueError:
            refused = True
        assert refused
        return {
            "snapshot": restored.snapshot(),
            "restart_replay_rejected": True,
            "tamper_rejected": refused,
            "security_scope": "in-process toy HMAC only",
        }
    if project == "argusloop":
        from argusloop.audit import AuditLog
        from argusloop.models import Action, StepRecord

        spec = importlib.util.spec_from_file_location(
            "controlled_benchmark",
            ROOT
            / "portfolio_projects/renteria-argusloop/scripts/controlled_benchmark.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        benchmarks = {
            "policy": module.run_policy(),
            "coordinates": module.run_coordinates(),
            "dispatch": module.run_dispatch(),
        }
        summary = module.summarize(benchmarks)
        assert summary["failed"] == 0
        with tempfile.TemporaryDirectory() as d:
            audit = AuditLog(Path(d))
            other = AuditLog(Path(d))
            assert audit.path != other.path
            audit.append(
                StepRecord(
                    step=1,
                    action=Action(
                        action="type", text=fixture["text"], reasoning=fixture["text"]
                    ),
                    status="blocked",
                    observation_hash="fixture",
                    latency_ms=0,
                    message=fixture["text"],
                )
            )
            raw = audit.path.read_text()
            assert fixture["text"] not in raw
            assert audit.path.stat().st_mode & 0o777 == 0o600
            event = json.loads(raw)
        return {
            "benchmark_summary": summary,
            "audit_content_redacted": True,
            "audit_unique_private_files": True,
            "event": stable(event),
            "external_actions_replayed": False,
        }
