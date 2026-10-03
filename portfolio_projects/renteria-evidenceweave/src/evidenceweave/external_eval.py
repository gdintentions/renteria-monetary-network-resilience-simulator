from __future__ import annotations

import json
from pathlib import Path
import re
import urllib.request

from .models import Claim, EvidenceBlock, Modality, Source
from .pipeline import EvidenceWeave

BASE = "https://raw.githubusercontent.com/Tianzhe26/ConflictQA/main/data/COMP/TripleConf"
POS_URL = BASE + "/Comp_TextPos.json"
CONF_URL = BASE + "/Comp_TextPos_TripleConf.json"
TRIPLE = re.compile(r"^\((.*?),\s*([^,]+),\s*(.*?)\)$")


def download_json(url: str) -> list[dict]:
    request = urllib.request.Request(url, headers={"User-Agent": "evidenceweave-eval/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_triple(text: str) -> tuple[str, str, str] | None:
    match = TRIPLE.match(text.strip())
    if not match:
        return None
    return tuple(part.strip() for part in match.groups())


def weave_from_triples(item_id: str, groups: list[tuple[str, list[str]]]) -> EvidenceWeave:
    weave = EvidenceWeave()
    for source_id, _triples in groups:
        weave.add_source(Source(source_id, source_id, authority=0.8, freshness=1.0))
    index = 0
    for source_id, triples in groups:
        for raw in triples:
            parsed = parse_triple(raw)
            if not parsed:
                continue
            subject, predicate, value = parsed
            block_id = f"{item_id}:b{index}"
            claim_id = f"{item_id}:c{index}"
            weave.add_block(EvidenceBlock(block_id, source_id, Modality.table, raw))
            weave.add_claim(Claim(claim_id, subject, predicate, value, [block_id]))
            index += 1
    return weave


def evaluate() -> dict:
    positive = {row["id"]: row for row in download_json(POS_URL)}
    conflict = {row["id"]: row for row in download_json(CONF_URL)}
    shared = sorted(set(positive) & set(conflict))

    tp = fp = tn = fn = 0
    failures = []
    for item_id in shared:
        pos = positive[item_id]
        conf = conflict[item_id]

        control = weave_from_triples(
            item_id + ":control",
            [("positive", pos.get("positive_triples", []))],
        )
        control_detected = bool(control.graph.conflicts())
        if control_detected:
            fp += 1
            failures.append({
                "id": item_id,
                "case": "positive-control",
                "failure_category": "false-positive-conflict",
                "conflicts": control.graph.conflicts(),
            })
        else:
            tn += 1

        mixed = weave_from_triples(
            item_id + ":conflict",
            [
                ("positive", pos.get("positive_triples", [])),
                ("conflicting", conf.get("positive_triples", [])),
            ],
        )
        conflict_detected = bool(mixed.graph.conflicts())
        if conflict_detected:
            tp += 1
        else:
            fn += 1
            failures.append({
                "id": item_id,
                "case": "known-conflict",
                "failure_category": "missed-conflict",
                "positive_triples": pos.get("positive_triples", [])[:6],
                "conflicting_triples": conf.get("positive_triples", [])[:6],
            })

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "dataset": "ConflictQA COMP/TripleConf",
        "paired_items": len(shared),
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "failure_count": len(failures),
        "failures": failures,
        "evaluation_boundary": (
            "Tests EvidenceWeave conflict surfacing after structured triples are normalized into claims. "
            "It does not evaluate free-text contradiction extraction or LLM reasoning."
        ),
    }


def write_report(result: dict, path: Path) -> None:
    lines = [
        "# EvidenceWeave External Conflict Evaluation — ConflictQA",
        "",
        result["evaluation_boundary"],
        "",
        "ConflictQA labels the paired file as KG/triple-conflict evidence. The positive-only counterpart is used as a non-conflict control.",
        "",
        "## Results",
        "",
        f"- Paired benchmark items: {result['paired_items']}",
        f"- Precision: {result['precision']:.4f}",
        f"- Recall: {result['recall']:.4f}",
        f"- F1: {result['f1']:.4f}",
        f"- True positives: {result['true_positive']}",
        f"- False positives: {result['false_positive']}",
        f"- True negatives: {result['true_negative']}",
        f"- Missed conflicts: {result['false_negative']}",
        "",
        "## Published failures",
        "",
        "| ID | Case | Failure category |",
        "|---|---|---|",
    ]
    for row in result["failures"]:
        lines.append(f"| {row['id']} | {row['case']} | {row['failure_category']} |")
    if not result["failures"]:
        lines.append("| — | — | No failures in this run |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- A missed conflict means the current graph rule did not find two differing values under the same normalized subject/predicate key.",
        "- Some benchmark conflicts are multi-hop or structurally indirect; those are expected to expose the limits of exact-key graph comparison.",
        "- A false positive means multiple values occur in the positive control under the same key; that may represent legitimate multi-valued facts rather than contradiction.",
        "- The next model layer should distinguish mutually exclusive values from legitimate multi-valued relations and add text-level contradiction inference.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = evaluate()
    report = Path("docs/CONFLICTQA_EXTERNAL_EVAL.md")
    write_report(result, report)
    artifact = Path("artifacts/conflictqa-external-eval.json")
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"failures"}}, indent=2))


if __name__ == "__main__":
    main()
