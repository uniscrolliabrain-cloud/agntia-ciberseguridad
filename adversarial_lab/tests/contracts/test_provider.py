import unittest

from agntia_adversarial.providers.base import Provider, ProviderBlocked
from agntia_adversarial.providers.mock import MockProvider
from agntia_adversarial.providers.registry import default_registry
from agntia_adversarial.providers.subprocess_adapter import SubprocessProvider


class ProviderTests(unittest.TestCase):
    def test_mock_satisfies_protocol(self):
        self.assertIsInstance(MockProvider(), Provider)

    def test_mock_is_deterministic_and_offline(self):
        provider = MockProvider()
        plan = provider.plan("exp-1", ["h1", "h2"])
        result = provider.execute("exp-1", plan)
        self.assertEqual(plan, ["exp-1:1:verify", "exp-1:2:verify"])
        self.assertEqual(result.status, "PARTIAL")
        self.assertEqual(provider.report("exp-1")["model_calls"], 0)

    def test_unverified_providers_are_blocked(self):
        registry = default_registry()
        self.assertEqual(registry.status()["codex"].split(":")[0], "BLOCKED")
        with self.assertRaises(ProviderBlocked):
            registry.get("codex")

    def test_subprocess_provider_requires_explicit_enablement(self):
        with self.assertRaises(ProviderBlocked):
            SubprocessProvider("python").plan("exp-1", ["h1"])


if __name__ == "__main__":
    unittest.main()
