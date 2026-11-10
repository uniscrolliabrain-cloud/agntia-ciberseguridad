"""Read-only cache attestation. Download/update is a separate administrator process."""
from datetime import datetime,timezone,timedelta
import hashlib
from pathlib import Path
import re
from .adapters.common import InvalidReport
from .util import digest

def validate_metadata(meta,instant):
    if (not isinstance(meta,dict) or set(meta)-{'sha256','fetched_at','max_age_hours','ecosystems','source','fixture'}
            or not re.fullmatch('[a-f0-9]{64}',meta.get('sha256',''))):raise InvalidReport('Invalid cache attestation')
    when=datetime.fromisoformat(meta['fetched_at'])
    hours=meta.get('max_age_hours',24)
    if when.tzinfo is None or type(hours) is not int or not 1<=hours<=168 or when>instant+timedelta(minutes=5):raise InvalidReport('Invalid DB age')
    ecosystems=meta.get('ecosystems',[])
    if not isinstance(ecosystems,list) or not ecosystems or len(ecosystems)>32 or any(not isinstance(e,str) or not re.fullmatch('[A-Za-z0-9._ -]{1,64}',e) for e in ecosystems):raise InvalidReport('Invalid ecosystems')
    return {**meta,'stale':instant-when>timedelta(hours=hours)}

def verify_cache(path,meta,instant):
    validated=validate_metadata(meta,instant)
    root=Path(path)
    inventories=[]
    for ecosystem in validated['ecosystems']:
        file=root/'osv-scalibr'/ecosystem/'all.zip'
        if file.is_symlink() or not file.is_file():raise InvalidReport('Missing offline database')
        if file.stat().st_size>100_000_000:raise InvalidReport('Offline database too large')
        inventories.append({'ecosystem':ecosystem,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    if digest(inventories)!=validated['sha256']:raise InvalidReport('Cache hash mismatch')
    return validated
