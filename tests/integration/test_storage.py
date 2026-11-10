from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import tempfile
import unittest

from agntia_ciberseguridad.storage import Database,MIGRATIONS
from agntia_ciberseguridad.util import canonical,digest


class StorageTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.db=Database(Path(self.tmp.name))
    def tearDown(self):self.tmp.cleanup()

    def test_fresh_upgrade_backup_and_idempotence(self):
        backup=self.db.migrate();self.assertTrue(backup.is_file());self.db.provision_tenants(['tenantA'])
        with self.db.transaction() as c:self.db.audit(c,'tenantA','actor','fixture','object','correlation',{'code':'safe'})
        extended=(*MIGRATIONS,(2,['CREATE TABLE fixture_upgrade(id TEXT PRIMARY KEY)']))
        backup2=self.db.migrate(extended);self.assertTrue(backup2.is_file());self.assertIsNone(self.db.migrate(extended))
        with self.db.connection(readonly=True) as c:self.assertTrue(self.db.verify_audit(c,'tenantA')['valid']);self.assertEqual(c.execute('SELECT count(*) FROM tenants').fetchone()[0],1)
        with sqlite3.connect(backup2) as c:self.assertEqual(c.execute('SELECT count(*) FROM audit').fetchone()[0],1)
        with self.assertRaises(ValueError):self.db.migrate()

    def test_failed_upgrade_rolls_back_existing_data_and_audit(self):
        self.db.migrate();self.db.provision_tenants(['tenantA'])
        with self.db.transaction() as c:self.db.audit(c,'tenantA','actor','before','object','correlation',{'code':'preserved'})
        with self.assertRaises(sqlite3.OperationalError):self.db.migrate((*MIGRATIONS,(2,['CREATE TABLE must_rollback(id TEXT)','INVALID SQL'])))
        with self.db.connection(readonly=True) as c:
            self.assertIsNone(c.execute("SELECT name FROM sqlite_master WHERE name='must_rollback'").fetchone())
            self.assertTrue(self.db.verify_audit(c,'tenantA')['valid']);self.assertEqual(c.execute('SELECT max(version) FROM schema_migrations').fetchone()[0],1)

    def test_foreign_keys_and_readonly_connections(self):
        self.db.migrate();self.db.provision_tenants(['tenantA','tenantB'])
        with self.db.transaction() as c:c.execute('INSERT INTO assets VALUES(?,?,?,?,?,?)',('tenantA','a'*32,'refA',0,'registered',canonical({'id':'a'*32})))
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.transaction() as c:c.execute('INSERT INTO grants VALUES(?,?,?,?,?,?)',('tenantB','b'*32,'a'*32,0,'proposed','{}'))
        with self.assertRaises(sqlite3.OperationalError):
            with self.db.connection(readonly=True) as c:c.execute('DELETE FROM assets')

    def test_concurrent_initialization_and_tenant_sequences(self):
        with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda _:self.db.migrate(),range(2)))
        self.db.provision_tenants(['tenantA','tenantB'])
        def append(i):
            with self.db.transaction() as c:self.db.audit(c,'tenantA','actor','parallel','object','correlation',{'index':i})
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(append,range(12)))
        with self.db.transaction() as c:self.db.audit(c,'tenantB','actor','isolated','object','correlation',{'code':'safe'})
        with self.db.connection(readonly=True) as c:
            self.assertEqual(self.db.verify_audit(c,'tenantA')['checked_events'],12)
            self.assertEqual(self.db.verify_audit(c,'tenantB')['checked_events'],1)
            self.assertTrue(self.db.verify_audit(c,'tenantA')['valid'])

    def test_restore_backup_and_detect_tampering(self):
        self.db.migrate();self.db.provision_tenants(['tenantA'])
        with self.db.transaction() as c:self.db.audit(c,'tenantA','actor','original','object','correlation',{'code':'safe'})
        target=Path(self.tmp.name)/'restored.sqlite3'
        with sqlite3.connect(self.db.path) as source,sqlite3.connect(target) as dest:source.backup(dest)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.transaction() as c:c.execute("DELETE FROM audit")
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.transaction() as c:c.execute("UPDATE audit SET hash='forbidden'")
        # Simulate a privileged administrator removing the guard, outside service permissions.
        with self.db.transaction() as c:
            c.execute("DROP TRIGGER audit_no_update")
            c.execute("UPDATE audit SET body=json_set(body,'$.detail.code','altered') WHERE tenant_id='tenantA'")
        with self.db.connection(readonly=True) as c:self.assertFalse(self.db.verify_audit(c,'tenantA')['valid'])
        with sqlite3.connect(target) as source,sqlite3.connect(self.db.path) as dest:source.backup(dest)
        with self.db.connection(readonly=True) as c:self.assertTrue(self.db.verify_audit(c,'tenantA')['valid'])


class DuplicateMutationTests(unittest.TestCase):
    def test_concurrent_duplicate_asset_yields_one_object(self):
        from tests.support import Fixture
        from agntia_ciberseguridad.contracts import AssetCreate
        from agntia_ciberseguridad.errors import DomainError
        fixture=Fixture()
        try:
            actor=fixture.service.auth.authenticate(fixture.headers()['Authorization'])
            body=AssetCreate(target_ref='repoA',kind='repository',display_name='Concurrent synthetic fixture')
            def insert(_):
                try:
                    fixture.service.create_asset(actor,'tenantA',body,'concurrent-fixture')
                    return 'created'
                except DomainError as error:return error.code
            with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(insert,range(2)))
            self.assertCountEqual(results,['created','conflict'])
            with fixture.app.state.db.connection(readonly=True) as db:
                self.assertEqual(db.execute('SELECT count(*) FROM assets').fetchone()[0],1)
                self.assertTrue(fixture.app.state.db.verify_audit(db,'tenantA')['valid'])
        finally:fixture.close()


class MultiprocessMigrationTests(unittest.TestCase):
    def test_two_processes_initialize_without_lost_schema(self):
        import subprocess
        import sys
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temporary:
            code='from pathlib import Path; import sys; from agntia_ciberseguridad.storage import Database; Database(Path(sys.argv[1]), timeout=3).migrate()'
            processes=[subprocess.Popen([sys.executable,'-c',code,temporary],stdout=subprocess.PIPE,stderr=subprocess.PIPE) for _ in range(2)]
            for process in processes:
                out,error=process.communicate(timeout=10)
                self.assertEqual(process.returncode,0,error.decode())
            database=Database(Path(temporary))
            with database.connection(readonly=True) as db:
                self.assertEqual(db.execute('SELECT version FROM schema_migrations').fetchall()[0][0],1)
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
