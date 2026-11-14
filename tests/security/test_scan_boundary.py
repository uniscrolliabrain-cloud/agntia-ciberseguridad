from unittest.mock import AsyncMock
import unittest
from tests.security import test_ingestion as ingestion
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.runners.base import RunResult,Tool
from agntia_ciberseguridad.safety import ReleaseGates
from agntia_ciberseguridad.scanning import StaticScanner

class ScanBoundaryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Use fixture setup only, not its inherited test methods.
        self.fixture=ingestion.SnapshotTests();self.fixture.setUp()
    def tearDown(self):self.fixture.tearDown()
    async def test_release_denied_before_runner_and_validated_fixture_flow(self):
        f=self.fixture
        (f.f.repo/'normal.txt').write_text('Synthetic input')
        manifest=f.acquire()
        runner=AsyncMock()
        runner.run.return_value=RunResult(Tool.gitleaks,'8.30.1','completed',0,b'[]',cleanup_verified=True,policy_hash='a'*64,image='sha256:'+'b'*64)
        scanner=StaticScanner(f.f.service,runner)
        with self.assertRaises(DomainError):await scanner.scan(f.actor,'tenantA',f.body,manifest['id'],Tool.gitleaks,'fixture')
        runner.run.assert_not_called()
        # Test-only verification values; this does not approve an actual deployment review.
        scanner.gates=ReleaseGates(True,True,True)
        result=await scanner.scan(f.actor,'tenantA',f.body,manifest['id'],Tool.gitleaks,'fixture')
        self.assertEqual(result['status'],'no_findings')
        self.assertFalse(result['scan_clean'])
        f.f.settings.principals[0].enabled=False
        with self.assertRaises(DomainError):await scanner.scan(f.actor,'tenantA',f.body,manifest['id'],Tool.gitleaks,'fixture')
        self.assertEqual(runner.run.await_count,1)
