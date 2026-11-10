"""Create a documentation/source handoff from tracked files, never .git or private state."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT.parent/'agntia-ciberseguridad-campana-7-dias-2026-11-10.zip');args=p.parse_args()
    target=args.output.resolve()
    if target==ROOT or ROOT in target.parents:raise SystemExit('Write archive outside checkout to avoid recursive inclusion')
    entries=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT).decode().split('\0')
    selected={};index_lines=[]
    for entry in filter(None,entries):
        header,name=entry.split('\t',1);mode,sha,stage=header.split()
        if name.startswith('downloads/'):continue
        if stage!='0':raise SystemExit('Resolve unmerged files before packaging')
        selected[name]=sha;index_lines.append(mode+' '+sha+'\t'+name+'\0')
    # A temporary index makes source_tree independent of the generated ZIP itself.
    with tempfile.TemporaryDirectory() as temp:
        env={**os.environ,'GIT_INDEX_FILE':str(Path(temp)/'index')}
        subprocess.run(['git','read-tree','--empty'],cwd=ROOT,env=env,check=True)
        subprocess.run(['git','update-index','-z','--index-info'],input=''.join(index_lines),text=True,cwd=ROOT,env=env,check=True)
        tree=subprocess.check_output(['git','write-tree'],cwd=ROOT,env=env,text=True).strip()
    records=[];contents=[]
    for name in sorted(selected):
        path=ROOT/name
        if path.is_symlink() or ROOT not in path.resolve().parents:raise SystemExit('Unsafe tracked path')
        if not path.is_file():raise SystemExit('Tracked file missing: '+name)
        data=path.read_bytes()
        git_hash=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if git_hash!=selected[name]:raise SystemExit('Stage source changes before packaging: '+name)
        records.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()});contents.append((name,data))
    manifest=json.dumps({'source_tree_before_download_packaging':tree,'excluded':['.git','downloads/*','untracked/private data'],'scope':'tracked repository documentation/configuration/validators; not an implemented security platform','files':records},ensure_ascii=False,indent=2).encode()
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in [*contents,('EXPORT-MANIFEST.json',manifest)]:
            info=zipfile.ZipInfo('agntia-ciberseguridad/'+name,date_time=(2026,11,10,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            archive.writestr(info,data)
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:raise SystemExit('Archive integrity failed')
    print(json.dumps({'path':str(target),'files':len(records)+1,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_tree':tree,'status':'PASS'},ensure_ascii=False))

if __name__=='__main__':main()
