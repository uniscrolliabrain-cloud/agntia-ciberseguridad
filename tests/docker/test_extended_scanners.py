import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from agntia_ciberseguridad.adapters import semgrep,trivy
from agntia_ciberseguridad.runners.base import Tool,ToolImage,RunLimits
from agntia_ciberseguridad.runners.container import ContainerRunner

ROOT=Path(__file__).resolve().parents[2]
@unittest.skipUnless(os.getenv('AGNTIA_RUN_DOCKER_TESTS')=='1','Real Docker extended tools not requested')
class ExtendedScannerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.root.chmod(0o755)
        images=[ToolImage(Tool(x['tool']),x['version'],x['image'],x['policy_hash']) for x in json.loads((ROOT/'state/scanner-build/images.json').read_text())]
        self.runner=ContainerRunner(images,docker=shutil.which('docker'),limits=RunLimits(timeout_seconds=120,memory_mb=768,pids=64))
    def tearDown(self):self.temp.cleanup()
    async def test_real_semgrep_local_rules_hostile_comment_and_fixed_control(self):
        (self.root/'bad.py').write_text('def run(value):\n    return eval(value) # nosemgrep: agntia.python.dynamic-eval\n')
        (self.root/'.semgrepignore').write_text('*\n')
        run=await self.runner.run(Tool.semgrep,self.root)
        result=semgrep.parse(run,'a'*32,manifest_paths={'bad.py','.semgrepignore'})
        self.assertEqual(result['status'],'findings',{'exit':run.exit_code,'error':run.error_code,'parse':result['status']})
        self.assertTrue(any(f['rule_id']=='agntia.python.dynamic-eval' for f in result['findings']))
        self.assertNotIn('return eval(value)',json.dumps(result))
        (self.root/'bad.py').write_text('import ast\ndef run(value):\n    return ast.literal_eval(value)\n')
        clean=await self.runner.run(Tool.semgrep,self.root)
        self.assertEqual(semgrep.parse(clean,'a'*32)['status'],'no_findings',{'exit':clean.exit_code,'error':clean.error_code})
    async def test_real_trivy_config_root_rule_and_control_without_workload(self):
        (self.root/'Dockerfile').write_text('FROM alpine:3.20\nUSER root\n')
        run=await self.runner.run(Tool.trivy,self.root)
        result=trivy.parse(run,'a'*32,manifest_paths={'Dockerfile'})
        self.assertEqual(result['status'],'findings',{'exit':run.exit_code,'error':run.error_code,'parse':result['status']})
        self.assertTrue(any(f['rule_id']=='DS002' for f in result['findings']))
        (self.root/'Dockerfile').write_text('FROM alpine:3.20\nUSER 10001\n')
        control=await self.runner.run(Tool.trivy,self.root)
        parsed=trivy.parse(control,'a'*32,manifest_paths={'Dockerfile'})
        self.assertNotEqual(parsed['status'],'error',{'exit':control.exit_code,'error':control.error_code})
        self.assertFalse(any(f['rule_id']=='DS002' for f in parsed['findings']))
        self.assertEqual(parsed['coverage']['image_vulnerabilities'],'not_tested')
