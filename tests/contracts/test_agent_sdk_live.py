"""Live Node SDK -> FastAPI: manifest, human delegation, governed read and revoke."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import threading
import time
import unittest
import uvicorn
from tests.security.test_observability_controls import NewSetup

ROOT=Path(__file__).resolve().parents[2]
class AgentSdkLiveTests(unittest.TestCase):
    def test_node_creates_manifest_uses_and_revokes_human_delegation(self):
        if not shutil.which('node'):
            if os.getenv('CI'):self.fail('Node required in CI')
            self.skipTest('Node not installed')
        setup=NewSetup();prepared=False;server=None;thread=None
        try:
            setup.setUp();prepared=True;fixture=setup.f
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
            env={**os.environ,'CYBER_AGENT_CONTRACT_URL':f'http://127.0.0.1:{port}',
                 'CYBER_AGENT_CONTRACT_OWNER_TOKEN':fixture.tokens['analystA'],
                 'CYBER_AGENT_CONTRACT_REVIEWER_TOKEN':fixture.tokens['reviewerA'],
                 'CYBER_AGENT_CONTRACT_AGENT_TOKEN':os.environ['CYBER_AGENT_A'],
                 'CYBER_AGENT_CONTRACT_ASSET':setup.fixture.asset['id']}
            result=subprocess.run(['node','--test','--test-isolation=none','typescript/test/agent-contract.test.mjs'],cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('pass',result.stdout)
            self.assertNotIn('# SKIP',result.stdout)
        finally:
            if server:server.should_exit=True
            if thread:thread.join(timeout=3)
            if prepared:
                fixture.service.telemetry.close();setup.tearDown()
