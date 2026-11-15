import unittest

from agntia_adversarial.evaluation.oracles import evaluate_observations
from agntia_adversarial.evaluation.retest import retest
from agntia_adversarial.contracts.result import Observation
from agntia_adversarial.tools.api_probe import probe_authorization, probe_benign_control
from agntia_adversarial.twins.api import SyntheticAPI


def to_observation(finding: dict) -> Observation:
    return Observation(
        id="obs-authz-1",
        kind=finding["kind"],
        target_ref="synthetic-api",
        summary=finding["summary"],
        severity=finding["severity"],
        reproduced=finding["reproduced"],
    )


class ApiLabTests(unittest.TestCase):
    def test_vulnerable_api_is_detected_and_benign_control_works(self):
        api = SyntheticAPI(flaw_horizontal=True, flaw_role=True)
        findings = probe_authorization(api)
        self.assertEqual(len(findings), 2)
        self.assertTrue(probe_benign_control(api))
        verdict = evaluate_observations([to_observation(findings[0])], expect_finding=True)
        self.assertEqual(verdict.status, "PASS")

    def test_fixed_api_produces_no_finding_and_passes_retest(self):
        api = SyntheticAPI(flaw_horizontal=False, flaw_role=False)
        findings = probe_authorization(api)
        self.assertEqual(findings, [])
        self.assertTrue(probe_benign_control(api))
        verdict = evaluate_observations([], expect_finding=False)
        self.assertEqual(verdict.status, "PASS")
        self.assertEqual(retest(["obs-authz-1"], []).status, "PASS")

    def test_unauthenticated_request_is_rejected(self):
        api = SyntheticAPI()
        self.assertEqual(api.get_order("bogus", "order-100")["status"], 401)
        self.assertEqual(api.get_order("tok-user-1", "missing")["status"], 404)


if __name__ == "__main__":
    unittest.main()
