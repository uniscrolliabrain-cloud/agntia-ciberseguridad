import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agntia_adversarial.contracts.result import Observation, RunReceipt, Status
from agntia_adversarial.evidence.redaction import redact
from agntia_adversarial.evidence.vault import EvidenceTooLarge, Vault
from agntia_adversarial.reports.render import render_report


class EvidenceTests(unittest.TestCase):
    def test_roundtrip_and_verify(self):
        with tempfile.TemporaryDirectory() as root:
            vault = Vault(Path(root))
            reference = vault.put("tenant-a", "ev-1", b'{"ok":true}')
            self.assertTrue(vault.verify("tenant-a", reference))
            self.assertEqual(vault.get("tenant-a", "ev-1"), b'{"ok":true}')

    def test_tampered_blob_does_not_verify(self):
        with tempfile.TemporaryDirectory() as root:
            vault = Vault(Path(root))
            reference = vault.put("tenant-a", "ev-2", b"payload")
            blob_path = Path(root) / "tenant-a" / "ev-2.bin"
            blob = bytearray(blob_path.read_bytes())
            blob[-1] ^= 0xFF
            blob_path.write_bytes(bytes(blob))
            with self.assertRaises(Exception):
                vault.verify("tenant-a", reference)

    def test_size_limit_is_enforced(self):
        with tempfile.TemporaryDirectory() as root:
            vault = Vault(Path(root), max_bytes=4)
            with self.assertRaises(EvidenceTooLarge):
                vault.put("tenant-a", "ev-3", b"too-large")

    def test_redaction_hides_secrets_and_emails(self):
        text = redact("token=abc123 user@example.com AKIAABCDEFGHIJKLMNOP 10.0.0.1")
        self.assertNotIn("abc123", text)
        self.assertNotIn("user@example.com", text)
        self.assertNotIn("AKIAABCDEFGHIJKLMNOP", text)
        self.assertNotIn("10.0.0.1", text)

    def test_report_is_deterministic_and_declares_limitations(self):
        receipt = RunReceipt(
            run_id="run-1",
            experiment_id="exp-1",
            tenant_id="tenant-a",
            status=Status.PARTIAL,
            started_at=datetime(2026, 11, 15, tzinfo=timezone.utc),
            ended_at=datetime(2026, 11, 15, 0, 1, tzinfo=timezone.utc),
            observations=[Observation(id="o1", kind="authz", target_ref="api", summary="x", severity="high", reproduced=True)],
            limitations=["tools blocked"],
        )
        self.assertEqual(render_report(receipt), render_report(receipt))
        self.assertIn("tools blocked", render_report(receipt))


if __name__ == "__main__":
    unittest.main()
