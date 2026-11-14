import base64
from pathlib import Path
import os
import unittest
from unittest.mock import patch
from tests.security.support_custody import CustodySetup
from agntia_ciberseguridad.recovery import backup_lab,restore_lab
from agntia_ciberseguridad.storage import Database
from agntia_ciberseguridad.app import create_app
from agntia_ciberseguridad.errors import DomainError

class RecoveryTests(CustodySetup,unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp();self.key=patch.dict(os.environ,{'CYBER_BACKUP_FIXTURE':base64.b64encode(os.urandom(32)).decode()});self.key.start()
    def tearDown(self):self.key.stop();super().tearDown()
    def backup(self):return backup_lab(self.f.service,self.f.root/'copy.enc','CYBER_BACKUP_FIXTURE',quiesced=True)
    async def test_encrypted_backup_restore_integrity_scopes_and_blocked_api(self):
        doc=self.reviewed_document();receipt=self.backup();self.assertFalse(receipt['external_keys_included'])
        content=(self.f.root/'copy.enc').read_bytes();self.assertNotIn(b'Synthetic source reviewed',content);self.assertNotIn(self.f.tokens['reviewerA'].encode(),content)
        target=self.f.root/'restored';r=restore_lab(self.f.root/'copy.enc',target,'CYBER_BACKUP_FIXTURE');self.assertFalse(r['new_work_enabled']);self.assertTrue(r['privacy_reconciliation_required'])
        db=Database(target)
        with db.connection(readonly=True) as c:
            self.assertTrue(db.verify_audit(c,'tenantA')['valid']);self.assertEqual(c.execute('SELECT count(*) FROM evidence WHERE tenant_id=?',('tenantB',)).fetchone()[0],0)
        # Ciphertext and revision preserved; external key required to decrypt, API stays closed.
        self.assertEqual((target/'evidence'/'tenantA'/(doc['id']+'-redacted.enc')).read_bytes(),self.vault._file(self._meta(doc['id']),'redacted').read_bytes())
        settings=self.f.settings.model_copy(update={'data_dir':target});app=create_app(settings)
        import httpx
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture.invalid') as client:
            self.assertEqual((await client.get('/health/ready')).status_code,503)
            self.assertEqual((await client.get('/v1/tenants/tenantA/assets',headers=self.f.headers())).status_code,503)
        app.state.service.telemetry.close()
    def _meta(self,eid):
        with self.f.service.db.connection(readonly=True) as c:return self.vault._row(c,'tenantA',eid)
    async def test_corruption_wrong_key_and_no_overwrite(self):
        self.reviewed_document();self.backup();target=self.f.root/'restored'
        with patch.dict(os.environ,{'CYBER_BACKUP_FIXTURE':base64.b64encode(os.urandom(32)).decode()}):
            with self.assertRaises(DomainError):restore_lab(self.f.root/'copy.enc',target,'CYBER_BACKUP_FIXTURE')
        self.assertFalse(target.exists())
        blob=bytearray((self.f.root/'copy.enc').read_bytes());blob[-1]^=1;(self.f.root/'bad.enc').write_bytes(blob)
        with self.assertRaises(DomainError):restore_lab(self.f.root/'bad.enc',target,'CYBER_BACKUP_FIXTURE')
        restore_lab(self.f.root/'copy.enc',target,'CYBER_BACKUP_FIXTURE')
        with self.assertRaises(ValueError):restore_lab(self.f.root/'copy.enc',target,'CYBER_BACKUP_FIXTURE')
    async def test_backup_refuses_active_worker_nonlab_and_unquiesced(self):
        with self.assertRaises(DomainError):backup_lab(self.f.service,self.f.root/'copy.enc','CYBER_BACKUP_FIXTURE')
        self.submit()
        with self.assertRaises(DomainError):self.backup()
        self.f.settings.lab_mode=False
        with self.assertRaises(DomainError):self.backup()
