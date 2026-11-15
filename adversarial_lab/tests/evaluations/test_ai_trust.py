import unittest

from support import LIBRARY, engagement, scope

from agntia_adversarial.missions.compiler import compile_experiment
from agntia_adversarial.missions.registry import MissionRegistry
from agntia_adversarial.tools.garak import GarakAdapter
from agntia_adversarial.tools.pyrit import PyritAdapter


class AiTrustTests(unittest.TestCase):
    def test_ai_mission_targets_a_model(self):
        mission = MissionRegistry(LIBRARY).get("ai-trust")
        experiment = compile_experiment(mission, engagement(), scope(), "synthetic-model")
        self.assertEqual(experiment.targets[0].kind, "model")
        self.assertIn("ai.evaluate", experiment.capabilities)

    def test_ai_tools_are_blocked_without_license_audit(self):
        for adapter in (PyritAdapter(), GarakAdapter()):
            if not adapter.available():
                result = adapter.run(None, [])  # type: ignore[arg-type]
                self.assertEqual(result.status, "BLOCKED")


if __name__ == "__main__":
    unittest.main()
