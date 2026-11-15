import tempfile
import unittest
from pathlib import Path

from support import LIBRARY, config, engagement, scope

from agntia_adversarial.missions.registry import MissionRegistry
from agntia_adversarial.operations.daily import run_daily


class DailyCycleTests(unittest.TestCase):
    def test_daily_cycle_produces_evidence_report_and_partial_status(self):
        missions = list(MissionRegistry(LIBRARY).load().values())
        targets = {
            "repo": "synthetic-shop",
            "api": "synthetic-api",
            "model": "synthetic-model",
            "container": "synthetic-db",
        }
        for mission in missions:
            mission["target_ref"] = targets[mission["scope_kind"]]
        with tempfile.TemporaryDirectory() as root:
            outcome = run_daily(config(Path(root)), engagement(), scope(), missions)
            self.assertEqual(outcome.receipt.status.value, "PARTIAL")
            self.assertTrue(outcome.report_path.is_file())
            self.assertGreaterEqual(len(outcome.receipt.observations), 3)
            self.assertTrue(all(ref.sha256 for ref in outcome.receipt.evidence))
            self.assertTrue(outcome.blocked_tools)
            self.assertEqual(outcome.tenant_id, "tenant-a")

    def test_cross_tenant_run_is_not_visible(self):
        missions = list(MissionRegistry(LIBRARY).load().values())
        for mission in missions:
            mission["target_ref"] = {
                "repo": "synthetic-shop",
                "api": "synthetic-api",
                "model": "synthetic-model",
                "container": "synthetic-db",
            }[mission["scope_kind"]]
        with tempfile.TemporaryDirectory() as root:
            run_daily(config(Path(root)), engagement(), scope(), missions)
            from agntia_adversarial.store.sqlite import Store

            store = Store(Path(root) / "var" / "lab.sqlite")
            self.assertEqual(store.count_runs("tenant-a"), 1)
            self.assertEqual(store.count_runs("tenant-b"), 0)
            store.close()


if __name__ == "__main__":
    unittest.main()
