from dataclasses import replace
import json
import unittest
from agntia_ciberseguridad.adapters import semgrep,trivy
from agntia_ciberseguridad.runners.base import RunResult,Tool
from agntia_ciberseguridad.sbom_validation import validate,import_observed
from agntia_ciberseguridad.sbom import build
from agntia_ciberseguridad.adapters.common import InvalidReport
from agntia_ciberseguridad.util import canonical

class ExtendedParsers(unittest.TestCase):
    def result(self,tool,data,code):return RunResult(tool,'1.185.0' if tool==Tool.semgrep else '0.76.2','completed',code,json.dumps(data).encode(),cleanup_verified=True,policy_hash='a'*64,image='sha256:'+'b'*64)
    def test_semgrep_minimization_partial_unknown_and_clean(self):
        data={'version':'1.185.0','results':[{'check_id':'agntia.python.dynamic-eval','path':'bad.py','start':{'line':1},'end':{'line':1},'extra':{'lines':'PRIVATE_SENTINEL'}}],'errors':[]}
        result=semgrep.parse(self.result(Tool.semgrep,data,1),'a'*32)
        self.assertEqual(result['status'],'findings');self.assertNotIn('PRIVATE_SENTINEL',json.dumps(result))
        data['errors']=[{'message':'untrusted'}]
        self.assertEqual(semgrep.parse(self.result(Tool.semgrep,data,1),'a'*32)['status'],'partial')
        data['results'][0]['check_id']='unknown'
        self.assertEqual(semgrep.parse(self.result(Tool.semgrep,data,1),'a'*32)['status'],'error')
        self.assertEqual(semgrep.parse(self.result(Tool.semgrep,{'version':'1.185.0','results':[],'errors':[]},0),'a'*32)['status'],'no_findings')
    def test_trivy_minimized_config_and_unknown_or_missing_coverage(self):
        data={'SchemaVersion':2,'Results':[{'Class':'config','Target':'Dockerfile','Misconfigurations':[{'ID':'DS002','Status':'FAIL','Severity':'HIGH','Message':'PRIVATE_SENTINEL','CauseMetadata':{'StartLine':2}}]}]}
        result=trivy.parse(self.result(Tool.trivy,data,10),'a'*32)
        self.assertEqual(result['findings'][0]['severity'],'high');self.assertNotIn('PRIVATE_SENTINEL',json.dumps(result))
        self.assertEqual(result['coverage']['advisory_database'],'not_used')
        self.assertEqual(trivy.parse(self.result(Tool.trivy,{'SchemaVersion':2,'Results':[]},0),'a'*32)['status'],'partial')
        self.assertEqual(trivy.parse(self.result(Tool.trivy,{'SchemaVersion':99},0),'a'*32)['status'],'error')
    def test_official_offline_schema_and_unverified_import(self):
        document=build([{'id':'a'*64,'name':'demo','version':'1.0.0','purl':'pkg:pypi/demo@1.0.0','ecosystem':'PyPI'}],'a'*32)
        self.assertEqual(validate(canonical(document).encode())['specVersion'],'1.5')
        imported=import_observed(canonical(document).encode())
        self.assertEqual(imported['status'],'imported_unverified');self.assertEqual(imported['components'][0]['licenses'],'unknown')
        for bad in ({**document,'specVersion':'1.4'},{**document,'version':'one'},{'bomFormat':'CycloneDX','specVersion':'1.5','components':[{'type':'invalid','name':'x'}]}):
            with self.assertRaises(InvalidReport):validate(canonical(bad).encode())
        with self.assertRaises(InvalidReport):validate(b'x'*2100000)
