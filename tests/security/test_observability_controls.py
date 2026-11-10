import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import hashlib
import hmac
import json
import os
import sqlite3
import unittest
from unittest.mock import patch
from pydantic import ValidationError
from tests.security.support_custody import CustodySetup
from agntia_ciberseguridad.config import EventSource,PrincipalBinding
from agntia_ciberseguridad.contracts import Role
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.events.ingest import PassiveEvent,Ingest
from agntia_ciberseguridad.telemetry.logging import OperationalLogs
from agntia_ciberseguridad.telemetry.views import Views
from agntia_ciberseguridad.agents.registry import Registry,Manifest
from agntia_ciberseguridad.agents.capabilities import Delegations,GrantRequest,UseRequest
from agntia_ciberseguridad.util import canonical,utcnow,digest

class NewSetup(CustodySetup):
    def setUp(self):
        super().setUp();self.clock=[utcnow()]
        self.extra=patch.dict(os.environ,{'CYBER_SOURCE_KEY':'synthetic-source-'+'S'*48,'CYBER_DELEGATION_KEY':'synthetic-delegation-'+'D'*48,
            'CYBER_AGENT_A':'synthetic-agent-a-'+'A'*48,'CYBER_AGENT_CHILD':'synthetic-agent-child-'+'C'*48})
        self.extra.start();self.f.settings.event_sources={'sourceA':EventSource(tenant_id='tenantA',key_env='CYBER_SOURCE_KEY',target_refs=['repoA'],max_per_minute=3)}
        self.f.settings.delegation_key_env='CYBER_DELEGATION_KEY'
        from agntia_ciberseguridad.agents.policy import POLICY_HASH
        self.f.settings.agent_policy_hash=POLICY_HASH
        self.f.settings.agent_policy_expires_at=self.clock[0]+timedelta(hours=1)
        for binding,env in [('agentA','CYBER_AGENT_A'),('childA','CYBER_AGENT_CHILD')]:
            self.f.settings.principals.append(PrincipalBinding(id=binding,actor_id=binding,role='analyst',kind='agent',tenants=['tenantA'],token_env=env))
        self.agent=self.f.service.auth.current('agentA');self.child=self.f.service.auth.current('childA')
        self.logs=OperationalLogs(self.f.service,clock=lambda:self.clock[0]);self.ingest=Ingest(self.f.service,clock=lambda:self.clock[0]);self.registry=Registry(self.f.service);self.delegations=Delegations(self.f.service,clock=lambda:self.clock[0])
        self.f.settings.principals[0].role=Role.reviewer
        self.owner=self.f.service.auth.current('analystA')
    def tearDown(self):self.extra.stop();super().tearDown()
    def event(self,event_id='event-1',**values):
        return PassiveEvent(tenant_id='tenantA',source_id='sourceA',event_id=event_id,sent_at=self.clock[0],occurred_at=self.clock[0],type='security_observation',target_ref='repoA',**values)
    def sign(self,body):return hmac.new(os.environ['CYBER_SOURCE_KEY'].encode(),canonical(body.model_dump(mode='json')).encode(),hashlib.sha256).hexdigest()
    def accepted(self,body):return self.ingest.accept('tenantA','sourceA',body,self.sign(body))
    def approved(self,binding='agentA',caps=None):
        body=Manifest(agent_binding=binding,version='v1',artifact_hash='a'*64,capabilities=caps or ['assets.read','findings.read'],resource_ids=[self.fixture.asset['id']])
        record=self.registry.create(self.owner,'tenantA',body,'fixture')
        return self.registry.approve(self.reviewer,'tenantA',record['id'],0,'fixture')
    def grant(self,manifest,**updates):
        values=dict(manifest_id=manifest['id'],capabilities=['assets.read'],resource_ids=[self.fixture.asset['id']],expires_at=self.clock[0]+timedelta(minutes=2));values.update(updates)
        return GrantRequest(**values)

class LogTests(NewSetup,unittest.TestCase):
    def test_closed_schema_drops_hostile_headers_messages_and_exceptions(self):
        sentinel='AGNTIA_TEST_SECRET_'+'Z'*40
        self.logs.record('tenantA',message=sentinel+'\r\nFAKE\x1b[31m<script>',headers={'Authorization':sentinel},exception=sentinel,code=sentinel,event=sentinel)
        rows=self.logs.search(self.viewer,'tenantA');self.assertEqual(len(rows),1)
        encoded=canonical(rows);self.assertNotIn(sentinel,encoded);self.assertNotIn('<script>',encoded);self.assertNotIn('FAKE',encoded)
        self.assertEqual(rows[0]['code'],'other')
        with self.assertRaises(DomainError):self.logs.search(self.viewer,'tenantB')
    def test_retention_hold_quota_and_no_audit_deletion(self):
        self.f.settings.log_max_records=2
        self.assertTrue(self.logs.record('tenantA'));self.assertTrue(self.logs.record('tenantA'));self.assertFalse(self.logs.record('tenantA'))
        self.logs.hold(self.reviewer,'tenantA',True,'fixture');self.clock[0]+=timedelta(days=8)
        self.assertEqual(self.logs.purge(self.reviewer,'tenantA','fixture'),0)
        self.assertEqual(len(self.logs.search(self.viewer,'tenantA')),2)
        self.logs.hold(self.reviewer,'tenantA',False,'fixture')
        self.assertEqual(self.logs.purge(self.reviewer,'tenantA','fixture'),2)
        with self.f.service.db.connection(readonly=True) as db:self.assertTrue(self.f.service.db.verify_audit(db,'tenantA')['valid'])
    def test_actual_byte_quota_is_enforced_even_with_free_record_slots(self):
        self.f.settings.log_max_bytes=1024
        for _ in range(30):self.logs.record('tenantA')
        with self.f.service.db.connection(readonly=True) as db:self.assertLessEqual(db.execute('SELECT sum(bytes) FROM operational_logs').fetchone()[0],1024)

class EventTests(NewSetup,unittest.TestCase):
    def test_signed_replay_content_conflict_out_of_order_and_no_incident(self):
        event=self.event();first=self.accepted(event);self.assertEqual(self.accepted(event)['status'],'duplicate')
        with self.assertRaises(DomainError) as error:self.accepted(event.model_copy(update={'count':2}))
        self.assertEqual(error.exception.status,409)
        older=event.model_copy(update={'event_id':'older','occurred_at':self.clock[0]-timedelta(minutes=2)})
        self.accepted(older);rows=self.ingest.list(self.viewer,'tenantA');self.assertEqual(len(rows),2);self.assertTrue(rows[1]['out_of_order'])
        self.assertEqual(rows[0]['interpretation'],'unverified_observation')
        self.assertFalse(self.ingest.acknowledge(self.reviewer,'tenantA',first['sequence'],'fixture')['incident_confirmed'])
    def test_scope_signature_audience_and_clock_denied_before_persist(self):
        event=self.event()
        for body,signature in [(event,'bad'),(event.model_copy(update={'tenant_id':'tenantB'}),self.sign(event)),(event.model_copy(update={'sent_at':self.clock[0]-timedelta(minutes=6)}),'signed')]:
            with self.assertRaises(DomainError):self.ingest.accept('tenantA','sourceA',body,self.sign(body) if signature=='signed' else signature)
        with self.assertRaises(ValidationError):PassiveEvent(**{**event.model_dump(),'audience':'attacker'})
        with self.f.service.db.connection(readonly=True) as db:self.assertEqual(db.execute('SELECT count(*) FROM passive_events').fetchone()[0],0)
    def test_backpressure_rate_limit_revocation_and_recovery(self):
        self.f.settings.event_pending_limit=1
        first=self.accepted(self.event())
        with self.assertRaises(DomainError) as error:self.accepted(self.event('second'))
        self.assertEqual(error.exception.status,429)
        self.ingest.acknowledge(self.reviewer,'tenantA',first['sequence'],'fixture');self.accepted(self.event('second'))
        self.f.settings.event_sources['sourceA'].enabled=False
        with self.assertRaises(DomainError):self.accepted(self.event('third'))
        self.f.settings.event_sources['sourceA'].enabled=True;self.f.settings.event_pending_limit=10
        self.accepted(self.event('third'))
        with self.assertRaises(DomainError) as error:self.accepted(self.event('fourth'))
        self.assertEqual(error.exception.code,'source_rate_limit')
    def test_concurrent_replay_inserts_once_and_restart_preserves_cursor(self):
        event=self.event()
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:self.accepted(event),range(2)))
        self.assertEqual(results[0]['sequence'],results[1]['sequence'])
        restarted=Ingest(self.f.service,clock=lambda:self.clock[0]);self.assertEqual(len(restarted.list(self.viewer,'tenantA')),1)
        with self.f.service.db.connection(readonly=True) as db:self.assertEqual(db.execute('SELECT received FROM source_state').fetchone()[0],1)

class DelegationTests(NewSetup,unittest.TestCase):
    def test_manifest_requires_two_humans_and_closed_read_schema(self):
        body=Manifest(agent_binding='agentA',version='v1',artifact_hash='a'*64,capabilities=['assets.read'],resource_ids=[self.fixture.asset['id']])
        record=self.registry.create(self.owner,'tenantA',body,'fixture')
        with self.assertRaises(DomainError):self.registry.approve(self.owner,'tenantA',record['id'],0,'fixture')
        with self.assertRaises(DomainError):self.registry.approve(self.agent,'tenantA',record['id'],0,'fixture')
        with self.assertRaises(ValidationError):Manifest(**{**body.model_dump(),'capabilities':['shell.execute']})
        with self.assertRaises(ValidationError):Manifest(**{**body.model_dump(),'network':['external']})
        with self.assertRaises(DomainError):self.delegations.issue(self.owner,'tenantA',self.grant(record),'fixture')
    def test_one_use_wrong_subject_signature_and_resource_fail_without_burning_token(self):
        manifest=self.approved();grant=self.delegations.issue(self.owner,'tenantA',self.grant(manifest),'fixture')
        request=UseRequest(token=grant['token'],capability='assets.read',resource_id=self.fixture.asset['id'])
        with self.assertRaises(DomainError):self.delegations.use(self.child,'tenantA',request,'fixture')
        with self.assertRaises(DomainError):self.delegations.use(self.agent,'tenantA',request.model_copy(update={'token':grant['token'][:-1]+('f' if grant['token'][-1]!='f' else 'e')}),'fixture')
        with self.assertRaises(DomainError):self.delegations.use(self.agent,'tenantA',request.model_copy(update={'resource_id':'b'*32}),'fixture')
        result=self.delegations.use(self.agent,'tenantA',request,'fixture');self.assertEqual(result['data'][0]['id'],self.fixture.asset['id'])
        with self.assertRaises(DomainError):self.delegations.use(self.agent,'tenantA',request,'fixture')
        with self.f.service.db.connection(readonly=True) as db:
            self.assertNotIn(grant['token'],db.execute('SELECT body FROM delegations').fetchone()[0])
    def test_delegation_attenuation_parent_revocation_and_credential_rotation(self):
        parent=self.approved();child=self.approved('childA');root=self.delegations.issue(self.owner,'tenantA',self.grant(parent),'fixture')
        expanded=self.grant(child,capabilities=['findings.read'],parent_token=root['token'])
        with self.assertRaises(DomainError):self.delegations.issue(self.agent,'tenantA',expanded,'fixture')
        delegated=self.delegations.issue(self.agent,'tenantA',self.grant(child,parent_token=root['token']),'fixture')
        self.delegations.revoke(self.reviewer,'tenantA',root['id'],'fixture')
        with self.assertRaises(DomainError):self.delegations.use(self.child,'tenantA',UseRequest(token=delegated['token'],capability='assets.read',resource_id=self.fixture.asset['id']),'fixture')
        root=self.delegations.issue(self.owner,'tenantA',self.grant(parent),'fixture');os.environ['CYBER_AGENT_A']='rotated-synthetic-'+'R'*50
        with self.assertRaises(DomainError):self.delegations.use(self.f.service.auth.current('agentA'),'tenantA',UseRequest(token=root['token'],capability='assets.read',resource_id=self.fixture.asset['id']),'fixture')
    def test_child_positive_audience_rejection_and_foreign_scope_before_key(self):
        parent=self.approved();child=self.approved('childA')
        root=self.delegations.issue(self.owner,'tenantA',self.grant(parent),'fixture')
        issued=self.delegations.issue(self.agent,'tenantA',self.grant(child,parent_token=root['token']),'fixture')
        self.assertEqual(self.delegations.use(self.child,'tenantA',UseRequest(token=issued['token'],capability='assets.read',resource_id=self.fixture.asset['id']),'fixture')['data'][0]['id'],self.fixture.asset['id'])
        body=self.delegations._decode(root['token']);body['audience']='wrong-audience'
        with self.assertRaises(DomainError):self.delegations._decode(self.delegations._encode(body))
        with patch.object(self.delegations,'_key',side_effect=AssertionError('Must reject tenant before key lookup')):
            with self.assertRaises(DomainError) as error:self.delegations.use(self.agent,'tenantB',UseRequest(token=root['token'],capability='assets.read',resource_id=self.fixture.asset['id']),'fixture')
            self.assertEqual(error.exception.status,404)

    def test_concurrent_use_only_one_succeeds_and_expiry_invalidates(self):
        manifest=self.approved();grant=self.delegations.issue(self.owner,'tenantA',self.grant(manifest),'fixture');request=UseRequest(token=grant['token'],capability='assets.read',resource_id=self.fixture.asset['id'])
        def use(_):
            try:self.delegations.use(self.agent,'tenantA',request,'fixture');return True
            except DomainError:return False
        with ThreadPoolExecutor(max_workers=2) as pool:self.assertEqual(sum(pool.map(use,range(2))),1)
        nextgrant=self.delegations.issue(self.owner,'tenantA',self.grant(manifest),'fixture');self.clock[0]+=timedelta(minutes=3)
        with self.assertRaises(DomainError):self.delegations.use(self.agent,'tenantA',request.model_copy(update={'token':nextgrant['token']}),'fixture')

class ViewsApiTests(NewSetup,unittest.IsolatedAsyncioTestCase):
    async def test_console_headers_scoped_views_and_unknown_without_data(self):
        async with self.f.client() as client:
            shell=await client.get('/console');self.assertEqual(shell.status_code,200);self.assertIn("frame-ancestors 'none'",shell.headers['content-security-policy'])
            script=await client.get('/console/console.js');self.assertNotIn('localStorage',script.text);self.assertNotIn('innerHTML',script.text)
            own=await client.get('/v1/tenants/tenantA/dashboard',headers=self.f.headers('viewerA'));self.assertEqual(own.status_code,200)
            self.assertEqual(own.json()['coverage'],'not_tested');self.assertEqual(own.json()['collector_status'],'not_monitored')
            foreign=await client.get('/v1/tenants/tenantB/dashboard',headers=self.f.headers('viewerA'));self.assertEqual(foreign.status_code,404)
            logs=await client.get('/v1/tenants/tenantA/logs',headers=self.f.headers('viewerA'));self.assertTrue(logs.json()['records'])
            nohold=await client.post('/v1/tenants/tenantA/logs/hold',headers=self.f.headers('viewerA'),json={'enabled':True});self.assertEqual(nohold.status_code,403)
    async def test_pending_job_does_not_invent_fresh_scan_and_completed_result_can_age(self):
        from agntia_ciberseguridad.jobs.worker import Worker
        self.store.submit(self.owner,'tenantA',self.body,'dashboard-pending','fixture')
        views=Views(self.f.service,clock=lambda:self.clock[0])
        self.assertEqual(views.dashboard(self.viewer,'tenantA')['freshness'],'unknown')
        await Worker(self.store,self.scanner(self.result()),'dashboard-worker').run_once()
        self.clock[0]+=timedelta(hours=25)
        self.assertEqual(views.dashboard(self.viewer,'tenantA')['freshness'],'stale')

    async def test_signed_webhook_api_scope_and_denied_agent_privilege(self):
        event=self.event()
        async with self.f.client() as client:
            accepted=await client.post('/v1/tenants/tenantA/sources/sourceA/events',json=event.model_dump(mode='json'),headers={'X-Source-Signature':self.sign(event)});self.assertEqual(accepted.status_code,202)
            foreign=await client.post('/v1/tenants/tenantB/sources/sourceA/events',json=event.model_dump(mode='json'),headers={'X-Source-Signature':self.sign(event)});self.assertEqual(foreign.status_code,404)
            records=await client.get('/v1/tenants/tenantA/events',headers=self.f.headers('viewerA'));self.assertEqual(len(records.json()['events']),1)
