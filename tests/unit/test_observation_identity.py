import unittest
from agntia_ciberseguridad.findings.normalize import normalize
from agntia_ciberseguridad.adapters.common import InvalidReport

class IdentityTests(unittest.TestCase):
    def row(self,**update):
        return {'id':'a'*32,'tenant_id':'A','asset_id':'b'*32,'snapshot_id':'c'*32,'tool':'osv','policy_hash':'d'*64,**update}
    def result(self,tool='osv',**update):
        return {'tool':tool,'policy_hash':'d'*64,'tool_version':'2.7.1','findings':[{'advisory_id':'CVE-2026-12345','component_id':'e'*64,'path':'requirements.txt','severity':'high','state':'verified_fixed'}],**update}
    def test_cross_tool_relation_preserves_distinct_identities_and_unverified_state(self):
        osv=normalize(self.row(),self.result())[0]
        other=normalize(self.row(tool='trivy'),self.result('trivy',tool_version='0.76.2'))[0]
        self.assertNotEqual(osv['finding_id'],other['finding_id'])
        self.assertEqual(osv['relation_id'],other['relation_id'])
        self.assertEqual(osv['state'],'suspected')
        self.assertEqual(osv['reachability'],'unknown')
        self.assertNotEqual(osv['finding_id'],normalize(self.row(tenant_id='B'),self.result())[0]['finding_id'])
    def test_changed_policy_separates_identity_and_raw_traversal_is_rejected(self):
        item=normalize(self.row(),self.result())[0]
        other=normalize(self.row(policy_hash='f'*64),self.result(policy_hash='f'*64))[0]
        self.assertNotEqual(item['finding_id'],other['finding_id'])
        bad=self.result();bad['findings'][0]['path']='../private'
        with self.assertRaises(InvalidReport):normalize(self.row(),bad)
