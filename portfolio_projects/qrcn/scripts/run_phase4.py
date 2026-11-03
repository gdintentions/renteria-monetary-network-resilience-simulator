"""Deterministic Phase 4 prototype evidence; synthetic transaction values only."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from qrcn.paxos import Acceptor, PartitionNetwork, Proposer, canonical_value

def run():
    with TemporaryDirectory() as root:
        paths={x:Path(root)/(x+".sqlite") for x in "abc"}
        nodes={x:Acceptor(x,p) for x,p in paths.items()}
        net=PartitionNetwork(nodes)
        proposer=Proposer(tuple("abc"),net.call)
        first=canonical_value("synthetic-001",12500)
        competing=canonical_value("synthetic-001",99000)
        net.reachable={"a"}
        minority=proposer.propose("synthetic-001",1,first)
        net.reachable={"a","b"}
        majority=proposer.propose("synthetic-001",2,first)
        nodes["b"]=Acceptor("b",paths["b"])
        net.nodes=nodes
        net.reachable={"b","c"}
        recovery=proposer.propose("synthetic-001",3,competing)
        net.drop_accept={"b","c"}
        missing=proposer.propose("synthetic-002",4,canonical_value("synthetic-002",200))
        return {
            "algorithm":"single-decree Paxos per transaction ID (educational)",
            "prototype_only":True,"real_payment_movement":False,
            "node_storage":"three independent SQLite files",
            "events":{"minority":minority.status,"majority":majority.status,
                      "conflicting_proposal":recovery.status,
                      "original_value_preserved":recovery.chosen_value==first,
                      "accept_quorum_lost":missing.status,
                      "restarted_node_retained_value":nodes["b"].inspect("synthetic-001")["accepted_value"]==first},
            "observed_messages":len(net.trace),
            "unresolved":["No full replicated log or automatic ballots","Unauthenticated localhost transport",
                          "No Byzantine fault tolerance or live payment clearing",
                          "No integrated post-quantum handshake"]}
if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
