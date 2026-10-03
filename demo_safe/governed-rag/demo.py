from __future__ import annotations
import math
import re
import sys
from collections import Counter

POLICY = {
    "Vendor Access": "Vendor access requires approval from the internal owner before production access is granted.",
    "External Review": "External document access is logged and reviewed quarterly by the responsible control owner.",
    "Legal Questions": "Legal interpretation questions must be escalated to qualified human review.",
    "Audit Trail": "Released answers retain the question, evidence identifier, confidence, and governance decision.",
}
STOP = {"the","is","a","an","what","who","how","to","of","and","are","be","from"}

def tokens(text: str) -> list[str]:
    return [x for x in re.findall(r"[a-z0-9']+", text.lower()) if x not in STOP]

def cosine(query: str, document: str) -> float:
    q, d = Counter(tokens(query)), Counter(tokens(document))
    terms = set(q) | set(d)
    dot = sum(q[t] * d[t] for t in terms)
    nq = math.sqrt(sum(v*v for v in q.values()))
    nd = math.sqrt(sum(v*v for v in d.values()))
    return dot / (nq * nd) if nq and nd else 0.0

def ask(question: str) -> dict:
    qterms = set(tokens(question))
    ranked = []
    for section, text in POLICY.items():
        matched = qterms & set(tokens(text))
        ranked.append((cosine(question, text), len(matched), section, text, sorted(matched)))
    score, match_count, section, text, matched = max(ranked)
    coverage = match_count / max(len(qterms), 1)
    confidence = round(min(1.0, 0.7 * score + 0.3 * coverage), 3)

    if match_count < 2 or confidence < 0.18:
        return {"decision":"block","answer":"Insufficient approved evidence.","section":None,
                "confidence":confidence,"matched_terms":matched}

    decision = "review" if confidence < 0.42 or "legal" in qterms else "safe"
    return {"decision":decision,"answer":text,"section":section,
            "confidence":confidence,"matched_terms":matched}

def self_test() -> None:
    assert ask("Who approves vendor production access?")["section"] == "Vendor Access"
    assert ask("What is the vacation policy?")["decision"] == "block"
    assert ask("What legal questions require review?")["decision"] == "review"
    print("governed-rag demo-safe self-test: PASS")

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        for q in (
            "Who approves vendor production access?",
            "What legal questions require review?",
            "What is the cafeteria menu?",
        ):
            print("\nQUESTION:", q)
            print(ask(q))
