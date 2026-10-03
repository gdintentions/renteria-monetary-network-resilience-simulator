from __future__ import annotations
import re
import sys

DOCS = {
    "Vendor Access":"Vendor production access requires internal owner approval.",
    "External Review":"External document access is reviewed quarterly.",
    "Legal Questions":"Legal interpretation requires qualified human review.",
    "Audit Trail":"Released answers retain evidence and governance decisions.",
}
CASES = [
    ("vendor production approval","Vendor Access"),
    ("quarterly external access review","External Review"),
    ("qualified human legal review","Legal Questions"),
    ("retain evidence governance decision","Audit Trail"),
]

def words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def jaccard(a,b):
    x,y=words(a),words(b)
    return len(x&y)/len(x|y) if x|y else 0.0

def trigrams(text):
    s=re.sub(r"\s+"," ",text.lower()).strip()
    return {s[i:i+3] for i in range(max(0,len(s)-2))}

def dice(a,b):
    x,y=trigrams(a),trigrams(b)
    return 2*len(x&y)/(len(x)+len(y)) if x or y else 0.0

def score(model,q,d):
    if model=="jaccard": return jaccard(q,d)
    if model=="trigram": return dice(q,d)
    if model=="hybrid": return 0.65*jaccard(q,d)+0.35*dice(q,d)
    raise ValueError("unknown model")

def predict(model,q):
    return max(DOCS, key=lambda k: score(model,q,DOCS[k]))

def evaluate(model):
    correct=sum(predict(model,q)==expected for q,expected in CASES)
    return {"model":model,"correct":correct,"total":len(CASES),"accuracy":correct/len(CASES)}

def self_test():
    for model in ("jaccard","trigram","hybrid"):
        result=evaluate(model)
        assert result["correct"] >= 3
    print("governed-rag-model-lab demo-safe self-test: PASS")

if __name__=="__main__":
    if "--self-test" in sys.argv:self_test()
    else:
        for model in ("jaccard","trigram","hybrid"): print(evaluate(model))
        print("Toy authored fixture only; not an external model-quality claim.")
