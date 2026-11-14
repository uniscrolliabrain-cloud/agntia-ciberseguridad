"""Build a platform-specific immutable pilot bundle, then install offline outside checkout."""
import argparse
import email
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote
import venv
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def wheel_inventory(folder):
    records=[];seen=set()
    for wheel in sorted(folder.glob('*.whl')):
        with zipfile.ZipFile(wheel) as z:
            metadata=[n for n in z.namelist() if n.endswith('.dist-info/METADATA')]
            if len(metadata)!=1:raise ValueError('Ambiguous wheel metadata')
            m=email.message_from_bytes(z.read(metadata[0]));name=m['Name'];version=m['Version']
            key=name.lower().replace('_','-')
            if key in seen:raise ValueError('Duplicate distribution')
            seen.add(key)
            records.append({'name':name,'version':version,'file':wheel.name,'sha256':sha(wheel),'license_metadata':(m.get('License-Expression') or m.get('License') or 'unknown')[:160]})
    if 'agntia-ciberseguridad' not in seen:raise ValueError('Project wheel missing')
    return records

def verify(folder):
    folder=Path(folder);manifest=json.loads((folder/'manifest.json').read_text())
    expected=manifest['files']
    if not isinstance(expected,dict) or len(expected)>300:raise ValueError('Invalid manifest')
    for name,checksum in expected.items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or str(path.as_posix())!=name:raise ValueError('Invalid manifest path')
        file=folder/path
        if file.is_symlink() or any(p.is_symlink() for p in file.parents if p!=folder.parent):raise ValueError('Symlink in bundle')
        if not file.is_file() or sha(file)!=checksum:raise ValueError('Bundle hash mismatch')
    found={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    if found != set(expected)|{'manifest.json','SHA256SUMS'}:raise ValueError('Unexpected or missing artifact')
    checks={}
    for line in (folder/'SHA256SUMS').read_text().splitlines():
        h,n=line.split('  ',1)
        if n in checks:raise ValueError('Duplicate checksum')
        checks[n]=h
    if checks!={**expected,'manifest.json':sha(folder/'manifest.json')}:raise ValueError('Checksums mismatch')
    return manifest

def build(output):
    if output.exists():raise ValueError('Output must be a new directory')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Commit changes before release build')
    npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
    if not npm:raise ValueError('npm unavailable')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    output.mkdir(parents=True,mode=0o700);wheels=output/'wheelhouse';wheels.mkdir()
    subprocess.run([sys.executable,'-m','pip','wheel','--only-binary=:all:','--wheel-dir',str(wheels),str(ROOT)+'[dev]'],check=True,cwd=ROOT)
    records=wheel_inventory(wheels)
    (output/'requirements.lock').write_text(''.join(f"{r['name']}=={r['version']} --hash=sha256:{r['sha256']}\n" for r in records))
    subprocess.run([npm,'ci','--ignore-scripts','--no-audit','--no-fund'],cwd=ROOT/'typescript',check=True)
    subprocess.run([npm,'run','build'],cwd=ROOT/'typescript',check=True)
    packed=subprocess.check_output([npm,'pack','--ignore-scripts','--json','--pack-destination',str(output)],cwd=ROOT/'typescript',text=True)
    packs=json.loads(packed)
    if len(packs)!=1:raise ValueError('Unexpected npm artifact')
    with tempfile.TemporaryDirectory(prefix='agntia-clean-install-') as temp:
        env_path=Path(temp)/'environment';venv.EnvBuilder(with_pip=True).create(env_path)
        python=env_path/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        clean_env={k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONHOME','AGNTIA_CYBER_CONFIG_FILE')}
        subprocess.run([str(python),'-m','pip','install','--no-index','--require-hashes','--find-links',str(wheels),'-r',str(output/'requirements.lock')],check=True,cwd=temp,env=clean_env)
        receipt=subprocess.check_output([str(python),'-I','-m','agntia_ciberseguridad.releasecheck'],cwd=temp,env=clean_env,text=True)
        installed=json.loads(receipt.strip().splitlines()[-1])
        if str(ROOT) in installed['package_path'] or installed['installed_artifact_smoke']!='PASS':raise ValueError('Smoke imported checkout')
        sdk_root=Path(temp)/'sdk'
        subprocess.run([npm,'install','--ignore-scripts','--no-audit','--no-fund','--prefix',str(sdk_root),str(output/packs[0]['filename'])],check=True,cwd=temp)
        sdk_url=(sdk_root/'node_modules/@agntia/ciberseguridad/dist/client.js').as_uri()
        hono_url=(sdk_root/'node_modules/@agntia/ciberseguridad/dist/hono.js').as_uri()
        probe='import {CyberClient} from '+json.dumps(sdk_url)+';import {cyberRoutes} from '+json.dumps(hono_url)+';if(typeof CyberClient!=="function"||typeof cyberRoutes!=="function")throw Error("SDK artifact invalid");console.log("SDK_INSTALLED_ARTIFACT_PASS");'
        sdk_receipt=subprocess.check_output(['node','--input-type=module','-e',probe],cwd=temp,text=True)
        if 'SDK_INSTALLED_ARTIFACT_PASS' not in sdk_receipt:raise ValueError('SDK artifact smoke failed')
        installed['sdk_tarball_installed']=True
        installed['package_path']='isolated venv site-packages (temporary directory removed)'
        (output/'installed-smoke.json').write_text(json.dumps(installed,indent=2)+'\n')
    sbom={'bomFormat':'CycloneDX','specVersion':'1.5','version':1,'components':[{'type':'library','name':r['name'],'version':r['version'],'purl':'pkg:pypi/'+quote(r['name'].lower().replace('_','-'))+'@'+quote(r['version']),'hashes':[{'alg':'SHA-256','content':r['sha256']}]} for r in records]}
    lock=json.loads((ROOT/'typescript/package-lock.json').read_text())
    for name,r in lock['packages'].items():
        if name.startswith('node_modules/'):
            sbom['components'].append({'type':'library','name':name[len('node_modules/'):],'version':r['version'],'purl':'pkg:npm/'+quote(name[len('node_modules/'):],safe='/@')+'@'+r['version'],'properties':[{'name':'agntia:lock-integrity','value':r.get('integrity','unknown')}]})
    (output/'sbom.cdx.json').write_text(json.dumps(sbom,indent=2)+'\n')
    (output/'THIRD-PARTY-NOTICES.json').write_text(json.dumps({'scope':'metadata only; not legal approval','python':records,'npm_lock':lock,'own_license':'UNDECIDED_NOT_FOR_COMMERCIAL_RELEASE'},indent=2)+'\n')
    (output/'manifest.json').write_text(json.dumps({'schema_version':1,'source_commit':source,'classification':'SYNTHETIC_DEMO_NOT_PRODUCTION','python':platform.python_version(),'platform':platform.platform(),'architecture':platform.machine(),'dependency_resolution':'Exact wheelhouse hashes in this bundle; future builds may resolve different upstream versions','signature':'GitHub workflow attestation if successful; checksums alone do not authenticate publisher','files':{p.relative_to(output).as_posix():sha(p) for p in sorted(output.rglob('*')) if p.is_file()}},indent=2)+'\n')
    manifest=json.loads((output/'manifest.json').read_text())
    (output/'SHA256SUMS').write_text(''.join(f'{checksum}  {name}\n' for name,checksum in sorted({**manifest['files'],'manifest.json':sha(output/'manifest.json')}.items())))
    verify(output)
    print(json.dumps({'release_bundle':'PASS','source_commit':source,'wheels':len(records),'installed_artifact_smoke':'PASS','manifest_sha256':sha(output/'manifest.json'),'production_accepted':False}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);parser.add_argument('--verify',type=Path);args=parser.parse_args()
    if bool(args.output)==bool(args.verify):parser.error('Choose output or verify')
    if args.verify:verify(args.verify.resolve());print(json.dumps({'bundle_integrity':'PASS','publisher_identity':'requires independent signature/attestation verification'}))
    else:build(args.output.resolve())
