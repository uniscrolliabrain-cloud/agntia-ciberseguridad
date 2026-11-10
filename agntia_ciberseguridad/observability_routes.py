from pathlib import Path
from fastapi import Depends,Header,Query,Request
from fastapi.responses import HTMLResponse,Response
from pydantic import Field
from .agents.registry import Registry,Manifest
from .agents.capabilities import Delegations,GrantRequest,UseRequest
from .contracts import Model,OpaqueId,ResourceId,Revision
from .events.ingest import Ingest,PassiveEvent
from .telemetry.logging import SafeRequestLogs
from .telemetry.views import Views

class Hold(Model):enabled:bool

def register_observability(app,service,principal):
    ingest=Ingest(service);registry=Registry(service);delegations=Delegations(service);views=Views(service)
    app.state.ingest=ingest;app.state.registry=registry;app.state.delegations=delegations
    app.add_middleware(SafeRequestLogs,service=service)
    def corr(request):return request.state.correlation_id
    @app.get('/v1/tenants/{tenant}/logs')
    async def logs(tenant:OpaqueId,after:int=Query(0,ge=0),limit:int=Query(50,ge=1,le=100),actor=Depends(principal)):
        return {'records':service.logs.search(actor,tenant,after=after,limit=limit),'retention_days':service.settings.log_retention_days}
    @app.post('/v1/tenants/{tenant}/logs/hold')
    async def hold(tenant:OpaqueId,body:Hold,request:Request,actor=Depends(principal)):
        service.logs.hold(actor,tenant,body.enabled,corr(request));return {'enabled_for_existing_records':body.enabled}
    @app.post('/v1/tenants/{tenant}/logs/purge-expired')
    async def purge(tenant:OpaqueId,request:Request,actor=Depends(principal)):
        return {'purged':service.logs.purge(actor,tenant,corr(request))}
    @app.post('/v1/tenants/{tenant}/sources/{source_id}/events',status_code=202)
    async def events(tenant:OpaqueId,source_id:OpaqueId,body:PassiveEvent,x_source_signature:str=Header('',max_length=128)):
        try:return ingest.accept(tenant,source_id,body,x_source_signature)
        except Exception:
            service.telemetry.metrics.signal('events','rejected');raise
    @app.get('/v1/tenants/{tenant}/events')
    async def list_events(tenant:OpaqueId,after:int=Query(0,ge=0),limit:int=Query(50,ge=1,le=100),actor=Depends(principal)):
        return {'events':ingest.list(actor,tenant,after,limit),'incident_confirmation':False}
    @app.post('/v1/tenants/{tenant}/events/{sequence}/acknowledge')
    async def acknowledge(tenant:OpaqueId,sequence:int,request:Request,actor=Depends(principal)):
        return ingest.acknowledge(actor,tenant,sequence,corr(request))
    @app.get('/v1/tenants/{tenant}/dashboard')
    async def dashboard(tenant:OpaqueId,actor=Depends(principal)):return views.dashboard(actor,tenant)
    @app.get('/v1/tenants/{tenant}/investigation/jobs/{job_id}')
    async def investigation(tenant:OpaqueId,job_id:ResourceId,actor=Depends(principal)):return views.investigation(actor,tenant,job_id)
    @app.get('/v1/tenants/{tenant}/agents')
    async def agents(tenant:OpaqueId,actor=Depends(principal)):return registry.list(actor,tenant)
    @app.post('/v1/tenants/{tenant}/agents/manifests',status_code=201)
    async def manifest(tenant:OpaqueId,body:Manifest,request:Request,actor=Depends(principal)):return registry.create(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/agents/manifests/{manifest_id}/approve')
    async def approve(tenant:OpaqueId,manifest_id:ResourceId,body:Revision,request:Request,actor=Depends(principal)):return registry.approve(actor,tenant,manifest_id,body.expected_revision,corr(request))
    @app.post('/v1/tenants/{tenant}/delegations',status_code=201)
    async def delegate(tenant:OpaqueId,body:GrantRequest,request:Request,actor=Depends(principal)):return delegations.issue(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/delegations/use')
    async def use(tenant:OpaqueId,body:UseRequest,request:Request,actor=Depends(principal)):return delegations.use(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/delegations/{delegation_id}/revoke')
    async def revoke(tenant:OpaqueId,delegation_id:ResourceId,request:Request,actor=Depends(principal)):return delegations.revoke(actor,tenant,delegation_id,corr(request))
    @app.get('/console',response_class=HTMLResponse)
    async def console():
        return HTMLResponse((Path(__file__).parent/'web'/'console.html').read_text(),headers={'Cache-Control':'no-store','Content-Security-Policy':"default-src 'none'; style-src 'self'; script-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'",'X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'})
    @app.get('/console/{asset}')
    async def console_asset(asset:str):
        if asset not in ('console.js','console.css'):
            from .errors import not_found
            not_found()
        return Response((Path(__file__).parent/'web'/asset).read_text(),media_type='text/javascript' if asset.endswith('.js') else 'text/css',headers={'X-Content-Type-Options':'nosniff'})
