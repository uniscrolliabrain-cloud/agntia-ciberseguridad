"""Bounded synthetic in-process API measurement; no network, scans or SLA claim."""
import asyncio
import json
import platform
import resource
import statistics
import time
from tests.support import Fixture

async def main():
    fixture=Fixture();latency=[];errors=0
    try:
        async with fixture.client() as client:
            for _ in range(10):await client.get('/v1/tenants/tenantA/operations',headers=fixture.headers('viewerA'))
            for _ in range(200):
                started=time.perf_counter()
                response=await client.get('/v1/tenants/tenantA/operations',headers=fixture.headers('viewerA'))
                latency.append((time.perf_counter()-started)*1000)
                errors+=response.status_code!=200
        ordered=sorted(latency)
        print(json.dumps({'scope':'Synthetic ASGI transport, sequential, warm cache, no TCP/TLS/scanner/production SLA',
            'requests':len(latency),'warmup':10,'concurrency':1,'errors':errors,'python':platform.python_version(),
            'sdk_available':fixture.service.telemetry.available,'p50_ms':statistics.median(latency),
            'p95_ms':ordered[int(.95*(len(ordered)-1))],'max_ms':max(latency),
            'process_peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'process_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime,
            'metric_series':fixture.service.telemetry.metrics.series_count(),'contractual_sla':False}))
    finally:
        fixture.service.telemetry.close();fixture.close()
if __name__=='__main__':asyncio.run(main())
