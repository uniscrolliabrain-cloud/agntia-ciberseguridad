"""Synthetic SQLite audit contention; not a scanner or production capacity benchmark."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import statistics
import tempfile
import time
from agntia_ciberseguridad.storage import Database

with tempfile.TemporaryDirectory() as temporary:
    database=Database(Path(temporary),timeout=3);database.migrate();database.provision_tenants(['synthetic'])
    def append(index):
        start=time.perf_counter()
        with database.transaction() as db:database.audit(db,'synthetic','synthetic','fixture','synthetic','synthetic',{'index':index})
        return (time.perf_counter()-start)*1000
    start=time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:values=sorted(pool.map(append,range(100)))
    elapsed=time.perf_counter()-start
    with database.connection(readonly=True) as db:integrity=database.verify_audit(db,'synthetic')
    print(json.dumps({'scope':'single-node synthetic audit append only','samples':100,'threads':4,'elapsed_seconds':elapsed,'p50_ms':statistics.median(values),'p95_ms':values[94],'max_ms':max(values),'errors':0,'integrity':integrity,'production_capacity_verified':False}))
