"""CI-only synthetic image build, digest pin, least-privilege run; never host socket mount."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
release=ROOT/'dist/release'
base='python:3.12.14-slim-bookworm'
subprocess.run(['docker','pull',base],check=True)
digests=json.loads(subprocess.check_output(['docker','image','inspect',base,'--format','{{json .RepoDigests}}']))
pin=next((d for d in digests if re.fullmatch(r'[^\s]+@sha256:[a-f0-9]{64}',d)),None)
if not pin:raise ValueError('No immutable Python base digest')
# Only explicitly allowed release artifacts enter build context.
with tempfile.TemporaryDirectory(prefix='agntia-image-') as temporary:
    context=Path(temporary);shutil.copytree(release/'wheelhouse',context/'wheelhouse');shutil.copy(release/'requirements.lock',context/'requirements.lock')
    subprocess.run(['docker','build','--network=none','--build-arg','PYTHON_BASE='+pin,'--iidfile',str(context/'image.id'),'-f',str(ROOT/'infra/Dockerfile'),str(context)],check=True)
    image=(context/'image.id').read_text().strip()
    if not re.fullmatch('sha256:[a-f0-9]{64}',image):raise ValueError('Invalid image identity')
    args=['docker','run','--rm','--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--pids-limit=128','--memory=512m','--cpus=1','--tmpfs','/tmp:rw,size=128m,mode=1777','--entrypoint','python',image,'-I','-m','agntia_ciberseguridad.releasecheck']
    result=subprocess.check_output(args,text=True);receipt=json.loads(result.strip().splitlines()[-1])
    if receipt.get('installed_artifact_smoke')!='PASS':raise ValueError('Runtime image smoke failed')
    inspection=json.loads(subprocess.check_output(['docker','image','inspect',image]))[0]
    if inspection['Config']['User']!='65532:65532':raise ValueError('Unexpected container user')
    provenance={'base_tag_resolved':base,'immutable_base':pin,'runtime_image_id':image,'network':'none','read_only':True,'uid':'65532:65532','container_smoke':'PASS','scope':'synthetic API in-process only, no source snapshots/daemon socket/external target'}
    (ROOT/'state').mkdir(exist_ok=True)
    (ROOT/'state/runtime-image.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps(provenance))
