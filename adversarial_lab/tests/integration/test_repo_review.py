import unittest

from support import LIBRARY

from agntia_adversarial.execution.sandbox import Sandbox
from agntia_adversarial.missions.registry import MissionRegistry
from agntia_adversarial.tools.osv import OsvAdapter
from agntia_adversarial.tools.semgrep import SemgrepAdapter
from agntia_adversarial.tools.syft import SyftAdapter


class RepoReviewTests(unittest.TestCase):
    def test_mission_requires_static_capabilities(self):
        mission = MissionRegistry(LIBRARY).get("repo-review")
        self.assertIn("repo.static", mission["required_capabilities"])
        self.assertIn("sbom", mission["required_capabilities"])

    def test_adapters_do_not_fake_results(self):
        with Sandbox([]) as sandbox:
            for adapter in (SemgrepAdapter(), OsvAdapter(), SyftAdapter()):
                result = adapter.run(sandbox, ["--version"])
                self.assertIn(result.status, {"BLOCKED", "FAIL"})
                if not adapter.available():
                    self.assertEqual(result.status, "BLOCKED")


if __name__ == "__main__":
    unittest.main()
