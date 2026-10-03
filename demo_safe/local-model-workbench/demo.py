from __future__ import annotations
import sys

SYNTHETIC_MODELS = {
    "model-a":{"text":"Synthetic concise answer.","wall_ms":145,"tokens":7},
    "model-b":{"text":"Synthetic structured answer.","wall_ms":210,"tokens":11},
    "model-error":{"error":"Synthetic runtime unavailable."},
}

def run(prompt: str, models: list[str]) -> list[dict]:
    results=[]
    for name in models:
        row={"model":name,"prompt_retained":False}
        fixture=SYNTHETIC_MODELS.get(name,{"error":"Unknown synthetic model."})
        if "error" in fixture:
            row.update({"ok":False,"error":fixture["error"]})
        else:
            row.update({"ok":True,**fixture})
        results.append(row)
    return results

def self_test():
    rows=run("Explain evidence governance.",["model-a","model-error"])
    assert rows[0]["ok"] is True
    assert rows[1]["ok"] is False
    assert all(r["prompt_retained"] is False for r in rows)
    print("local-model-workbench demo-safe self-test: PASS")

if __name__=="__main__":
    if "--self-test" in sys.argv:self_test()
    else:
        print(run("Explain evidence governance.",["model-a","model-b","model-error"]))
        print("All outputs/timings above are synthetic fixtures.")
