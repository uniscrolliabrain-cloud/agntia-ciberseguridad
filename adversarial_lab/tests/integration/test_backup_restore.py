import tempfile
import unittest
from pathlib import Path

from support import engagement, experiment, receipt, scope

from agntia_adversarial.evidence.vault import Vault
from agntia_adversarial.store.backup import BackupCorrupt, backup, restore
from agntia_adversarial.store.sqlite import Store


class BackupRestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store_path = self.root / "live" / "lab.sqlite"
        self.evidence_root = self.root / "live" / "evidence"
        self.store = Store(self.store_path)
        self.store.add_engagement(engagement())
        self.store.add_scope(scope())
        self.store.add_experiment(experiment())
        self.store.add_run(receipt())
        self.store.record_transition("tenant-a", "run-1", "NOT_RUN", "PARTIAL", "daily")
        self.vault = Vault(self.evidence_root)
        self.ref = self.vault.put("tenant-a", "ev-1", b'{"finding":"synthetic"}')

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_backup_then_restore_recovers_ledger_and_evidence(self):
        archive = self.root / "backup"
        manifest = backup(self.store_path, self.evidence_root, archive)
        self.assertIn("lab.sqlite", manifest["files"])
        self.store.close()
        self.store_path.unlink()
        for path in sorted(self.evidence_root.rglob("*"), reverse=True):
            path.unlink() if path.is_file() else path.rmdir()
        self.evidence_root.rmdir()

        result = restore(archive, self.store_path, self.evidence_root)
        self.assertGreaterEqual(result["files_verified"], 2)
        self.assertGreaterEqual(result["rto_ms_measured"], 0)

        restored = Store(self.store_path)
        try:
            self.assertIsNotNone(restored.get_run("tenant-a", "run-1"))
            self.assertEqual(restored.ledger("tenant-a", "run-1")[0]["to_status"], "PARTIAL")
            self.assertIsNone(restored.get_run("tenant-b", "run-1"))
        finally:
            restored.close()
        self.assertEqual(Vault(self.evidence_root).get("tenant-a", "ev-1"), b'{"finding":"synthetic"}')

    def test_corrupt_backup_is_refused_without_touching_live_data(self):
        archive = self.root / "backup"
        backup(self.store_path, self.evidence_root, archive)
        victim = archive / "lab.sqlite"
        victim.write_bytes(victim.read_bytes() + b"tamper")
        before = self.store_path.read_bytes()
        with self.assertRaises(BackupCorrupt):
            restore(archive, self.store_path, self.evidence_root)
        self.assertEqual(self.store_path.read_bytes(), before)

    def test_missing_manifest_is_refused(self):
        empty = self.root / "empty"
        empty.mkdir()
        with self.assertRaises(BackupCorrupt):
            restore(empty, self.store_path, self.evidence_root)


if __name__ == "__main__":
    unittest.main()
