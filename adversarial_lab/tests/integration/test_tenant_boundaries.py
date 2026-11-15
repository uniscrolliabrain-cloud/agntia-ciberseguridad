import tempfile
import unittest
from pathlib import Path

from support import engagement, experiment, receipt, scope

from agntia_adversarial.store.sqlite import Store, TenantBoundaryError


class TenantBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "lab.sqlite")
        self.store.add_engagement(engagement())
        self.store.add_scope(scope())

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_scope_cannot_belong_to_another_engagement_tenant(self):
        foreign = scope(id="scope-x", tenant_id="tenant-b")
        with self.assertRaises(TenantBoundaryError):
            self.store.add_scope(foreign)

    def test_experiment_cannot_borrow_another_tenant_scope(self):
        self.store.add_experiment(experiment())
        with self.assertRaises(TenantBoundaryError):
            self.store.add_experiment(experiment(id="exp-x", tenant_id="tenant-b"))
        self.assertIsNone(self.store.get_run("tenant-b", "run-1"))

    def test_run_cannot_borrow_another_tenant_experiment(self):
        self.store.add_experiment(experiment())
        with self.assertRaises(TenantBoundaryError):
            self.store.add_run(receipt(tenant_id="tenant-b"))
        self.assertEqual(self.store.count_runs("tenant-b"), 0)
        self.assertEqual(self.store.count_runs("tenant-a"), 0)

    def test_snapshot_is_tenant_scoped(self):
        self.store.add_experiment(experiment())
        self.store.add_run(receipt())
        self.assertEqual(self.store.snapshot("tenant-b"), {"runs": [], "run_count": 0, "ledger_entries": 0})
        self.assertEqual(self.store.snapshot("tenant-a")["run_count"], 1)


if __name__ == "__main__":
    unittest.main()
