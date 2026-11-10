"""Reviewed evidence-scope rights requests and conditional breach preparation, no notifications."""
from datetime import datetime,timedelta
from typing import Literal
import json
from pydantic import AwareDatetime,Field,StrictInt
from .store import Cases
from .legal import Legal,Tri
from ..auth import require_human
from ..contracts import Model,ResourceId,OpaqueId
from ..evidence.vault import Vault
from ..errors import reject,DomainError
from ..util import canonical,digest,utcnow

class EvidenceTarget(Model):
    evidence_id: ResourceId
    expected_revision: StrictInt=Field(ge=0)
class RightsRequest(Model):
    action: Literal['restrict','delete','export_metadata']
    targets: list[EvidenceTarget]=Field(min_length=1,max_length=10)
    legal_basis_ref: OpaqueId
    purpose_ref: OpaqueId
class Breach(Model):
    resource_id: ResourceId
    owner_ref: OpaqueId
    detected_at: AwareDatetime
    awareness_at: AwareDatetime|None=None
    personal_data: Tri='unknown'
    breach_confirmed: Tri='unknown'
    gdpr_role: Literal['unknown','controller','processor','both']='unknown'
    risk: Literal['unknown','unlikely','risk','high']='unknown'
    affected_count: StrictInt|None=Field(default=None,ge=0,le=100000000)
    category_refs: list[OpaqueId]=Field(default_factory=list,max_length=10)

class Privacy:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.clock=clock;self.cases=Cases(service,clock=clock);self.vault=Vault(service,clock=clock)
    def request(self,actor,tenant,body,correlation):
        self.service.authorize(actor,tenant,'privacy.propose');sources=[]
        for target in body.targets:
            meta=self.vault.metadata(actor,tenant,target.evidence_id)
            if meta['revision']!=target.expected_revision:reject('conflict','Revisión de fuente distinta',409)
            sources.append(meta)
        return self.cases.create(actor,tenant,'privacy_request',{**body.model_dump(mode='json'),'source_snapshots':sources,'execution_status':'not_executed','backups_reconciled':False,'whole_subject_coverage':'not_evaluated'},correlation)
    def apply(self,actor,tenant,record_id,correlation):
        require_human(self.service,actor,tenant,'privacy.manage')
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'privacy.manage');record=self.cases.row(db,tenant,record_id,'privacy_request');self.cases.current_review(record)
            if record['state'] in ('restricted','prepared_metadata','awaiting_backup_reconciliation'):return record
            if record['state']!='reviewed':reject('privacy_reconciliation_required','Solicitud no lista o estado incierto',409)
            for source in record['fields']['source_snapshots']:
                current=Vault._row(db,tenant,source['id'])
                if current['revision']!=source['revision']:reject('conflict','Fuente modificada tras revisión',409)
            action=record['fields']['action']
            if action=='restrict':
                for target in record['fields']['targets']:
                    db.execute('INSERT INTO evidence_privacy VALUES(?,?,?,?) ON CONFLICT(tenant_id,evidence_id) DO UPDATE SET restricted=excluded.restricted,body=excluded.body',(tenant,target['evidence_id'],1,canonical({'request_id':record_id,'reviewed_by':actor.actor_id})))
                record['state']='restricted';record['fields']['execution_status']='read_restriction_active'
            elif action=='export_metadata':
                record['fields']['export']=[self.vault.public(Vault._row(db,tenant,t['evidence_id'])) for t in record['fields']['targets']]
                record['state']='prepared_metadata';record['fields']['execution_status']='metadata_only_not_full_sar'
            else:
                blocked=any(s['legal_hold'] or datetime.fromisoformat(s['expires_at'])>self.clock() for s in record['fields']['source_snapshots'])
                record['state']='blocked_retention' if blocked else 'executing'
                record['fields']['execution_status']='retention_or_legal_hold' if blocked else 'purge_started'
            record['revision']+=1;self.cases.save(db,tenant,record)
            self.service.db.audit(db,tenant,actor.actor_id,'privacy.request_applied',record_id,correlation,{'state':record['state'],'action':action})
        if record['state']=='executing':
            try:
                for target in record['fields']['targets']:
                    self.vault.manage(actor,tenant,target['evidence_id'],target['expected_revision'],'purge',correlation,reason='Reviewed evidence-scope erasure '+record_id)
                state='awaiting_backup_reconciliation'
            except Exception:state='reconciliation_required'
            with self.service.db.transaction() as db:
                current=self.cases.row(db,tenant,record_id,'privacy_request');current['state']=state;current['revision']+=1
                current['fields']['execution_status']=state;self.cases.save(db,tenant,current)
                self.service.db.audit(db,tenant,actor.actor_id,'privacy.purge_result',record_id,correlation,{'state':state,'backups_reconciled':False})
            return current
        return record
    def breach(self,actor,tenant,body,correlation):
        self.service.authorize(actor,tenant,'privacy.propose');self.cases.owner(tenant,body.owner_ref)
        with self.service.db.connection(readonly=True) as db:self.service._asset(db,tenant,body.resource_id)
        if body.detected_at>self.clock()+timedelta(minutes=5) or (body.awareness_at and (body.awareness_at<body.detected_at or body.awareness_at>self.clock()+timedelta(minutes=5))):reject('breach_clock','Cronología requiere corrección/revisión',422)
        return self.cases.create(actor,tenant,'breach',{**body.model_dump(mode='json'),'source_bundle_hash':Legal(self.service).bundle_hash,'notification_sent':False},correlation)
    def breach_view(self,actor,tenant,record_id,correlation):
        record=self.cases.get(actor,tenant,record_id,correlation)
        if record['kind']!='breach':reject('breach_scope','Registro no es brecha',422)
        facts=record['fields'];result={'assessment':'human_review_required','authority_due_at':None,'processor_action':None,'data_subject_action':None,'notification_sent':False,'automatic_notification':False}
        try:self.cases.current_review(record);reviewed=True
        except DomainError:reviewed=False
        legal=Legal(self.service,clock=self.clock)
        sources_current=facts['source_bundle_hash']==legal.bundle_hash and self.clock().date().isoformat()<=legal.catalogue['review_valid_until']
        if reviewed and sources_current:
            if facts['personal_data']=='no' or facts['breach_confirmed']=='no':result['assessment']='not_a_confirmed_personal_breach_on_reviewed_facts'
            elif facts['personal_data']=='yes' and facts['breach_confirmed']=='yes' and facts['awareness_at'] and facts['gdpr_role']!='unknown' and facts['risk']!='unknown':
                result['assessment']='conditional_preparation_only'
                if facts['gdpr_role'] in ('processor','both'):result['processor_action']='inform_controller_without_undue_delay'
                if facts['gdpr_role'] in ('controller','both') and facts['risk'] in ('risk','high'):
                    result['authority_due_at']=(datetime.fromisoformat(facts['awareness_at'])+timedelta(hours=72)).isoformat()
                    result['authority_action']='competent_human_must_decide_and_notify_without_undue_delay'
                if facts['gdpr_role'] in ('controller','both') and facts['risk']=='high':result['data_subject_action']='assess_communication_without_undue_delay_and_Article34_exceptions'
        return {**record,'breach_preparation':result,'other_regimes_deadlines':'not_inferred_from_gdpr'}
