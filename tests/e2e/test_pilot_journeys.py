"""Cross-component synthetic journeys; mocked scan result is explicitly NOT a real scan."""
from datetime import timedelta
import json
import unittest
from tests.security.support_custody import CustodySetup
from agntia_ciberseguridad.contracts import AssetCreate
from agntia_ciberseguridad.billing.reservations import Ledger,ReservationRequest
from agntia_ciberseguridad.billing.rates import BudgetPolicy,Rate
from agntia_ciberseguridad.events.outbox import Outbox,SyntheticConsumer
from agntia_ciberseguridad.findings.store import FindingStore
from agntia_ciberseguridad.reports import ReportRequest
from agntia_ciberseguridad.reviews import ReviewProposal,ReviewApproval
from agntia_ciberseguridad.governance.legal import Legal,Inventory,Assessment
from agntia_ciberseguridad.util import utcnow
from agntia_ciberseguridad.errors import DomainError

class PilotJourneys(CustodySetup,unittest.IsolatedAsyncioTestCase):
    def seed(self):
        receipt=self.submit();row=self.store.claim('synthetic-e2e')
        self.store.complete(row,'synthetic-e2e',row['fence'],self.result([{'rule_id':'synthetic-rule','path':'file.py','start_line':1,'severity':'high'}]))
        return receipt,FindingStore(self.f.service).list(self.actor,'tenantA')['items'][0]
    async def test_snapshot_job_human_review_report_export_two_tenants_and_event_replay(self):
        receipt,finding=self.seed();evidence=self.reviewed_document(receipt['id'])
        proposal=self.reviews.propose(self.actor,'tenantA',ReviewProposal(finding_id=finding['id'],expected_finding_revision=0,action='confirm',reason='Synthetic source manually checked',evidence_ids=[evidence['id']]),'synthetic')
        async with self.f.client() as client:
            prefix='/v1/tenants/tenantA'
            detail=await client.get(prefix+'/reviews/proposals/'+proposal['id'],headers=self.f.headers('reviewerA'))
            self.assertEqual(detail.status_code,200);self.assertFalse(detail.json()['external_action'])
            ack={'expected_revision':0,'proposal_hash':proposal['proposal_hash']}
            self.assertEqual((await client.post(prefix+'/reviews/proposals/'+proposal['id']+'/approve',json=ack,headers=self.f.headers('viewerA'))).status_code,403)
            self.assertEqual((await client.post(prefix+'/reviews/proposals/'+proposal['id']+'/approve',json=ack,headers=self.f.headers('reviewerA'))).status_code,200)
            self.assertEqual((await client.post(prefix+'/reviews/proposals/'+proposal['id']+'/approve',json=ack,headers=self.f.headers('reviewerA'))).status_code,409)
            work=(await client.get(prefix+'/workspace',headers=self.f.headers('viewerA'))).json()
            self.assertEqual(work['findings'][0]['state'],'confirmed');self.assertFalse(work['security_guarantee'])
            for endpoint in ['/workspace','/reviews/proposals/'+proposal['id'],'/evidence/'+evidence['id']+'/content']:
                self.assertEqual((await client.get(prefix+endpoint,headers=self.f.headers('operatorB'))).status_code,404)
            other=(await client.get('/v1/tenants/tenantB/workspace',headers=self.f.headers('operatorB'))).json()
            self.assertEqual(other['jobs'],[]);self.assertEqual(other['review_proposals'],[])
        report=self.reports.create(self.actor,'tenantA',ReportRequest(job_ids=[receipt['id']]),'synthetic')
        self.assertEqual(report['summary']['findings'],1);self.assertFalse(report['security_guarantee'])
        self.assertNotIn(self.f.tokens['analystA'],json.dumps(report))
        outbox=Outbox(self.f.service);items=outbox.poll(self.reviewer,'tenantA','synthetic-e2e')['events'];self.assertEqual(len(items),1)
        self.assertEqual(items[0]['envelope']['type'],'cyber.job.completed')
        consumer=SyntheticConsumer(self.f.root/'e2e-inbox.sqlite3');self.assertTrue(consumer.consume(items[0]));self.assertFalse(consumer.consume(items[0]))
    async def test_budget_exhaustion_unknown_compliance_does_not_turn_security_green(self):
        legal=Legal(self.f.service);inventory=legal.inventory(self.actor,'tenantA',Inventory(resource_id=self.fixture.asset['id'],owner_ref='reviewerA'),'synthetic')
        assessment=legal.assess(self.actor,'tenantA',Assessment(inventory_id=inventory['id'],source_bundle_hash=legal.bundle_hash),'synthetic')
        self.assertIn('insufficient_information',json.dumps(assessment));self.assertNotIn('"compliant": true',json.dumps(assessment))
        self.f.settings.budget_policies={'tenantA':BudgetPolicy(plan='Lite',fixed_commitment_cents=3000,allocation_review_ref='synthetic-commitment')}
        async with self.f.client() as client:
            view=(await client.get('/v1/tenants/tenantA/workspace',headers=self.f.headers('viewerA'))).json()
            self.assertEqual(view['budget_status'],'exhausted');self.assertEqual(view['coverage'],'not_tested');self.assertFalse(view['security_guarantee']);self.assertFalse(view['budget']['security_controls_degraded'])
    async def test_concurrent_review_stale_proposal_and_revoked_credential_fail_closed(self):
        receipt,finding=self.seed();evidence=self.reviewed_document(receipt['id'])
        proposal=self.reviews.propose(self.actor,'tenantA',ReviewProposal(finding_id=finding['id'],expected_finding_revision=0,action='confirm',reason='Synthetic parallel reviewer',evidence_ids=[evidence['id']]),'fixture')
        from concurrent.futures import ThreadPoolExecutor
        body=ReviewApproval(expected_revision=0,proposal_hash=proposal['proposal_hash'])
        def approve(_):
            try:self.reviews.approve(self.reviewer,'tenantA',proposal['id'],body,'fixture');return 'approved'
            except DomainError as e:return e.code
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(approve,range(2)))
        self.assertEqual(sorted(results),['approved','conflict'])
        self.f.settings.principals[1].enabled=False
        async with self.f.client() as client:self.assertEqual((await client.get('/v1/tenants/tenantA/workspace',headers=self.f.headers('reviewerA'))).status_code,401)
