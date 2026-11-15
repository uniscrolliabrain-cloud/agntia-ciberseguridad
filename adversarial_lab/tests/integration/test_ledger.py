import tempfile
import unittest
from pathlib import Path

from support import engagement, scope

from agntia_adversarial.contracts.result import Status
from agntia_adversarial.ledger.transitions import can_transition
from agntia_adversarial.store.sqlite import Store


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "lab.sqlite")
        self.store.add_engagement(engagement())
        self.store.add_scope(scope())

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_tenant_isolation(self):
        self.assertEqual(self.store.list_run_ids("tenant-a"), [])
        self.assertEqual(self.store.list_run_ids("tenant-b"), [])
        self.assertEqual(self.store.count_runs("tenant-b"), 0)

    def test_transition_rules(self):
        self.assertTrue(can_transition(Status.NOT_RUN, Status.PASS))
        self.assertTrue(can_transition(Status.PARTIAL, Status.PASS))
        self.assertFalse(can_transition(Status.PASS, Status.NOT_RUN))

    def test_ledger_records_transition(self):
        self.store.record_transition("run-1", "NOT_RUN", "PARTIAL", "tools blocked")
        entries = self.store.ledger("run-1")
        self.assertEqual(entries[0]["to_status"], "PARTIAL")


if __name__ == "__main__":
    unittest.main()
