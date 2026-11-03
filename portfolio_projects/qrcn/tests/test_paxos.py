"""Tests for independent durable acceptors: safety scenarios, not proof."""
import tempfile
import unittest
from pathlib import Path
from qrcn.paxos import Acceptor, Proposer, PartitionNetwork, canonical_value

class PaxosPrototypeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.paths={x:Path(self.tmp.name)/(x+".sqlite") for x in "abc"}
        self.nodes={x:Acceptor(x,p) for x,p in self.paths.items()}
        self.net=PartitionNetwork(self.nodes)
        self.proposer=Proposer(tuple("abc"),self.net.call)
        self.v=canonical_value("tx-1",100)
        self.other=canonical_value("tx-1",200)
    def tearDown(self):self.tmp.cleanup()
    def test_majority_chooses_value(self):
        d=self.proposer.propose("tx-1",1,self.v)
        self.assertEqual(d.status,"chosen")
        self.assertEqual(sum(n.inspect("tx-1")["accepted_value"]==self.v for n in self.nodes.values()),3)
    def test_minority_partition_fails_closed(self):
        self.net.reachable={"a"}
        self.assertEqual(self.proposer.propose("tx-1",1,self.v).status,"no_prepare_quorum")
        self.assertFalse(any(x.inspect("tx-1") and x.inspect("tx-1")["accepted_value"] for x in self.nodes.values()))
    def test_partition_majority_adopts_prior(self):
        self.net.reachable={"a","b"}
        self.assertEqual(self.proposer.propose("tx-1",1,self.v).status,"chosen")
        self.net.reachable={"b","c"}
        d=self.proposer.propose("tx-1",2,self.other)
        self.assertEqual((d.status,d.chosen_value),("adopted_prior",self.v))
    def test_restart_preserves_promise_and_value(self):
        self.net.reachable={"a","b"}
        self.proposer.propose("tx-1",10,self.v)
        self.nodes={x:Acceptor(x,p) for x,p in self.paths.items()}
        self.net=PartitionNetwork(self.nodes)
        self.proposer=Proposer(tuple("abc"),self.net.call)
        self.net.reachable={"b","c"}
        self.assertEqual(self.proposer.propose("tx-1",11,self.other).chosen_value,self.v)
        self.assertFalse(self.nodes["b"].prepare("tx-1",5)["ok"])
    def test_prepare_quorum_without_accept_quorum_not_decided(self):
        self.net.drop_accept={"b","c"}
        d=self.proposer.propose("tx-1",1,self.v)
        self.assertEqual(d.status,"no_accept_quorum")
        self.assertIsNone(d.chosen_value)
        self.net.drop_accept.clear()
        d=self.proposer.propose("tx-1",2,self.other)
        self.assertEqual((d.status,d.chosen_value),("adopted_prior",self.v))
    def test_preemption_blocks_stale_ballot(self):
        self.nodes["a"].prepare("tx-1",100)
        self.nodes["b"].prepare("tx-1",100)
        self.assertEqual(self.proposer.propose("tx-1",10,self.v).status,"no_prepare_quorum")
    def test_same_ballot_cannot_accept_different_value(self):
        self.nodes["a"].prepare("tx-1",4)
        self.assertTrue(self.nodes["a"].accept("tx-1",4,self.v)["ok"])
        self.assertFalse(self.nodes["a"].accept("tx-1",4,self.other)["ok"])
    def test_chosen_value_never_changes_sequential_ballots(self):
        self.assertEqual(self.proposer.propose("tx-1",1,self.v).chosen_value,self.v)
        for i in range(2,12):
            self.assertEqual(self.proposer.propose("tx-1",i,self.other).chosen_value,self.v)
    def test_independent_slots(self):
        self.proposer.propose("tx-1",1,self.v)
        other=canonical_value("tx-2",900)
        self.assertEqual(self.proposer.propose("tx-2",1,other).chosen_value,other)
    def test_invalid_value_rejected(self):
        with self.assertRaises(ValueError):canonical_value("id",-1)
        with self.assertRaises(ValueError):self.nodes["a"].accept("tx-1",1,"not-json")
        with self.assertRaises(ValueError):self.proposer.propose("wrong",1,self.v)

if __name__=="__main__":unittest.main()
