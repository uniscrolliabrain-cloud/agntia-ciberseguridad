from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.runners.base import RunLimits,ToolImage,Tool
from agntia_ciberseguridad.runners.container import ContainerRunner

class RunnerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.binary=self.root/'docker';self.binary.write_text('never executed by these contract tests')
        self.input=self.root/'input';self.input.mkdir()
        self.image=ToolImage(Tool.gitleaks,'8.30.1','sha256:'+'a'*64,'b'*64)
        self.runner=ContainerRunner([self.image],docker=str(self.binary))
    def tearDown(self):self.temp.cleanup()

    async def test_profile_is_immutable_no_shell_socket_or_network(self):
        command=self.runner.command(Tool.gitleaks,self.input,'agntia-test')
        self.assertIn('--network=none',command);self.assertIn('--read-only',command)
        self.assertIn('--user=65532:65532',command);self.assertIn('--cap-drop=ALL',command)
        self.assertIn('--log-driver=none',command)
        self.assertNotIn('sh',command);self.assertFalse(any('dst=/var/run/docker.sock' in arg for arg in command))
        self.assertIn('--ignore-gitleaks-allow',command)
        with self.assertRaises(ValueError):ToolImage(Tool.gitleaks,'8.30.1','image:latest','b'*64)
        with self.assertRaises(ValueError):ToolImage(Tool.gitleaks,'unknown','sha256:'+'a'*64,'b'*64)
        with self.assertRaises(ValueError):RunLimits(max_output_bytes=float('inf'))

    async def test_timeout_output_limit_and_cleanup_failures(self):
        for exception,code in [(TimeoutError(),'timeout'),(OverflowError(),'output_limit'),(OSError(),'runner_unavailable')]:
            with patch.object(self.runner,'_process',side_effect=exception),patch.object(self.runner,'_cleanup',return_value=True):
                result=await self.runner.run(Tool.gitleaks,self.input)
                self.assertEqual(result.status,'error');self.assertEqual(result.error_code,code);self.assertTrue(result.cleanup_verified)
        with patch.object(self.runner,'_process',return_value=(0,b'[]')),patch.object(self.runner,'_cleanup',return_value=False):
            result=await self.runner.run(Tool.gitleaks,self.input)
            self.assertEqual(result.error_code,'cleanup_unverified');self.assertEqual(result.output,b'')

    async def test_revocation_cancels_before_launch(self):
        with patch.object(self.runner,'_process') as process,patch.object(self.runner,'_cleanup',return_value=True):
            result=await self.runner.run(Tool.gitleaks,self.input,cancelled=lambda:True)
            self.assertEqual(result.error_code,'cancelled');process.assert_not_called()

    async def test_cache_required_and_mount_path_injection_rejected(self):
        runner=ContainerRunner([ToolImage(Tool.osv,'2.7.1','sha256:'+'c'*64,'b'*64)],docker=str(self.binary))
        with self.assertRaises(DomainError):runner.command(Tool.osv,self.input,'test')
        invalid=self.root/'bad,dst=/host';invalid.mkdir(parents=True)
        with self.assertRaises(DomainError):self.runner.command(Tool.gitleaks,invalid,'test')
