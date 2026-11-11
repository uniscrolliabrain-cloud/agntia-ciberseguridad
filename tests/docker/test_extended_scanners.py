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
        (self.root/'bad.js').write_text('function run(value) { return eval(value); } // nosemgrep: agntia.javascript.dynamic-eval\n')
        (self.root/'bad.ts').write_text('function run(value: string) { return eval(value); } // nosemgrep: agntia.javascript.dynamic-eval\n')
        (self.root/'.semgrepignore').write_text('*\n')
        run=await self.runner.run(Tool.semgrep,self.root)
        result=semgrep.parse(run,'a'*32,manifest_paths={'bad.py','bad.js','bad.ts','.semgrepignore'})
        self.assertEqual(result['status'],'findings',{'exit':run.exit_code,'error':run.error_code,'parse':result['status']})
        self.assertTrue(any(f['rule_id']=='agntia.python.dynamic-eval' for f in result['findings']))
        self.assertNotIn('return eval(value)',json.dumps(result))
        self.assertEqual({f['path'] for f in result['findings'] if f['rule_id']=='agntia.javascript.dynamic-eval'},{'bad.js','bad.ts'})
        (self.root/'bad.py').write_text('import ast\ndef run(value):\n    return ast.literal_eval(value)\n')
        (self.root/'bad.js').write_text('function run(value) { return JSON.parse(value); }\n')
        (self.root/'bad.ts').write_text('function run(value: string) { return JSON.parse(value); }\n')
        clean=await self.runner.run(Tool.semgrep,self.root)
        self.assertEqual(semgrep.parse(clean,'a'*32)['status'],'no_findings',{'exit':clean.exit_code,'error':clean.error_code})
    async def test_real_trivy_config_root_rule_and_control_without_workload(self):
        (self.root/'Dockerfile').write_text('FROM alpine:3.20\nUSER root\n')
        run=await self.runner.run(Tool.trivy,self.root)
        result=trivy.parse(run,'a'*32,manifest_paths={'Dockerfile'})
        self.assertEqual(result['status'],'findings',{'exit':run.exit_code,'error':run.error_code,'parse':result['status']})
        self.assertTrue(any(f['rule_id']=='DS-0002' for f in result['findings']))
        (self.root/'Dockerfile').write_text('FROM alpine:3.20\nUSER 10001\n')
        control=await self.runner.run(Tool.trivy,self.root)
        parsed=trivy.parse(control,'a'*32,manifest_paths={'Dockerfile'})
        self.assertNotEqual(parsed['status'],'error',{'exit':control.exit_code,'error':control.error_code})
        self.assertFalse(any(f['rule_id']=='DS-0002' for f in parsed['findings']))
        self.assertEqual(parsed['coverage']['image_vulnerabilities'],'not_tested')

    async def test_real_snapshot_job_worker_result_and_replay(self):
        from tests.security import test_ingestion as ingestion
        from agntia_ciberseguridad.jobs.contracts import AuditJobCreate
        from agntia_ciberseguridad.jobs.store import JobStore
        from agntia_ciberseguridad.jobs.worker import Worker
        from agntia_ciberseguridad.findings.store import FindingStore
        from agntia_ciberseguridad.scanning import StaticScanner
        from agntia_ciberseguridad.safety import ReleaseGates
        fixture=ingestion.SnapshotTests();fixture.setUp()
        try:
            secret='AGNTIA_TEST_SECRET_'+'J'*32
            (fixture.f.repo/'canary.txt').write_text(secret)
            manifest=fixture.acquire()
            image=self.runner.images[Tool.gitleaks]
            fixture.f.settings.tool_policy_hashes={'gitleaks':image.policy_hash}
            # Only synthetic fixtures. This does not verify the independent release review.
            gates=ReleaseGates(True,True,True)
            store=JobStore(fixture.f.service,gates=gates)
            scanner=StaticScanner(fixture.f.service,self.runner,gates=gates)
            body=AuditJobCreate(asset_id=fixture.asset['id'],grant_id=fixture.body.grant_id,
                snapshot_id=manifest['id'],snapshot_hash=manifest['manifest_hash'],expected_grant_revision=1,tool='gitleaks')
            receipt=store.submit(fixture.actor,'tenantA',body,'real-worker-fixture','fixture')
            done=await Worker(store,scanner,'fixture-worker').run_once()
            self.assertEqual(done['state'],'completed')
            self.assertEqual(done['id'],receipt['id'])
            replay=store.submit(fixture.actor,'tenantA',body,'real-worker-fixture','replay')
            self.assertEqual(replay['id'],receipt['id'])
            self.assertIsNone(await Worker(store,scanner,'fixture-worker').run_once())
            observations=FindingStore(fixture.f.service).list(fixture.actor,'tenantA')['items']
            self.assertTrue(observations)
            self.assertNotIn(secret,json.dumps(observations))
            with store.db.connection(readonly=True) as db:
                self.assertEqual(db.execute('SELECT count(*) FROM job_results').fetchone()[0],1)
                self.assertEqual(db.execute('SELECT count(*) FROM job_reservations').fetchone()[0],1)
            import base64
            from datetime import timedelta
            from unittest.mock import patch
            from agntia_ciberseguridad.config import EvidencePolicy
            from agntia_ciberseguridad.evidence.vault import Vault
            from agntia_ciberseguridad.reviews import Reviews,ReviewProposal,ReviewApproval
            from agntia_ciberseguridad.reports import Reports,ReportRequest
            from agntia_ciberseguridad.util import utcnow
            with patch.dict(os.environ,{'SYNTHETIC_REPORT_KEY':base64.b64encode(os.urandom(32)).decode()}):
                fixture.f.settings.evidence_policies={'tenantA':EvidencePolicy(key_refs=['SYNTHETIC_REPORT_KEY'],legal_basis_ref='synthetic-authority',custodian_ref='fixture-owner')}
                reviewer=fixture.f.service.auth.authenticate(fixture.f.headers('reviewerA')['Authorization'])
                vault=Vault(fixture.f.service)
                evidence=vault.put(fixture.actor,'tenantA',('Nonfunctional fixture '+secret).encode(),'text/plain','fixture',source_job_id=receipt['id'])
                vault.manage(reviewer,'tenantA',evidence['id'],0,'review','fixture',reason='Synthetic distinct human verification')
                finding=next(f for f in observations if f['rule_id']=='agntia-canary')
                reviews=Reviews(fixture.f.service)
                proposal=reviews.propose(fixture.actor,'tenantA',ReviewProposal(finding_id=finding['id'],expected_finding_revision=finding.get('revision',0),action='false_positive',reason='Invented nonfunctional canary, not an actual credential',evidence_ids=[evidence['id']],expires_at=(utcnow()+timedelta(days=1)).isoformat()),'fixture')
                reviews.approve(reviewer,'tenantA',proposal['id'],ReviewApproval(expected_revision=0,proposal_hash=proposal['proposal_hash']),'fixture')
                reports=Reports(fixture.f.service)
                report=reports.create(fixture.actor,'tenantA',ReportRequest(job_ids=[receipt['id']]),'fixture')
                self.assertTrue(report['findings']);self.assertNotIn(secret,json.dumps(report))
                self.assertIn('false_positive',{f['state'] for f in report['findings']})
                self.assertEqual(reports.create(fixture.actor,'tenantA',ReportRequest(job_ids=[receipt['id']]),'fixture')['id'],report['id'])
                (fixture.f.repo/'canary.txt').write_text('Ordinary benign fixture with no credentials')
                benign_snapshot=fixture.acquire()
                benign_body=body.model_copy(update={'snapshot_id':benign_snapshot['id'],'snapshot_hash':benign_snapshot['manifest_hash']})
                benign=store.submit(fixture.actor,'tenantA',benign_body,'benign-report-fixture','fixture')
                self.assertEqual((await Worker(store,scanner,'fixture-worker').run_once())['state'],'completed')
                benign_report=reports.create(fixture.actor,'tenantA',ReportRequest(job_ids=[benign['id']]),'fixture')
                self.assertEqual(benign_report['findings'],[])
                self.assertFalse(benign_report['security_guarantee'])
        finally:fixture.tearDown()
    async def test_real_governed_remediation_candidates_preserve_source(self):
        from tests.security.test_governance import GovernanceSetup
        from agntia_ciberseguridad.scanning import StaticScanner
        from agntia_ciberseguridad.jobs.store import JobStore
        from agntia_ciberseguridad.jobs.worker import Worker
        from agntia_ciberseguridad.findings.store import FindingStore
        from agntia_ciberseguridad.governance.remediation import RemediationPlan
        from agntia_ciberseguridad.safety import ReleaseGates
        gates=ReleaseGates(True,True,True)
        for rule,path,tool,rule_id,content in [
            ('remove_synthetic_canary','canary.txt',Tool.gitleaks,'agntia-canary','AGNTIA_TEST_SECRET_'+'R'*32+'\n'),
            ('remove_fixture_eval','fixture_eval.py',Tool.semgrep,'agntia.python.dynamic-eval','def run(value):\n    return eval(value)\n')]:
            fixture=GovernanceSetup();fixture.setUp()
            try:
                (fixture.f.repo/'file.py').write_text('# benign synthetic fixture\n')
                (fixture.f.repo/path).write_text(content)
                fixture.f.settings.tool_policy_hashes={name.value:image.policy_hash for name,image in self.runner.images.items()}
                manifest=fixture.fixture.acquire();store=JobStore(fixture.f.service,gates=gates)
                scanner=StaticScanner(fixture.f.service,self.runner,gates=gates)
                body=fixture.body.model_copy(update={'snapshot_id':manifest['id'],'snapshot_hash':manifest['manifest_hash'],'tool':tool})
                receipt=store.submit(fixture.actor,'tenantA',body,'real-remediation-'+tool.value,'fixture')
                done=await Worker(store,scanner,'real-remediation-worker').run_once()
                self.assertEqual(done['state'],'completed')
                finding=next(f for f in FindingStore(fixture.f.service).list(fixture.actor,'tenantA')['items'] if f['rule_id']==rule_id and f['path']==path)
                plan=fixture.remediation.plan(fixture.actor,'tenantA',RemediationPlan(snapshot_id=manifest['id'],finding_id=finding['id'],expected_finding_revision=finding.get('revision',0),rule=rule,source_license_ref='original-synthetic-fixture'),'fixture')
                fixture.review(plan);fixture.remediation.materialize(fixture.reviewer,'tenantA',plan['id'],'fixture')
                result=await fixture.remediation.retest(fixture.reviewer,'tenantA',plan['id'],self.runner,'fixture',gates=gates)
                self.assertEqual(result['state'],'retest_passed_fixture',result['fields'].get('retest'))
                self.assertEqual((fixture.f.repo/path).read_text(),content)
                self.assertFalse(result['fields']['verified_fixed']);self.assertFalse(result['fields']['merge_enabled'])
                unchanged=FindingStore(fixture.f.service).history(fixture.actor,'tenantA',finding['id'])['finding']
                self.assertNotEqual(unchanged['state'],'verified_fixed')
            finally:fixture.tearDown()
