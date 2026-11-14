import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from agntia_ciberseguridad.releasecheck import check

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('release_bundle',ROOT/'scripts/release_bundle.py');release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)
class ReleaseTests(unittest.IsolatedAsyncioTestCase):
    async def test_package_resources_and_synthetic_auth_contract(self):
        result=await check();self.assertEqual(result['installed_artifact_smoke'],'PASS');self.assertFalse(result['production_accepted']);self.assertFalse(result['scanner_executed'])
    async def test_bundle_integrity_missing_extra_tampered_and_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'payload').write_bytes(b'synthetic');manifest={'files':{'payload':release.sha(root/'payload')}}
            (root/'manifest.json').write_text(json.dumps(manifest));(root/'SHA256SUMS').write_text(f"{manifest['files']['payload']}  payload\n{release.sha(root/'manifest.json')}  manifest.json\n")
            self.assertEqual(release.verify(root)['files'],manifest['files'])
            (root/'extra').write_text('unexpected')
            with self.assertRaises(ValueError):release.verify(root)
            (root/'extra').unlink();(root/'payload').write_text('changed')
            with self.assertRaises(ValueError):release.verify(root)
            (root/'manifest.json').write_text(json.dumps({'files':{'../escape':'a'*64}}))
            with self.assertRaises(ValueError):release.verify(root)
    async def test_wheel_inventory_requires_project_and_unique_distribution(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with self.assertRaises(ValueError):release.wheel_inventory(root)
            for n in ('one','two'):
                with zipfile.ZipFile(root/(n+'.whl'),'w') as z:z.writestr('project.dist-info/METADATA','Name: agntia-ciberseguridad\nVersion: 0.1.0a1\n')
                if n=='one':self.assertEqual(release.wheel_inventory(root)[0]['version'],'0.1.0a1')
            with self.assertRaises(ValueError):release.wheel_inventory(root)
