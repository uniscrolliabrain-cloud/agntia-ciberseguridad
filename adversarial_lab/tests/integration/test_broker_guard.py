import unittest
from datetime import datetime, timedelta, timezone

from agntia_adversarial.contracts.experiment import ExperimentSpec, Limits, TargetRef
from agntia_adversarial.execution.broker import Broker, BrokerError


def experiment() -> ExperimentSpec:
    return ExperimentSpec(
        id="exp-guard",
        campaign_id="B04",
        mission_id="repo-review",
        tenant_id="tenant-a",
        engagement_id="eng-1",
        scope_id="scope-1",
        targets=[TargetRef(kind="repo", ref="synthetic-shop", fingerprint="a" * 64)],
        capabilities=["repo.static"],
        limits=Limits(max_requests=5),
        stop_conditions=["never_network"],
        created_at=datetime.now(timezone.utc),
    )


class FakeSandbox:
    def __init__(self, stdout: str = "ok") -> None:
        self.calls = 0
        self.stdout = stdout

    def run(self, argv):
        self.calls += 1
        return {"status": "PASS", "exit": 0, "stdout": self.stdout, "stderr": ""}


class BrokerGuardTests(unittest.TestCase):
    def test_revoked_authorization_denies_before_sandbox(self):
        sandbox = FakeSandbox()
        broker = Broker(experiment(), {"semgrep": "repo.static"}, sandbox, authorize=lambda: False)
        with self.assertRaises(BrokerError):
            broker.invoke("semgrep", "repo.static", ["semgrep", "--version"])
        self.assertEqual(sandbox.calls, 0)

    def test_expired_window_denies(self):
        broker = Broker(
            experiment(),
            {"semgrep": "repo.static"},
            FakeSandbox(),
            deadline=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        with self.assertRaises(BrokerError):
            broker.invoke("semgrep", "repo.static", ["semgrep", "--version"])

    def test_idempotency_prevents_double_effect(self):
        sandbox = FakeSandbox()
        broker = Broker(experiment(), {"semgrep": "repo.static"}, sandbox)
        first = broker.invoke("semgrep", "repo.static", ["semgrep"], idempotency_key="k1")
        second = broker.invoke("semgrep", "repo.static", ["semgrep"], idempotency_key="k1")
        self.assertEqual(sandbox.calls, 1)
        self.assertTrue(second["deduplicated"])
        self.assertEqual(first["status"], "PASS")
        self.assertEqual(broker.calls, 1)

    def test_output_is_truncated(self):
        broker = Broker(experiment(), {"semgrep": "repo.static"}, FakeSandbox(stdout="x" * 1000), max_output=64)
        result = broker.invoke("semgrep", "repo.static", ["semgrep"])
        self.assertLessEqual(len(result["stdout"]), 64 + len("\n[truncated]"))
        self.assertTrue(result["stdout"].endswith("[truncated]"))

    def test_tool_outside_catalog_is_denied(self):
        broker = Broker(experiment(), {"semgrep": "repo.static"}, FakeSandbox())
        with self.assertRaises(BrokerError):
            broker.invoke("bash", "repo.static", ["bash", "-c", "id"])


if __name__ == "__main__":
    unittest.main()
