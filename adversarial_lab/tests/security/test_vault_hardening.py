import shutil
import tempfile
import unittest
from pathlib import Path

from agntia_adversarial.evidence.paths import PathEscape, confined
from agntia_adversarial.evidence.vault import EvidenceIntegrityError, Vault


class VaultHardeningTests(unittest.TestCase):
    def test_traversal_in_tenant_or_evidence_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            vault = Vault(Path(root))
            for tenant, evidence in (("../escape", "ev-1"), ("tenant-a", "../../etc/passwd"), (".", "ev-1")):
                with self.assertRaises(PathEscape):
                    vault.put(tenant, evidence, b"x")

    def test_symlinked_tenant_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            outside = Path(root) / "outside"
            outside.mkdir()
            (Path(root) / "tenant-a").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(PathEscape):
                confined(Path(root), "tenant-a", "ev-1.bin")

    def test_blob_copied_to_another_tenant_does_not_decrypt(self):
        with tempfile.TemporaryDirectory() as root:
            vault = Vault(Path(root))
            vault.put("tenant-a", "ev-9", b"secret-a")
            source = Path(root) / "tenant-a" / "ev-9.bin"
            target = Path(root) / "tenant-b" / "ev-9.bin"
            target.parent.mkdir()
            shutil.copy2(source, target)
            with self.assertRaises(EvidenceIntegrityError):
                vault.get("tenant-b", "ev-9")

    def test_evidence_is_bound_to_its_id(self):
        with tempfile.TemporaryDirectory() as root:
            vault = Vault(Path(root))
            vault.put("tenant-a", "ev-1", b"one")
            source = Path(root) / "tenant-a" / "ev-1.bin"
            shutil.copy2(source, Path(root) / "tenant-a" / "ev-2.bin")
            with self.assertRaises(EvidenceIntegrityError):
                vault.get("tenant-a", "ev-2")

    def test_write_is_atomic_and_owner_only(self):
        with tempfile.TemporaryDirectory() as root:
            vault = Vault(Path(root))
            vault.put("tenant-a", "ev-3", b"payload")
            blob = Path(root) / "tenant-a" / "ev-3.bin"
            self.assertEqual(oct(blob.stat().st_mode & 0o777), "0o600")
            self.assertEqual(list(blob.parent.glob("*.tmp")), [])

    def test_same_id_in_two_tenants_coexists(self):
        with tempfile.TemporaryDirectory() as root:
            vault = Vault(Path(root))
            vault.put("tenant-a", "ev-1", b"a")
            vault.put("tenant-b", "ev-1", b"b")
            self.assertEqual(vault.get("tenant-a", "ev-1"), b"a")
            self.assertEqual(vault.get("tenant-b", "ev-1"), b"b")


if __name__ == "__main__":
    unittest.main()
