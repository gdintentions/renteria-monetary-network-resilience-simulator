from evidenceweave.demo_data import build_demo
from evidenceweave.models import Claim, EvidenceBlock, Modality, Source
from evidenceweave.pipeline import EvidenceWeave


def test_demo_detects_accuracy_conflict():
    answer = build_demo().query("What is BGE-M3 accuracy?")
    assert answer.conflicts
    assert "0.88" in answer.conflicts[0]
    assert "0.91" in answer.conflicts[0]


def test_unknown_source_is_rejected():
    weave = EvidenceWeave()
    block = EvidenceBlock("b", "missing", Modality.text, "some evidence")
    try:
        weave.add_block(block)
    except KeyError as exc:
        assert "unknown source" in str(exc)
    else:
        raise AssertionError("expected unknown source to fail")


def test_claim_requires_known_evidence():
    weave = EvidenceWeave()
    weave.add_source(Source("s", "Source"))
    try:
        weave.add_claim(Claim("c", "x", "is", "y", ["missing"]))
    except KeyError as exc:
        assert "unknown evidence" in str(exc)
    else:
        raise AssertionError("expected unknown evidence to fail")


def test_dashboard_metrics():
    assert build_demo().dashboard_metrics() == {
        "sources": 2,
        "evidence_blocks": 5,
        "claims": 5,
        "conflicts": 1,
        "modalities": 4,
    }

