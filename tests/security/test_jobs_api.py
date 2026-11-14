import asyncio
import unittest
from tests.integration import test_jobs as jobs
from agntia_ciberseguridad.safety import ReleaseGates

class JobApiTests(jobs.Setup,unittest.IsolatedAsyncioTestCase):
    async def call(self,method,path,*,actor='analystA',body=None,key=None):
        async def request():
            async with self.f.client() as client:
                headers=self.f.headers(actor)
                if key:headers['Idempotency-Key']=key
                return await client.request(method,'/v1/tenants/'+path,headers=headers,json=body)
        task=asyncio.create_task(request())
        try:
            async with asyncio.timeout(5):
                while not task.done():await asyncio.sleep(.01)
            return await task
        finally:
            if not task.done():task.cancel()
    async def test_async_receipt_scope_replay_and_cancel(self):
        self.f.app.state.jobs.gates=ReleaseGates(True,True,True)
        result=await self.call('POST','tenantA/audits',body=self.body.model_dump(mode='json'),key='api-key-001')
        self.assertEqual(result.status_code,202,result.text)
        data=result.json();self.assertEqual(data['state'],'pending');self.assertFalse(data['audit_completed'])
        again=await self.call('POST','tenantA/audits',body=self.body.model_dump(mode='json'),key='api-key-001')
        self.assertEqual(again.json()['id'],data['id'])
        foreign=await self.call('GET','tenantB/jobs/'+data['id'])
        self.assertEqual(foreign.status_code,404)
        viewer=await self.call('POST','tenantA/audits',actor='viewerA',body=self.body.model_dump(mode='json'),key='viewer-key')
        self.assertEqual(viewer.status_code,403)
        cancel=await self.call('POST','tenantA/jobs/'+data['id']+'/cancel',body={'expected_revision':0})
        self.assertEqual(cancel.json()['state'],'cancelled')
        self.assertNotIn('authorization_stamp',cancel.text)
