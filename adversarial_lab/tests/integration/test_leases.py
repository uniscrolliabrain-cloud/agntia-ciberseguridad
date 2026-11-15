import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from support import engagement, experiment, receipt, scope

from agntia_adversarial.planning.leases import LeaseError, LeaseManager
from agntia_adversarial.store.sqlite import Store


class LeaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "lab.sqlite"
        self.store = Store(self.path)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_second_owner_is_denied_while_lease_is_live(self):
        manager = LeaseManager(self.store)
        first = manager.acquire("tenant-a", "repo-review", "worker-1", ttl_seconds=60)
        self.assertIsNotNone(first)
        self.assertIsNone(manager.acquire("tenant-a", "repo-review", "worker-2", ttl_seconds=60))
        self.assertNotEqual(manager.acquire("tenant-b", "repo-review", "worker-2", ttl_seconds=60), None)

    def test_expired_lease_is_taken_over_with_higher_fence(self):
        manager = LeaseManager(self.store)
        past = datetime.now(timezone.utc) - timedelta(minutes=5)
        first = manager.acquire("tenant-a", "repo-review", "worker-1", ttl_seconds=1, now=past)
        takeover = manager.acquire("tenant-a", "repo-review", "worker-2", ttl_seconds=60)
        self.assertEqual(takeover.fence, first.fence + 1)
        self.assertFalse(manager.release(first))
        self.assertFalse(manager.owns(first))
        self.assertIsNone(manager.renew(first))
        self.assertTrue(manager.owns(takeover))

    def test_release_and_idempotent_run_keys(self):
        manager = LeaseManager(self.store)
        lease = manager.acquire("tenant-a", "repo-review", "worker-1")
        self.assertTrue(manager.release(lease))
        run_id, created = manager.register_run("tenant-a", "2026-11-15", "run-1")
        self.assertTrue(created)
        again, created_again = manager.register_run("tenant-a", "2026-11-15", "run-2")
        self.assertFalse(created_again)
        self.assertEqual(again, "run-1")
        self.assertEqual(manager.register_run("tenant-b", "2026-11-15", "run-9")[0], "run-9")

    def test_lease_survives_restart(self):
        LeaseManager(self.store).acquire("tenant-a", "repo-review", "worker-1", ttl_seconds=60)
        second = Store(self.path)
        try:
            manager = LeaseManager(second)
            self.assertIsNone(manager.acquire("tenant-a", "repo-review", "worker-2"))
            self.assertEqual(manager.durable_state("tenant-a"), {"leases": 1, "run_keys": 0})
        finally:
            second.close()

    def test_invalid_ttl_is_rejected(self):
        with self.assertRaises(LeaseError):
            LeaseManager(self.store).acquire("tenant-a", "m", "owner", ttl_seconds=0)


if __name__ == "__main__":
    unittest.main()
