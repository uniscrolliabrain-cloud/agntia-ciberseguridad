"""Private SDK provider, bounded batch export, fresh public roots and trusted internal context."""
from contextlib import contextmanager
import re
from .metrics import Metrics
from .export import BoundedSpanProcessor

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace.sampling import ALWAYS_ON
    from opentelemetry.sdk.trace.export import SpanExportResult
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    AVAILABLE=True
except ImportError:AVAILABLE=False

NAMES={'db.transaction','api.request','policy.authorize','job.submit','job.execute','scanner.run','evidence.write','evidence.read','review.approve','report.build'}
ATTRS={'component','operation','outcome','tool','job_id','correlation_id','causation_id'}
SAFE_VALUE=re.compile(r'^[A-Za-z0-9_.:-]{1,100}$')
TRACEPARENT=re.compile(r'^00-[a-f0-9]{32}-[a-f0-9]{16}-0[01]$')

class Telemetry:
    def __init__(self,settings):
        self.metrics=Metrics();self.available=AVAILABLE;self.provider=None;self.tracer=None
        if AVAILABLE:
            self.provider=TracerProvider(resource=Resource({'service.name':'agntia-ciberseguridad','service.version':'0.1.0a1'}),sampler=ALWAYS_ON)
            self.tracer=self.provider.get_tracer('agntia.security','1')
            if settings.telemetry_export=='local_collector':
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
                import requests
                class LocalOnlySession(requests.Session):
                    def __init__(self):
                        super().__init__();self.trust_env=False
                    def request(self,method,url,*args,**kwargs):
                        if url!='http://127.0.0.1:4318/v1/traces':raise ValueError('Unapproved telemetry endpoint')
                        kwargs['allow_redirects']=False
                        return super().request(method,url,*args,**kwargs)
                exporter=OTLPSpanExporter(endpoint='http://127.0.0.1:4318/v1/traces',timeout=.5,
                    session=LocalOnlySession(),headers={'Content-Type':'application/x-protobuf'})
                self.provider.add_span_processor(BoundedSpanProcessor(exporter,self.metrics))
    @contextmanager
    def span(self,name,*,parent=None,root=False,**attributes):
        if not self.available:
            yield None;return
        name=name if name in NAMES else 'policy.authorize'
        safe={}
        for key,value in attributes.items():
            value=str(value)
            if key not in ATTRS:continue
            if key=='job_id' and not re.fullmatch('[a-f0-9]{32}',value):continue
            if key in ('correlation_id','causation_id') and not re.fullmatch('[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}',value):continue
            if key=='tool' and value not in {'gitleaks','osv','semgrep','trivy'}:continue
            if key=='component' and value not in {'api','storage','policy','jobs','worker','runner','evidence','review','report'}:continue
            if key=='operation' and value not in {'read','write','health','metrics','authorize','submit','create'}:continue
            if key=='outcome' and value not in {'success','error','blocked','partial'}:continue
            safe[key]=value
        context=None
        if root:
            from opentelemetry.context import Context
            context=Context()
        elif parent and TRACEPARENT.fullmatch(parent) and parent.split('-')[1]!='0'*32 and parent.split('-')[2]!='0'*16:
            context=TraceContextTextMapPropagator().extract({'traceparent':parent})
        with self.tracer.start_as_current_span(name,context=context,attributes=safe,record_exception=False,set_status_on_exception=False) as span:
            try:yield span
            except Exception:
                span.set_attribute('outcome','error')
                raise
    def current_parent(self):
        if not self.available:return None
        carrier={};TraceContextTextMapPropagator().inject(carrier)
        return carrier.get('traceparent')
    def link_internal(self,parent):
        if self.available and parent and TRACEPARENT.fullmatch(parent):
            context=TraceContextTextMapPropagator().extract({'traceparent':parent})
            linked=trace.get_current_span(context).get_span_context()
            current=trace.get_current_span()
            if linked.is_valid and current.is_recording():current.add_link(linked)

    def close(self):
        if self.provider:self.provider.shutdown()
