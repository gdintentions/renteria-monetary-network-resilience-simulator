import pytest
from engineering import load, save


def test_checkpoints_refuse_overwrite_and_corruption(tmp_path):
    path = tmp_path / "snapshot"
    receipt = save(path, {"synthetic": True})
    assert load(path, receipt) == {"synthetic": True}
    with pytest.raises(FileExistsError):
        save(path, {})
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError):
        load(path, receipt)


def test_qrcn_restore_requires_original_key_and_rejects_replay():
    from qrcn import ClearingNetwork, Transaction

    n = ClearingNetwork(key=b"x" * 32)
    tx = Transaction("fixture", "a", "b", 100)
    n.clear(tx, attack="drop_after_commit")
    n.rotate_keys()
    with pytest.raises(ValueError):
        ClearingNetwork.restore(n.checkpoint(), key=b"y" * 32)
    restored = ClearingNetwork.restore(n.checkpoint(), key=b"x" * 32)
    assert restored.clear(tx).status == "duplicate_rejected"
    assert restored.snapshot() == n.snapshot()


def test_evidence_restore_checks_provenance_before_returning(tmp_path):
    import hashlib
    import json

    from evidenceweave.checkpoint import restore, save
    from evidenceweave.demo_data import build_demo

    n = build_demo()
    path = tmp_path / "evidence"
    receipt = save(n, path)
    assert restore(path, receipt).dashboard_metrics() == n.dashboard_metrics()
    value = json.loads(path.read_text())
    value["claims"][0]["evidence_ids"] = ["absent"]
    raw = json.dumps(value).encode()
    path.write_bytes(raw)
    with pytest.raises(KeyError):
        restore(path, hashlib.sha256(raw).hexdigest())
    assert n.dashboard_metrics()["claims"] == 5


def test_argus_audit_omits_sensitive_free_text(tmp_path):
    from argusloop.audit import AuditLog
    from argusloop.models import Action, StepRecord

    token = "invented sensitive entry"
    one = AuditLog(tmp_path)
    two = AuditLog(tmp_path)
    assert one.path != two.path
    one.append(
        StepRecord(
            step=1,
            action=Action(action="type", text=token, reasoning=token),
            status="blocked",
            observation_hash="fixture",
            latency_ms=0,
            message=token,
        )
    )
    assert token not in one.path.read_text()
    assert one.path.stat().st_mode & 0o777 == 0o600
