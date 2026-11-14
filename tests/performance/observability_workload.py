"""Bounded synthetic concurrency with injected optional-backend outage; not an SLA."""
import asyncio
import json
import resource
import statistics
import time
from unittest.mock import patch
from tests.support import Fixture

async def main():
    fixture=Fixture();fixture.settings.log_max_records=10;latencies=[];unexpected=0
    semaphore=asyncio.Semaphore(10)
    try:
        async with fixture.client() as client:
            async def request(i):
                nonlocal unexpected
                async with semaphore:
                    start=time.perf_counter();foreign=i%5==0
                    result=await client.get('/v1/tenants/'+('tenantB' if foreign else 'tenantA')+'/dashboard',headers=fixture.headers('viewerA'))
                    latencies.append((time.perf_counter()-start)*1000)
                    unexpected+=result.status_code!=(404 if foreign else 200)
            await asyncio.gather(*(request(i) for i in range(100)))
            with patch.object(fixture.service.logs,'record',side_effect=OSError('synthetic-storage-unavailable')):
                result=await client.get('/v1/tenants/tenantB/dashboard',headers=fixture.headers('viewerA'))
                assert result.status_code==404
                result=await client.get('/v1/tenants/tenantA/dashboard',headers=fixture.headers('viewerA'))
                assert result.status_code==200
        with fixture.service.db.connection(readonly=True) as db:
            records,bytes_=db.execute('SELECT count(*),coalesce(sum(bytes),0) FROM operational_logs').fetchone()
        assert records<=10
        assert not unexpected
        print(json.dumps({'scope':'Synthetic ASGI, concurrency10, no TCP/TLS or scans; no contractual SLA',
            'requests':100,'expected_cross_tenant_denials':20,'unexpected_results':unexpected,
            'p50_ms':statistics.median(latencies),'p95_ms':sorted(latencies)[94],
            'operational_log_records':records,'operational_log_bytes':bytes_,'bytes_per_record':bytes_/records if records else None,
            'peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'process_cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime,
            'metric_series':fixture.service.telemetry.metrics.series_count(),
            'optional_log_failure_does_not_bypass_auth':True,'sdk_available':fixture.service.telemetry.available,
            'signals':fixture.service.telemetry.metrics.signals.__repr__(),
            'cost_formula':'storage_bytes=events_per_day*average_bytes*retention_days*replication_factor; price requires provider quote'}))
    finally:fixture.service.telemetry.close();fixture.close()
if __name__=='__main__':asyncio.run(main())
