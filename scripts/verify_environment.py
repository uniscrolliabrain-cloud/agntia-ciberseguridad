"""Read-only, sanitized environment inventory; no scanner or network target is contacted."""
import argparse,hashlib,importlib.metadata,json,os,platform,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def command(argv,timeout=6,env=None):
    try:
        p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=timeout,env=env)
        return {'exit_code':p.returncode,'output':p.stdout.strip()[:2000],'error_class':('permission_denied' if 'permission denied' in p.stderr.lower() else 'command_failed') if p.returncode else None}
    except subprocess.TimeoutExpired:return {'exit_code':None,'error_class':'timeout'}
    except FileNotFoundError:return {'exit_code':None,'error_class':'not_installed'}
def collect(remote_sha=None):
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    inventory=[{'path':p,'bytes':(ROOT/p).stat().st_size,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths if p]
    packages={}
    for name in ('fastapi','pydantic','httpx','cryptography','uvicorn','setuptools','pytest'):
        try:packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:packages[name]=None
    docker_env={k:v for k,v in os.environ.items() if k not in ('DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH')}
    docker=command(['docker','--host=unix:///var/run/docker.sock','info','--format','{{json .ServerVersion}}'],env=docker_env)
    return {'at':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),'python':platform.python_version(),'cpu_count':os.cpu_count(),'packages':packages,'local_head':command(['git','rev-parse','HEAD'])['output'],'remote_baseline_sha':remote_sha,'source_tree':command(['git','rev-parse','HEAD^{tree}'])['output'],'git_status':command(['git','status','--short'])['output'],'tools':{name:bool(shutil.which(name)) for name in ('node','pnpm','docker','gitleaks','osv-scanner','semgrep','trivy')},'docker_local_socket':docker,'source_inventory':inventory,'security_scans_executed':0}
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);p.add_argument('--remote-sha');args=p.parse_args();data=collect(args.remote_sha)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k!='source_inventory'},indent=2))
if __name__=='__main__':main()
