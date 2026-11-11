import random
import unittest
from pydantic import ValidationError
from tests.support import Fixture
from agntia_ciberseguridad.billing.reservations import ReservationRequest
from agntia_ciberseguridad.billing.rates import BudgetPolicy
from agntia_ciberseguridad.events.outbox import Outbox

class HardeningTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):self.f=Fixture()
    def tearDown(self):self.f.service.telemetry.close();self.f.close()
    async def test_seeded_unknown_identity_and_numeric_fuzz_are_rejected(self):
        rng=random.Random(20261111)
        for _ in range(100):
            bad=rng.choice([True,False,-rng.randint(1,1000000),float('nan'),float('inf'),'1',None,{},[]])
            with self.assertRaises(ValidationError):ReservationRequest(rate_ref='fixture',units=bad,operation_key='synthetic-test')
        async with self.f.client() as client:
            for field in ('tenant_id','actor_id','role','capability','url','shell','allowed_company_ids'):
                r=await client.post('/v1/tenants/tenantA/budget/reservations',headers=self.f.headers('reviewerA'),json={'rate_ref':'fixture','units':1,'operation_key':'synthetic-fuzz',field:'injected'})
                self.assertEqual(r.status_code,422)
    async def test_restore_marker_blocks_signed_sources_and_all_api_mutations(self):
        (self.f.settings.data_dir/'RESTORE_BLOCKED').write_text('fixture restore')
        async with self.f.client() as client:
            for method,path in [('GET','/workspace'),('POST','/sources/nonexistent/events'),('POST','/agent/controls'),('POST','/budget/reservations')]:
                r=await client.request(method,'/v1/tenants/tenantA'+path,headers=self.f.headers('reviewerA'),json={})
                self.assertEqual(r.status_code,503)
            self.assertEqual((await client.get('/health/live')).status_code,200)
    async def test_viewer_cannot_reserve_ack_or_reconcile_even_with_valid_payload(self):
        async with self.f.client() as client:
            base='/v1/tenants/tenantA'
            for path,payload in [('/budget/reservations',{'rate_ref':'fixture','units':1,'operation_key':'synthetic-forbidden'}),('/outbox/'+'a'*32+'/ack',{'consumer_id':'test','content_hash':'a'*64})]:
                self.assertEqual((await client.post(base+path,headers=self.f.headers('viewerA'),json=payload)).status_code,403)
