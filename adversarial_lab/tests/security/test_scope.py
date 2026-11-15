import unittest
from datetime import datetime, timedelta, timezone

from support import engagement, scope

from agntia_adversarial.policy.authorization import Authorizer


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.authorizer = Authorizer()

    def decide(self, **overrides):
        engagement_obj = overrides.pop("engagement", engagement())
        scope_obj = overrides.pop("scope", scope())
        return self.authorizer.decide(
            engagement=engagement_obj,
            scope=scope_obj,
            tenant_id=overrides.pop("tenant_id", "tenant-a"),
            target_ref=overrides.pop("target_ref", "synthetic-api"),
            capability=overrides.pop("capability", "api.passive"),
            **overrides,
        )

    def test_allows_valid_request(self):
        self.assertTrue(self.decide().allowed)

    def test_denies_cross_tenant(self):
        decision = self.decide(tenant_id="tenant-b")
        self.assertFalse(decision.allowed)
        self.assertIn("tenant_mismatch", decision.reasons)

    def test_denies_expired_engagement(self):
        now = datetime.now(timezone.utc)
        expired = engagement(starts_at=now - timedelta(hours=2), ends_at=now - timedelta(hours=1))
        self.assertFalse(self.decide(engagement=expired).allowed)

    def test_denies_target_out_of_scope(self):
        decision = self.decide(target_ref="other-api")
        self.assertIn("target_out_of_scope", decision.reasons)

    def test_denies_missing_capability(self):
        decision = self.decide(capability="dast.active")
        self.assertIn("capability_not_granted", decision.reasons)

    def test_denies_changed_fingerprint(self):
        decision = self.decide(expected_fingerprint="f" * 64)
        self.assertIn("target_fingerprint_changed", decision.reasons)

    def test_denies_revoked_engagement(self):
        self.assertFalse(self.decide(engagement=engagement().revoke()).allowed)

    def test_denies_egress_enabled_scope(self):
        decision = self.decide(scope=scope(network_egress="allow"))
        self.assertIn("egress_must_be_denied", decision.reasons)


if __name__ == "__main__":
    unittest.main()
