"""Corrective evidence workflow with trusted-source and coverage gates."""
import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

@dataclass(frozen=True)
class Evidence:
    id: str
    text: str
    source: str
    expires: str
    claims: dict
    origin: str = "kb"

def run(question, required_claims, retrieve, grade, search, *, allowed_hosts, today=None, web_allowed=False):
    """Adapters are injected. Grades are claims of support, not ground truth.

    Returns cited extracts only; no free-form generation can invent a citation.
    Search receives the question only when callers explicitly permit web use.
    """
    today=today or date.today()
    if not question.strip() or not required_claims:raise ValueError("question and explicit required claims needed")
    events=[];rejected=[];seen=set()
    def filter_sources(items):
        valid=[]
        for doc in items:
            if not isinstance(doc,Evidence):raise ValueError("Evidence records required")
            if doc.id in seen:raise ValueError("duplicate evidence ID")
            seen.add(doc.id)
            url=urlparse(doc.source)
            trusted=url.scheme=="https" and url.hostname in allowed_hosts and not url.username and not url.password
            try:fresh=date.fromisoformat(doc.expires)>=today
            except ValueError:fresh=False
            if not trusted or not fresh or doc.origin not in {"kb","web"} or not doc.text.strip():
                rejected.append(doc.id);continue
            valid.append(doc)
        return valid
    def assessed(items):
        if not items:return []
        labels=grade(question,items)
        if set(labels)!={d.id for d in items} or any(v not in {"relevant","partial","irrelevant"} for v in labels.values()):
            raise ValueError("incomplete or invalid evaluator response")
        return [d for d in items if labels[d.id]!="irrelevant"]
    def covered(items):return set().union(*(set(d.claims) for d in items)) if items else set()
    try:
        local=filter_sources(retrieve(question));events.append("RETRIEVE")
        evidence=assessed(local);events.append("GRADE")
        if not set(required_claims)<=covered(evidence) and web_allowed:
            events.append("WEB_FALLBACK")
            evidence+=assessed(filter_sources(search(question)))
    except Exception as exc:
        return {"status":"NEEDS_REVIEW","reason":"ADAPTER_OR_SCHEMA_FAILURE", "error_type":type(exc).__name__,"events":events,"answer":None}
    conflicts=[]
    for key in required_claims:
        values={json.dumps(d.claims[key],sort_keys=True) for d in evidence if key in d.claims}
        if len(values)>1:conflicts.append(key)
    missing=sorted(set(required_claims)-covered(evidence))
    if conflicts or missing:
        return {"status":"NEEDS_REVIEW","reason":"CONFLICT" if conflicts else "MISSING_EVIDENCE",
                "conflicts":conflicts,"missing":missing,"rejected_ids":rejected,"events":events,"answer":None}
    return {"status":"CITED_EXTRACTS","answer":[{"text":d.text,"citation":d.id,"url":d.source} for d in evidence if set(d.claims)&set(required_claims)],
            "rejected_ids":rejected,"events":events,"basis":"supplied evaluator and claim metadata; human verification still needed"}

def demo(mode="complete"):
    # Fixture labels/claims are authored; this is not an independent semantic judge.
    kb=Evidence("kb-access","Fictional vendor access requires a sponsor.","https://policy.example/access","2099-01-01",{"approver":"sponsor"})
    web=Evidence("web-duration","Fictional access expires after 14 days.","https://policy.example/duration","2099-01-01",{"duration":14},"web")
    if mode=="conflict":web=Evidence("web-conflict","Fictional approver is IT; access lasts 14 days.",web.source,web.expires,{"approver":"IT","duration":14},"web")
    if mode=="untrusted":web=Evidence(web.id,web.text,"https://unknown.example/rule",web.expires,web.claims,"web")
    return run("Who approves access and for how long?",["approver","duration"],lambda q:[kb],
               lambda q,ds:{d.id:"partial" for d in ds},lambda q:[web],allowed_hosts={"policy.example"},web_allowed=mode!="offline")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=["complete","conflict","untrusted","offline"],default="complete")
    print(json.dumps(demo(p.parse_args().mode),indent=2))
