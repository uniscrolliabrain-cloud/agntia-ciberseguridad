"""Synthetic CI: validate real collector/Prometheus configs and deliver sanitized OTLP."""
import json
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request
from types import SimpleNamespace
from agntia_ciberseguridad.telemetry.tracing import Telemetry

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'infra/observability'

def run(args,**kw):return subprocess.run(['docker','--host=unix:///var/run/docker.sock',*args],check=True,**kw)
def main():
    pins=json.loads((CONFIG/'images.json').read_text());resolved={}
    for name in ('collector','prometheus'):
        run(['pull',pins[name]])
        value=subprocess.check_output(['docker','image','inspect',pins[name],'--format','{{json .RepoDigests}}']).decode()
        resolved[name]=json.loads(value)[0]
    run(['run','--rm','--network=none','-v',str(CONFIG/'collector.yaml')+':/etc/otelcol/config.yaml:ro',resolved['collector'],'validate','--config=/etc/otelcol/config.yaml'])
    with tempfile.TemporaryDirectory() as temporary:
        token=Path(temporary)/'metrics-token';token.write_text('synthetic-fixture-not-a-real-token');token.chmod(0o444)
        mount=['-v',str(CONFIG)+':/etc/prometheus:ro','-v',str(token)+':/run/secrets/agntia_metrics_token:ro']
        run(['run','--rm','--network=none',*mount,'--entrypoint=/bin/promtool',resolved['prometheus'],'check','config','/etc/prometheus/prometheus.yaml'])
        run(['run','--rm','--network=none',*mount,'--entrypoint=/bin/promtool',resolved['prometheus'],'check','rules','/etc/prometheus/alerts.yaml'])
    name='agntia-collector-synthetic-fixture'
    try:
        run(['run','--detach','--name',name,'--memory=128m','--cpus=1','-p','127.0.0.1:4318:4318','-p','127.0.0.1:13133:13133',
             '-v',str(CONFIG/'collector.yaml')+':/etc/otelcol/config.yaml:ro',resolved['collector'],'--config=/etc/otelcol/config.yaml'])
        for _ in range(50):
            try:
                with urllib.request.urlopen('http://127.0.0.1:13133/',timeout=.5) as response:
                    if response.status==200:break
            except OSError:time.sleep(.1)
        else:raise RuntimeError('Collector not healthy')
        telemetry=Telemetry(SimpleNamespace(telemetry_export='local_collector'))
        try:
            with telemetry.span('api.request',root=True,component='api',operation='read',password='SYNTHETIC_SECRET_SENTINEL_NOT_EXPORTED'):pass
            if not telemetry.provider.force_flush(1000):raise RuntimeError('Collector flush incomplete')
            time.sleep(1.2)
            logs=subprocess.check_output(['docker','logs',name],stderr=subprocess.STDOUT)
            if b'SYNTHETIC_SECRET_SENTINEL_NOT_EXPORTED' in logs:raise RuntimeError('Sensitive diagnostic leaked')
            if b'spans' not in logs.lower():raise RuntimeError('No collector trace signal')
            if telemetry.metrics.dropped or telemetry.metrics.export_failures:raise RuntimeError('OTLP delivery failed')
        finally:telemetry.close()
        print(json.dumps({'observability_validation':'PASS','resolved_images':resolved,'collector_otlp_received':True,
                          'scope':'Synthetic local collector only; no production backend or contractual SLA'}))
    finally:run(['rm','--force',name],stdout=subprocess.DEVNULL)
if __name__=='__main__':main()
