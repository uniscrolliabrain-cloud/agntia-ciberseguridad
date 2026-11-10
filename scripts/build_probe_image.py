"""Build a synthetic Python sandbox probe, recording the resolved immutable base digest."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'state/scanner-build/probe';folder.mkdir(parents=True,exist_ok=True)
base='python:3.12-slim'
subprocess.run(['docker','pull',base],check=True)
digest=json.loads(subprocess.check_output(['docker','image','inspect',base,'--format','{{json .RepoDigests}}']))[0]
(folder/'Dockerfile').write_text('FROM '+digest+'\nCOPY --chmod=0555 probe.py /scanner\nUSER 65532:65532\nENTRYPOINT ["/scanner"]\n')
shutil.copyfile(ROOT/'tests/docker/probe.py',folder/'probe.py')
subprocess.run(['docker','build','--network=none','--iidfile',str(folder.parent/'probe.id'),str(folder)],check=True)
(folder/'base.json').write_text(json.dumps({'resolved_base_digest':digest,'scope':'Synthetic probe only, not production image pin'})+'\n')
