import json
import unittest
from datetime import datetime, timezone

from support import ROOT

from agntia_adversarial.contracts.experiment import ExperimentSpec, Limits, TargetRef
from agntia_adversarial.provenance.manifest import build_manifest, canonical_json, sha256_bytes


class ContractTests(unittest.TestCase):
    def test_experiment_roundtrip(self):
        experiment = ExperimentSpec(
            id="exp-1",
            campaign_id="C09",
            mission_id="api-authz",
            tenant_id="tenant-a",
            engagement_id="eng-1",
            scope_id="scope-1",
            targets=[TargetRef(kind="api", ref="synthetic-api", fingerprint="b" * 64)],
            capabilities=["api.passive"],
            limits=Limits(),
            stop_conditions=["never_network"],
            created_at=datetime.now(timezone.utc),
        )
        restored = ExperimentSpec.model_validate_json(experiment.model_dump_json())
        self.assertEqual(restored, experiment)
        self.assertTrue(restored.requires("api.passive"))
        self.assertFalse(restored.requires("chaos.simulate"))

    def test_canonical_json_is_stable(self):
        first = canonical_json({"b": 1, "a": [2, 3]})
        second = canonical_json({"a": [2, 3], "b": 1})
        self.assertEqual(first, second)
        self.assertEqual(sha256_bytes(first.encode()), sha256_bytes(second.encode()))

    def test_manifest_changes_with_content(self):
        target = ROOT / "fixtures" / "synthetic_shop" / "schema.json"
        first = build_manifest([target])
        second = build_manifest([target])
        self.assertEqual(first["digest"], second["digest"])
        self.assertEqual(len(first["files"]), 1)
        self.assertEqual(json.loads(json.dumps(first)), first)


if __name__ == "__main__":
    unittest.main()
