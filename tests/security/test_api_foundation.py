import asyncio
import json
import os
import unittest
from datetime import timedelta
from unittest.mock import patch

from tests.support import Fixture
from agntia_ciberseguridad.contracts import AssetCreate, AuditPreview, GrantApproval, GrantCreate, GrantRevocation
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.util import utcnow


class ApiTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.close()

    async def request(self, method, path, actor='analystA', **kwargs):
        async with self.f.client() as client:
            return await client.request(method, '/v1/tenants/' + path, headers=self.f.headers(actor), **kwargs)

    async def asset(self, actor='analystA', tenant='tenantA', target='repoA', kind='repository'):
        result = await self.request('POST',tenant+'/assets',actor,json={'target_ref':target,'kind':kind,'display_name':'Synthetic fixture'})
        self.assertEqual(result.status_code,201,result.text)
        return result.json()

    async def approved(self, **overrides):
        asset = await self.asset(**overrides)
        body = self.f.grant_body(asset['id'],profile='passive_web' if overrides.get('kind')=='web' else 'static_read')
        proposed = await self.request('POST','tenantA/grants',json=body)
        self.assertEqual(proposed.status_code,201,proposed.text)
        grant = proposed.json()
        result = await self.request('POST','tenantA/grants/'+grant['id']+'/approve','reviewerA',json={'expected_revision':0,'proposal_hash':grant['proposal_hash'],'notes':'Human test reviewer authorization'})
        self.assertEqual(result.status_code,200,result.text)
        return asset,result.json()

    async def test_auth_required_and_duplicate_credentials_denied(self):
        async with self.f.client() as client:
            for headers in ({},{'Authorization':'Bearer invalid'},[('Authorization',self.f.headers()['Authorization']),('Authorization','Bearer other')]):
                result=await client.get('/v1/tenants/tenantA/assets',headers=headers)
                self.assertIn(result.status_code,(400,401))
                self.assertNotIn('Bearer',result.text)
        first=self.f.settings.principals[0]
        second=self.f.settings.principals[1]
        with patch.dict(os.environ,{second.token_env:self.f.tokens['analystA']}):
            result=await self.request('GET','tenantA/assets')
            self.assertEqual(result.status_code,401)

    async def test_tenant_asset_isolation_and_no_server_paths(self):
        a=await self.asset()
        b=await self.asset('operatorB','tenantB','repoB')
        for tenant,resource,actor in [('tenantA',b['id'],'analystA'),('tenantB',b['id'],'analystA'),('tenantA','0'*32,'analystA')]:
            result=await self.request('GET',tenant+'/assets/'+resource,actor)
            self.assertEqual(result.status_code,404)
            self.assertEqual(result.json()['code'],'not_found')
        result=await self.request('POST','tenantA/assets',json={'target_ref':'repoB','kind':'repository','display_name':'Wrong company'})
        self.assertEqual(result.status_code,404)
        self.assertNotIn(str(self.f.root),json.dumps(a))
        page=await self.request('GET','tenantA/assets?limit=1')
        self.assertEqual(page.json()['items'][0]['id'],a['id'])
        empty=await self.request('GET','tenantA/assets?after='+page.json()['next_cursor'])
        self.assertEqual(empty.json()['items'],[])
        self.assertEqual((await self.request('GET','tenantA/assets?after=invalid')).status_code,422)

    async def test_viewer_cannot_mutate_or_preview(self):
        result=await self.request('POST','tenantA/assets','viewerA',json={'target_ref':'repoA','kind':'repository','display_name':'Denied fixture'})
        self.assertEqual(result.status_code,403)
        self.assertEqual((await self.request('POST','tenantA/audits/preview','viewerA',json={'asset_id':'a'*32,'grant_id':'b'*32,'profile':'static_read'})).status_code,403)
        self.assertEqual((await self.request('GET','tenantA/assets','viewerA')).status_code,200)

    async def test_human_review_preview_and_revocation(self):
        asset,grant=await self.approved()
        body={'asset_id':asset['id'],'grant_id':grant['id'],'profile':'static_read'}
        result=await self.request('POST','tenantA/audits/preview',json=body)
        self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(result.json()['status'],'preflight_passed')
        self.assertFalse(result.json()['security_scan_executed'])
        result=await self.request('POST','tenantA/grants/'+grant['id']+'/revoke','reviewerA',json={'expected_revision':1,'notes':'Withdraw synthetic authorization'})
        self.assertEqual(result.status_code,200,result.text)
        denied=await self.request('POST','tenantA/audits/preview',json=body)
        self.assertEqual(denied.status_code,403)
        integrity=await self.request('GET','tenantA/audit/integrity')
        self.assertTrue(integrity.json()['valid'])
        self.assertGreaterEqual(integrity.json()['checked_events'],6)

    async def test_separation_revision_and_hash_checks(self):
        asset=await self.asset('reviewerA')
        grant=(await self.request('POST','tenantA/grants','reviewerA',json=self.f.grant_body(asset['id']))).json()
        approval={'expected_revision':0,'proposal_hash':grant['proposal_hash'],'notes':'Synthetic separate approval'}
        self.assertEqual((await self.request('POST','tenantA/grants/'+grant['id']+'/approve','reviewerA',json=approval)).status_code,403)
        self.assertEqual((await self.request('POST','tenantA/grants/'+grant['id']+'/approve','analystA',json=approval)).status_code,403)
        # A different privileged principal may approve, but an altered proposal hash must fail.
        grant=(await self.request('POST','tenantA/grants',json=self.f.grant_body(asset['id']))).json()
        approval['proposal_hash']='0'*64
        self.assertEqual((await self.request('POST','tenantA/grants/'+grant['id']+'/approve','reviewerA',json=approval)).status_code,409)
        approval.update(proposal_hash=grant['proposal_hash'],expected_revision=9)
        self.assertEqual((await self.request('POST','tenantA/grants/'+grant['id']+'/approve','reviewerA',json=approval)).status_code,409)

    async def test_grant_cannot_expand_consent_or_accept_llm_identity(self):
        asset=await self.asset()
        for overrides,status in [({'max_requests':101},403),({'max_cost_cents':1},403),({'actor_id':'reviewerA'},422),({'context':{'allowed_company_ids':[2]}},422),({'expires_at':(utcnow()+timedelta(days=5)).isoformat()},422)]:
            response=await self.request('POST','tenantA/grants',json=self.f.grant_body(asset['id'],**overrides))
            self.assertEqual(response.status_code,status,response.text)

    async def test_expired_grant_and_changed_config_fail_closed(self):
        asset,grant=await self.approved()
        body={'asset_id':asset['id'],'grant_id':grant['id'],'profile':'static_read'}
        with patch('agntia_ciberseguridad.service.utcnow',return_value=utcnow()+timedelta(days=2)):
            self.assertEqual((await self.request('POST','tenantA/audits/preview',json=body)).status_code,403)
        self.f.settings.targets['repoA'].location=str(self.f.workspace)
        result=await self.request('POST','tenantA/audits/preview',json=body)
        self.assertEqual(result.status_code,409)
        self.assertEqual(result.json()['code'],'configuration_changed')

    async def test_revoked_principal_and_rotated_token_fail_closed(self):
        asset,grant=await self.approved()
        body={'asset_id':asset['id'],'grant_id':grant['id'],'profile':'static_read'}
        principal=self.f.service.auth.authenticate(self.f.headers()['Authorization'])
        binding=self.f.settings.principals[0]
        with patch.dict(os.environ,{binding.token_env:'synthetic-rotation-'+'z'*32}):
            self.assertEqual((await self.request('GET','tenantA/assets')).status_code,401)
            with self.assertRaises(DomainError):self.f.service.authorize(principal,'tenantA','assets.read')
        self.f.settings.principals[1].enabled=False
        result=await self.request('POST','tenantA/audits/preview',json=body)
        self.assertIn(result.status_code,(401,403))
        async with self.f.client() as client:
            self.assertEqual((await client.get('/health/ready')).status_code,200)

    async def test_bounds_errors_correlation_and_no_secret_reflection(self):
        sentinel='SYNTHETIC_SECRET_SENTINEL_NEVER_REFLECT'
        async with self.f.client() as client:
            result=await client.post('/v1/tenants/tenantA/assets',headers=self.f.headers(),content=sentinel*4000)
            self.assertEqual(result.status_code,413)
            self.assertEqual(result.headers['x-correlation-id'],result.json()['correlation_id'])
            self.assertNotIn(sentinel,result.text)
            result=await client.post('/v1/tenants/tenantA/assets',headers=self.f.headers(),json={'target_ref':'repoA','kind':'repository','display_name':'Fixture','role':sentinel})
            self.assertEqual(result.status_code,422)
            self.assertNotIn(sentinel,result.text)
            result=await client.get('/health/ready')
            self.assertFalse(result.json()['security_scanners_ready'])

    async def test_revocation_during_dns_preflight_denied(self):
        asset,grant=await self.approved(target='webA',kind='web')
        actor=self.f.service.auth.authenticate(self.f.headers()['Authorization'])
        reviewer=self.f.service.auth.authenticate(self.f.headers('reviewerA')['Authorization'])
        body=AuditPreview(asset_id=asset['id'],grant_id=grant['id'],profile='passive_web')
        def resolver(*args,**kwargs):
            self.f.service.revoke_grant(reviewer,'tenantA',grant['id'],GrantRevocation(expected_revision=1,notes='Revoke while resolving DNS'),'synthetic-dns')
            return ['192.0.2.10']
        with self.assertRaises(DomainError) as caught:self.f.service.preview(actor,'tenantA',body,'synthetic-dns',resolver)
        self.assertEqual(caught.exception.code,'grant_not_active')

    async def test_duplicate_asset_is_conflict_and_failed_attempt_audited(self):
        await self.asset()
        result=await self.request('POST','tenantA/assets',json={'target_ref':'repoA','kind':'repository','display_name':'Duplicate fixture'})
        self.assertEqual(result.status_code,409)
        integrity=await self.request('GET','tenantA/audit/integrity')
        self.assertTrue(integrity.json()['valid'])
        self.assertEqual(integrity.json()['checked_events'],2)


class BoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_frame_stream_is_bounded(self):
        from agntia_ciberseguridad.app import RequestBoundary
        count=0
        sent=[]
        async def receive():
            nonlocal count
            count+=1
            return {'type':'http.request','body':b'','more_body':True}
        async def unexpected(*args):self.fail('Must not dispatch an unbounded request')
        async def send(message):sent.append(message)
        await RequestBoundary(unexpected,1024)({'type':'http','headers':[]},receive,send)
        self.assertEqual(sent[0]['status'],413)
        self.assertLessEqual(count,257)
