"""Deterministic, invented OSV advisory cache for the real executable's contract test."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import zipfile
from agntia_ciberseguridad.util import digest

def create(root):
    folder=Path(root)/'osv-scalibr/PyPI';folder.mkdir(parents=True,exist_ok=True)
    advisory={'schema_version':'1.6.0','id':'AGNTIA-TEST-0001','modified':'2026-11-10T00:00:00Z',
              'published':'2026-11-10T00:00:00Z','summary':'Synthetic fixture, not a real advisory',
              'affected':[{'package':{'ecosystem':'PyPI','name':'agntia-demo-package'},
                'ranges':[{'type':'ECOSYSTEM','events':[{'introduced':'0'},{'fixed':'2.0.0'}]}]}]}
    archive=folder/'all.zip'
    info=zipfile.ZipInfo('AGNTIA-TEST-0001.json',date_time=(2026,11,10,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(archive,'w') as out:out.writestr(info,json.dumps(advisory,sort_keys=True))
    metadata={'sha256':digest([{'ecosystem':'PyPI','sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}]),
              'fetched_at':datetime.now(timezone.utc).isoformat(),'max_age_hours':24,'ecosystems':['PyPI'],
              'source':'agntia synthetic fixture only','fixture':True}
    (Path(root)/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return metadata
if __name__=='__main__':
    import sys
    print(json.dumps(create(Path(sys.argv[1]))))
