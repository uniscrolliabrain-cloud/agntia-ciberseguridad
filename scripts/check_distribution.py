"""Build an installable wheel and verify offline schema resources without importing client code."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temporary:
    subprocess.run(['python','-m','pip','wheel','--no-deps','--wheel-dir',temporary,str(root)],check=True)
    wheel=next(Path(temporary).glob('agntia_ciberseguridad-*.whl'))
    names=['bom-1.5.schema.json','spdx.schema.json','jsf-0.82.schema.json','LICENSE.txt']
    hashes={}
    with zipfile.ZipFile(wheel) as archive:
        for name in names:
            path='agntia_ciberseguridad/data/cyclonedx/'+name
            content=archive.read(path)
            hashes[name]=hashlib.sha256(content).hexdigest()
        for name in ('console.html','console.js','console.css'):
            content=archive.read('agntia_ciberseguridad/web/'+name)
            assert content, 'Missing console resource'
            hashes['web/'+name]=hashlib.sha256(content).hexdigest()
        legal=archive.read('agntia_ciberseguridad/governance/legal_sources.json')
        assert json.loads(legal)['version']=='2026-11-10-primary-v1'
        hashes['governance/legal_sources.json']=hashlib.sha256(legal).hexdigest()
    print(json.dumps({'distribution_schema_resources_verified':True,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'schema_hashes':hashes},sort_keys=True))
