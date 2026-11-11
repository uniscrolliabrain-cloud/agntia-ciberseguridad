"""Reviewed cases and explicit lab-only revocation; alert receipt is not containment."""
from datetime import datetime
from uuid import uuid4
import json
from typing import Literal
from pydantic import Field,StrictInt
from .store import Cases
from ..auth import require_human
from ..contracts import Model,ResourceId,Hash,OpaqueId,GrantRevocation
from ..errors import reject,DomainError,not_found
from ..util import canonical,digest

class Incident(Model):
    resource_id: ResourceId
    owner_ref: OpaqueId
    severity: Literal['unknown','low','medium','high','critical']='unknown'
    event_sequences: list[StrictInt]=Field(default_factory=list,max_length=20)
    finding_ids: list[Hash]=Field(default_factory=list,max_length=20)
    evidence_ids: list[ResourceId]=Field(min_length=1,max_length=20)
    case_key: OpaqueId
class IncidentTransition(Model):
    expected_revision: StrictInt=Field(ge=0)
    target_state: Literal['triaged','contained','recovering','resolved']
    reason_ref: OpaqueId
    evidence_id: ResourceId
    containment_id: ResourceId|None=None
    resolution: Literal['unknown','false_positive','recovered']='unknown'
class Containment(Model):
    incident_id: ResourceId
    grant_id: ResourceId
    expected_grant_revision: StrictInt=Field(ge=0)
    action: Literal['lab_revoke_work_grant']='lab_revoke_work_grant'

class Incidents:
    def __init__(self,service,*,clock=None):self.service=service;self.cases=Cases(service,**({'clock':clock} if clock else {}))
    def create(self,actor,tenant,body,correlation):
        self.service.authorize(actor,tenant,'governance.propose');self.cases.owner(tenant,body.owner_ref)
        with self.service.db.connection(readonly=True) as db:
            asset=self.service._asset(db,tenant,body.resource_id);sources=[]
            for sequence in body.event_sequences:
                row=db.execute('SELECT body FROM passive_events WHERE tenant_id=? AND sequence=?',(tenant,sequence)).fetchone()
                if not row:not_found()
                event=json.loads(row[0])
                if event['target_ref']!=asset['target_ref']:reject('incident_scope','Evento de otro activo',403)
                sources.append({'kind':'event','sequence':sequence,'hash':digest(event)})
            for finding_id in body.finding_ids:
                row=db.execute('SELECT body FROM finding_current WHERE tenant_id=? AND id=?',(tenant,finding_id)).fetchone()
                if not row:not_found()
                finding=json.loads(row[0])
                if finding['asset_id']!=body.resource_id:reject('incident_scope','Finding de otro activo',403)
                sources.append({'kind':'finding','id':finding_id,'hash':digest(finding)})
            for evidence_id in body.evidence_ids:
                row=db.execute('SELECT body FROM evidence WHERE tenant_id=? AND id=?',(tenant,evidence_id)).fetchone()
                if not row:not_found()
                sources.append({'kind':'evidence','id':evidence_id,'hash':digest(json.loads(row[0]))})
        return self.cases.create(actor,tenant,'incident',{**body.model_dump(mode='json'),'source_refs':sources,'workflow_state':'detected','confidence':'unverified_observations','regulatory_notification':'not_evaluated','coverage':'pilot_no_24x7_response'},correlation,key=body.case_key)
    def transition(self,actor,tenant,record_id,body,correlation):
        require_human(self.service,actor,tenant,'governance.review')
        from ..evidence.vault import Vault
        metadata=Vault(self.service).metadata(actor,tenant,body.evidence_id)
        if metadata['state']!='reviewed':reject('evidence_unreviewed','Revisión requiere evidencia',422)
        Vault(self.service).read(actor,tenant,body.evidence_id,correlation)
        allowed={'detected':{'triaged'},'triaged':{'contained','resolved'},'contained':{'recovering'},'recovering':{'resolved'}}
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'governance.review');record=self.cases.row(db,tenant,record_id,'incident')
            if record['revision']!=body.expected_revision or body.target_state not in allowed.get(record['fields']['workflow_state'],set()):reject('conflict','Transición/revisión no permitida',409)
            if body.target_state=='contained':
                containment=self.cases.row(db,tenant,body.containment_id,'containment') if body.containment_id else None
                if not containment or containment['state']!='executed_lab' or containment['fields']['incident_id']!=record_id:reject('containment_required','Se requiere contención de laboratorio verificada',422)
            if body.target_state=='resolved' and record['fields']['workflow_state']=='triaged' and body.resolution!='false_positive':reject('recovery_required','Resolver requiere recuperación o falso positivo revisado',422)
            record['fields'].update(workflow_state=body.target_state,resolution=body.resolution,last_transition={'by':actor.actor_id,'at':self.cases.clock().isoformat(),'reason_ref':body.reason_ref,'evidence_id':body.evidence_id})
            record['revision']+=1;self.cases.save(db,tenant,record)
            self.service.db.audit(db,tenant,actor.actor_id,'incident.transition',record_id,correlation,{'state':body.target_state,'notification_sent':False})
        return record
    def propose_containment(self,actor,tenant,body,correlation):
        incident=self.cases.get(actor,tenant,body.incident_id,correlation)
        if incident['kind']!='incident':reject('incident_scope','Caso no es incidente',422)
        with self.service.db.connection(readonly=True) as db:
            grant=self.service._grant(db,tenant,body.grant_id)
            if grant['asset_id']!=incident['fields']['resource_id'] or grant['revision']!=body.expected_grant_revision or grant['state']!='approved':reject('containment_scope','Autorización fuera de origen/revisión',409)
        return self.cases.create(actor,tenant,'containment',{**body.model_dump(mode='json'),'resource_id':grant['asset_id'],'before_hash':digest(grant),'expected_state':'revoked','risk':'lab_work_authorization_only','cost_cents':0,'rollback':'reissue_new_grant_with_new_human_approval','provider_effect':'none'},correlation)
    def _finish(self,actor,tenant,record_id,state,correlation):
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'governance.review')
            record=self.cases.row(db,tenant,record_id,'containment');record['state']=state;record['revision']+=1;self.cases.save(db,tenant,record)
            self.service.db.audit(db,tenant,actor.actor_id,'containment.result',record_id,correlation,{'state':state,'production_effect':False})
        return record
    def execute(self,actor,tenant,record_id,correlation):
        require_human(self.service,actor,tenant,'governance.review')
        if not self.service.settings.lab_mode:reject('lab_only','Contención ejecutable solo en laboratorio',424)
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'governance.review');record=self.cases.row(db,tenant,record_id,'containment');self.cases.current_review(record)
            if record['state']=='executed_lab':return record
            if record['state']!='reviewed':reject('reconciliation_required','Estado no ejecutable; conciliar antes de repetir',409)
            grant=self.service._grant(db,tenant,record['fields']['grant_id'])
            if digest(grant)!=record['fields']['before_hash']:reject('conflict','Grant modificado tras aprobación',409)
            record['fields']['execution_correlation_id']=str(uuid4());record['state']='executing';record['revision']+=1;self.cases.save(db,tenant,record)
            self.service.db.audit(db,tenant,actor.actor_id,'containment.started',record_id,correlation,{'grant_id':grant['id']})
        try:
            self.service.revoke_grant(actor,tenant,grant['id'],GrantRevocation(expected_revision=grant['revision'],notes='Reviewed lab containment '+record_id),record['fields']['execution_correlation_id'])
        except Exception:return self._finish(actor,tenant,record_id,'reconciliation_required',correlation)
        return self._finish(actor,tenant,record_id,'executed_lab',correlation)
    def reconcile(self,actor,tenant,record_id,correlation):
        require_human(self.service,actor,tenant,'governance.review')
        with self.service.db.connection(readonly=True) as db:
            record=self.cases.row(db,tenant,record_id,'containment')
            if record['state'] not in ('executing','reconciliation_required'):reject('conflict','No requiere conciliación',409)
            grant=self.service._grant(db,tenant,record['fields']['grant_id'])
            proof=db.execute("SELECT 1 FROM audit WHERE tenant_id=? AND json_extract(body,'$.action')='grant.revoked' AND json_extract(body,'$.object_id')=? AND json_extract(body,'$.correlation_id')=?",(tenant,grant['id'],record['fields']['execution_correlation_id'])).fetchone()
            if not self.service.db.verify_audit(db,tenant)['valid']:reject('audit_integrity','Auditoría no íntegra',409)
            state='executed_lab' if grant['state']=='revoked' and proof else 'reconciliation_required'
        return self._finish(actor,tenant,record_id,state,correlation)
