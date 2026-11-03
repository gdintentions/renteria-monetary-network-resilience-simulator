"""QRCN Phase 3 quorum admission tests: NOT distributed consensus."""
import tempfile
import unittest
from pathlib import Path
from qrcn.core import Transaction
from qrcn.durable import SQLiteJournal
from qrcn.quorum import QuorumClearing

KEY=b"phase3-illustrative-secret-value-0000"
def tx(i="id-1",c=500):
    return Transaction(i,"payer","payee",c)

class QuorumTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.journal=SQLiteJournal(Path(self.temp.name)/"quorum.sqlite")
        self.members=("a","b","c")
    def tearDown(self):
        self.temp.cleanup()
    def q(self,epoch=None):
        return QuorumClearing(self.journal,self.members,key=KEY,epoch=epoch)

    def test_majority_admits_and_commits_once(self):
        r=self.q().clear(tx(),reachable=("a","b"))
        self.assertEqual(r.status,"accepted")
        self.assertEqual(self.journal.snapshot()["accepted_count"],1)
        self.assertEqual(self.q().clear(tx(),reachable=("a","c")).status,"duplicate_rejected")

    def test_minority_fails_closed_without_writing(self):
        r=self.q().clear(tx(),reachable=("b",))
        self.assertEqual(r.status,"quorum_unavailable")
        self.assertEqual(self.journal.snapshot()["accepted_count"],0)

    def test_disjoint_partitions_cannot_both_have_majority(self):
        q=self.q()
        majority=q.clear(tx(),reachable=("a","b"))
        minority=q.clear(tx("minority"),reachable=("c",))
        self.assertEqual(majority.status,"accepted")
        self.assertEqual(minority.status,"quorum_unavailable")
        self.assertEqual(self.journal.snapshot()["accepted_count"],1)

    def test_all_nodes_down_and_no_writes(self):
        r=self.q().clear(tx(),reachable=())
        self.assertEqual(r.status,"quorum_unavailable")
        self.assertEqual(self.journal.snapshot()["accepted_count"],0)

    def test_epoch_fences_old_coordinator(self):
        old=self.q()
        term=self.journal.advance_epoch()
        self.assertEqual(old.clear(tx(),reachable=self.members).status,"stale_writer_rejected")
        self.assertEqual(self.q(epoch=term).clear(tx(),reachable=("a","b")).status,"accepted")

    def test_overlap_and_two_views_use_same_unique_id_journal(self):
        first=self.q().clear(tx(),reachable=("a","b"))
        second=self.q().clear(tx(c=1500),reachable=("b","c"))
        self.assertEqual((first.status,second.status),("accepted","duplicate_rejected"))
        self.assertEqual(self.journal.snapshot()["accepted_cents"],500)

    def test_five_member_quorum(self):
        five=QuorumClearing(self.journal,("a","b","c","d","e"),key=KEY)
        self.assertEqual(five.majority,3)
        self.assertEqual(five.clear(tx(),reachable=("a","b")).status,"quorum_unavailable")
        self.assertEqual(five.clear(tx(),reachable=("a","c","e")).status,"accepted")

    def test_unknown_member_and_invalid_membership(self):
        with self.assertRaises(ValueError):
            self.q().vote(("unknown",))
        for members in (("a","b"),("a","a","b"),("a","b","c","d")):
            with self.assertRaises(ValueError):
                QuorumClearing(self.journal,members,key=KEY)

    def test_tampered_payload_rejected_even_with_quorum(self):
        r=self.q().clear(tx(),reachable=("a","b"),attack="tamper")
        self.assertEqual(r.status,"rejected_integrity")
        self.assertEqual(self.journal.snapshot()["accepted_count"],0)

    def test_stale_auth_and_quorum_cannot_bypass_integrity(self):
        q=self.q()
        q_backend=q.clear(tx(),reachable=("a","b"),attack="stale_tag")
        self.assertEqual(q_backend.status,"rejected_integrity")
        self.assertEqual(self.journal.snapshot()["accepted_count"],0)
if __name__=="__main__":unittest.main()
