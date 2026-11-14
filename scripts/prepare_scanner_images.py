"""CI/admin only: download exact official release assets, verify hashes, build scratch images.

Does not execute downloaded binaries on the host. Not callable through the HTTP API.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
TOOLS={
'gitleaks':{'version':'8.30.1','url':'https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz','sha256':'551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb','license':'MIT'},
'trivy':{'version':'0.76.2','url':'https://github.com/aquasecurity/trivy/releases/download/v0.76.2/trivy_0.76.2_Linux-64bit.tar.gz','sha256':'bc0fc726e017b8927a62b2d3531d7a84ee01769daf5c99ed866dced54089fdbf','license':'Apache-2.0'},
'osv':{'version':'2.7.1','url':'https://github.com/google/osv-scanner/releases/download/v2.7.1/osv-scanner_linux_amd64','sha256':'fb7dab19a8bd9bbe5c3189f09d4b7ee1820c9553a23bac202648a56efd2f6ee8','license':'Apache-2.0'}}

def main():
    from agntia_ciberseguridad.util import digest
    folder=ROOT/'state/scanner-build';folder.mkdir(parents=True,exist_ok=True)
    pins=[]
    for name,info in TOOLS.items():
        destination=folder/name;destination.mkdir(exist_ok=True)
        request=urllib.request.Request(info['url'],headers={'User-Agent':'Agntia-Synthetic-Contract/0.1'})
        with urllib.request.urlopen(request,timeout=60) as response:
            data=response.read(200_000_001)
        if len(data)>200_000_000 or hashlib.sha256(data).hexdigest()!=info['sha256']:raise SystemExit('Release size/hash mismatch: '+name)
        binary=destination/'scanner'
        if name in ('gitleaks','trivy'):
            import io
            with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:
                member=archive.getmember('gitleaks' if name=='gitleaks' else 'trivy')
                if not member.isfile() or member.size>(300_000_000 if name=='trivy' else 150_000_000):raise SystemExit('Unsafe release member')
                with archive.extractfile(member) as source:binary.write_bytes(source.read(300_000_001 if name=='trivy' else 150_000_001))
        else:binary.write_bytes(data)
        binary.chmod(0o555)
        shutil.copyfile(ROOT/'infra/scanners/Dockerfile',destination/'Dockerfile')
        policy=destination/'policy';policy.mkdir(exist_ok=True)
        for filename in ('gitleaks.toml','osv.toml','empty.ignore','trivy.yaml'):shutil.copyfile(ROOT/'infra/scanners'/filename,policy/filename)
        shutil.copyfile(ROOT/'rules/semgrep/pilot.yml',policy/'semgrep.yml')
        shutil.copytree(ROOT/'infra/scanners/licenses',destination/'licenses',dirs_exist_ok=True)
        policy_hash=digest({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(policy.iterdir())})
        iid=destination/'image.id'
        subprocess.run(['docker','--host=unix:///var/run/docker.sock','build','--network=none','--iidfile',str(iid),str(destination)],check=True)
        version_arg='version' if name=='gitleaks' else '--version'
        reported=subprocess.check_output(['docker','run','--rm','--network=none','--read-only','--cap-drop=ALL','--user=65532:65532',iid.read_text().strip(),version_arg],timeout=15).decode()
        if info['version'] not in reported:raise SystemExit('Unexpected tool version')
        pins.append({'reported_version_verified':True,'tool':name,'version':info['version'],'image':iid.read_text().strip(),'policy_hash':policy_hash,'release_sha256':info['sha256'],'license':info['license']})
    ref=json.loads((ROOT/'infra/scanners/semgrep-image.json').read_text())['reference']
    subprocess.run(['docker','pull',ref],check=True)
    inspected=json.loads(subprocess.check_output(['docker','image','inspect',ref]))[0]
    immutable=inspected['RepoDigests'][0]
    destination=folder/'semgrep';destination.mkdir(exist_ok=True)
    policy=destination/'policy';policy.mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'rules/semgrep/pilot.yml',policy/'semgrep.yml')
    (destination/'scanner').write_text('#!/bin/sh\nexec semgrep "$@"\n')
    (destination/'scanner').chmod(0o555)
    (destination/'Dockerfile').write_text('FROM '+immutable+'\nCOPY --chmod=0555 scanner /scanner\nCOPY policy/ /policy/\nUSER 65532:65532\nENTRYPOINT ["/scanner"]\n')
    iid=destination/'image.id'
    subprocess.run(['docker','build','--network=none','--iidfile',str(iid),str(destination)],check=True)
    reported=subprocess.check_output(['docker','run','--rm','--network=none','--read-only',
        '--env=HOME=/tmp','--env=SEMGREP_SEND_METRICS=off','--env=SEMGREP_ENABLE_VERSION_CHECK=0',
        '--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=32m,mode=1777',iid.read_text().strip(),'--version'],timeout=30).decode()
    if '1.185.0' not in reported:raise SystemExit('Unexpected Semgrep version')
    pins.append({'tool':'semgrep','version':'1.185.0','image':iid.read_text().strip(),
        'policy_hash':digest({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(policy.iterdir())}),
        'upstream_digest':immutable,'license':'LGPL-2.1','reported_version_verified':True})
    (folder/'images.json').write_text(json.dumps(pins,indent=2)+'\n')
    print(json.dumps({'images':pins,'downloaded_binaries_executed_on_host':False}))
if __name__=='__main__':main()
