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

def run(
    question, required_claims, retrieve, grade, search, *,
    allowed_hosts, today=None, web_allowed=False, search_missing=None,
):
    """Adapters are injected. Grades are claims of support, not ground truth.

    Returns cited extracts only; no free-form generation can invent a citation.
    Search receives the question only when callers explicitly permit web use.
    When supplied, search_missing takes precedence and receives only an ordered
    tuple of uncovered claim keys. Callers should use public, predefined keys.
    """
    today=today or date.today()
    if not isinstance(question,str) or not question.strip() or len(question)>2000:raise ValueError("question must contain 1 to 2000 characters")
    if not isinstance(required_claims,(list,tuple)) or not 1<=len(required_claims)<=100 or any(not isinstance(k,str) or not k or len(k)>100 for k in required_claims):
        raise ValueError("explicit required claim keys needed")
    if len(set(required_claims))!=len(required_claims):raise ValueError("duplicate required claim keys")
    if type(web_allowed) is not bool:raise ValueError("web_allowed must be boolean")
    if search_missing is not None and not callable(search_missing):
        raise ValueError("search_missing must be callable")
    events=[];rejected=[];seen=set()
    correction = {}
    def filter_sources(items, expected_origin=None):
        valid=[]
        for index, doc in enumerate(items):
            if index>=100:raise ValueError("at most 100 evidence records per adapter")
            if not isinstance(doc,Evidence):raise ValueError("Evidence records required")
            if not isinstance(doc.id,str) or not doc.id or len(doc.id)>200:raise ValueError("invalid evidence ID")
            if not isinstance(doc.claims,dict) or any(not isinstance(k,str) or not k for k in doc.claims):raise ValueError("claims must be an object with string keys")
            json.dumps(doc.claims,sort_keys=True,allow_nan=False)
            if not all(isinstance(v,str) for v in (doc.text,doc.source,doc.expires,doc.origin)) or len(doc.text)>10000:raise ValueError("invalid evidence fields")
            if doc.id in seen:raise ValueError("duplicate evidence ID")
            seen.add(doc.id)
            url=urlparse(doc.source)
            trusted=url.scheme=="https" and url.hostname in allowed_hosts and not url.username and not url.password
            try:fresh=date.fromisoformat(doc.expires)>=today
            except ValueError:fresh=False
            if (
                not trusted or not fresh or doc.origin not in {"kb", "web"}
                or (expected_origin is not None and doc.origin != expected_origin)
                or not doc.text.strip()
            ):
                rejected.append(doc.id);continue
            valid.append(doc)
        return valid
    def assessed(items):
        if not items:return []
        labels=grade(question,items)
        if not isinstance(labels,dict) or set(labels)!={d.id for d in items} or any(not isinstance(v,str) or v not in {"relevant","partial","irrelevant"} for v in labels.values()):
            raise ValueError("incomplete or invalid evaluator response")
        return [d for d in items if labels[d.id]!="irrelevant"]
    def covered(items):return set().union(*(set(d.claims) for d in items)) if items else set()
    def conflicting_claims(items):
        return [
            key for key in required_claims
            if len({json.dumps(d.claims[key], sort_keys=True) for d in items if key in d.claims}) > 1
        ]

    try:
        local=filter_sources(retrieve(question));events.append("RETRIEVE")
        evidence=assessed(local);events.append("GRADE")
        local_coverage = covered(evidence)
        missing_local = tuple(key for key in required_claims if key not in local_coverage)
        if search_missing is not None:
            correction["missing_local"] = list(missing_local)
            correction["requested"] = []
            if missing_local and web_allowed and not conflicting_claims(evidence):
                events.append("WEB_FALLBACK")
                correction["requested"] = list(missing_local)
                candidates = filter_sources(search_missing(missing_local), expected_origin="web")
                missing_keys = set(missing_local)
                correction["out_of_scope_ids"] = [
                    doc.id for doc in candidates if not missing_keys.intersection(doc.claims)
                ]
                scoped = [doc for doc in candidates if missing_keys.intersection(doc.claims)]
                evidence += assessed(scoped)
        elif missing_local and web_allowed:
            events.append("WEB_FALLBACK")
            evidence+=assessed(filter_sources(search(question)))
    except Exception as exc:
        return {"status":"NEEDS_REVIEW","reason":"ADAPTER_OR_SCHEMA_FAILURE", "error_type":type(exc).__name__,"events":events,"answer":None,
                **({"correction": correction} if correction else {})}
    conflicts = conflicting_claims(evidence)
    missing=sorted(set(required_claims)-covered(evidence))
    trace = {"correction": correction} if correction else {}
    if conflicts or missing:
        return {"status":"NEEDS_REVIEW","reason":"CONFLICT" if conflicts else "MISSING_EVIDENCE",
                "conflicts":conflicts,"missing":missing,"rejected_ids":rejected,"events":events,"answer":None, **trace}
    return {"status":"CITED_EXTRACTS","answer":[{"text":d.text,"citation":d.id,"url":d.source} for d in evidence if set(d.claims)&set(required_claims)],
            "rejected_ids":rejected,"events":events,"basis":"supplied evaluator and claim metadata; human verification still needed", **trace}

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
