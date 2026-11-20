"""Rollout configuration: born pending, fails closed without consent, budget or a valid ring."""
from datetime import timedelta
from pathlib import Path
import unittest

from pydantic import ValidationError

from agntia_ciberseguridad.config import RolloutConfig, Settings
from agntia_ciberseguridad.util import utcnow

TENANT = 'tenantA'


def rollout(**overrides):
    document = {
        'tenant_id': TENANT,
        'capability': 'findings.read',
        'ring': 'A',
        'state': 'pending',
        'revision': 1,
        'consent_ref': 'consentA',
        'budget_cents': 100,
        'expires_at': (utcnow() + timedelta(days=7)).isoformat(),
        'secret_ref': 'CYBER_AGENT_CREDENTIAL',
    }
    document.update(overrides)
    return document


def settings(rollouts, consents=None):
    now = utcnow()
    consent = {'tenant_id': TENANT, 'target_refs': ['repoA'], 'profiles': ['static_read'],
               'evidence_ref': 'synthetic-consent', 'authority_actor_id': 'ownerA',
               'starts_at': (now - timedelta(hours=1)).isoformat(),
               'expires_at': (now + timedelta(days=30)).isoformat()}
    return Settings(data_dir=Path('/tmp/agntia-rollout-config'),
        principals=[{'id': 'ownerA', 'actor_id': 'ownerA', 'role': 'owner', 'tenants': [TENANT],
                     'token_env': 'CYBER_ROLLOUT_OWNER'}],
        targets={'repoA': {'tenant_id': TENANT, 'kind': 'repository', 'location': '/synthetic/repository'}},
        consents={'consentA': consent} if consents is None else consents, rollouts=rollouts)


class RolloutModelTests(unittest.TestCase):
    def test_valid_rollout_is_born_pending_and_keeps_a_reference_not_a_value(self):
        config = RolloutConfig.model_validate(rollout())
        self.assertEqual(config.state, 'pending')
        self.assertEqual(config.secret_ref, 'CYBER_AGENT_CREDENTIAL')

    def test_consent_reference_is_required(self):
        document = rollout()
        document.pop('consent_ref')
        with self.assertRaises(ValidationError):
            RolloutConfig.model_validate(document)

    def test_budget_must_be_positive(self):
        for budget in (0, -1):
            with self.assertRaises(ValidationError):
                RolloutConfig.model_validate(rollout(budget_cents=budget))

    def test_unknown_ring_state_or_capability_are_rejected(self):
        for overrides in ({'ring': 'E'}, {'state': 'active'}, {'capability': 'rollout.apply'}):
            with self.assertRaises(ValidationError):
                RolloutConfig.model_validate(rollout(**overrides))

    def test_expired_rollout_is_rejected(self):
        with self.assertRaises(ValidationError):
            RolloutConfig.model_validate(rollout(expires_at=(utcnow() - timedelta(minutes=1)).isoformat()))

    def test_ring_cannot_skip_or_move_backwards(self):
        for overrides in ({'previous_ring': 'A', 'ring': 'D'}, {'previous_ring': 'C', 'ring': 'B'}, {'ring': 'D'}):
            with self.assertRaises(ValidationError):
                RolloutConfig.model_validate(rollout(**overrides))
        self.assertEqual(RolloutConfig.model_validate(rollout(previous_ring='B', ring='C')).ring, 'C')
        self.assertEqual(RolloutConfig.model_validate(rollout(previous_ring='C', ring='D')).ring, 'D')

    def test_secret_reference_must_be_an_environment_name(self):
        for value in ('sk-live-abc123', 'lowercase', 'CYBER_TOKEN=abc'):
            with self.assertRaises(ValidationError):
                RolloutConfig.model_validate(rollout(secret_ref=value))
        self.assertIsNone(RolloutConfig.model_validate(rollout(secret_ref=None)).secret_ref)


class RolloutSettingsTests(unittest.TestCase):
    def test_settings_accept_a_rollout_bound_to_a_provisioned_consent(self):
        configured = settings([rollout()])
        self.assertEqual([(entry.tenant_id, entry.capability, entry.state) for entry in configured.rollouts],
                         [(TENANT, 'findings.read', 'pending')])

    def test_settings_reject_an_unprovisioned_tenant(self):
        with self.assertRaises(ValidationError):
            settings([rollout(tenant_id='tenantB')])

    def test_settings_reject_an_unknown_or_foreign_consent(self):
        with self.assertRaises(ValidationError):
            settings([rollout(consent_ref='consentB')])

    def test_settings_reject_a_duplicate_binding(self):
        with self.assertRaises(ValidationError):
            settings([rollout(), rollout(revision=2)])

    def test_settings_reject_a_rollout_without_budget_or_after_expiry(self):
        with self.assertRaises(ValidationError):
            settings([rollout(budget_cents=0)])
        with self.assertRaises(ValidationError):
            settings([rollout(expires_at=(utcnow() - timedelta(seconds=1)).isoformat())])

    def test_no_rollouts_keeps_existing_behaviour(self):
        configured = settings([])
        self.assertEqual(configured.rollouts, [])


if __name__ == '__main__':
    unittest.main()
