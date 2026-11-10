"""Explicit opt-in synthetic integration. A skipped case is never Docker evidence."""
import asyncio
from dataclasses import replace
from datetime import timedelta
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from agntia_ciberseguridad.adapters import gitleaks,osv
from agntia_ciberseguridad.offline_database import verify_cache
from agntia_ciberseguridad.runners.base import Tool,ToolImage,RunLimits
from agntia_ciberseguridad.runners.container import ContainerRunner
from agntia_ciberseguridad.util import utcnow
from scripts.create_offline_fixture import create

ROOT=Path(__file__).resolve().parents[2]
ENABLED=os.getenv('AGNTIA_RUN_DOCKER_TESTS')=='1'

@unittest.skipUnless(ENABLED,'Docker integration not requested; no sandbox claim')
class RealScannerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.source=self.root/'input';self.source.mkdir()
        self.db=self.root/'db';self.db.mkdir()
        self.metadata=create(self.db)
        self.images=[ToolImage(Tool(x['tool']),x['version'],x['image'],x['policy_hash']) for x in json.loads((ROOT/'state/scanner-build/images.json').read_text())]
        self.runner=ContainerRunner(self.images,docker=shutil.which('docker'),limits=RunLimits(timeout_seconds=60,memory_mb=512))
    def tearDown(self):self.temp.cleanup()

    async def test_real_gitleaks_canary_and_clean_control(self):
        secret='AGNTIA_TEST_SECRET_'+'Q'*32
        (self.source/'canary.txt').write_text(secret+' # gitleaks:allow\n')
        # The scanner must ignore repository-controlled policy/suppression.
        (self.source/'.gitleaks.toml').write_text('title="Ignore everything"\n')
        (self.source/'.gitleaksignore').write_text('*\n')
        run=await self.runner.run(Tool.gitleaks,self.source)
        result=gitleaks.parse(run,'a'*32,manifest_paths={'canary.txt','.gitleaks.toml','.gitleaksignore'})
        self.assertEqual(result['status'],'findings',{'status':run.status,'code':run.exit_code,'error':run.error_code,'parser':result['status']})
        self.assertNotIn(secret,json.dumps(result));self.assertNotIn(secret,repr(run))
        self.assertTrue(any(f['rule_id']=='agntia-canary' for f in result['findings']))
        for path in self.source.iterdir():path.unlink()
        (self.source/'normal.txt').write_text('Ordinary public fixture with no credentials\n')
        clean=await self.runner.run(Tool.gitleaks,self.source)
        self.assertEqual(gitleaks.parse(clean,'a'*32)['status'],'no_findings')

    async def test_real_osv_vulnerable_control_stale_and_missing_db(self):
        verify_cache(self.db,self.metadata,utcnow())
        (self.source/'requirements.txt').write_text('agntia-demo-package==1.0.0\n')
        (self.source/'osv-scanner.toml').write_text('[[PackageOverrides]]\nignore = true\n')
        run=await self.runner.run(Tool.osv,self.source,cache=self.db)
        result=osv.parse(run,'a'*32,database=self.metadata,manifest_paths={'requirements.txt','osv-scanner.toml'})
        self.assertEqual(result['status'],'findings',{'status':run.status,'code':run.exit_code,'error':run.error_code,'parser':result['status']})
        self.assertEqual(result['findings'][0]['advisory_id'],'AGNTIA-TEST-0001')
        (self.source/'requirements.txt').write_text('agntia-demo-package==2.0.0\n')
        clean=await self.runner.run(Tool.osv,self.source,cache=self.db)
        self.assertEqual(osv.parse(clean,'a'*32,database=self.metadata)['status'],'no_findings')
        stale={**self.metadata,'fetched_at':(utcnow()-timedelta(days=2)).isoformat()}
        self.assertEqual(osv.parse(clean,'a'*32,database=stale)['status'],'stale')
        (self.db/'osv-scalibr/PyPI/all.zip').unlink()
        missing=await self.runner.run(Tool.osv,self.source,cache=self.db)
        parsed=osv.parse(missing,'a'*32,database=self.metadata)
        self.assertNotEqual(parsed['status'],'no_findings')
        self.assertFalse(parsed['scan_clean'])


@unittest.skipUnless(ENABLED,'Docker integration not requested; no sandbox claim')
class RealSandboxTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.image=ToolImage(Tool.gitleaks,'8.30.1',(ROOT/'state/scanner-build/probe.id').read_text().strip(),'c'*64)
    def tearDown(self):self.temp.cleanup()
    async def run_mode(self,mode,limits=None):
        (self.root/'mode.txt').write_text(mode)
        runner=ContainerRunner([self.image],docker=shutil.which('docker'),limits=limits)
        return await runner.run(Tool.gitleaks,self.root)
    async def test_real_uid_files_network_proxy_and_secret_isolation(self):
        os.environ['AGNTIA_HOST_SECRET']='SYNTHETIC_HOST_SENTINEL_NOT_FOR_CONTAINER'
        try:result=await self.run_mode('inspect')
        finally:os.environ.pop('AGNTIA_HOST_SECRET',None)
        self.assertEqual(result.status,'completed',result.error_code)
        checks=json.loads(result.output)
        self.assertEqual(checks.pop('uid'),65532)
        self.assertTrue(all(checks.values()),checks)
        self.assertTrue(result.cleanup_verified)
    async def test_real_timeout_output_pids_and_cleanup(self):
        timeout=await self.run_mode('timeout',RunLimits(timeout_seconds=.2))
        self.assertEqual(timeout.error_code,'timeout');self.assertTrue(timeout.cleanup_verified)
        output=await self.run_mode('output',RunLimits(max_output_bytes=1024))
        self.assertEqual(output.error_code,'output_limit');self.assertTrue(output.cleanup_verified)
        pids=await self.run_mode('pids')
        self.assertEqual(pids.status,'completed',pids.error_code)
        self.assertTrue(json.loads(pids.output)['pids_limit_applied']);self.assertTrue(pids.cleanup_verified)
