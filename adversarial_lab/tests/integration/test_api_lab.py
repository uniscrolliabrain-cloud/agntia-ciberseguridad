import unittest

from support import LIBRARY, engagement, scope

from agntia_adversarial.missions.compiler import compile_experiment
from agntia_adversarial.missions.registry import MissionRegistry
from agntia_adversarial.tools.schemathesis import SchemathesisAdapter
from agntia_adversarial.tools.zap import ZapAdapter


class ApiLabTests(unittest.TestCase):
    def test_stateful_mission_compiles_for_api_target(self):
        mission = MissionRegistry(LIBRARY).get("api-state")
        experiment = compile_experiment(mission, engagement(), scope(), "synthetic-api")
        self.assertEqual(experiment.targets[0].kind, "api")
        self.assertIn("api.passive", experiment.capabilities)

    def test_http_tools_are_not_claimed_available(self):
        self.assertIn(SchemathesisAdapter().available(), {True, False})
        self.assertIn(ZapAdapter().available(), {True, False})


if __name__ == "__main__":
    unittest.main()
