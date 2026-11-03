"""Run an isolated quorum-admission scenario ledger; NOT Raft/Paxos."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from qrcn.core import Transaction
from qrcn.durable import SQLiteJournal
from qrcn.quorum import QuorumClearing

def run():
    with TemporaryDirectory() as root:
        journal=SQLiteJournal(Path(root)/"sim.sqlite")
        key=b"qrcn-phase3-illustrative-not-secret"
        a=QuorumClearing(journal,("alpha","beta","gamma"),key=key)
        tx=lambda ident,cents=1000: Transaction(ident,"payer","recipient",cents)
        minority=a.clear(tx("minority"),reachable=("gamma",))
        majority=a.clear(tx("once"),reachable=("alpha","beta"))
        duplicate=a.clear(tx("once",2000),reachable=("beta","gamma"))
        stale=a
        new_epoch=journal.advance_epoch()
        fenced=stale.clear(tx("fenced"),reachable=("alpha","beta","gamma"))
        active=QuorumClearing(journal,("alpha","beta","gamma"),
                              key=key,epoch=new_epoch)
        after_fence=active.clear(tx("after-fence"),reachable=("beta","gamma"))
        return {
            "demo_only":True,
            "model":"single-process quorum-admission proxy plus shared SQLite journal",
            "actual_distributed_consensus":False,
            "events":{
                "minority_partition":minority.status,
                "majority_partition":majority.status,
                "overlapping_majority_duplicate":duplicate.status,
                "stale_writer_after_term_change":fenced.status,
                "new_writer":after_fence.status},
            "journal":journal.snapshot(),
            "unresolved":"No network voting, replicated log, independent crash safety, consensus election or Byzantine security"
        }
if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
