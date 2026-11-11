"""Bounded pilot workspace. Review only uses existing two-human business operation."""
from datetime import datetime
import json
from fastapi import Depends, Request
from .contracts import OpaqueId, ResourceId
from .errors import not_found
from .governance.privacy_guard import ensure_readable
from .telemetry.views import Views
from .util import utcnow

class Workspace:
    def __init__(self,service):self.service=service
    def view(self,actor,tenant):
        data=Views(self.service).dashboard(actor,tenant)
        assets=self.service.list_assets(actor,tenant,20)['items']
        with self.service.db.connection(readonly=True) as db:
            rows=db.execute('SELECT body FROM review_proposals WHERE tenant_id=? ORDER BY rowid DESC LIMIT 20',(tenant,)).fetchall()
        proposals=[]
        for row in rows:
            p=json.loads(row['body'])
            proposals.append({'id':p['id'],'finding_id':p['finding_id'],'revision':p['revision'],'state':p['state'],
                'action':p['payload']['action'],'proposal_hash':p['proposal_hash'],'approval_expires_at':p['approval_expires_at']})
        return {**data,'assets':assets,'review_proposals':proposals,'human_review_required':True,
            'product_state':'synthetic_pilot_not_production','policy':{'customer_execution_enabled':False,'agent_policy_configured':bool(self.service.settings.agent_policy_hash)}}
    def proposal(self,actor,tenant,pid):
        self.service.authorize(actor,tenant,'findings.read')
        with self.service.db.connection(readonly=True) as db:
            row=db.execute('SELECT body FROM review_proposals WHERE tenant_id=? AND id=?',(tenant,pid)).fetchone()
            if not row:not_found()
            p=json.loads(row['body'])
            for eid in p['payload']['evidence_ids']:ensure_readable(db,tenant,eid,utcnow())
        return {'id':p['id'],'finding_id':p['finding_id'],'revision':p['revision'],'state':p['state'],
            'proposal_hash':p['proposal_hash'],'approval_expires_at':p['approval_expires_at'],
            'expired':datetime.fromisoformat(p['approval_expires_at'])<=utcnow(),
            'action':p['payload']['action'],'expected_finding_revision':p['payload']['expected_finding_revision'],
            'reason':p['payload']['reason'],'evidence_ids':p['payload']['evidence_ids'],
            'destination':'local_finding_state','external_action':False,
            'impact':'Cambiar interpretación del hallazgo; no repara ni despliega software.'}

def register_workspace(app,service,principal):
    workspace=Workspace(service)
    @app.get('/v1/tenants/{tenant}/workspace')
    async def view(tenant:OpaqueId,actor=Depends(principal)):return workspace.view(actor,tenant)
    @app.get('/v1/tenants/{tenant}/reviews/proposals/{proposal_id}')
    async def proposal(tenant:OpaqueId,proposal_id:ResourceId,actor=Depends(principal)):return workspace.proposal(actor,tenant,proposal_id)
