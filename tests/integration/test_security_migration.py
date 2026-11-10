from pathlib import Path
import tempfile
import unittest
from agntia_ciberseguridad.storage import Database,MIGRATIONS,CURRENT_SCHEMA

class SecurityMigrationTests(unittest.TestCase):
    def test_upgrade_from_job_baseline_preserves_audit_and_adds_custody_and_trace_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            db=Database(Path(temporary));db.migrate(MIGRATIONS[:3]);db.provision_tenants(['synthetic'])
            with db.transaction() as connection:db.audit(connection,'synthetic','owner','before.upgrade','fixture','fixture',{'code':'preserved'})
            backup=db.migrate();self.assertTrue(backup.is_file())
            with db.connection(readonly=True) as connection:
                self.assertEqual(connection.execute('SELECT max(version) FROM schema_migrations').fetchone()[0],CURRENT_SCHEMA)
                self.assertTrue(db.verify_audit(connection,'synthetic')['valid'])
                self.assertIn('trace_parent',{r[1] for r in connection.execute('PRAGMA table_info(jobs)')})
                self.assertEqual(connection.execute('SELECT count(*) FROM evidence').fetchone()[0],0)
    def test_rollback_does_not_emit_successful_telemetry_callbacks(self):
        with tempfile.TemporaryDirectory() as temporary:
            db=Database(Path(temporary));db.migrate();calls=[]
            with self.assertRaises(RuntimeError):
                with db.transaction() as connection:
                    db.after_commit(lambda:calls.append('committed'))
                    raise RuntimeError('Synthetic rollback')
            self.assertEqual(calls,[])
            with db.transaction() as connection:db.after_commit(lambda:calls.append('committed'))
            self.assertEqual(calls,['committed'])
    def test_upgrade_from_custody_schema_preserves_existing_records(self):
        from agntia_ciberseguridad.util import canonical
        with tempfile.TemporaryDirectory() as temporary:
            db=Database(Path(temporary));db.migrate(MIGRATIONS[:4]);db.provision_tenants(['synthetic'])
            original=canonical({'id':'fixture','ciphertext_ref':'retained-envelope'})
            with db.transaction() as connection:
                connection.execute('INSERT INTO evidence VALUES(?,?,?,?,?)',('synthetic','a'*32,None,original,0))
                db.audit(connection,'synthetic','reviewer','custody.before.upgrade','a'*32,'fixture',{'preserved':True})
            self.assertTrue(db.migrate().is_file())
            with db.connection(readonly=True) as connection:
                self.assertEqual(connection.execute('SELECT body FROM evidence').fetchone()[0],original)
                self.assertTrue(db.verify_audit(connection,'synthetic')['valid'])
                for table in ('operational_logs','passive_events','source_state','agent_manifests','delegations'):
                    self.assertEqual(connection.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
    def test_upgrade_from_phase25_keeps_old_grants_and_audit_for_reconciliation(self):
        from agntia_ciberseguridad.util import canonical
        with tempfile.TemporaryDirectory() as temporary:
            db=Database(Path(temporary));db.migrate(MIGRATIONS[:5]);db.provision_tenants(['synthetic'])
            original=canonical({'id':'b'*32,'policy_version':'delegated-read-v1','legacy':True})
            with db.transaction() as connection:
                connection.execute('INSERT INTO delegations VALUES(?,?,?,?,?,?,?)',('synthetic','b'*32,None,original,'c'*64,None,0))
                db.audit(connection,'synthetic','reviewer','before.gateway.upgrade','b'*32,'fixture',{'preserved':True})
            self.assertTrue(db.migrate().is_file())
            with db.connection(readonly=True) as connection:
                self.assertEqual(connection.execute('SELECT body FROM delegations').fetchone()[0],original)
                self.assertTrue(db.verify_audit(connection,'synthetic')['valid'])
                self.assertEqual(connection.execute('SELECT count(*) FROM agent_controls').fetchone()[0],0)
    def test_schema6_upgrade_preserves_audit_and_adds_privacy_tables(self):
        from agntia_ciberseguridad.util import canonical
        with tempfile.TemporaryDirectory() as temporary:
            db=Database(Path(temporary));db.migrate(MIGRATIONS[:6]);db.provision_tenants(['synthetic'])
            with db.transaction() as connection:db.audit(connection,'synthetic','reviewer','before.privacy.upgrade','fixture','fixture',{'preserved':True})
            backup=db.migrate();self.assertTrue(backup.is_file())
            with db.connection(readonly=True) as connection:
                self.assertTrue(db.verify_audit(connection,'synthetic')['valid'])
                for table in ('governance_records','governance_history','evidence_privacy','report_source_scopes'):
                    self.assertEqual(connection.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
