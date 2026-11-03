import unittest
from qrcn import ClearingNetwork, Transaction


def tx(id="demo-001", cents=1350):
    return Transaction(id, "alice", "bob", cents)


class ClearingTests(unittest.TestCase):
    def test_happy_path_and_exactly_once_local_journal(self):
        n = ClearingNetwork(key=b"x" * 32)
        a = n.clear(tx())
        self.assertEqual(a.status, "accepted")
        self.assertEqual(n.clear(tx()).status, "duplicate_rejected")
        self.assertEqual(n.snapshot()["accepted_cents"], 1350)
        self.assertEqual(n.snapshot()["accepted_count"], 1)

    def test_duplicate_identifier_with_changed_amount_is_rejected(self):
        n = ClearingNetwork(key=b"x" * 32)
        n.clear(tx())
        self.assertEqual(n.clear(tx(cents=2000)).status, "duplicate_rejected")
        self.assertEqual(n.snapshot()["accepted_cents"], 1350)

    def test_tampered_message_never_commits(self):
        n = ClearingNetwork(key=b"x" * 32)
        r = n.clear(tx(), attack="tamper")
        self.assertEqual(r.status, "rejected_integrity")
        self.assertIn("tamper_detected", r.events)
        self.assertEqual(n.snapshot()["accepted_count"], 0)

    def test_old_epoch_authentication_rejected(self):
        n = ClearingNetwork(key=b"x" * 32)
        n.rotate_keys()
        r = n.clear(tx(), attack="stale_tag")
        self.assertEqual(r.status, "rejected_integrity")
        self.assertIn("stale_authentication", r.events)

    def test_outage_reroutes_and_commits_once(self):
        n = ClearingNetwork(key=b"x" * 32)
        n.outage.add("alpha")
        r = n.clear(tx())
        self.assertEqual(r.route, ("beta",))
        self.assertEqual(r.status, "accepted")
        self.assertIn("node_unavailable:alpha", r.events)

    def test_all_nodes_unavailable(self):
        n = ClearingNetwork(key=b"x" * 32)
        n.outage.update(n.nodes)
        self.assertEqual(n.clear(tx()).status, "unavailable")
        self.assertEqual(n.snapshot()["accepted_count"], 0)

    def test_lost_ack_replay_does_not_duplicate(self):
        n = ClearingNetwork(key=b"x" * 32)
        r = n.clear(tx(), attack="drop_after_commit")
        self.assertIn("acknowledgment_lost", r.events)
        self.assertEqual(n.clear(tx()).status, "duplicate_rejected")
        self.assertEqual(n.snapshot()["accepted_count"], 1)

    def test_invalid_transaction(self):
        n = ClearingNetwork(key=b"x" * 32)
        for cents in (0, -1, True, 2.5):
            with self.assertRaises(ValueError):
                n.clear(tx(cents=cents))

    def test_invalid_key_and_nodes(self):
        with self.assertRaises(ValueError):
            ClearingNetwork(nodes=("a", "a"), key=b"x" * 32)
        with self.assertRaises(ValueError):
            ClearingNetwork(key=b"small")


if __name__ == "__main__":
    unittest.main()
