"""Actual Node client to loopback FastAPI, synthetic server credentials only."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import threading
import time
import unittest
import uvicorn
from tests.support import Fixture
from agntia_ciberseguridad.contracts import AssetCreate

ROOT=Path(__file__).resolve().parents[2]
class PythonTypeScriptTests(unittest.TestCase):
    def test_actual_node_client_reads_python_dtos_and_safe_errors(self):
        if not shutil.which('node'):
            if os.getenv('CI'):self.fail('Node required in CI')
            self.skipTest('Node not installed')
        fixture=Fixture();server=None;thread=None
        try:
            actor=fixture.service.auth.authenticate(fixture.headers()['Authorization'])
            fixture.service.create_asset(actor,'tenantA',AssetCreate(target_ref='repoA',kind='repository',display_name='Synthetic contract asset'),'fixture')
            built=ROOT/'typescript/dist/client.js'
            if not built.is_file():
                result=subprocess.run(['node','typescript/build-runtime.mjs'],cwd=ROOT,capture_output=True,text=True,timeout=20)
                self.assertEqual(result.returncode,0,result.stderr)
            try:
                with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
            except PermissionError:
                if os.getenv('CI'):raise
                self.skipTest('Sandbox denies loopback socket; CI contract required')
            server=uvicorn.Server(uvicorn.Config(fixture.app,host='127.0.0.1',port=port,log_level='error',access_log=False))
            thread=threading.Thread(target=server.run,daemon=True);thread.start()
            for _ in range(100):
                if server.started:break
                time.sleep(.02)
            self.assertTrue(server.started)
            env={**os.environ,'CYBER_CONTRACT_URL':f'http://127.0.0.1:{port}','CYBER_CONTRACT_TOKEN':fixture.tokens['viewerA']}
            result=subprocess.run(['node','--test','--test-isolation=none','typescript/test/client.test.mjs'],cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('pass',result.stdout)
            self.assertNotIn('live Python contract when started by test_python_ts # SKIP',result.stdout)
        finally:
            if server:server.should_exit=True
            if thread:thread.join(timeout=3)
            fixture.service.telemetry.close();fixture.close()
