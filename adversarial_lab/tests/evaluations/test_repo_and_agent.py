import tempfile
import unittest
from pathlib import Path

from agntia_adversarial.tools.agent_probe import probe_injection
from agntia_adversarial.tools.repo_scan import scan_repo
from agntia_adversarial.twins.agent import INJECTION_MARKER, SyntheticAgent
from agntia_adversarial.twins.repo import build_repo


class RepoReviewTests(unittest.TestCase):
    def test_canary_secret_and_unpinned_dependency_are_found(self):
        with tempfile.TemporaryDirectory() as root:
            findings = scan_repo(build_repo(Path(root)))
        kinds = {item["kind"] for item in findings}
        self.assertEqual(kinds, {"secret", "dependency"})
        secrets = [item for item in findings if item["kind"] == "secret"]
        self.assertTrue(secrets and all(item["evidence"]["canary"] is True for item in secrets))

    def test_clean_repo_has_no_findings(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)
            (path / "app.py").write_text("print('ok')\n", encoding="utf-8")
            (path / "requirements.txt").write_text("requests==2.32.3\n", encoding="utf-8")
            self.assertEqual(scan_repo(path), [])


class AgentTrustTests(unittest.TestCase):
    def test_guarded_agent_ignores_injection(self):
        agent = SyntheticAgent(guarded=True)
        self.assertEqual(probe_injection(agent), [])
        self.assertEqual(agent.tools_outside_manifest(), [])

    def test_unguarded_agent_exfiltrates(self):
        findings = probe_injection(SyntheticAgent(guarded=False))
        self.assertEqual(len(findings), 1)
        self.assertIn("email.send", findings[0]["evidence"]["tools"])
        self.assertIn("attacker", str(findings[0]["evidence"]["destination"]))

    def test_marker_is_the_documented_canary(self):
        self.assertTrue(INJECTION_MARKER)


if __name__ == "__main__":
    unittest.main()
