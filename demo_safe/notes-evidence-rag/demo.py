from __future__ import annotations
import hashlib
import re
import sys

NOTES = {
    "privacy.md":"Local prototypes should avoid collecting unnecessary user data.\nPrivate records require explicit handling boundaries.",
    "governance.md":"Released AI answers should expose supporting evidence.\nUnsupported answers should abstain or enter review.",
}

def passages():
    out=[]
    for source,body in NOTES.items():
        digest=hashlib.sha256(body.encode()).hexdigest()
        for line,text in enumerate(body.splitlines(),1):
            out.append({"id":f"{source}:{line}","source":source,"line":line,
                        "text":text,"sha256":digest})
    return out

def retrieve(question: str):
    q=set(re.findall(r"[a-z]+",question.lower()))
    ranked=[]
    for p in passages():
        terms=q & set(re.findall(r"[a-z]+",p["text"].lower()))
        if terms: ranked.append((len(terms),p,sorted(terms)))
    ranked.sort(key=lambda x:x[0],reverse=True)
    return [{**p,"matched_terms":terms} for _,p,terms in ranked[:3]]

def ask(question: str, generated: str|None=None):
    hits=retrieve(question)
    if not hits:
        return {"mode":"abstained","answer":"No matching evidence found.","citations":[]}
    if generated is None:
        return {"mode":"extractive","answer":"Relevant source excerpts.","citations":hits}
    used=set(re.findall(r"\[([^\[\]]+)\]",generated))
    known={h["id"] for h in hits}
    if not used or not used<=known:
        return {"mode":"review-required","answer":"Draft withheld: citation IDs missing or unknown.","citations":hits}
    return {"mode":"generated-draft","answer":generated,"citations":hits,
            "warning":"Source IDs exist; claim support still requires human review."}

def self_test():
    r=ask("What should unsupported answers do?")
    assert r["mode"]=="extractive" and r["citations"][0]["source"]=="governance.md"
    assert ask("volcanic basalt")["mode"]=="abstained"
    cid=r["citations"][0]["id"]
    assert ask("unsupported answers",f"Abstain [{cid}]")["mode"]=="generated-draft"
    assert ask("unsupported answers","Claim [invented]")["mode"]=="review-required"
    print("notes-evidence-rag demo-safe self-test: PASS")

if __name__=="__main__":
    if "--self-test" in sys.argv:self_test()
    else:
        result=ask("What should unsupported answers do?")
        print(result)
