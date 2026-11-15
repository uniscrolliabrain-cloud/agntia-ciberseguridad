import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("releasecheck", ROOT / "scripts" / "releasecheck.py")
releasecheck = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(releasecheck)


class ReleaseGateTests(unittest.TestCase):
    def test_releasecheck_passes(self):
        self.assertEqual(releasecheck.main(), 0)

    def test_lab_does_not_import_the_middleware(self):
        import re

        pattern = re.compile(r"^\s*(from|import)\s+agntia_ciberseguridad", re.MULTILINE)
        for path in (ROOT / "src").rglob("*.py"):
            self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")), str(path))

    def test_boundary_script_guards_ownership(self):
        spec = importlib.util.spec_from_file_location("verify_boundary", ROOT / "scripts" / "verify_boundary.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertIn("agntia_ciberseguridad/", module.FORBIDDEN_PREFIXES)
        self.assertIn("adversarial_lab/", module.ALLOWED)


if __name__ == "__main__":
    unittest.main()
