import json
import tempfile
import unittest
from pathlib import Path

from agntia_adversarial.tools.faults import FaultInjector


class ResilienceTests(unittest.TestCase):
    def test_loss_is_detected_and_restore_verified(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            data = root_path / "data.json"
            data.write_text(json.dumps({"rows": [1, 2, 3]}), encoding="utf-8")
            result = FaultInjector().destroy_and_restore(data, root_path / "backups")
        self.assertEqual(result.status, "PASS")
        self.assertTrue(result.metadata["corrupt_backup_rejected"])
        self.assertGreaterEqual(result.metadata["rto_ms_measured"], 0)

    def test_missing_file_is_not_run(self):
        result = FaultInjector().destroy_and_restore(Path("/nonexistent"), Path("/tmp"))
        self.assertEqual(result.status, "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
