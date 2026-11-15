import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "releasecheck.py"


def run(*args: str) -> tuple[int, dict]:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )
    return completed.returncode, json.loads(completed.stdout)


class ReleaseGateTests(unittest.TestCase):
    def test_integrity_mode_passes_but_is_not_release_eligible(self):
        code, payload = run()
        self.assertEqual(code, 0)
        self.assertEqual(payload["mode"], "integrity")
        self.assertEqual(payload["status"], "PASS")
        self.assertFalse(payload["release_eligible"])

    def test_production_mode_fails_closed_without_dependency_audit(self):
        code, payload = run("--production")
        self.assertEqual(code, 1)
        self.assertEqual(payload["mode"], "production")
        self.assertFalse(payload["release_eligible"])
        self.assertTrue(any("dependency audit" in item for item in payload["findings"]))
        self.assertTrue(any("attestation" in item for item in payload["findings"]))


if __name__ == "__main__":
    unittest.main()
