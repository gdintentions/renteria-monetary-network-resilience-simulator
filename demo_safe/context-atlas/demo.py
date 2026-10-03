from __future__ import annotations
import re
import sys

NOTES = {
    "Governance":"AI systems should expose [[Evidence]] and review paths.",
    "Evidence":"Citations and provenance support [[Governance]].",
    "Resilience":"Scenario tests measure stress and recovery.",
    "Draft":"This references [[Missing Note]].",
}
STOP={"this","that","should","and","the","a","an","is","to","of"}

def words(text):
    return {w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP and len(w)>3}

def graph(notes=NOTES):
    explicit=[];broken=[]
    for title,body in notes.items():
        for target in re.findall(r"\[\[([^\]]+)\]\]",body):
            if target in notes: explicit.append((title,target,"explicit wikilink"))
            else: broken.append((title,target))
    suggested=[]
    titles=list(notes)
    for i,a in enumerate(titles):
        for b in titles[i+1:]:
            shared=sorted(words(notes[a]) & words(notes[b]))
            if len(shared)>=2 and not any(x[0]==a and x[1]==b for x in explicit):
                suggested.append((a,b,"shared terms: "+", ".join(shared)))
    return {"explicit":explicit,"suggested":suggested,"broken":broken}

def self_test():
    g=graph()
    assert ("Governance","Evidence","explicit wikilink") in g["explicit"]
    assert ("Draft","Missing Note") in g["broken"]
    print("context-atlas demo-safe self-test: PASS")

if __name__=="__main__":
    if "--self-test" in sys.argv:self_test()
    else: print(graph())
