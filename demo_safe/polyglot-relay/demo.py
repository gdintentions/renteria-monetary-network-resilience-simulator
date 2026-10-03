from __future__ import annotations
import re
import sys

SAMPLES = {
    ("hello","es"): "hola",
    ("hello","fr"): "bonjour",
    ("hello","ja"): "こんにちは",
    ("thank you","es"): "gracias",
    ("thank you","fr"): "merci",
    ("thank you","ja"): "ありがとう",
}
RISK = {"medical","legal","emergency","bank","password","account"}

def translate(text: str, target: str) -> dict:
    source=text.strip().lower()
    key=(source,target)
    supported=key in SAMPLES
    high_risk=bool(set(re.findall(r"[a-z]+", source)) & RISK)
    if not supported:
        return {"output":"Translation unavailable in this demo-safe fixture.",
                "supported":False,"decision":"review" if high_risk else "block",
                "quality":0.0}
    quality=0.98
    return {"output":SAMPLES[key],"supported":True,
            "decision":"review" if high_risk else "safe","quality":quality}

def self_test():
    assert translate("hello","es")["output"]=="hola"
    assert translate("hello","de")["supported"] is False
    assert translate("legal emergency","es")["decision"]=="review"
    print("polyglot-relay demo-safe self-test: PASS")

if __name__=="__main__":
    if "--self-test" in sys.argv:self_test()
    else:
        for item in [("hello","es"),("thank you","ja"),("unknown phrase","fr")]:
            print(item, translate(*item))
