import tempfile
import unittest
from pathlib import Path

from agntia_adversarial.release.sbom import audit_status, build_sbom, sign_manifest, verify_signature


class ReleaseSigningTests(unittest.TestCase):
    def test_sbom_lists_files_and_dependencies(self):
        sbom = build_sbom()
        self.assertEqual(sbom["bomFormat"], "CycloneDX")
        self.assertTrue(any(component["type"] == "file" for component in sbom["components"]))
        self.assertTrue(any(component["type"] == "library" for component in sbom["components"]))
        self.assertEqual(len(sbom["digest"]), 64)

    def test_signature_detects_tampering(self):
        payload = {"sbom_digest": "a" * 64}
        with tempfile.TemporaryDirectory() as root:
            signature = sign_manifest(payload, Path(root) / "release.key")
        self.assertTrue(verify_signature(payload, signature))
        self.assertFalse(verify_signature({"sbom_digest": "b" * 64}, signature))

    def test_audit_never_claims_success_without_running(self):
        status = audit_status()
        self.assertIn(status["status"], {"BLOCKED", "PARTIAL"})


if __name__ == "__main__":
    unittest.main()
