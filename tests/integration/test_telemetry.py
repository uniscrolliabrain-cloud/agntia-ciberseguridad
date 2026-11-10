import asyncio
import json
import os
from types import SimpleNamespace
import unittest
from agntia_ciberseguridad.telemetry.metrics import Metrics
from agntia_ciberseguridad.telemetry.export import BoundedSpanProcessor
from agntia_ciberseguridad.telemetry.tracing import AVAILABLE
from tests.security.support_custody import CustodySetup

class MetricsTests(unittest.TestCase):
    def test_hundred_thousand_external_dimensions_do_not_create_unbounded_series(self):
        metrics=Metrics()
        for i in range(100000):metrics.request('untrusted-'+str(i),200,.001)
        self.assertLess(metrics.series_count(),25)
        self.assertNotIn('untrusted-',metrics.export())
        self.assertIn('100000',metrics.export())
    def test_failed_partial_and_unknown_scans_never_count_as_complete_scope(self):
        metrics=Metrics()
        for status in ('error','partial','stale','blocked'):metrics.scan(status)
        self.assertNotIn('coverage="declared_scope_complete"',metrics.export())
        self.assertIn('coverage="incomplete"} 3',metrics.export())
        try:from prometheus_client.parser import text_string_to_metric_families
        except ImportError:return
        self.assertTrue(list(text_string_to_metric_families(metrics.export())))
    def test_bounded_export_queue_records_loss_and_failure_without_exception_payload(self):
        class Exporter:
            def export(self,batch):raise RuntimeError('SYNTHETIC_SECRET_DO_NOT_EXPORT')
            def shutdown(self):pass
        metrics=Metrics();processor=BoundedSpanProcessor(Exporter(),metrics,capacity=2,batch_size=1,start=False)
        for _ in range(10):processor.on_end(SimpleNamespace())
        self.assertEqual(metrics.dropped,8)
        processor.drain_once();self.assertEqual(metrics.dropped,9);self.assertEqual(metrics.export_failures,1)
        self.assertNotIn('SYNTHETIC_SECRET',metrics.export())
        processor.shutdown()

class OperationsApiTests(CustodySetup,unittest.IsolatedAsyncioTestCase):
    async def test_metrics_has_separate_auth_and_operations_are_tenant_scoped(self):
        async with self.f.client() as client:
            denied=await client.get('/metrics',headers=self.f.headers('viewerA'));self.assertEqual(denied.status_code,401)
            own=await client.get('/v1/tenants/tenantA/operations',headers=self.f.headers('viewerA'))
            self.assertEqual(own.json()['coverage_status'],'not_tested')
            foreign=await client.get('/v1/tenants/tenantB/operations',headers=self.f.headers('viewerA'))
            self.assertEqual(foreign.status_code,404)
            response=await client.get('/metrics',headers={'Authorization':'Bearer '+os.environ['CYBER_METRICS_GLOBAL']})
            self.assertEqual(response.status_code,200)
            self.assertNotIn('tenantA',response.text);self.assertNotIn('tenantB',response.text)
            self.assertNotIn('/v1/tenants/',response.text)
    async def test_metrics_credential_collision_denies_global_export(self):
        os.environ['CYBER_METRICS_GLOBAL']=self.f.tokens['analystA']
        async with self.f.client() as client:
            result=await client.get('/metrics',headers=self.f.headers())
            self.assertEqual(result.status_code,503)

@unittest.skipUnless(AVAILABLE,'OpenTelemetry SDK unavailable locally; verified separately in CI')
class TraceTests(CustodySetup,unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
        self.exporter=InMemorySpanExporter();self.f.service.telemetry.provider.add_span_processor(SimpleSpanProcessor(self.exporter))
    async def test_untrusted_context_does_not_choose_trace_or_identity_or_leak(self):
        sentinel='AGNTIA_TEST_SECRET_'+'T'*32
        async with self.f.client() as client:
            response=await client.get('/v1/tenants/tenantA/assets',headers={**self.f.headers(),
                'traceparent':'00-'+'b'*32+'-'+'c'*16+'-01','baggage':'tenant_id=tenantB,role=owner,secret='+sentinel})
            self.assertEqual(response.status_code,200)
        spans=self.exporter.get_finished_spans();self.assertTrue(spans)
        self.assertTrue(all(span.context.trace_id!=int('b'*32,16) for span in spans))
        with self.f.service.telemetry.span('api.request',root=True,job_id=sentinel,password=sentinel):
            try:
                with self.f.service.telemetry.span('policy.authorize'):raise ValueError(sentinel)
            except ValueError:pass
        encoded=''.join(span.to_json() for span in self.exporter.get_finished_spans())
        self.assertNotIn(sentinel,encoded);self.assertNotIn('tenantB',encoded);self.assertNotIn('"role"',encoded)
    async def test_persisted_trace_propagates_to_worker_and_report_link(self):
        from agntia_ciberseguridad.jobs.worker import Worker
        from agntia_ciberseguridad.reports import ReportRequest
        from agntia_ciberseguridad.safety import ReleaseGates
        from uuid import uuid4
        self.f.app.state.jobs.gates=ReleaseGates(True,True,True)
        async def submit():
            async with self.f.client() as client:return await client.post('/v1/tenants/tenantA/audits',headers={**self.f.headers(),'Idempotency-Key':'trace-fixture','X-Correlation-ID':str(uuid4())},json=self.body.model_dump(mode='json'))
        task=asyncio.create_task(submit())
        async with asyncio.timeout(5):
            while not task.done():await asyncio.sleep(.01)
        receipt=(await task).json();self.assertEqual(receipt['state'],'pending')
        with self.f.service.db.connection(readonly=True) as db:row=self.f.app.state.jobs._row(db,'tenantA',receipt['id'])
        self.assertTrue(row['trace_parent'])
        await Worker(self.f.app.state.jobs,self.scanner(self.result()),'trace-worker').run_once()
        report=self.reports.create(self.actor,'tenantA',ReportRequest(job_ids=[receipt['id']]),'trace-report')
        spans=self.exporter.get_finished_spans();trace_id=int(row['trace_parent'].split('-')[1],16)
        worker=[s for s in spans if s.name=='job.execute'];self.assertEqual(worker[-1].context.trace_id,trace_id)
        reports=[s for s in spans if s.name=='report.build'];self.assertTrue(any(link.context.trace_id==trace_id for link in reports[-1].links))
        self.assertFalse(report['security_guarantee'])

@unittest.skipUnless(AVAILABLE,'Actual OTLP SDK transport requires installed SDK')
class OtlpWireTests(unittest.TestCase):
    def test_otlp_payload_is_sanitized_and_failed_collector_is_non_blocking(self):
        from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
        import threading
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from agntia_ciberseguridad.telemetry.tracing import Telemetry
        captured=[]
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                captured.append(self.rfile.read(min(int(self.headers['Content-Length']),1000000)))
                self.send_response(200);self.end_headers()
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        telemetry=Telemetry(SimpleNamespace(telemetry_export='disabled'))
        processor=BoundedSpanProcessor(OTLPSpanExporter(endpoint=f'http://127.0.0.1:{server.server_port}/v1/traces',timeout=.3),telemetry.metrics)
        telemetry.provider.add_span_processor(processor)
        sentinel='AGNTIA_TEST_SECRET_'+'W'*32
        try:
            with telemetry.span('api.request',root=True,tool=sentinel,password=sentinel):pass
            self.assertTrue(processor.force_flush(1000));self.assertTrue(captured)
            self.assertNotIn(sentinel.encode(),b''.join(captured))
        finally:telemetry.close();server.shutdown();server.server_close();thread.join(timeout=2)

    def test_configured_exporter_disables_redirects_proxy_and_environment_headers(self):
        from unittest.mock import patch
        from agntia_ciberseguridad.telemetry.tracing import Telemetry
        import requests
        exporter=SimpleNamespace(export=lambda batch:SimpleNamespace(name='SUCCESS'),shutdown=lambda:None)
        with patch('opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter',return_value=exporter) as factory:
            telemetry=Telemetry(SimpleNamespace(telemetry_export='local_collector'))
            try:
                session=factory.call_args.kwargs['session']
                self.assertFalse(session.trust_env)
                self.assertNotIn('Authorization',factory.call_args.kwargs['headers'])
                with patch.object(requests.Session,'request',return_value=SimpleNamespace(status_code=302)) as send:
                    session.request('POST','http://127.0.0.1:4318/v1/traces')
                    self.assertFalse(send.call_args.kwargs['allow_redirects'])
                with self.assertRaises(ValueError):session.request('POST','http://169.254.169.254/')
            finally:telemetry.close()
