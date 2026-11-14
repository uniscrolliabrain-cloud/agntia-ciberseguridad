import os
from datetime import timedelta
from pathlib import Path
import tempfile
from unittest.mock import patch

import httpx

from agntia_ciberseguridad.app import create_app
from agntia_ciberseguridad.config import Settings
from agntia_ciberseguridad.util import utcnow


class Fixture:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workspace = self.root / 'approved'
        self.workspace.mkdir()
        self.repo = self.workspace / 'repository'
        self.repo.mkdir()
        self.tokens = {name: 'synthetic-' + name + '-token-' + 'x' * 30 for name in ('analystA', 'reviewerA', 'viewerA', 'operatorB', 'reviewerB')}
        principals = []
        values = {}
        for name, role, tenant in [('analystA', 'analyst', 'tenantA'), ('reviewerA', 'reviewer', 'tenantA'), ('viewerA', 'viewer', 'tenantA'), ('operatorB', 'operator', 'tenantB'), ('reviewerB', 'reviewer', 'tenantB')]:
            ref = 'CYBER_TEST_' + name.upper()
            values[ref] = self.tokens[name]
            principals.append({'id': name, 'actor_id': name, 'role': role, 'tenants': [tenant], 'token_env': ref})
        start, end = utcnow() - timedelta(hours=1), utcnow() + timedelta(days=3)
        self.settings = Settings(data_dir=self.root / 'state', principals=principals,
            approved_workspace_roots=[self.workspace], lab_mode=True,
            targets={
                'repoA': {'tenant_id': 'tenantA', 'kind': 'repository', 'location': str(self.repo)},
                'repoB': {'tenant_id': 'tenantB', 'kind': 'repository', 'location': str(self.repo)},
                'webA': {'tenant_id': 'tenantA', 'kind': 'web', 'location': 'https://approved.example.invalid/app', 'allowed_networks': ['192.0.2.0/24']},
            }, consents={
                'consentA': {'tenant_id': 'tenantA', 'target_refs': ['repoA','webA'], 'profiles':['static_read','passive_web'], 'evidence_ref':'synthetic-only-consent-A', 'authority_actor_id':'reviewerA','starts_at':start,'expires_at':end,'max_requests':100,'max_cost_cents':0},
                'consentB': {'tenant_id': 'tenantB', 'target_refs': ['repoB'], 'profiles':['static_read'], 'evidence_ref':'synthetic-only-consent-B', 'authority_actor_id':'reviewerB','starts_at':start,'expires_at':end,'max_requests':100,'max_cost_cents':0},
            })
        self.env = patch.dict(os.environ, values)
        self.env.start()
        self.app = create_app(self.settings)
        self.service = self.app.state.service

    def headers(self, name='analystA'):
        return {'Authorization': 'Bearer ' + self.tokens[name]}

    def client(self):
        return httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app), base_url='http://fixture.invalid')

    def grant_body(self, asset_id, **overrides):
        return {'asset_id':asset_id,'consent_ref':'consentA','profile':'static_read',
                'starts_at':(utcnow()-timedelta(minutes=1)).isoformat(),
                'expires_at':(utcnow()+timedelta(days=1)).isoformat(),
                'purpose':'Synthetic authorized static analysis only',**overrides}

    def close(self):
        self.env.stop()
        self.temp.cleanup()
