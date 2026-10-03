from __future__ import annotations
import sys
import uuid

class Ledger:
    def __init__(self):
        self.memory={}
        self.tasks={}
        self.audit=[]

    def save_memory(self,key,value):
        self.memory[key]=value
        self.audit.append(("memory.save",key))

    def delete_memory(self,key):
        self.memory.pop(key,None)
        self.audit.append(("memory.delete",key))

    def create_task(self,title,kind="reminder"):
        if kind not in {"reminder","external-draft"}: raise ValueError("unsupported task kind")
        ident=uuid.uuid4().hex[:8]
        status="scheduled" if kind=="reminder" else "awaiting-approval"
        self.tasks[ident]={"id":ident,"title":title,"kind":kind,"status":status}
        self.audit.append(("task.create",ident))
        return ident

    def approve(self,ident):
        task=self.tasks[ident]
        if task["status"]!="awaiting-approval": raise ValueError("only pending drafts can be approved")
        task["status"]="approved-draft"
        self.audit.append(("task.approve",ident))

    def cancel(self,ident):
        task=self.tasks[ident]
        if task["status"] in {"completed","cancelled"}: raise ValueError("task already terminal")
        task["status"]="cancelled"
        self.audit.append(("task.cancel",ident))

    def complete_local_reminders(self):
        for ident,task in self.tasks.items():
            if task["status"]=="scheduled":
                task["status"]="completed"
                self.audit.append(("task.local-complete",ident))

def self_test():
    l=Ledger()
    l.save_memory("study-window","afternoon")
    assert "afternoon" not in repr(l.audit)
    reminder=l.create_task("Review notes")
    draft=l.create_task("Draft outreach","external-draft")
    l.approve(draft)
    l.complete_local_reminders()
    assert l.tasks[reminder]["status"]=="completed"
    assert l.tasks[draft]["status"]=="approved-draft"
    print("personal-assistant-ledger demo-safe self-test: PASS")

if __name__=="__main__":
    if "--self-test" in sys.argv:self_test()
    else:
        l=Ledger()
        l.save_memory("example-preference","synthetic value")
        rid=l.create_task("Review portfolio")
        did=l.create_task("Draft recruiter message","external-draft")
        l.approve(did)
        l.complete_local_reminders()
        print({"memory":l.memory,"tasks":l.tasks,"audit":l.audit})
