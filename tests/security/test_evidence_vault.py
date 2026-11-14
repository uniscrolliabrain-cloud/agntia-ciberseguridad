import base64
from datetime import timedelta
import json
import os
import shutil
import unittest
from agntia_ciberseguridad.evidence.vault import Vault
from agntia_ciberseguridad.config import EvidencePolicy
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.util import utcnow
from tests.security.support_custody import CustodySetup

class VaultTests(CustodySetup,unittest.TestCase):
    def test_actual_encryption_redaction_permissions_and_no_secret_in_public_metadata(self):
        secret='AGNTIA_TEST_SECRET_'+'Z'*32
        item=self.vault.put(self.actor,'tenantA',('original '+secret+' Bearer '+'b'*32+' test@example.invalid').encode(),'text/plain','fixture')
        redacted=self.vault.read(self.viewer,'tenantA',item['id'],'fixture')
        self.assertNotIn(secret.encode(),redacted);self.assertNotIn(b'test@example.invalid',redacted)
        self.assertNotIn('key_ref',item);self.assertNotIn('original_sha256',item)
        for file in self.vault.root.rglob('*.enc'):self.assertNotIn(secret.encode(),file.read_bytes())
        self.assertNotIn(secret.encode(),self.f.service.db.path.read_bytes())
        with self.assertRaises(DomainError):self.vault.read(self.viewer,'tenantA',item['id'],'fixture',original=True,reason='Unauthorized original read')
        original=self.vault.read(self.reviewer,'tenantA',item['id'],'fixture',original=True,reason='Human custody verification')
        self.assertIn(secret.encode(),original)
        foreign=self.f.service.auth.authenticate(self.f.headers('operatorB')['Authorization'])
        with self.assertRaises(DomainError) as error:self.vault.metadata(foreign,'tenantA',item['id'])
        self.assertEqual(error.exception.status,404)

    def test_corruption_missing_key_and_restore_fail_closed(self):
        item=self.vault.put(self.actor,'tenantA',b'synthetic original','text/plain','fixture')
        file=self.vault.root/'tenantA'/(item['id']+'-redacted.enc');backup=file.read_bytes()
        file.chmod(0o600);file.write_bytes(b'corrupt')
        with self.assertRaises(DomainError) as error:self.vault.read(self.viewer,'tenantA',item['id'],'fixture')
        self.assertEqual(error.exception.code,'evidence_integrity')
        file.write_bytes(backup)
        self.assertEqual(self.vault.read(self.viewer,'tenantA',item['id'],'fixture'),b'synthetic original')
        old=os.environ.pop('CYBER_EVIDENCE_A')
        try:
            with self.assertRaises(DomainError) as error:self.vault.read(self.viewer,'tenantA',item['id'],'fixture')
            self.assertEqual(error.exception.code,'evidence_key_unavailable')
        finally:os.environ['CYBER_EVIDENCE_A']=old

    def test_rotation_preserves_old_envelopes_with_approved_key_versions(self):
        item=self.vault.put(self.actor,'tenantA',b'old key content','text/plain','fixture')
        os.environ['CYBER_EVIDENCE_A2']=base64.b64encode(os.urandom(32)).decode()
        try:
            self.f.settings.evidence_policies['tenantA']=EvidencePolicy(key_refs=['CYBER_EVIDENCE_A2','CYBER_EVIDENCE_A'],legal_basis_ref='synthetic-A',custodian_ref='owner-A')
            self.vault.put(self.actor,'tenantA',b'new key content','text/plain','fixture')
            self.assertEqual(self.vault.read(self.viewer,'tenantA',item['id'],'fixture'),b'old key content')
        finally:os.environ.pop('CYBER_EVIDENCE_A2',None)

    def test_hold_retention_and_explicit_purge(self):
        item=self.vault.put(self.actor,'tenantA',b'retain me','text/plain','fixture')
        held=self.vault.manage(self.reviewer,'tenantA',item['id'],0,'hold','fixture',enabled=True,reason='Synthetic legal hold')
        future=utcnow()+timedelta(days=31);vault=Vault(self.f.service,clock=lambda:future)
        with self.assertRaises(DomainError):vault.manage(self.reviewer,'tenantA',item['id'],held['revision'],'purge','fixture',reason='Expired but held')
        released=vault.manage(self.reviewer,'tenantA',item['id'],held['revision'],'hold','fixture',enabled=False,reason='Hold legitimately ended')
        with self.assertRaises(DomainError) as error:vault.read(self.viewer,'tenantA',item['id'],'fixture')
        self.assertEqual(error.exception.code,'evidence_expired')
        deleted=vault.manage(self.reviewer,'tenantA',item['id'],released['revision'],'purge','fixture',reason='Synthetic policy expiry')
        self.assertEqual(deleted['state'],'deleted')
        self.assertFalse(list((vault.root/'tenantA').glob('*.enc')))

    def test_invalid_mime_pdf_quarantine_agent_and_same_actor_review(self):
        with self.assertRaises(DomainError):self.vault.put(self.actor,'tenantA',b'not a pdf','application/pdf','fixture')
        item=self.vault.put(self.actor,'tenantA',b'%PDF-1.7\nUntrusted fixture','application/pdf','fixture')
        self.assertEqual(item['state'],'quarantined')
        with self.assertRaises(DomainError):self.vault.manage(self.reviewer,'tenantA',item['id'],0,'review','fixture',reason='No antivirus override')
        self.f.settings.principals[1].kind='agent'
        with self.assertRaises(DomainError) as error:self.vault.read(self.reviewer,'tenantA',item['id'],'fixture',original=True,reason='Agent wants original')
        self.assertEqual(error.exception.code,'human_required')
