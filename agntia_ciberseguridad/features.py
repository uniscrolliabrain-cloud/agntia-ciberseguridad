"""Named capabilities only: custody, human reviews, scoped reports and operational signals."""
import base64
from datetime import datetime
import json
from typing import Literal
from fastapi import Depends,Request,Query
from fastapi.responses import Response
from .auth import Principal
from .contracts import OpaqueId,ResourceId,Model
from .evidence.contracts import EvidenceUpload,EvidenceReview,EvidenceHold
from .evidence.vault import Vault
from .errors import reject
from .reports import Reports,ReportRequest
from .reviews import Reviews,ReviewProposal,ReviewApproval
from .telemetry.api import ObserveRequests,metrics_response
from .util import utcnow
from pydantic import Field

class OriginalAccess(Model):
    reason: str=Field(min_length=5,max_length=500)

SAFE_HEADERS={'X-Content-Type-Options':'nosniff','Cache-Control':'no-store',
              'Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; sandbox"}

def register_features(app,service,principal):
    vault=Vault(service);reviews=Reviews(service);reports=Reports(service)
    app.state.vault=vault;app.state.reviews=reviews;app.state.reports=reports
    app.add_middleware(ObserveRequests,telemetry=service.telemetry)
    def corr(request):return request.state.correlation_id

    @app.post('/v1/tenants/{tenant}/evidence',status_code=201)
    async def create_evidence(tenant:OpaqueId,body:EvidenceUpload,request:Request,actor:Principal=Depends(principal)):
        try:content=base64.b64decode(body.content_b64,validate=True)
        except ValueError:reject('evidence_encoding','Base64 inválido',422)
        return vault.put(actor,tenant,content,body.media_type,corr(request),source_job_id=body.source_job_id)

    @app.get('/v1/tenants/{tenant}/evidence/{evidence_id}')
    async def evidence_metadata(tenant:OpaqueId,evidence_id:ResourceId,actor:Principal=Depends(principal)):
        return vault.metadata(actor,tenant,evidence_id)

    @app.get('/v1/tenants/{tenant}/evidence/{evidence_id}/content')
    async def evidence_content(tenant:OpaqueId,evidence_id:ResourceId,request:Request,actor:Principal=Depends(principal)):
        data=vault.read(actor,tenant,evidence_id,corr(request))
        return Response(data,media_type='text/plain',headers={**SAFE_HEADERS,'Content-Disposition':f'attachment; filename="{evidence_id}.txt"'})

    @app.post('/v1/tenants/{tenant}/evidence/{evidence_id}/original')
    async def evidence_original(tenant:OpaqueId,evidence_id:ResourceId,body:OriginalAccess,request:Request,actor:Principal=Depends(principal)):
        data=vault.read(actor,tenant,evidence_id,corr(request),original=True,reason=body.reason)
        return Response(data,media_type='application/octet-stream',headers={**SAFE_HEADERS,'Content-Disposition':f'attachment; filename="{evidence_id}.bin"'})

    @app.post('/v1/tenants/{tenant}/evidence/{evidence_id}/review')
    async def review_evidence(tenant:OpaqueId,evidence_id:ResourceId,body:EvidenceReview,request:Request,actor:Principal=Depends(principal)):
        return vault.manage(actor,tenant,evidence_id,body.expected_revision,'review',corr(request),reason=body.reason)

    @app.post('/v1/tenants/{tenant}/evidence/{evidence_id}/hold')
    async def hold_evidence(tenant:OpaqueId,evidence_id:ResourceId,body:EvidenceHold,request:Request,actor:Principal=Depends(principal)):
        return vault.manage(actor,tenant,evidence_id,body.expected_revision,'hold',corr(request),reason=body.reason,enabled=body.enabled)

    @app.post('/v1/tenants/{tenant}/evidence/{evidence_id}/purge')
    async def purge_evidence(tenant:OpaqueId,evidence_id:ResourceId,body:EvidenceReview,request:Request,actor:Principal=Depends(principal)):
        return vault.manage(actor,tenant,evidence_id,body.expected_revision,'purge',corr(request),reason=body.reason)

    @app.post('/v1/tenants/{tenant}/reviews/proposals',status_code=201)
    async def propose_review(tenant:OpaqueId,body:ReviewProposal,request:Request,actor:Principal=Depends(principal)):
        return reviews.propose(actor,tenant,body,corr(request))

    @app.post('/v1/tenants/{tenant}/reviews/proposals/{proposal_id}/approve')
    async def approve_review(tenant:OpaqueId,proposal_id:ResourceId,body:ReviewApproval,request:Request,actor:Principal=Depends(principal)):
        return reviews.approve(actor,tenant,proposal_id,body,corr(request))

    @app.post('/v1/tenants/{tenant}/reports',status_code=201)
    async def create_report(tenant:OpaqueId,body:ReportRequest,request:Request,actor:Principal=Depends(principal)):
        return reports.create(actor,tenant,body,corr(request))

    @app.get('/v1/tenants/{tenant}/reports/{report_id}')
    async def get_report(tenant:OpaqueId,report_id:ResourceId,request:Request,format:Literal['json','html','csv']='json',actor:Principal=Depends(principal)):
        report=reports.get(actor,tenant,report_id,corr(request))
        if format=='json':return report
        content=reports.render_html(report) if format=='html' else reports.render_csv(report)
        return Response(content,media_type='text/html' if format=='html' else 'text/csv',
                        headers={**SAFE_HEADERS,'Content-Disposition':f'attachment; filename="{report_id}.{format}"'})

    @app.get('/v1/tenants/{tenant}/operations')
    async def operations(tenant:OpaqueId,actor:Principal=Depends(principal)):
        service.authorize(actor,tenant,'jobs.read')
        with service.db.connection(readonly=True) as db:
            states={row['state']:row['n'] for row in db.execute('SELECT state,count(*) n FROM jobs WHERE tenant_id=? GROUP BY state',(tenant,))}
            oldest=db.execute("SELECT min(created_at) FROM jobs WHERE tenant_id=? AND state='pending'",(tenant,)).fetchone()[0]
            n=db.execute('SELECT count(*) FROM job_results WHERE tenant_id=?',(tenant,)).fetchone()[0]
            incomplete=db.execute("SELECT count(*) FROM jobs WHERE tenant_id=? AND state NOT IN ('completed','cancelled')",(tenant,)).fetchone()[0]
        return {'tenant_id':tenant,'job_states':states,'queue_lag_seconds':max(0,(utcnow()-datetime.fromisoformat(oldest)).total_seconds()) if oldest else None,
                'coverage_status':'not_tested' if n==0 else 'incomplete' if incomplete else 'recorded_scope_only',
                'security_guarantee':False,'telemetry':{'sdk_available':service.telemetry.available,'export':service.settings.telemetry_export}}

    @app.get('/metrics')
    async def metrics(request:Request):return metrics_response(request,service)
