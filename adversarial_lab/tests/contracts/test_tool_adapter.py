import unittest

from agntia_adversarial.execution.sandbox import Sandbox
from agntia_adversarial.tools.base import ToolAdapter
from agntia_adversarial.tools.fuzz import FuzzProbe
from agntia_adversarial.tools.receipts import build_receipt
from agntia_adversarial.tools.registry import ToolRegistry, default_catalog


class ToolTests(unittest.TestCase):
    def test_unknown_tool_is_denied(self):
        registry = ToolRegistry()
        with self.assertRaises(KeyError):
            registry.get("nmap")

    def test_missing_binary_is_blocked_not_passing(self):
        class Ghost(ToolAdapter):
            name = "ghost"
            binary = "definitely-not-installed-binary"

        with Sandbox(["echo"]) as sandbox:
            result = Ghost().run(sandbox, ["--help"])
        self.assertEqual(result.status, "BLOCKED")

    def test_receipt_is_stable_and_binds_output(self):
        class Echo(ToolAdapter):
            name = "echo"
            binary = "echo"

        with Sandbox(["echo"]) as sandbox:
            result = Echo().run(sandbox, ["hello"])
            first = build_receipt(result, ["hello"])
            second = build_receipt(Echo().run(sandbox, ["hello"]), ["hello"])
        self.assertEqual(first["receipt_sha256"], second["receipt_sha256"])
        self.assertNotEqual(first["receipt_sha256"], build_receipt(result, ["bye"])["receipt_sha256"])

    def test_fuzz_probe_reports_unexpected_exception(self):
        def fragile(payload: str) -> None:
            if "\x00" in payload:
                raise TypeError("boom")
            if "<" in payload:
                raise ValueError("expected")

        result = FuzzProbe().probe(fragile, iterations=200)
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(result.metadata["failures"])

    def test_default_catalog_is_closed_and_honest(self):
        catalog = default_catalog()
        self.assertIn("semgrep", catalog.catalog())
        status = catalog.status()
        self.assertIn(status["semgrep"], {"AVAILABLE", "BLOCKED"})


if __name__ == "__main__":
    unittest.main()
