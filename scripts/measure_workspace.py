"""Synthetic ASGI workspace latency per configured plan, not scanner capacity or SLA."""
import asyncio
import json
import os
from pathlib import Path
import platform
import resource
import statistics
import time
from tests.support import Fixture
from agntia_ciberseguridad.billing.rates import BudgetPolicy

async def main():
    results=[]
    for plan in ('Lite','L','XL'):
        fixture=Fixture();fixture.settings.budget_policies={'tenantA':BudgetPolicy(plan=plan,allocation_review_ref='synthetic-allocation')}
        times=[];errors=0;started=time.process_time()
        try:
            async with fixture.client() as client:
                for i in range(110):
                    start=time.perf_counter();response=await client.get('/v1/tenants/tenantA/workspace',headers=fixture.headers('viewerA'))
                    if i>=10:times.append((time.perf_counter()-start)*1000);errors+=response.status_code!=200
            ordered=sorted(times)
            disk=sum(p.stat().st_size for p in fixture.settings.data_dir.rglob('*') if p.is_file())
            results.append({'plan':plan,'requests':100,'warmup':10,'concurrency':1,'errors':errors,'p50_ms':statistics.median(times),'p95_ms':ordered[94],'max_ms':max(times),'process_cpu_seconds':time.process_time()-started,'state_disk_bytes':disk,'peak_process_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'sdk_available':fixture.service.telemetry.available})
        finally:fixture.service.telemetry.close();fixture.close()
    print(json.dumps({'scope':'Synthetic empty-workspace ASGI, sequential, no TCP/TLS/scanners/provider, not tenant capacity or contractual SLA','python':platform.python_version(),'cpu_count':os.cpu_count(),'plans':results,'actual_provider_cost':'not_measured_no_calls','infrastructure_cost':'not_verified','security_controls_identical':True}))
if __name__=='__main__':asyncio.run(main())
