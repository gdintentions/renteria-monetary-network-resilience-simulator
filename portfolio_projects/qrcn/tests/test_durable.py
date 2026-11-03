"""Phase 2 durability, concurrency and split-brain tests (local SQLite only)."""
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from qrcn.core import Transaction
from qrcn.durable import DurableClearingNetwork, SQLiteJournal, audit_partitions

KEY = b"phase-two-demo-shared-secret-0000000"


def tx(identifier="tx-1", cents=2500):
    return Transaction(identifier, "payer", "payee", cents)


class DurableJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "journal.db"

    def tearDown(self):
        self.tmp.cleanup()

    def journal(self):
        return SQLiteJournal(self.path)

    def network(self, writer_epoch=None):
        return DurableClearingNetwork(
            self.journal(), key=KEY, writer_epoch=writer_epoch
        )

    def test_commit_survives_object_recreation(self):
        first = self.network()
        self.assertEqual(first.clear(tx()).status, "accepted")
        reopened = self.network()
        self.assertEqual(reopened.clear(tx()).status, "duplicate_rejected")
        self.assertEqual(reopened.journal.snapshot()["accepted_cents"], 2500)

    def test_different_payload_same_id_rejected_across_restart(self):
        self.network().clear(tx())
        self.assertEqual(self.network().clear(tx(cents=9000)).status, "duplicate_rejected")
        self.assertEqual(self.journal().snapshot()["accepted_cents"], 2500)

    def test_simulated_crash_before_commit_allows_safe_retry(self):
        r = self.network().clear(tx(), attack="crash_before_commit")
        self.assertEqual(r.status, "interrupted_before_commit")
        self.assertEqual(self.journal().snapshot()["accepted_count"], 0)
        self.assertEqual(self.network().clear(tx()).status, "accepted")

    def test_lost_ack_after_commit_replay_is_rejected(self):
        n = self.network()
        r = n.clear(tx(), attack="drop_after_commit")
        self.assertEqual(r.status, "accepted")
        self.assertIn("acknowledgment_lost", r.events)
        self.assertEqual(self.network().clear(tx()).status, "duplicate_rejected")
        self.assertEqual(self.journal().snapshot()["accepted_count"], 1)

    def test_parallel_threads_single_file_single_commit(self):
        workers = 24
        def attempt(_):
            return self.network().clear(tx()).status
        with ThreadPoolExecutor(max_workers=12) as pool:
            outcomes = list(pool.map(attempt, range(workers)))
        self.assertEqual(outcomes.count("accepted"), 1)
        self.assertEqual(outcomes.count("duplicate_rejected"), workers - 1)
        self.assertEqual(self.journal().snapshot()["accepted_cents"], 2500)

    def test_distinct_ids_concurrent_sum(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            statuses = list(pool.map(lambda i: self.network().clear(tx("t-" + str(i))).status,
                                     range(20)))
        self.assertEqual(statuses, ["accepted"] * 20)
        self.assertEqual(self.journal().snapshot()["accepted_cents"], 50000)

    def test_fencing_epoch_prevents_stale_writer_on_shared_file(self):
        old_writer = self.network()
        epoch = self.journal().advance_epoch()
        self.assertEqual(epoch, 1)
        self.assertEqual(old_writer.clear(tx()).status, "stale_writer_rejected")
        fresh_writer = self.network(writer_epoch=epoch)
        self.assertEqual(fresh_writer.clear(tx()).status, "accepted")
        self.assertEqual(self.journal().snapshot()["accepted_count"], 1)

    def test_tamper_and_outage_do_not_commit(self):
        n = self.network()
        self.assertEqual(n.clear(tx(), attack="tamper").status, "rejected_integrity")
        n.outage.update(n.nodes)
        self.assertEqual(n.clear(tx()).status, "unavailable")
        self.assertEqual(self.journal().snapshot()["accepted_count"], 0)

    def test_split_brain_independent_journals_both_accept(self):
        a = self.journal()
        b = SQLiteJournal(Path(self.tmp.name) / "partition-b.db")
        left = DurableClearingNetwork(a, key=KEY)
        right = DurableClearingNetwork(b, key=KEY)
        self.assertEqual(left.clear(tx()).status, "accepted")
        self.assertEqual(right.clear(tx(cents=9900)).status, "accepted")
        report = audit_partitions((a, b))
        self.assertEqual(report["duplicate_ids"], ["tx-1"])
        self.assertEqual(report["conflicting_ids"], ["tx-1"])
        self.assertTrue(report["requires_adjudication"])
        self.assertFalse(report["automatic_merge_performed"])

    def test_same_payload_independent_journals_still_ambiguous(self):
        a = self.journal()
        b = SQLiteJournal(Path(self.tmp.name) / "other.db")
        DurableClearingNetwork(a, key=KEY).clear(tx())
        DurableClearingNetwork(b, key=KEY).clear(tx())
        report = audit_partitions((a, b))
        self.assertEqual(report["duplicate_ids"], ["tx-1"])
        self.assertEqual(report["conflicting_ids"], [])
        self.assertTrue(report["requires_adjudication"])

    def test_process_restart_rejects_committed_id(self):
        self.network().clear(tx())
        program = (
            "from qrcn.core import Transaction; "
            "from qrcn.durable import SQLiteJournal,DurableClearingNetwork; "
            "import sys; "
            "db=SQLiteJournal(sys.argv[1]); "
            "n=DurableClearingNetwork(db,key=b'phase-two-demo-shared-secret-0000000'); "
            "print(n.clear(Transaction('tx-1','payer','payee',2500)).status)"
        )
        result = subprocess.run(
            [sys.executable, "-c", program, str(self.path)],
            check=True, capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.stdout.strip(), "duplicate_rejected")

    def test_reject_in_memory_database(self):
        with self.assertRaises(ValueError):
            SQLiteJournal(":memory:")


if __name__ == "__main__":
    unittest.main()
