import unittest
from datetime import datetime, timezone

from support import scope

from agntia_adversarial.contracts.experiment import ExperimentSpec, Limits, TargetRef
from agntia_adversarial.execution.broker import Broker, BrokerError
from agntia_adversarial.execution.network import EgressDenied, EgressPolicy
from agntia_adversarial.execution.sandbox import Sandbox, SandboxError


def experiment(capabilities=("sandbox.test",)) -> ExperimentSpec:
    return ExperimentSpec(
        id="exp-1",
        campaign_id="C05",
        mission_id="api-authz",
        tenant_id="tenant-a",
        engagement_id="eng-1",
        scope_id="scope-1",
        targets=[TargetRef(kind="api", ref="synthetic-api", fingerprint="b" * 64)],
        capabilities=list(capabilities),
        limits=Limits(max_requests=2),
        stop_conditions=["never_network"],
        created_at=datetime.now(timezone.utc),
    )


class IsolationTests(unittest.TestCase):
    def test_egress_is_denied(self):
        with self.assertRaises(EgressDenied):
            EgressPolicy().check("https://example.com")
        with self.assertRaises(EgressDenied):
            EgressPolicy(allow=True).check("https://example.com")

    def test_sandbox_rejects_unknown_binary(self):
        with Sandbox(["echo"]) as sandbox:
            with self.assertRaises(SandboxError):
                sandbox.run(["sh", "-c", "echo hi"])

    def test_sandbox_allows_echo_without_shell(self):
        with Sandbox(["echo"]) as sandbox:
            result = sandbox.run(["echo", "hi; rm -rf /"])
        self.assertEqual(result["status"], "PASS")
        self.assertIn("hi; rm -rf /", result["stdout"])

    def test_broker_denies_unknown_tool_and_missing_capability(self):
        with Sandbox(["echo"]) as sandbox:
            broker = Broker(experiment=experiment(), catalog={"echo": "sandbox.test"}, sandbox=sandbox)
            with self.assertRaises(BrokerError):
                broker.invoke("semgrep", "sandbox.test", ["echo", "x"])
            with self.assertRaises(BrokerError):
                broker.invoke("echo", "api.active", ["echo", "x"])

    def test_broker_enforces_request_budget(self):
        with Sandbox(["echo"]) as sandbox:
            broker = Broker(experiment=experiment(), catalog={"echo": "sandbox.test"}, sandbox=sandbox)
            broker.invoke("echo", "sandbox.test", ["echo", "1"])
            broker.invoke("echo", "sandbox.test", ["echo", "2"])
            with self.assertRaises(BrokerError):
                broker.invoke("echo", "sandbox.test", ["echo", "3"])


if __name__ == "__main__":
    unittest.main()
