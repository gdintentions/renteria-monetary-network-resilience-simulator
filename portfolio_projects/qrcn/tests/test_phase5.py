"""Phase 5 adversarial single-decree schedules and persistent ballot tests.

These tests enumerate selected executions; they do not model-check the protocol.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from qrcn.ballots import DurableBallots
from qrcn.paxos import Acceptor, PartitionNetwork, Proposer, canonical_value


class Phase5BallotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.members = ("proposer-a", "proposer-b", "proposer-c")

    def allocator(self, identity):
        return DurableBallots(identity, self.members, self.root / (identity + ".sqlite"))

    def test_distinct_proposers_generate_distinct_ballots(self):
        a, b = self.allocator("proposer-a"), self.allocator("proposer-b")
        values = [a.next_ballot(), b.next_ballot(), b.next_ballot(), a.next_ballot()]
        self.assertEqual(len(values), len(set(values)))

    def test_restart_keeps_counter_monotonic(self):
        ballot = self.allocator("proposer-a").next_ballot()
        self.assertGreater(self.allocator("proposer-a").next_ballot(), ballot)

    def test_observed_higher_ballot_is_exceeded(self):
        a = self.allocator("proposer-a")
        self.assertGreater(a.next_ballot(greater_than=999), 999)
        self.assertGreater(a.next_ballot(), 999)

    def test_reject_identity_reuse_and_membership_change(self):
        path = self.root / "ballots.sqlite"
        DurableBallots("proposer-a", self.members, path)
        with self.assertRaises(ValueError):
            DurableBallots("proposer-b", self.members, path)
        with self.assertRaises(ValueError):
            DurableBallots("proposer-a", ("proposer-a", "proposer-b"), path)

    def test_invalid_counter_arguments(self):
        a = self.allocator("proposer-a")
        with self.assertRaises(ValueError):
            a.next_ballot(True)
        with self.assertRaises(ValueError):
            a.next_ballot(-2)


class Phase5InterleavingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.nodes = {n: Acceptor(n, root / (n + ".db")) for n in "abc"}
        self.net = PartitionNetwork(self.nodes)
        self.first = canonical_value("synthetic-5", 100)
        self.second = canonical_value("synthetic-5", 200)
        members = ("proposer-a", "proposer-b", "proposer-c")
        self.low = DurableBallots("proposer-a", members, root / "pa.db").next_ballot()
        self.high = DurableBallots("proposer-b", members, root / "pb.db").next_ballot()
        self.assertGreater(self.high, self.low)

    def test_higher_proposer_preempts_before_low_accept(self):
        triggered = []
        def interleaved(node, op, slot, ballot, value):
            result = self.net.call(node, op, slot, ballot, value)
            if op == "prepare" and node == "b" and ballot == self.low and not triggered:
                triggered.append(Proposer(tuple("abc"), self.net.call).propose(slot, self.high, self.second))
            return result
        outer = Proposer(tuple("abc"), interleaved).propose("synthetic-5", self.low, self.first)
        self.assertEqual(triggered[0].chosen_value, self.second)
        self.assertEqual(outer.status, "no_accept_quorum")
        recovered = Proposer(tuple("abc"), self.net.call).propose("synthetic-5", self.high + 3, self.first)
        self.assertEqual(recovered.chosen_value, self.second)

    def test_high_ballot_adopts_low_chosen_value_after_accept_majority(self):
        triggered = []
        def interleaved(node, op, slot, ballot, value):
            result = self.net.call(node, op, slot, ballot, value)
            if op == "accept" and node == "b" and ballot == self.low and not triggered:
                triggered.append(Proposer(tuple("abc"), self.net.call).propose(slot, self.high, self.second))
            return result
        outer = Proposer(tuple("abc"), interleaved).propose("synthetic-5", self.low, self.first)
        self.assertEqual(outer.chosen_value, self.first)
        self.assertEqual(triggered[0].chosen_value, self.first)
        self.assertTrue(triggered[0].adopted_prior)

    def test_crash_and_partition_keep_majority_intersection(self):
        self.net.reachable = {"a", "b"}
        first = Proposer(tuple("abc"), self.net.call).propose("synthetic-5", self.low, self.first)
        self.assertEqual(first.chosen_value, self.first)
        self.nodes["b"] = Acceptor("b", self.nodes["b"].path)
        self.net.nodes = self.nodes
        self.net.reachable = {"b", "c"}
        result = Proposer(tuple("abc"), self.net.call).propose("synthetic-5", self.high, self.second)
        self.assertEqual(result.chosen_value, self.first)

    def test_minority_cannot_choose(self):
        self.net.reachable = {"c"}
        self.assertEqual(Proposer(tuple("abc"), self.net.call).propose(
            "synthetic-5", self.high, self.second).status, "no_prepare_quorum")


if __name__ == "__main__":
    unittest.main()
