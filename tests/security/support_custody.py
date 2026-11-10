import base64
import os
from unittest.mock import patch
from tests.integration import test_jobs as jobs
from agntia_ciberseguridad.config import EvidencePolicy
from agntia_ciberseguridad.evidence.vault import Vault
from agntia_ciberseguridad.reviews import Reviews
from agntia_ciberseguridad.reports import Reports

class CustodySetup(jobs.Setup):
    def setUp(self):
        super().setUp()
        self.keys=patch.dict(os.environ,{'CYBER_EVIDENCE_A':base64.b64encode(os.urandom(32)).decode(),
            'CYBER_EVIDENCE_B':base64.b64encode(os.urandom(32)).decode(),
            'CYBER_METRICS_GLOBAL':'synthetic-global-metrics-'+'m'*32})
        self.keys.start()
        self.f.settings.evidence_policies={
            'tenantA':EvidencePolicy(key_refs=['CYBER_EVIDENCE_A'],legal_basis_ref='synthetic-authority-A',custodian_ref='owner-A'),
            'tenantB':EvidencePolicy(key_refs=['CYBER_EVIDENCE_B'],legal_basis_ref='synthetic-authority-B',custodian_ref='owner-B')}
        self.f.settings.metrics_token_env='CYBER_METRICS_GLOBAL'
        self.vault=Vault(self.f.service);self.reviews=Reviews(self.f.service);self.reports=Reports(self.f.service)
        self.reviewer=self.f.service.auth.authenticate(self.f.headers('reviewerA')['Authorization'])
        self.viewer=self.f.service.auth.authenticate(self.f.headers('viewerA')['Authorization'])
    def tearDown(self):
        self.keys.stop();self.f.service.telemetry.close();super().tearDown()
    def reviewed_document(self,job_id=None):
        item=self.vault.put(self.actor,'tenantA',b'Synthetic source reviewed by a distinct principal','text/plain','fixture',source_job_id=job_id)
        return self.vault.manage(self.reviewer,'tenantA',item['id'],0,'review','fixture',reason='Synthetic manual verification')
