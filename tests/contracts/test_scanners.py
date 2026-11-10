from dataclasses import replace
from datetime import timedelta
import json
import unittest
from agntia_ciberseguridad.adapters import gitleaks,osv
from agntia_ciberseguridad.runners.base import RunResult,Tool
from agntia_ciberseguridad.sbom import diff
from agntia_ciberseguridad.util import utcnow

class ScannerContracts(unittest.TestCase):
    def result(self,tool,data,code=0,**kwargs):
        return RunResult(tool,{'gitleaks':'8.30.1','osv':'2.7.1'}[tool.value],'completed',code,
                         json.dumps(data).encode(),cleanup_verified=True,**kwargs)
    def metadata(self,**overrides):
        return {'sha256':'a'*64,'fetched_at':utcnow().isoformat(),'max_age_hours':24,'ecosystems':['PyPI'],'source':'synthetic','fixture':True,**overrides}
    def osv_payload(self,version='2.2.24',vulns=True):
        advisory={'id':'AGNTIA-TEST-0001','affected':[{'package':{'name':'django','ecosystem':'PyPI'},'ranges':[{'type':'ECOSYSTEM','events':[{'introduced':'0'},{'fixed':'2.2.25'}]}]}]}
        return {'results':[{'source':{'path':'/input/requirements.txt','type':'lockfile'},'packages':[{'package':{'name':'django','version':version,'ecosystem':'PyPI'},'vulnerabilities':[advisory] if vulns else []}]}]}

    def test_gitleaks_canary_minimized_and_duplicate_stable(self):
        secret='AGNTIA_TEST_SECRET_'+'A'*32
        leak={'RuleID':'agntia-canary','File':'/input/canary.txt','StartLine':1,'EndLine':1,'Secret':secret,'Match':secret,'Description':secret}
        result=gitleaks.parse(self.result(Tool.gitleaks,[leak,leak],10),'a'*32,manifest_paths={'canary.txt'})
        self.assertEqual(result['status'],'findings');self.assertEqual(len(result['findings']),1)
        self.assertNotIn(secret,json.dumps(result));self.assertNotIn('Secret',json.dumps(result))
        changed={**leak,'Secret':'different-sensitive-value'}
        self.assertEqual(result['findings'][0]['fingerprint'],gitleaks.parse(self.result(Tool.gitleaks,[changed],10),'a'*32)['findings'][0]['fingerprint'])

    def test_gitleaks_error_malformed_exit_and_unknown_version_never_clean(self):
        base=self.result(Tool.gitleaks,[])
        cases=[replace(base,version='unknown'),replace(base,output=b'not-json'),replace(base,status='error'),replace(base,exit_code=10),replace(base,output=b'[{"RuleID":"x","File":"../escape","StartLine":1,"EndLine":1}]',exit_code=10)]
        for case in cases:
            result=gitleaks.parse(case,'a'*32)
            self.assertEqual(result['status'],'error');self.assertFalse(result['scan_clean'])
        self.assertEqual(gitleaks.parse(base,'a'*32)['status'],'no_findings')

    def test_osv_components_advisory_fix_and_sbom_without_exploit_claim(self):
        result=osv.parse(self.result(Tool.osv,self.osv_payload(),1),'a'*32,database=self.metadata(),manifest_paths={'requirements.txt'})
        self.assertEqual(result['status'],'findings',result)
        self.assertEqual(result['findings'][0]['reported_fixed_versions'],['2.2.25'])
        self.assertEqual(result['findings'][0]['reachability'],'unknown')
        self.assertEqual(result['sbom']['specVersion'],'1.5')
        self.assertEqual(result['components'][0]['purl'],'pkg:pypi/django@2.2.24')
        self.assertEqual(result['components'][0]['licenses'],'unknown')

    def test_osv_stale_missing_unknown_and_unpinned_not_safe(self):
        clean=self.result(Tool.osv,self.osv_payload('2.2.25',False))
        self.assertEqual(osv.parse(clean,'a'*32,database=self.metadata())['status'],'no_findings')
        stale=self.metadata(fetched_at=(utcnow()-timedelta(days=2)).isoformat())
        self.assertEqual(osv.parse(clean,'a'*32,database=stale)['status'],'stale')
        self.assertEqual(osv.parse(clean,'a'*32,database={})['status'],'error')
        self.assertEqual(osv.parse(clean,'a'*32,database=self.metadata(ecosystems=['npm']))['status'],'partial')
        bad=self.result(Tool.osv,self.osv_payload('>=2',False))
        self.assertEqual(osv.parse(bad,'a'*32,database=self.metadata())['status'],'error')
        self.assertEqual(osv.parse(replace(clean,output=b'NaN'),'a'*32,database=self.metadata())['status'],'error')

    def test_missing_component_not_claimed_fixed(self):
        change=diff([{'id':'a','name':'old'}],[])
        self.assertEqual(change['not_observed'][0]['name'],'old')
        self.assertNotIn('fixed',change)

    def test_cache_bytes_attestation_and_tampering(self):
        from scripts.create_offline_fixture import create
        from agntia_ciberseguridad.offline_database import verify_cache
        from agntia_ciberseguridad.adapters.common import InvalidReport
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);metadata=create(root)
            self.assertFalse(verify_cache(root,metadata,utcnow())['stale'])
            (root/'osv-scalibr/PyPI/all.zip').write_bytes(b'corrupted')
            with self.assertRaises(InvalidReport):verify_cache(root,metadata,utcnow())
            with self.assertRaises(InvalidReport):verify_cache(root,{**metadata,'ecosystems':['..']},utcnow())
