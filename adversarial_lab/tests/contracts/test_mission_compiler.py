import unittest

from support import LIBRARY, engagement, scope

from agntia_adversarial.missions.compiler import MissionError, compile_experiment
from agntia_adversarial.missions.registry import MissionRegistry
from agntia_adversarial.missions.validator import MissionInvalid, validate_mission


class MissionTests(unittest.TestCase):
    def setUp(self):
        self.registry = MissionRegistry(LIBRARY)
        self.missions = self.registry.load()

    def test_library_has_five_families(self):
        self.assertEqual(len(self.missions), 5)
        self.assertIn("api-authz", self.missions)

    def test_tampered_mission_is_rejected(self):
        mission = dict(self.missions["api-authz"])
        mission["stop_conditions"] = []
        with self.assertRaises(MissionInvalid):
            validate_mission(mission)

    def test_unknown_capability_is_rejected(self):
        mission = dict(self.missions["api-authz"])
        mission["required_capabilities"] = ["shell.any"]
        with self.assertRaises(MissionInvalid):
            validate_mission(mission)

    def test_compile_produces_authorized_experiment(self):
        experiment = compile_experiment(self.missions["api-authz"], engagement(), scope(), "synthetic-api")
        self.assertEqual(experiment.tenant_id, "tenant-a")
        self.assertEqual(experiment.limits.network_egress, "deny")
        self.assertTrue(experiment.requires("api.passive"))

    def test_compile_refuses_out_of_scope_target(self):
        with self.assertRaises(MissionError):
            compile_experiment(self.missions["api-authz"], engagement(), scope(), "other-api")

    def test_compile_refuses_revoked_engagement(self):
        with self.assertRaises(MissionError):
            compile_experiment(
                self.missions["api-authz"], engagement().revoke(), scope(), "synthetic-api"
            )


if __name__ == "__main__":
    unittest.main()
