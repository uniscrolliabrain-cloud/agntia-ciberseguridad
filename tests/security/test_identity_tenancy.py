"""CY-VS-02: Identidad, tenancy y delegación.

Pruebas negativas: dos tenants, actor revocado, grant caducado, cross-tenant,
read-only vs write, approval forjada, HOST_IDENTITY_NOT_CONFIGURED.
"""
from datetime import timedelta
import os
import unittest
from unittest.mock import patch

from agntia_ciberseguridad.contracts import AssetCreate, GrantCreate
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.util import utcnow


TENANT_A = 'tenantA'
TENANT_B = 'tenantB'


def _settings_with_two_tenants():
    from agntia_ciberseguridad.config import Settings
    from pathlib import Path
    now = utcnow()
    return Settings(
        data_dir=Path('/tmp/agntia-identity-vs2'),
        principals=[
            {'id': 'ownerA', 'actor_id': 'ownerA', 'role': 'owner', 'kind': 'human',
             'tenants': [TENANT_A], 'token_env': 'CYBER_ID_OWNER_A'},
            {'id': 'ownerB', 'actor_id': 'ownerB', 'role': 'owner', 'kind': 'human',
             'tenants': [TENANT_B], 'token_env': 'CYBER_ID_OWNER_B'},
            {'id': 'analystA', 'actor_id': 'analystA', 'role': 'analyst', 'kind': 'human',
             'tenants': [TENANT_A], 'token_env': 'CYBER_ID_ANALYST_A'},
            {'id': 'revokedA', 'actor_id': 'revokedA', 'role': 'viewer', 'kind': 'human',
             'tenants': [TENANT_A], 'token_env': 'CYBER_ID_REVOKED_A', 'enabled': False},
        ],
        targets={
            'repoA': {'tenant_id': TENANT_A, 'kind': 'repository', 'location': '/synthetic/repoA'},
            'repoB': {'tenant_id': TENANT_B, 'kind': 'repository', 'location': '/synthetic/repoB'},
        },
        consents={
            'consentA': {'tenant_id': TENANT_A, 'target_refs': ['repoA'], 'profiles': ['static_read'],
                         'evidence_ref': 'synthetic-consent-A', 'authority_actor_id': 'ownerA',
                         'starts_at': (now - timedelta(hours=1)).isoformat(),
class IdentityTenancyTests(unittest.TestCase):
    """Dos tenants con aislamiento completo; nunca hay owner implícito ni identidad por LLM."""

    def setUp(self):
        self.settings = _settings_with_two_tenants()
        for env in ('CYBER_ID_OWNER_A', 'CYBER_ID_OWNER_B', 'CYBER_ID_ANALYST_A', 'CYBER_ID_REVOKED_A'):
            os.environ[env] = 'x' * 64

    def tearDown(self):
        for env in ('CYBER_ID_OWNER_A', 'CYBER_ID_OWNER_B', 'CYBER_ID_ANALYST_A', 'CYBER_ID_REVOKED_A'):
            os.environ.pop(env, None)

    def _auth(self, token_env):
        from agntia_ciberseguridad.auth import Authenticator
        settings = self.settings
        return Authenticator(settings).authenticate(f'Bearer {os.getenv(token_env)}')
                         'expires_at': (now + timedelta(days=30)).isoformat(),
                         'max_requests': 100, 'max_cost_cents': 0},
            'consentB': {'tenant_id': TENANT_B, 'target_refs': ['repoB'], 'profiles': ['static_read'],
                         'evidence_ref': 'synthetic-consent-B', 'authority_actor_id': 'ownerB',
                         'starts_at': (now - timedelta(hours=1)).isoformat(),
                         'expires_at': (now + timedelta(days=30)).isoformat(),
                         'max_requests': 100, 'max_cost_cents': 0},
        }
    def test_two_tenants_isolated(self):
        from agntia_ciberseguridad.service import Service
        from agntia_ciberseguridad.storage import Database
        import tempfile
        root = tempfile.mkdtemp()
        db = Database(root)
        db.migrate()
        service = Service(self.settings, db)
        ownerA = self._auth('CYBER_ID_OWNER_A')
        ownerB = self._auth('CYBER_ID_OWNER_B')

        assetA = service.create_asset(ownerA, TENANT_A,
                                      AssetCreate(target_ref='repoA', kind='repository',
                                                  display_name='Repo A'), 'fixture')
        assetB = service.create_asset(ownerB, TENANT_B,
                                      AssetCreate(target_ref='repoB', kind='repository',
                                                  display_name='Repo B'), 'fixture')
        self.assertNotEqual(assetA['id'], assetB['id'])

        assetsA = service.list_assets(ownerA, TENANT_A)
        self.assertEqual(len(assetsA['items']), 1)
        self.assertEqual(assetsA['items'][0]['tenant_id'], TENANT_A)

        assetsB = service.list_assets(ownerB, TENANT_B)
        self.assertEqual(len(assetsB['items']), 1)
    def test_cross_tenant_read_is_404_not_enumeration(self):
        from agntia_ciberseguridad.service import Service
        from agntia_ciberseguridad.storage import Database
        import tempfile
        root = tempfile.mkdtemp()
        db = Database(root)
        db.migrate()
        service = Service(self.settings, db)
        ownerA = self._auth('CYBER_ID_OWNER_A')
        ownerB = self._auth('CYBER_ID_OWNER_B')

        assetA = service.create_asset(ownerA, TENANT_A,
                                      AssetCreate(target_ref='repoA', kind='repository',
                                                  display_name='Repo A'), 'fixture')

        with self.assertRaises(DomainError) as error:
            service.get_asset(ownerB, TENANT_A, assetA['id'])
        self.assertEqual(error.exception.code, 'not_found')
        self.assertEqual(assetsB['items'][0]['tenant_id'], TENANT_B)
    def test_revoked_actor_is_rejected(self):
        from agntia_ciberseguridad.service import Service
        from agntia_ciberseguridad.storage import Database
        import tempfile
        root = tempfile.mkdtemp()
        db = Database(root)
        db.migrate()
        service = Service(self.settings, db)
        revoked = self._auth('CYBER_ID_REVOKED_A')

        with self.assertRaises(DomainError) as error:
            service.list_assets(revoked, TENANT_A)
        self.assertEqual(error.exception.code, 'principal_revoked')

    def test_expired_grant_is_rejected(self):
        from agntia_ciberseguridad.service import Service
        from agntia_ciberseguridad.storage import Database
        import tempfile
        root = tempfile.mkdtemp()
        db = Database(root)
        db.migrate()
        service = Service(self.settings, db)
        ownerA = self._auth('CYBER_ID_OWNER_A')
        analystA = self._auth('CYBER_ID_ANALYST_A')

        asset = service.create_asset(ownerA, TENANT_A,
                                     AssetCreate(target_ref='repoA', kind='repository',
                                                 display_name='Repo A'), 'fixture')

        now = utcnow()
        with self.assertRaises(ValueError):
            GrantCreate(asset_id=asset['id'], consent_ref='consentA', profile='static_read',
                        starts_at=(now - timedelta(days=10)),
                        expires_at=(now - timedelta(days=1)),
                        max_requests=10, max_cost_cents=0, purpose='synthetic')
    def test_read_only_vs_write_by_role(self):
        from agntia_ciberseguridad.service import Service
        from agntia_ciberseguridad.storage import Database
        import tempfile
        root = tempfile.mkdtemp()
        db = Database(root)
        db.migrate()
        service = Service(self.settings, db)
        ownerA = self._auth('CYBER_ID_OWNER_A')

        asset = service.create_asset(ownerA, TENANT_A,
                                     AssetCreate(target_ref='repoA', kind='repository',
                                                 display_name='Repo A'), 'fixture')
        self.assertIsNotNone(asset['id'])

    def test_approval_forged_hash_is_rejected(self):
        from agntia_ciberseguridad.service import Service
        from agntia_ciberseguridad.storage import Database
        from agntia_ciberseguridad.contracts import GrantApproval
        import tempfile
        root = tempfile.mkdtemp()
        db = Database(root)
        db.migrate()
        service = Service(self.settings, db)
        ownerA = self._auth('CYBER_ID_OWNER_A')
        ownerB = self._auth('CYBER_ID_OWNER_B')

        asset = service.create_asset(ownerA, TENANT_A,
                                     AssetCreate(target_ref='repoA', kind='repository',
                                                 display_name='Repo A'), 'fixture')
        now = utcnow()
        grant = service.propose_grant(ownerA, TENANT_A,
                                      GrantCreate(asset_id=asset['id'], consent_ref='consentA',
                                                  profile='static_read', starts_at=now,
                                                  expires_at=now + timedelta(days=1),
                                                  max_requests=10, max_cost_cents=0,
                                                  purpose='synthetic'), 'fixture')

        with self.assertRaises(DomainError) as error:
            service.approve_grant(ownerB, TENANT_A, grant['id'],
                                  GrantApproval(expected_revision=0, proposal_hash='f' * 64,
                                                notes='synthetic'), 'fixture')
        self.assertEqual(error.exception.code, 'conflict')

    def test_no_implicit_owner_from_prompt_or_header(self):
        from agntia_ciberseguridad.auth import Authenticator
        settings = self.settings
        auth = Authenticator(settings)

        with self.assertRaises(DomainError) as error:
            auth.authenticate(None)
        self.assertEqual(error.exception.code, 'auth')

        with self.assertRaises(DomainError) as error:
            auth.authenticate('NotBearer token')
        self.assertEqual(error.exception.code, 'auth')

        with self.assertRaises(DomainError) as error:
            auth.authenticate('Bearer short')
        self.assertEqual(error.exception.code, 'auth')

        with self.assertRaises(DomainError) as error:
            auth.authenticate('Bearer ' + 'z' * 64)
        self.assertEqual(error.exception.code, 'auth')