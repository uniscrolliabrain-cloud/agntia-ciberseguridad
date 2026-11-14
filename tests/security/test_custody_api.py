import base64
import unittest
from tests.security.support_custody import CustodySetup

class CustodyApiTests(CustodySetup,unittest.IsolatedAsyncioTestCase):
    async def test_encrypted_upload_access_review_agent_denial_and_safe_exports(self):
        async with self.f.client() as client:
            secret='AGNTIA_TEST_SECRET_'+'A'*32
            response=await client.post('/v1/tenants/tenantA/evidence',headers=self.f.headers(),json={'content_b64':base64.b64encode(secret.encode()).decode(),'media_type':'text/plain'})
            self.assertEqual(response.status_code,201,response.text);evidence=response.json()
            content=await client.get('/v1/tenants/tenantA/evidence/'+evidence['id']+'/content',headers=self.f.headers('viewerA'))
            self.assertEqual(content.status_code,200);self.assertNotIn(secret,content.text)
            self.assertIn('attachment',content.headers['content-disposition'])
            self.assertIn('nosniff',content.headers['x-content-type-options'])
            denied=await client.post('/v1/tenants/tenantA/evidence/'+evidence['id']+'/original',headers=self.f.headers('viewerA'),json={'reason':'I cannot read original'})
            self.assertEqual(denied.status_code,403)
            original=await client.post('/v1/tenants/tenantA/evidence/'+evidence['id']+'/original',headers=self.f.headers('reviewerA'),json={'reason':'Synthetic human inspection'})
            self.assertEqual(original.status_code,200);self.assertEqual(original.text,secret)
            foreign=await client.get('/v1/tenants/tenantB/evidence/'+evidence['id'],headers=self.f.headers())
            self.assertEqual(foreign.status_code,404)
            reviewed=await client.post('/v1/tenants/tenantA/evidence/'+evidence['id']+'/review',headers=self.f.headers('reviewerA'),json={'expected_revision':0,'reason':'Synthetic human verification'})
            self.assertEqual(reviewed.json()['state'],'reviewed')
            report=await client.post('/v1/tenants/tenantA/reports',headers=self.f.headers(),json={})
            self.assertEqual(report.status_code,201,report.text)
            self.assertEqual(report.json()['coverage_status'],'incomplete_or_unknown')
            page=await client.get('/v1/tenants/tenantA/reports/'+report.json()['id']+'?format=html',headers=self.f.headers('viewerA'))
            self.assertEqual(page.status_code,200)
            self.assertIn('sandbox',page.headers['content-security-policy']);self.assertNotIn(secret,page.text)
            pdf=await client.get('/v1/tenants/tenantA/reports/'+report.json()['id']+'?format=pdf',headers=self.f.headers())
            self.assertEqual(pdf.status_code,422)
