import json
import tempfile
import unittest
from pathlib import Path

from agntia_adversarial.twins.builder import build_twin
from agntia_adversarial.twins.fidelity import fidelity_report


class TwinTests(unittest.TestCase):
    def test_twin_is_deterministic(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            twin_a = build_twin(Path(first))
            twin_b = build_twin(Path(second))
            self.assertEqual(twin_a.manifest["digest"], twin_b.manifest["digest"])
            self.assertTrue((Path(first) / "twin-manifest.json").exists())

    def test_fidelity_is_measured_not_asserted(self):
        with tempfile.TemporaryDirectory() as root:
            build_twin(Path(root))
            report = fidelity_report(Path(root), ["id", "email", "total_cents", "missing_field"])
        self.assertEqual(report["coverage"], 0.75)
        self.assertEqual(report["missing"], ["missing_field"])
        self.assertEqual(report["claim"], "synthetic_structural_only")

    def test_synthetic_emails_are_not_real(self):
        with tempfile.TemporaryDirectory() as root:
            build_twin(Path(root))
            users = json.loads((Path(root) / "data" / "users.json").read_text())
        self.assertTrue(all(user["email"].endswith("@example.invalid") for user in users))


if __name__ == "__main__":
    unittest.main()
