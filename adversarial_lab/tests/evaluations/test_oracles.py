import unittest

from agntia_adversarial.contracts.result import Observation
from agntia_adversarial.evaluation.benchmark import benchmark
from agntia_adversarial.evaluation.oracles import evaluate_observations
from agntia_adversarial.evaluation.retest import retest
from agntia_adversarial.evaluation.triage import triage


def finding(identifier: str = "obs-1", reproduced: bool = True, severity: str = "high") -> Observation:
    return Observation(
        id=identifier,
        kind="authorization",
        target_ref="synthetic-api",
        summary="acceso cruzado",
        severity=severity,
        reproduced=reproduced,
    )


class OracleTests(unittest.TestCase):
    def test_expected_reproduced_finding_passes(self):
        verdict = evaluate_observations([finding()], expect_finding=True)
        self.assertEqual(verdict.status, "PASS")

    def test_unreproduced_finding_does_not_count(self):
        verdict = evaluate_observations([finding(reproduced=False)], expect_finding=True)
        self.assertEqual(verdict.status, "FAIL")

    def test_unexpected_finding_fails(self):
        verdict = evaluate_observations([finding()], expect_finding=False)
        self.assertEqual(verdict.status, "FAIL")

    def test_canary_leak_is_a_failure(self):
        observation = finding()
        observation.summary = "salida con AKIA123"
        verdict = evaluate_observations([observation], expect_finding=True, forbidden_substrings=["AKIA"])
        self.assertEqual(verdict.status, "FAIL")

    def test_triage_deduplicates_and_requires_reproduction(self):
        different = finding("obs-2", reproduced=False)
        different.summary = "otro hallazgo distinto"
        items = triage([finding(), finding(), different])
        self.assertEqual(len(items), 2)
        confirmed = [item for item in items if item.confirmed]
        self.assertEqual(len(confirmed), 1)
        self.assertGreaterEqual(items[0].duplicates + items[1].duplicates, 1)

    def test_retest_fails_while_finding_reproduces(self):
        self.assertEqual(retest(["obs-1"], [finding()]).status, "FAIL")
        self.assertEqual(retest(["obs-1"], [finding("obs-9")]).status, "PASS")

    def test_benchmark_reports_denominators_and_na(self):
        metrics = benchmark(0, 0, 0)
        self.assertIsNone(metrics["precision"])
        self.assertIsNone(metrics["recall"])
        self.assertEqual(metrics["denominators"]["precision"], 0)


if __name__ == "__main__":
    unittest.main()
