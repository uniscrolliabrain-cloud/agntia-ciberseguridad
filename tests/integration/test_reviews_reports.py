from datetime import timedelta
import json
from unittest.mock import patch
import unittest
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.findings.store import FindingStore
from agntia_ciberseguridad.jobs.worker import Worker
from agntia_ciberseguridad.reviews import ReviewProposal,ReviewApproval
from agntia_ciberseguridad.reports import ReportRequest
from agntia_ciberseguridad.risk import effective
from agntia_ciberseguridad.util import utcnow
from tests.security.support_custody import CustodySetup

class ReviewReportTests(CustodySetup,unittest.IsolatedAsyncioTestCase):
    async def seed(self,*,status=None,severity='high'):
        receipt=self.submit()
        scanner=self.scanner(self.result([{'rule_id':'rule-test','path':'file.py','start_line':1,'severity':severity}],status=status))
        await Worker(self.store,scanner,'worker').run_once()
        finding=FindingStore(self.f.service).list(self.actor,'tenantA')['items'][0]
        evidence=self.reviewed_document(receipt['id'])
        return receipt,finding,evidence
    def propose(self,finding,evidence,action,**extra):
        return self.reviews.propose(self.actor,'tenantA',ReviewProposal(finding_id=finding['id'],expected_finding_revision=finding.get('revision',0),
            action=action,reason='Synthetic cited human review',evidence_ids=[evidence['id']],**extra),'fixture')
    def approve(self,proposal):
        return self.reviews.approve(self.reviewer,'tenantA',proposal['id'],ReviewApproval(expected_revision=0,proposal_hash=proposal['proposal_hash']),'fixture')

    async def test_human_approval_hashes_roles_and_unknown_not_exploitation(self):
        _,finding,evidence=await self.seed()
        proposal=self.propose(finding,evidence,'confirm')
        with self.assertRaises(DomainError):self.reviews.approve(self.actor,'tenantA',proposal['id'],ReviewApproval(expected_revision=0,proposal_hash=proposal['proposal_hash']),'fixture')
        self.f.settings.principals[1].kind='agent'
        with self.assertRaises(DomainError) as error:self.approve(proposal)
        self.assertEqual(error.exception.code,'human_required')
        self.f.settings.principals[1].kind='human'
        with self.assertRaises(DomainError):self.reviews.approve(self.reviewer,'tenantA',proposal['id'],ReviewApproval(expected_revision=0,proposal_hash='0'*64),'fixture')
        decision=self.approve(proposal)
        current=FindingStore(self.f.service).history(self.actor,'tenantA',finding['id'])['finding']
        self.assertEqual(current['state'],'confirmed');self.assertEqual(current['risk']['exploitation'],'unknown')
        self.assertEqual(current['last_decision_id'],decision['id'])
        with self.assertRaises(DomainError):self.approve(proposal)

    async def test_exception_expires_and_llm_cannot_supply_score(self):
        from pydantic import ValidationError
        _,finding,evidence=await self.seed(severity='unknown')
        self.assertIsNone(finding['risk']['score'])
        proposal=self.propose(finding,evidence,'accept_risk',expires_at=(utcnow()+timedelta(minutes=5)).isoformat())
        self.approve(proposal)
        current=FindingStore(self.f.service).history(self.actor,'tenantA',finding['id'])['finding']
        self.assertEqual(current['state'],'accepted_risk')
        expired=effective(current,utcnow()+timedelta(minutes=6))
        self.assertEqual(expired['state'],'suspected');self.assertTrue(expired['exception_expired'])
        with self.assertRaises(ValidationError):ReviewProposal(finding_id=finding['id'],expected_finding_revision=0,action='confirm',reason='LLM wants risk=0',evidence_ids=[evidence['id']],score=0)

    async def test_changed_observation_invalidates_proposal_and_requires_reviewed_evidence(self):
        _,finding,evidence=await self.seed()
        proposal=self.propose(finding,evidence,'confirm')
        self.submit('second-scan-key')
        await Worker(self.store,self.scanner(self.result([{'rule_id':'rule-test','path':'file.py','start_line':1,'severity':'critical'}])),'worker').run_once()
        with self.assertRaises(DomainError) as error:self.approve(proposal)
        self.assertEqual(error.exception.code,'conflict')
        unreviewed=self.vault.put(self.actor,'tenantA',b'not human reviewed','text/plain','fixture')
        current=FindingStore(self.f.service).history(self.actor,'tenantA',finding['id'])['finding']
        with self.assertRaises(DomainError):self.propose(current,unreviewed,'confirm')

    async def test_verified_fixed_needs_post_remediation_clean_equivalent_retest(self):
        _,finding,evidence=await self.seed()
        with self.assertRaises(DomainError):self.approve(self.propose(finding,evidence,'verify_fixed'))
        self.approve(self.propose(finding,evidence,'mark_remediated'))
        current=FindingStore(self.f.service).history(self.actor,'tenantA',finding['id'])['finding']
        (self.f.repo/'file.py').write_text('new source without the synthetic issue')
        snapshot=self.fixture.acquire()
        body=self.body.model_copy(update={'snapshot_id':snapshot['id'],'snapshot_hash':snapshot['manifest_hash']})
        retest=self.submit('verified-retest',body)
        await Worker(self.store,self.scanner(self.result()),'worker').run_once()
        self.approve(self.propose(current,evidence,'verify_fixed',retest_job_id=retest['id']))
        final=FindingStore(self.f.service).history(self.actor,'tenantA',finding['id'])['finding']
        self.assertEqual(final['state'],'verified_fixed')
        self.assertEqual(len(FindingStore(self.f.service).history(self.actor,'tenantA',finding['id'])['observations']),1)

    async def test_report_immutable_repeat_scoped_encrypted_and_not_certified(self):
        receipt,finding,evidence=await self.seed()
        self.approve(self.propose(finding,evidence,'confirm'))
        request=ReportRequest(job_ids=[receipt['id']])
        first=self.reports.create(self.actor,'tenantA',request,'fixture')
        second=self.reports.create(self.actor,'tenantA',request,'fixture')
        self.assertEqual(first,second)
        self.assertFalse(first['security_guarantee']);self.assertEqual(first['review_status'],'not_reviewed')
        self.assertEqual(first['findings'][0]['state'],'confirmed')
        self.assertIn('snapshot_manifest_hash',first['jobs'][0])
        foreign=self.f.service.auth.authenticate(self.f.headers('operatorB')['Authorization'])
        with self.assertRaises(DomainError) as error:self.reports.get(foreign,'tenantA',first['id'],'fixture')
        self.assertEqual(error.exception.status,404)
        with self.f.service.db.connection(readonly=True) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM reports').fetchone()[0],1)
            record=db.execute('SELECT body FROM reports').fetchone()[0]
            self.assertNotIn('findings',record)

    async def test_partial_and_empty_reports_never_become_green(self):
        await self.seed(status='partial')
        report=self.reports.create(self.actor,'tenantA',ReportRequest(),'fixture')
        self.assertEqual(report['coverage_status'],'incomplete_or_unknown')
        empty=self.reports.create(self.actor,'tenantA',ReportRequest(start='2000-01-01T00:00:00+00:00',end='2000-01-02T00:00:00+00:00'),'fixture')
        self.assertEqual(empty['coverage_status'],'incomplete_or_unknown');self.assertEqual(empty['findings'],[])

    async def test_html_csv_escape_content_and_report_tampering_fails(self):
        await self.seed();report=self.reports.create(self.actor,'tenantA',ReportRequest(),'fixture')
        hostile=json.loads(json.dumps(report));hostile['findings'][0]['path']='=HYPERLINK("evil")<script>alert(1)</script>'
        html=self.reports.render_html(hostile);csv=self.reports.render_csv(hostile)
        self.assertNotIn('<script>',html);self.assertIn('&lt;script&gt;',html)
        self.assertIn("'=HYPERLINK",csv)
        with self.f.service.db.connection(readonly=True) as db:ref=db.execute('SELECT evidence_id FROM reports WHERE id=?',(report['id'],)).fetchone()[0]
        file=self.vault.root/'tenantA'/(ref+'-redacted.enc');file.chmod(0o600);file.write_bytes(b'corrupted report')
        with self.assertRaises(DomainError) as error:self.reports.get(self.viewer,'tenantA',report['id'],'fixture')
        self.assertEqual(error.exception.code,'evidence_integrity')
