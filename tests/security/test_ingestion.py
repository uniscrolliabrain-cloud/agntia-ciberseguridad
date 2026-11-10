import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests.support import Fixture
from agntia_ciberseguridad.artifact_limits import ArtifactLimits
from agntia_ciberseguridad.contracts import AssetCreate,AuditPreview,GrantCreate,GrantApproval
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.snapshots import SnapshotStore

class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture();self.actor=self.f.service.auth.authenticate(self.f.headers()['Authorization'])
        reviewer=self.f.service.auth.authenticate(self.f.headers('reviewerA')['Authorization'])
        self.asset=self.f.service.create_asset(self.actor,'tenantA',AssetCreate(target_ref='repoA',kind='repository',display_name='Synthetic source'),'fixture')
        grant=self.f.service.propose_grant(self.actor,'tenantA',GrantCreate(**self.f.grant_body(self.asset['id'])),'fixture')
        self.f.service.approve_grant(reviewer,'tenantA',grant['id'],GrantApproval(expected_revision=0,proposal_hash=grant['proposal_hash'],notes='Synthetic approval'),'fixture')
        self.body=AuditPreview(asset_id=self.asset['id'],grant_id=grant['id'],profile='static_read')
        self.store=SnapshotStore(self.f.service)
    def tearDown(self):
        # Sealed snapshots are made writable only inside the test-owned temp directory.
        root=self.f.settings.data_dir/'snapshots'
        if root.exists():
            for base,dirs,files in os.walk(root):Path(base).chmod(0o700)
        self.f.close()
    def acquire(self,**kwargs):return self.store.acquire(self.actor,'tenantA',self.body,'fixture',**kwargs)

    def test_capture_seal_manifest_and_no_hook_execution(self):
        (self.f.repo/'hello.py').write_text('print("not executed")\n')
        hooks=self.f.repo/'.git/hooks';hooks.mkdir(parents=True)
        marker=self.f.root/'must-not-exist'
        (hooks/'post-checkout').write_text('touch '+str(marker))
        manifest=self.acquire()
        self.assertFalse(marker.exists())
        self.assertEqual([f['path'] for f in manifest['files']],['hello.py'])
        verified,contents=self.store.verify(self.actor,'tenantA',manifest['id'])
        self.assertEqual(verified['content_hash'],manifest['content_hash'])
        self.assertEqual((contents/'hello.py').read_text(),'print("not executed")\n')
        self.assertIsNone(manifest['git_commit'])
        self.assertEqual(manifest['coverage'],'partial')
        foreign=self.f.service.auth.authenticate(self.f.headers('operatorB')['Authorization'])
        with self.assertRaises(DomainError) as error:self.store.verify(foreign,'tenantA',manifest['id'])
        self.assertEqual(error.exception.status,404)

    def test_symlink_hardlink_and_fifo_rejected_before_read(self):
        outside=self.f.root/'outside.txt';outside.write_text('host sentinel')
        for kind in ('symlink','hardlink','fifo'):
            path=self.f.repo/'bad'
            if kind=='symlink':path.symlink_to(outside)
            elif kind=='hardlink':os.link(outside,path)
            else:os.mkfifo(path)
            with self.assertRaises(DomainError):self.acquire()
            path.unlink()
            self.assertEqual(outside.read_text(),'host sentinel')
            self.assertFalse(any((self.store.root/'tenantA').iterdir()))

    def test_limits_empty_directory_bomb_and_unsupported_archive(self):
        (self.f.repo/'huge').write_bytes(b'x'*128)
        self.store=SnapshotStore(self.f.service,ArtifactLimits(max_file_bytes=64))
        with self.assertRaises(DomainError) as error:self.acquire()
        self.assertEqual(error.exception.code,'artifact_limit')
        (self.f.repo/'huge').unlink()
        for name in ('one','two','three'):(self.f.repo/name).mkdir()
        self.store=SnapshotStore(self.f.service,ArtifactLimits(max_files=2))
        with self.assertRaises(DomainError):self.acquire()
        # Archives are copied as data, never extracted or executed.
        for name in ('one','two','three'):(self.f.repo/name).rmdir()
        (self.f.repo/'bomb.zip').write_bytes(b'PK'+b'0'*20)
        self.store=SnapshotStore(self.f.service)
        manifest=self.acquire()
        self.assertEqual(len(manifest['files']),1)
        self.assertFalse((self.f.root/'escaped').exists())

    def test_lfs_submodules_and_binary_coverage_explicit(self):
        (self.f.repo/'large.bin').write_text('version https://git-lfs.github.com/spec/v1\noid sha256:'+'a'*64+'\nsize 999999\n')
        (self.f.repo/'.gitmodules').write_text('[submodule "external"]\nurl=https://external.invalid/repo')
        (self.f.repo/'binary.bin').write_bytes(b'\0abc')
        manifest=self.acquire()
        self.assertEqual(manifest['coverage'],'partial')
        self.assertEqual({x['reason'] for x in manifest['exclusions']},{'external_submodule_not_acquired','lfs_pointer_not_materialized'})
        self.assertTrue(next(x for x in manifest['files'] if x['path']=='binary.bin')['binary'])

    def test_cancel_and_source_mutation_leave_no_snapshot(self):
        (self.f.repo/'file').write_text('original')
        with self.assertRaises(DomainError):self.acquire(cancelled=lambda:True)
        original=os.read
        def mutate(fd,size):
            content=original(fd,size)
            if content:(self.f.repo/'file').write_text('changed!')
            return content
        with patch('agntia_ciberseguridad.snapshots.os.read',side_effect=mutate):
            with self.assertRaises(DomainError) as error:self.acquire()
        self.assertEqual(error.exception.code,'artifact_changed')
        self.assertFalse(any((self.store.root/'tenantA').iterdir()))

    def test_content_tampering_detected(self):
        (self.f.repo/'file').write_text('original')
        manifest=self.acquire();folder=self.store.root/'tenantA'/manifest['id']/'content'
        (folder/'file').chmod(0o600);(folder/'file').write_text('altered')
        with self.assertRaises(DomainError) as error:self.store.verify(self.actor,'tenantA',manifest['id'])
        self.assertEqual(error.exception.code,'snapshot_integrity')

    def test_orphan_manifest_never_becomes_registered_snapshot(self):
        (self.f.repo/'file').write_text('original')
        manifest=self.acquire()
        with self.f.service.db.transaction() as db:db.execute('DELETE FROM snapshots WHERE id=?',(manifest['id'],))
        with self.assertRaises(DomainError) as error:self.store.verify(self.actor,'tenantA',manifest['id'])
        self.assertEqual(error.exception.status,404)
