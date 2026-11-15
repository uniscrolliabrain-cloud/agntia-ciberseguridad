import tempfile
import unittest
from pathlib import Path

from agntia_adversarial.keys import KeyFormatError, KeyRing


class KeyRingTests(unittest.TestCase):
    def test_key_is_created_once_with_owner_only_mode(self):
        with tempfile.TemporaryDirectory() as root:
            ring = KeyRing(Path(root))
            first = ring.ensure("evidence")
            second = ring.ensure("evidence")
            self.assertEqual(first, second)
            self.assertEqual(len(first), 32)
            self.assertEqual(oct((Path(root) / "evidence.key").stat().st_mode & 0o777), "0o600")

    def test_describe_never_returns_material(self):
        with tempfile.TemporaryDirectory() as root:
            ring = KeyRing(Path(root))
            ring.ensure("evidence")
            entry = ring.describe()["evidence"]
            self.assertEqual(entry["bytes"], 32)
            self.assertNotIn("material", entry)
            self.assertEqual(len(entry["fingerprint"]), 16)
            self.assertNotIn(ring.path("evidence").read_bytes().hex(), str(entry))

    def test_rotation_changes_fingerprint_and_keeps_old_copy(self):
        with tempfile.TemporaryDirectory() as root:
            ring = KeyRing(Path(root))
            ring.ensure("release")
            before = ring.describe()["release"]["fingerprint"]
            after = ring.rotate("release")
            self.assertNotEqual(before, after)
            self.assertTrue((Path(root) / "release.key.old").exists())

    def test_invalid_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(KeyFormatError):
                KeyRing(Path(root)).ensure("../escape")


if __name__ == "__main__":
    unittest.main()
