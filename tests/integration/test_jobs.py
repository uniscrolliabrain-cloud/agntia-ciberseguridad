import asyncio
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import AsyncMock,patch
import unittest
from tests.security import test_ingestion as ingestion
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.jobs.contracts import AuditJobCreate
from agntia_ciberseguridad.jobs.store import JobStore
from agntia_ciberseguridad.jobs.worker import Worker
from agntia_ciberseguridad.findings.store import FindingStore
from agntia_ciberseguridad.runners.base import Tool
from agntia_ciberseguridad.safety import ReleaseGates

class Setup:
    def setUp(self):
        self.fixture=ingestion.SnapshotTests();self.fixture.setUp();self.f=self.fixture.f
        (self.f.repo/'file.py').write_text('synthetic fixture only')
        self.manifest=self.fixture.acquire();self.actor=self.fixture.actor
        self.f.settings.tool_policy_hashes={'gitleaks':'a'*64,'semgrep':'a'*64,'osv':'a'*64,'trivy':'a'*64}
        self.instant=[1000.0]
        self.store=JobStore(self.f.service,gates=ReleaseGates(True,True,True),clock=lambda:self.instant[0])
        self.body=AuditJobCreate(asset_id=self.fixture.asset['id'],grant_id=self.fixture.body.grant_id,
            snapshot_id=self.manifest['id'],snapshot_hash=self.manifest['manifest_hash'],expected_grant_revision=1,
            tool='gitleaks',max_attempts=2)
    def tearDown(self):self.fixture.tearDown()
    def submit(self,key='test-key-001',body=None):return self.store.submit(self.actor,'tenantA',body or self.body,key,'fixture-correlation')
    def result(self,findings=None,status=None):
        findings=findings or []
        return {'schema_version':1,'tool':'gitleaks','tool_version':'8.30.1','status':status or ('findings' if findings else 'no_findings'),
            'findings':findings,'policy_hash':'a'*64,'snapshot_coverage':'captured_local_files','scan_clean':False}
    def scanner(self,result):
        return SimpleNamespace(runner=SimpleNamespace(images={Tool.gitleaks:SimpleNamespace(policy_hash='a'*64)}),scan=AsyncMock(return_value=result))

class JobStoreTests(Setup,unittest.TestCase):
    def test_concurrent_replay_payload_conflict_and_api_restart(self):
        with ThreadPoolExecutor(max_workers=2) as pool:receipts=list(pool.map(lambda _:self.submit(),range(2)))
        self.assertEqual(receipts[0]['id'],receipts[1]['id'])
        self.assertEqual(sum(not r['replayed'] for r in receipts),1)
        self.assertFalse(receipts[0]['audit_completed'])
        with self.f.service.db.connection(readonly=True) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM jobs').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT count(*) FROM job_reservations').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT amount_cents FROM job_reservations').fetchone()[0],0)
        with self.assertRaises(DomainError) as error:self.submit(body=self.body.model_copy(update={'max_attempts':1}))
        self.assertEqual(error.exception.code,'idempotency_conflict')
        restarted=JobStore(self.f.service,gates=ReleaseGates(True,True,True),clock=lambda:self.instant[0])
        self.assertEqual(restarted.submit(self.actor,'tenantA',self.body,'test-key-001','restarted')['id'],receipts[0]['id'])

    def test_tenancy_role_closed_body_and_zero_cost_only(self):
        from pydantic import ValidationError
        receipt=self.submit()
        foreign=self.f.service.auth.authenticate(self.f.headers('operatorB')['Authorization'])
        with self.assertRaises(DomainError) as error:self.store.get(foreign,'tenantA',receipt['id'])
        self.assertEqual(error.exception.status,404)
        viewer=self.f.service.auth.authenticate(self.f.headers('viewerA')['Authorization'])
        self.assertEqual(self.store.get(viewer,'tenantA',receipt['id'])['id'],receipt['id'])
        with self.assertRaises(DomainError):self.store.submit(viewer,'tenantA',self.body,'viewer-key-001','test')
        with self.assertRaises(ValidationError):AuditJobCreate(**{**self.body.model_dump(),'actor_id':'owner'})
        with self.assertRaises(ValidationError):AuditJobCreate(**{**self.body.model_dump(),'maximum_cost_cents':1})

    def test_pending_cancel_effective_running_only_requested(self):
        receipt=self.submit()
        self.assertEqual(self.store.cancel(self.actor,'tenantA',receipt['id'],0,'fixture')['state'],'cancelled')
        next_job=self.submit('next-key-001');claimed=self.store.claim('workerA')
        self.assertEqual(claimed['id'],next_job['id'])
        requested=self.store.cancel(self.actor,'tenantA',claimed['id'],claimed['revision'],'fixture')
        self.assertEqual(requested['state'],'running');self.assertTrue(requested['cancel_requested'])

    def test_expired_lease_never_blindly_reexecutes_or_accepts_old_ack(self):
        receipt=self.submit();first=self.store.claim('workerA',lease_seconds=2)
        self.instant[0]+=3;self.assertIsNone(self.store.claim('workerB'))
        self.assertEqual(self.store.get(self.actor,'tenantA',receipt['id'])['state'],'reconciliation_required')
        with self.assertRaises(DomainError) as error:self.store.complete(first,'workerA',first['fence'],self.result())
        self.assertEqual(error.exception.code,'stale_lease')
        with self.f.service.db.connection(readonly=True) as db:self.assertEqual(db.execute('SELECT count(*) FROM job_results').fetchone()[0],0)

    def test_backoff_attempt_budget_and_concurrency(self):
        self.submit();row=self.store.claim('workerA');self.assertIsNone(self.store.claim('workerB'))
        self.assertEqual(self.store.fail(row,'workerA',row['fence'],'timeout',retryable=True)['state'],'pending')
        self.assertIsNone(self.store.claim('workerB'));self.instant[0]+=5;second=self.store.claim('workerB')
        self.assertGreater(second['fence'],row['fence'])
        with self.assertRaises(DomainError):self.store.heartbeat('tenantA',row['id'],'workerA',row['fence'])
        self.assertEqual(self.store.fail(second,'workerB',second['fence'],'timeout',retryable=True)['state'],'failed')
        with self.f.service.db.connection(readonly=True) as db:self.assertEqual(db.execute('SELECT count(*) FROM job_reservations').fetchone()[0],1)

    def test_revoked_identity_or_policy_before_claim_is_blocked(self):
        receipt=self.submit();self.f.settings.principals[0].enabled=False
        self.assertIsNone(self.store.claim('workerA'));self.f.settings.principals[0].enabled=True
        self.assertEqual(self.store.get(self.actor,'tenantA',receipt['id'])['state'],'blocked')
        receipt=self.submit('policy-key-001');self.f.settings.tool_policy_hashes['gitleaks']='b'*64
        self.assertIsNone(self.store.claim('workerA'))
        self.assertEqual(self.store.get(self.actor,'tenantA',receipt['id'])['state'],'blocked')

    def test_default_release_gate_admission_is_blocked_not_completed(self):
        self.store.gates=ReleaseGates();receipt=self.submit()
        self.assertEqual(receipt['state'],'blocked');self.assertFalse(receipt['audit_completed'])
        with self.assertRaises(DomainError):self.store.claim('workerA')

class WorkerTests(Setup,unittest.IsolatedAsyncioTestCase):
    async def test_atomic_result_observations_and_no_second_claim(self):
        self.submit();scanner=self.scanner(self.result([{'rule_id':'canary-rule','path':'file.py','start_line':1}]))
        done=await Worker(self.store,scanner,'workerA').run_once();self.assertEqual(done['state'],'completed')
        self.assertIsNone(await Worker(self.store,scanner,'workerB').run_once())
        findings=FindingStore(self.f.service);items=findings.list(self.actor,'tenantA')['items']
        self.assertEqual(len(items),1);self.assertEqual(items[0]['state'],'suspected')
        self.assertEqual(len(findings.history(self.actor,'tenantA',items[0]['id'])['observations']),1)

    async def test_revocation_between_claim_and_external_effect(self):
        self.submit();scanner=self.scanner(self.result());original=self.store.claim
        def claim(*args,**kwargs):
            row=original(*args,**kwargs);self.f.settings.principals[0].enabled=False;return row
        self.store.claim=claim
        done=await Worker(self.store,scanner,'workerA').run_once()
        scanner.scan.assert_not_awaited();self.assertEqual(done['state'],'failed')

    async def test_uncertain_cleanup_never_retries(self):
        self.submit();scanner=self.scanner(self.result(status='error'));scanner.scan.return_value['error_code']='cleanup_unverified'
        self.assertEqual((await Worker(self.store,scanner,'workerA').run_once())['state'],'reconciliation_required')
        self.assertIsNone(self.store.claim('workerB'))

    async def test_reconciliation_requires_actual_cleanup_and_new_fence(self):
        receipt=self.submit();old=self.store.claim('workerA',lease_seconds=1);self.instant[0]+=2;self.store.claim('workerB')
        scanner=self.scanner(self.result());scanner.runner._cleanup=AsyncMock(return_value=False)
        worker=Worker(self.store,scanner,'workerB');reviewer=self.f.service.auth.authenticate(self.f.headers('reviewerA')['Authorization'])
        current=self.store.get(self.actor,'tenantA',receipt['id'])
        with self.assertRaises(DomainError):await worker.reconcile(reviewer,'tenantA',receipt['id'],current['revision'])
        scanner.runner._cleanup.return_value=True
        self.assertEqual((await worker.reconcile(reviewer,'tenantA',receipt['id'],current['revision']))['state'],'pending')
        with self.assertRaises(DomainError):self.store.complete(old,'workerA',old['fence'],self.result())
        self.assertEqual((await worker.run_once())['state'],'completed')
        scanner.runner._cleanup.assert_awaited_with('agntia-scan-'+receipt['id']+'-1')

    async def test_crash_between_result_and_observations_rolls_back(self):
        self.submit();scanner=self.scanner(self.result([{'rule_id':'rule','path':'file.py','start_line':1}]))
        with patch('agntia_ciberseguridad.findings.store.FindingStore.record',side_effect=RuntimeError('synthetic crash')):
            done=await Worker(self.store,scanner,'workerA').run_once()
        self.assertEqual(done['state'],'reconciliation_required')
        with self.f.service.db.connection(readonly=True) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM job_results').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT count(*) FROM finding_observations').fetchone()[0],0)

    async def test_findings_stable_across_snapshots_and_absence_not_fixed(self):
        finding={'rule_id':'rule-one','path':'file.py','start_line':1}
        self.submit();await Worker(self.store,self.scanner(self.result([finding])),'workerA').run_once()
        first=FindingStore(self.f.service).list(self.actor,'tenantA')['items'][0]
        (self.f.repo/'file.py').write_text('new synthetic snapshot')
        manifest=self.fixture.acquire()
        changed=self.body.model_copy(update={'snapshot_id':manifest['id'],'snapshot_hash':manifest['manifest_hash']})
        self.submit('second-observation',changed)
        await Worker(self.store,self.scanner(self.result([finding])),'workerA').run_once()
        history=FindingStore(self.f.service).history(self.actor,'tenantA',first['id'])
        self.assertEqual(len(history['observations']),2)
        self.assertNotEqual(history['observations'][0]['snapshot_id'],history['observations'][1]['snapshot_id'])
        self.submit('absent-findings',changed)
        await Worker(self.store,self.scanner(self.result()),'workerA').run_once()
        current=FindingStore(self.f.service).history(self.actor,'tenantA',first['id'])
        self.assertEqual(current['finding']['state'],'suspected')
        self.assertEqual(len(current['observations']),2)

    async def test_rule_change_and_partial_scan_preserve_old_observations(self):
        self.submit()
        await Worker(self.store,self.scanner(self.result([{'rule_id':'old-rule','path':'file.py','start_line':1}])),'workerA').run_once()
        self.submit('new-rule-key')
        await Worker(self.store,self.scanner(self.result([{'rule_id':'new-rule','path':'file.py','start_line':1}],status='partial')),'workerA').run_once()
        items=FindingStore(self.f.service).list(self.actor,'tenantA')['items']
        self.assertEqual(len(items),2)
        foreign=self.f.service.auth.authenticate(self.f.headers('operatorB')['Authorization'])
        with self.assertRaises(DomainError):FindingStore(self.f.service).history(foreign,'tenantA',items[0]['id'])
        with self.f.service.db.transaction() as db:
            import sqlite3
            with self.assertRaises(sqlite3.IntegrityError):db.execute('DELETE FROM finding_observations')
