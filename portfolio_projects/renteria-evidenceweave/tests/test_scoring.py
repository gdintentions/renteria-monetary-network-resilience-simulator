from evidenceweave.scoring import cosine_text, evidence_integrity


def test_cosine_relevance_orders_overlap():
    assert cosine_text("model accuracy", "model accuracy is high") > cosine_text(
        "model accuracy", "unrelated weather report"
    )


def test_contradiction_lowers_integrity():
    base = {
        "semantic": 0.8,
        "graph_support": 0.8,
        "cross_modal": 0.7,
        "source_reliability": 0.9,
        "freshness": 0.9,
        "ambiguity": 0.1,
    }
    clean = evidence_integrity(**base, contradiction=0.0)
    conflicted = evidence_integrity(**base, contradiction=0.8)
    assert clean.integrity > conflicted.integrity
