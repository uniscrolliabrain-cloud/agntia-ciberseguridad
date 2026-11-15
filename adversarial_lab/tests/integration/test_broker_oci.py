import unittest
from datetime import datetime, timezone

from agntia_adversarial.contracts.experiment import ExperimentSpec, Limits, TargetRef
from agntia_adversarial.execution.broker import Broker
from agntia_adversarial.execution.oci import OCISandbox, RuntimeSpec

IMAGE = "ghcr.io/example/scanner@sha256:" + "c" * 64


class BrokerOCITests(unittest.TestCase):
    def test_broker_uses_hardened_oci_command(self):
        captured = {}

        def runner(command):
            captured["command"] = list(command)
            return {"returncode": 0, "stdout": "scan ok", "stderr": ""}

        experiment = ExperimentSpec(
            id="exp-oci",
            campaign_id="C10",
            mission_id="repo-review",
            tenant_id="tenant-a",
            engagement_id="eng-1",
            scope_id="scope-1",
            targets=[TargetRef(kind="repo", ref="synthetic-shop", fingerprint="a" * 64)],
            capabilities=["repo.static"],
            limits=Limits(max_requests=2),
            stop_conditions=["never_network"],
            created_at=datetime.now(timezone.utc),
        )
        broker = Broker(
            experiment=experiment,
            catalog={"semgrep": "repo.static"},
            sandbox=OCISandbox(RuntimeSpec(image=IMAGE), runner=runner),
        )
        result = broker.invoke("semgrep", "repo.static", ["semgrep", "--json", "/work"])
        self.assertEqual(result["status"], "PASS")
        self.assertIn("--network=none", captured["command"])
        self.assertEqual(broker.calls, 1)


if __name__ == "__main__":
    unittest.main()
