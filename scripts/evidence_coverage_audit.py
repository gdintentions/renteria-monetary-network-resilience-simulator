"""Reproduce existing labels and diagnose structured-input coverage without tuning."""

import argparse
import hashlib
import json
import sys
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "portfolio_projects/renteria-evidenceweave/src"))
from evidenceweave.external_eval import parse_triple, weave_from_triples

REVISION = "be7f9c5b7b0c9b6907aeaeeda8bb3c83e6b2e448"
HASHES = {
    "Comp_TextPos.json": "4992e1177e6b20a8089eeca608f4bdea54c063ac66680d6a842b468e7fb2f87c",
    "Comp_TextPos_TripleConf.json": "9d4400923ac8078572e214014e7d4dd54087c16b26ede0afb722b4339d260d89",
}


def load(cache, name):
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / name
    if not path.exists():
        url = f"https://raw.githubusercontent.com/Tianzhe26/ConflictQA/{REVISION}/data/COMP/TripleConf/{name}"
        with urllib.request.urlopen(url, timeout=60) as response:
            path.write_bytes(response.read())
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != HASHES[name]:
        raise ValueError("Frozen benchmark checksum mismatch")
    rows = json.loads(raw)
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate benchmark IDs")
    return {row["id"]: row for row in rows}


def normalized_conflict(triples):
    keys = {}
    for raw in triples:
        parsed = parse_triple(raw)
        if parsed is None:
            raise ValueError("Unparsed triple must not be silently dropped")
        subject, predicate, value = (
            " ".join(unicodedata.normalize("NFKC", x).casefold().split())
            for x in parsed
        )
        keys.setdefault((subject, predicate), set()).add(value)
    return any(len(values) > 1 for values in keys.values())


def run(cache):
    positive = load(cache, "Comp_TextPos.json")
    conflict = load(cache, "Comp_TextPos_TripleConf.json")
    if positive.keys() != conflict.keys():
        raise ValueError("Unmatched paired IDs")
    rows = []
    for item in sorted(positive):
        a, b = positive[item]["positive_triples"], conflict[item]["positive_triples"]
        control = bool(weave_from_triples(item, [("positive", a)]).graph.conflicts())
        mixed = bool(
            weave_from_triples(
                item, [("positive", a), ("conflicting", b)]
            ).graph.conflicts()
        )
        rows.append(
            {
                "id": item,
                "control_flagged": control,
                "conflict_flagged": mixed,
                "normalized_control_flagged": normalized_conflict(a),
                "normalized_conflict_flagged": normalized_conflict(a + b),
            }
        )
    tp = sum(r["conflict_flagged"] for r in rows)
    fp = sum(r["control_flagged"] for r in rows)
    return {
        "dataset_revision": REVISION,
        "sha256": HASHES,
        "paired_items": len(rows),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": len(rows) - tp,
        "normalization_changed_cases": sum(
            r["control_flagged"] != r["normalized_control_flagged"]
            or r["conflict_flagged"] != r["normalized_conflict_flagged"]
            for r in rows
        ),
        "decision": "Do not promote Unicode/whitespace normalization as a measured recall improvement: no cases change. Preserve all 258 misses and all four false positives.",
        "coverage_limit": "The 258 missed items have no differing values under the same normalized subject/predicate in supplied triples. Some known conflicts rely on supplied text or multi-hop facts. This diagnosis does not remove them from the denominator, relabel them, or prove they are impossible to solve.",
        "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.cache)
    (ROOT / "artifacts/evidence_coverage_2026-10-09.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    assert (
        result["paired_items"],
        result["true_positive"],
        result["false_positive"],
    ) == (430, 172, 4)
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))
