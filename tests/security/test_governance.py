import asyncio
from datetime import timedelta
import json
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch,AsyncMock
from pydantic import ValidationError
from tests.security.support_custody import CustodySetup
from agntia_ciberseguridad.config import VerificationChannel
from agntia_ciberseguridad.governance.store import Cases,CaseReview
from agntia_ciberseguridad.governance.legal import Legal,Inventory,Assessment,DateClaim,Control
from agntia_ciberseguridad.governance.privacy import Privacy,RightsRequest,EvidenceTarget,Breach
from agntia_ciberseguridad.governance.fraud import Fraud,FraudObservation,FraudVerification
from agntia_ciberseguridad.governance.incidents import Incidents,Incident,Containment,IncidentTransition
from agntia_ciberseguridad.governance.remediation import Remediation,RemediationPlan
from agntia_ciberseguridad.evidence.vault import Vault
from agntia_ciberseguridad.agents.flows import DataFlows,FlowCreate
from agntia_ciberseguridad.reports import Reports,ReportRequest
from agntia_ciberseguridad.jobs.worker import Worker
from agntia_ciberseguridad.findings.store import FindingStore
from agntia_ciberseguridad.runners.base import RunResult,Tool,ToolImage
from agntia_ciberseguridad.safety import ReleaseGates
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.util import canonical,digest,utcnow

class GovernanceSetup(CustodySetup):
    def setUp(self):
        super().setUp();self.cases=Cases(self.f.service);self.legal=Legal(self.f.service);self.privacy=Privacy(self.f.service);self.fraud=Fraud(self.f.service);self.incidents=Incidents(self.f.service);self.remediation=Remediation(self.f.service)
        self.f.settings.remediation_fixture_refs=['repoA']
        self.f.settings.verification_channels={'directoryA':VerificationChannel(tenant_id='tenantA',directory_ref='approved-directory-before-message',method='in_person')}
    def tearDown(self):
        root=self.f.settings.data_dir/'remediations'
        if root.exists():
            for base,dirs,files in os.walk(root):os.chmod(base,0o700)
        super().tearDown()
    def review(self,record,evidence=None):
        evidence=evidence or self.reviewed_document()
        return self.cases.review(self.reviewer,'tenantA',record['id'],CaseReview(expected_revision=record['revision'],record_hash=record['record_hash'],evidence_ids=[evidence['id']],competence_ref='synthetic-competent-human-attestation'),'fixture')
    def inventory(self,**updates):
        values=dict(resource_id=self.fixture.asset['id'],owner_ref='reviewerA',purpose_refs=['synthetic-appsec'],eu_scope='yes',personal_data='yes',gdpr_role='controller',ai_role='deployer',cra_role='neither',nis2_in_scope='no',dora_financial_entity='no',dora_ict_provider='no',ens_public_scope='no')
        values.update(updates);return self.legal.inventory(self.actor,'tenantA',Inventory(**values),'fixture')
    def rights(self,evidence,action='restrict'):
        return self.privacy.request(self.actor,'tenantA',RightsRequest(action=action,targets=[EvidenceTarget(evidence_id=evidence['id'],expected_revision=evidence['revision'])],legal_basis_ref='synthetic-lawful-request',purpose_ref='synthetic-purpose'),'fixture')
    def incident(self,key='incident-one'):
        evidence=self.reviewed_document()
        return self.incidents.create(self.actor,'tenantA',Incident(resource_id=self.fixture.asset['id'],owner_ref='reviewerA',evidence_ids=[evidence['id']],case_key=key),'fixture'),evidence
    async def seeded_remediation(self,rule='remove_synthetic_canary'):
        path='canary.txt' if rule=='remove_synthetic_canary' else 'fixture_eval.py'
        content=('AGNTIA_TEST_SECRET_'+'K'*32+'\n') if rule=='remove_synthetic_canary' else 'def run(value):\n    return eval(value)\n'
        (self.f.repo/path).write_text(content);manifest=self.fixture.acquire()
        tool='gitleaks' if rule=='remove_synthetic_canary' else 'semgrep';rule_id='agntia-canary' if tool=='gitleaks' else 'agntia.python.dynamic-eval'
        body=self.body.model_copy(update={'snapshot_id':manifest['id'],'snapshot_hash':manifest['manifest_hash'],'tool':Tool(tool)})
        self.store.submit(self.actor,'tenantA',body,'remediation-'+tool,'fixture')
        result=self.result([{'rule_id':rule_id,'path':path,'start_line':1,'severity':'unknown'}]);result.update(tool=tool,tool_version='8.30.1' if tool=='gitleaks' else '1.185.0')
        scanner=self.scanner(result);scanner.runner.images={Tool(tool):SimpleNamespace(policy_hash='a'*64)}
        await Worker(self.store,scanner,'fixture-remediation-worker').run_once()
        finding=next(f for f in FindingStore(self.f.service).list(self.actor,'tenantA')['items'] if f['path']==path)
        plan=self.remediation.plan(self.actor,'tenantA',RemediationPlan(snapshot_id=manifest['id'],finding_id=finding['id'],expected_finding_revision=finding.get('revision',0),rule=rule,source_license_ref='owner-declared-fixture-license'),'fixture')
        return plan,finding,content

class LegalTests(GovernanceSetup,unittest.TestCase):
    def test_missing_facts_no_role_inference_and_no_compliance_seal(self):
        inventory=self.inventory(purpose_refs=[],eu_scope='unknown',gdpr_role='unknown')
        result=self.legal.assess(self.actor,'tenantA',Assessment(inventory_id=inventory['id'],source_bundle_hash=self.legal.bundle_hash),'fixture')
        self.assertEqual(result['fields']['preparation_status'],'insufficient_information');self.assertEqual(result['fields']['compliance_verdict'],'not_provided')
        self.assertTrue(all(v=='insufficient_information' for v in result['fields']['matrix'].values()))
    def test_candidates_distinct_regimes_and_guide_conflict_blocks_deadlines(self):
        inventory=self.inventory();body=Assessment(inventory_id=inventory['id'],source_bundle_hash=self.legal.bundle_hash,date_claims=[DateClaim(milestone='ai_high_risk_annex_iii',claimed_date='2026-08-02',evidence_ref='outdated-guide')])
        result=self.legal.assess(self.actor,'tenantA',body,'fixture');fields=result['fields']
        self.assertEqual(fields['matrix']['gdpr'],'candidate_applicable');self.assertEqual(fields['matrix']['ens'],'candidate_not_applicable')
        self.assertEqual(fields['preparation_status'],'source_conflict');self.assertFalse(fields['deadline_automation_enabled'])
        self.assertEqual(fields['milestones']['ai_high_risk_annex_iii']['date'],'2027-12-02')
    def test_source_update_marks_previous_assessment_stale(self):
        inventory=self.inventory();record=self.legal.assess(self.actor,'tenantA',Assessment(inventory_id=inventory['id'],source_bundle_hash=self.legal.bundle_hash),'fixture');self.review(record)
        catalogue={**self.legal.catalogue,'version':'synthetic-next-version'};updated=Legal(self.f.service,catalogue=catalogue)
        self.assertEqual(updated.view(self.actor,'tenantA',record['id'],'fixture')['effective_review_state'],'stale_sources')
        with self.assertRaises(DomainError):updated.assess(self.actor,'tenantA',Assessment(inventory_id=inventory['id'],source_bundle_hash=self.legal.bundle_hash),'fixture')
    def test_human_review_hash_separation_and_control_evidence_status(self):
        inventory=self.inventory();evidence=self.reviewed_document()
        with self.assertRaises(DomainError):self.cases.review(self.actor,'tenantA',inventory['id'],CaseReview(expected_revision=0,record_hash=inventory['record_hash'],evidence_ids=[evidence['id']],competence_ref='self'),'fixture')
        reviewed=self.review(inventory,evidence);self.assertEqual(reviewed['state'],'reviewed')
        record=self.legal.assess(self.actor,'tenantA',Assessment(inventory_id=inventory['id'],source_bundle_hash=self.legal.bundle_hash),'fixture')
        control=self.legal.control(self.actor,'tenantA',Control(assessment_id=record['id'],regime='gdpr',control_ref='access_control',owner_ref='reviewerA',evidence_ids=[evidence['id']]),'fixture')
        self.assertEqual(control['fields']['evidence_state_at_capture'],'evidence_reviewed');self.assertEqual(control['fields']['control_effectiveness'],'not_certified')
    def test_source_catalogue_has_six_separate_regimes_and_amendment(self):
        data=self.legal.sources(self.viewer,'tenantA')
        self.assertIn('ai_amendment',{s['id'] for s in data['sources']});self.assertFalse(data['legal_certification'])
        self.assertFalse(data['full_document_hashes_captured'])

class PrivacyTests(GovernanceSetup,unittest.IsolatedAsyncioTestCase):
    async def test_restriction_blocks_original_projection_and_cached_report_artifact(self):
        receipt=self.submit();await Worker(self.store,self.scanner(self.result()),'privacy-worker').run_once()
        evidence=self.vault.put(self.actor,'tenantA',canonical({'packages':[{'name':'demo','version':'1.0'}]}).encode(),'application/json','fixture',source_job_id=receipt['id'])
        flow=DataFlows(self.f.service).create(self.actor,'tenantA',FlowCreate(evidence_id=evidence['id'],resource_id=self.fixture.asset['id']),'fixture')
        reports=Reports(self.f.service);report=reports.create(self.actor,'tenantA',ReportRequest(job_ids=[receipt['id']]),'fixture')
        request=self.rights(evidence);self.review(request);applied=self.privacy.apply(self.reviewer,'tenantA',request['id'],'fixture');self.assertEqual(applied['state'],'restricted')
        with self.assertRaises(DomainError) as error:self.vault.read(self.actor,'tenantA',evidence['id'],'fixture')
        self.assertEqual(error.exception.status,423)
        with self.assertRaises(DomainError):self.vault.read(self.reviewer,'tenantA',evidence['id'],'fixture',original=True,reason='Synthetic access test')
        with self.assertRaises(DomainError):reports.get(self.actor,'tenantA',report['id'],'fixture')
        with self.f.service.db.connection(readonly=True) as db:
            artifact=db.execute('SELECT evidence_id FROM reports WHERE id=?',(report['id'],)).fetchone()[0]
            with self.assertRaises(DomainError):DataFlows(self.f.service).project(db,'tenantA',flow['resource_id'],[flow['id']])
        with self.assertRaises(DomainError):self.vault.read(self.actor,'tenantA',artifact,'fixture')
    async def test_erasure_respects_hold_and_never_claims_backups_erased(self):
        old=Vault(self.f.service,clock=lambda:utcnow()-timedelta(days=31));evidence=old.put(self.actor,'tenantA',b'Synthetic expired record','text/plain','fixture')
        held=self.vault.manage(self.reviewer,'tenantA',evidence['id'],0,'hold','fixture',enabled=True,reason='Synthetic legal retention hold')
        request=self.rights(held,'delete');self.review(request)
        self.assertEqual(self.privacy.apply(self.reviewer,'tenantA',request['id'],'fixture')['state'],'blocked_retention')
        released=self.vault.manage(self.reviewer,'tenantA',evidence['id'],held['revision'],'hold','fixture',enabled=False,reason='Synthetic hold released after review')
        request=self.rights(released,'delete');self.review(request);result=self.privacy.apply(self.reviewer,'tenantA',request['id'],'fixture')
        self.assertEqual(result['state'],'awaiting_backup_reconciliation');self.assertFalse(result['fields']['backups_reconciled'])
        with self.assertRaises(DomainError):self.vault.read(self.actor,'tenantA',evidence['id'],'fixture')
    async def test_metadata_export_scoped_and_viewer_cannot_read_breach(self):
        evidence=self.reviewed_document();request=self.rights(evidence,'export_metadata');self.review(request)
        result=self.privacy.apply(self.reviewer,'tenantA',request['id'],'fixture');self.assertEqual(len(result['fields']['export']),1)
        self.assertNotIn('key_ref',canonical(result));self.assertEqual(result['fields']['execution_status'],'metadata_only_not_full_sar')
        with self.assertRaises(DomainError):self.cases.get(self.viewer,'tenantA',request['id'])
        foreign=self.f.service.auth.authenticate(self.f.headers('operatorB')['Authorization'])
        with self.assertRaises(DomainError):self.cases.get(foreign,'tenantA',request['id'])
    async def test_legacy_report_artifact_fails_closed_until_lineage_reconciled(self):
        artifact=self.vault.put(self.actor,'tenantA',b'{"legacy_report":true}','application/json','fixture')
        with self.f.service.db.transaction() as db:
            db.execute('INSERT INTO reports VALUES(?,?,?,?,?)',('tenantA','f'*32,'e'*64,artifact['id'],canonical({'id':'f'*32})))
        with self.assertRaises(DomainError) as error:self.vault.read(self.actor,'tenantA',artifact['id'],'fixture')
        self.assertEqual(error.exception.code,'privacy_reconciliation_required')

    async def test_lifting_requires_fresh_review_and_cannot_clear_newer_restriction(self):
        evidence=self.reviewed_document();stale=self.rights(evidence,'release_restriction');self.review(stale)
        restrict=self.rights(evidence);self.review(restrict);self.privacy.apply(self.reviewer,'tenantA',restrict['id'],'fixture')
        with self.assertRaises(DomainError):self.privacy.apply(self.reviewer,'tenantA',stale['id'],'fixture')
        fresh=self.rights(evidence,'release_restriction');self.review(fresh)
        self.assertEqual(self.privacy.apply(self.reviewer,'tenantA',fresh['id'],'fixture')['state'],'restriction_released')
        self.assertTrue(self.vault.read(self.actor,'tenantA',evidence['id'],'fixture'))

    async def test_technical_alert_does_not_start_gdpr_clock(self):
        body=Breach(resource_id=self.fixture.asset['id'],owner_ref='reviewerA',detected_at=utcnow()-timedelta(hours=1),awareness_at=utcnow(),personal_data='no',breach_confirmed='unknown',gdpr_role='controller',risk='high')
        case=self.privacy.breach(self.actor,'tenantA',body,'fixture');self.review(case)
        result=self.privacy.breach_view(self.reviewer,'tenantA',case['id'],'fixture')['breach_preparation']
        self.assertIsNone(result['authority_due_at']);self.assertFalse(result['automatic_notification'])
    async def test_controller_and_processor_clocks_are_distinct_and_reviewed(self):
        aware=utcnow()-timedelta(minutes=5)
        for role in ('controller','processor'):
            body=Breach(resource_id=self.fixture.asset['id'],owner_ref='reviewerA',detected_at=aware-timedelta(minutes=10),awareness_at=aware,personal_data='yes',breach_confirmed='yes',gdpr_role=role,risk='high')
            case=self.privacy.breach(self.actor,'tenantA',body,'fixture')
            self.assertIsNone(self.privacy.breach_view(self.actor,'tenantA',case['id'],'fixture')['breach_preparation']['authority_due_at'])
            self.review(case);result=self.privacy.breach_view(self.reviewer,'tenantA',case['id'],'fixture')['breach_preparation']
            if role=='controller':self.assertEqual(result['authority_due_at'],(aware+timedelta(hours=72)).isoformat())
            else:self.assertIsNone(result['authority_due_at']);self.assertEqual(result['processor_action'],'inform_controller_without_undue_delay')
            self.assertFalse(result['notification_sent'])

class FraudTests(GovernanceSetup,unittest.TestCase):
    def test_domain_headers_and_new_destination_are_signals_not_a_verdict(self):
        with patch('socket.getaddrinfo',side_effect=AssertionError('No network permitted')):
            case=self.fraud.observe(self.actor,'tenantA',FraudObservation(sender='sender@раypal.invalid',reply_to='person@other.invalid',claimed_url='http://169.254.169.254/latest/meta-data',new_payment_destination_claimed=True,authentication_results_claim='pass',evidence_ref='synthetic-message'),'fixture')
        self.assertFalse(case['fields']['network_visited']);self.assertEqual(case['fields']['verdict'],'not_determined');self.assertEqual(case['fields']['authenticated_spf_dkim_dmarc'],'unknown')
        self.assertIn('mixed_script_signal',case['fields']['signals']);self.assertNotIn('sender@',canonical(case))
        with self.assertRaises(ValidationError):FraudObservation(sender='a@b.invalid\r\nBcc: x@y.invalid',evidence_ref='fake')
    def test_message_channel_is_not_trusted_and_registered_channel_needs_human_evidence(self):
        case=self.fraud.observe(self.actor,'tenantA',FraudObservation(sender='sender@vendor.invalid',new_payment_destination_claimed=True,evidence_ref='message-ref'),'fixture');evidence=self.reviewed_document()
        body=FraudVerification(expected_revision=0,record_hash=case['record_hash'],channel_ref='message-supplied-phone',evidence_id=evidence['id'],decision='human_attested_verified')
        with self.assertRaises(DomainError):self.fraud.verify(self.reviewer,'tenantA',case['id'],body,'fixture')
        result=self.fraud.verify(self.reviewer,'tenantA',case['id'],body.model_copy(update={'channel_ref':'directoryA'}),'fixture')
        self.assertFalse(result['fields']['payment_or_blocking_action']);self.assertEqual(result['fields']['verification']['authenticity'],'human_attested_not_provider_verified')
    def test_benign_unicode_data_no_definitive_deepfake_or_fraud_claim(self):
        case=self.fraud.observe(self.actor,'tenantA',FraudObservation(sender='office@vendor.invalid',reply_to='help@vendor.invalid',claimed_url='https://vendor.invalid/info',evidence_ref='benign'),'fixture')
        self.assertEqual(case['fields']['signals'],[]);self.assertEqual(case['fields']['deepfake'],'not_evaluated');self.assertEqual(case['fields']['verdict'],'not_determined')

class IncidentTests(GovernanceSetup,unittest.TestCase):
    def test_replay_and_false_positive_do_not_revoke_anything(self):
        case,evidence=self.incident()
        body=Incident(**{k:case['fields'][k] for k in Incident.model_fields})
        replay=self.incidents.create(self.actor,'tenantA',body,'fixture');self.assertEqual(case['id'],replay['id'])
        with self.assertRaises(DomainError):self.incidents.create(self.actor,'tenantA',body.model_copy(update={'severity':'high'}),'fixture')
        triaged=self.incidents.transition(self.reviewer,'tenantA',case['id'],IncidentTransition(expected_revision=0,target_state='triaged',reason_ref='triage-proof',evidence_id=evidence['id']),'fixture')
        closed=self.incidents.transition(self.reviewer,'tenantA',case['id'],IncidentTransition(expected_revision=triaged['revision'],target_state='resolved',resolution='false_positive',reason_ref='reviewed-false-positive',evidence_id=evidence['id']),'fixture')
        self.assertEqual(closed['fields']['workflow_state'],'resolved')
        with self.f.service.db.connection(readonly=True) as db:self.assertEqual(self.f.service._grant(db,'tenantA',self.body.grant_id)['state'],'approved')
    def test_reviewed_lab_containment_reconciles_timeout_without_retry(self):
        case,evidence=self.incident('containment');proposal=self.incidents.propose_containment(self.actor,'tenantA',Containment(incident_id=case['id'],grant_id=self.body.grant_id,expected_grant_revision=1),'fixture');self.review(proposal)
        original=self.f.service.revoke_grant
        def uncertain(*args,**kwargs):original(*args,**kwargs);raise TimeoutError('Synthetic ACK lost after local commit')
        with patch.object(self.f.service,'revoke_grant',side_effect=uncertain):result=self.incidents.execute(self.reviewer,'tenantA',proposal['id'],'fixture')
        self.assertEqual(result['state'],'reconciliation_required')
        with self.assertRaises(DomainError):self.incidents.execute(self.reviewer,'tenantA',proposal['id'],'fixture')
        self.assertEqual(self.incidents.reconcile(self.reviewer,'tenantA',proposal['id'],'fixture')['state'],'executed_lab')
    def test_production_and_cross_tenant_containment_blocked(self):
        case,evidence=self.incident('no-production');proposal=self.incidents.propose_containment(self.actor,'tenantA',Containment(incident_id=case['id'],grant_id=self.body.grant_id,expected_grant_revision=1),'fixture');self.review(proposal);self.f.settings.lab_mode=False
        with self.assertRaises(DomainError):self.incidents.execute(self.reviewer,'tenantA',proposal['id'],'fixture')
        with self.assertRaises(DomainError):self.incidents.execute(self.reviewer,'tenantB',proposal['id'],'fixture')

class RemediationTests(GovernanceSetup,unittest.IsolatedAsyncioTestCase):
    async def test_proposal_approval_candidate_replay_and_no_source_overwrite(self):
        plan,finding,original=await self.seeded_remediation();self.review(plan);candidate=self.remediation.materialize(self.reviewer,'tenantA',plan['id'],'fixture')
        self.assertEqual(candidate['state'],'candidate_ready');self.assertNotIn('AGNTIA_TEST_SECRET_',candidate['fields']['diff_redacted'])
        self.assertEqual((self.f.repo/'canary.txt').read_text(),original)
        self.assertEqual(self.remediation.materialize(self.reviewer,'tenantA',plan['id'],'fixture')['fields']['candidate_hash'],candidate['fields']['candidate_hash'])
        self.assertFalse(candidate['fields']['merge_enabled']);self.assertFalse(candidate['fields']['deploy_enabled'])
    async def test_changed_origin_after_review_is_stale_and_never_overwritten(self):
        plan,_,_=await self.seeded_remediation();self.review(plan);(self.f.repo/'unrelated.txt').write_text('Concurrent human work')
        with self.assertRaises(DomainError):self.remediation.materialize(self.reviewer,'tenantA',plan['id'],'fixture')
        self.assertEqual((self.f.repo/'unrelated.txt').read_text(),'Concurrent human work')
        self.assertEqual(self.cases.get(self.actor,'tenantA',plan['id'])['state'],'stale_origin')
    async def test_failed_scanner_is_not_fixed_and_default_gates_deny(self):
        plan,_,_=await self.seeded_remediation();self.review(plan);self.remediation.materialize(self.reviewer,'tenantA',plan['id'],'fixture')
        runner=SimpleNamespace(images={Tool.gitleaks:ToolImage(Tool.gitleaks,'8.30.1','sha256:'+'a'*64,'a'*64)},run=AsyncMock(return_value=RunResult(Tool.gitleaks,'8.30.1','error',None,error_code='synthetic_scanner_failure')))
        with self.assertRaises(DomainError):await self.remediation.retest(self.reviewer,'tenantA',plan['id'],runner,'fixture')
        self.assertEqual(runner.run.await_count,0)
        result=await self.remediation.retest(self.reviewer,'tenantA',plan['id'],runner,'fixture',gates=ReleaseGates(True,True,True))
        self.assertEqual(result['state'],'retest_failed');self.assertFalse(result['fields']['verified_fixed'])
    async def test_fixture_eval_rule_and_workflow_changes_forbidden(self):
        plan,_,_=await self.seeded_remediation('remove_fixture_eval');self.review(plan);candidate=self.remediation.materialize(self.reviewer,'tenantA',plan['id'],'fixture')
        self.assertEqual(candidate['fields']['path_change_allowlist'],['fixture_eval.py'])
        with self.assertRaises(ValidationError):RemediationPlan(snapshot_id=plan['fields']['snapshot_id'],finding_id=plan['fields']['finding_id'],expected_finding_revision=0,rule='remove_fixture_eval',source_license_ref='declared',target_path='.github/workflows/publish.yml')

class GovernanceApiTests(GovernanceSetup,unittest.IsolatedAsyncioTestCase):
    async def test_sources_and_case_routes_auth_scope_and_no_free_form_actions(self):
        async with self.f.client() as client:
            own=await client.get('/v1/tenants/tenantA/governance/sources',headers=self.f.headers('viewerA'));self.assertEqual(own.status_code,200)
            foreign=await client.get('/v1/tenants/tenantB/governance/sources',headers=self.f.headers('viewerA'));self.assertEqual(foreign.status_code,404)
            response=await client.post('/v1/tenants/tenantA/fraud/observations',headers=self.f.headers(),json={'sender':'support@vendor.invalid','evidence_ref':'test-ref','action':'send_payment'});self.assertEqual(response.status_code,422)
