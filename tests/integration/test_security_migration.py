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
