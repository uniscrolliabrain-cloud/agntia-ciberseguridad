"""Separate applicability candidates per regime; facts and dates are never a compliance seal."""
from datetime import date,datetime
import json
from pathlib import Path
from typing import Literal
from pydantic import Field
from .store import Cases
from ..contracts import Model,OpaqueId,ResourceId,Hash
from ..errors import reject,DomainError
from ..evidence.vault import Vault
from ..util import digest,utcnow

Tri=Literal['unknown','yes','no']
class Provider(Model):
    provider_ref: OpaqueId
    region: Literal['EU','non_EU','unknown']='unknown'
    subprocessor: Tri='unknown'
    dpa_ref: OpaqueId|None=None
    transfer_safeguard_ref: OpaqueId|None=None
class Inventory(Model):
    resource_id: ResourceId
    purpose_refs: list[OpaqueId]=Field(default_factory=list,max_length=10)
    sector_ref: OpaqueId='unknown'
    owner_ref: OpaqueId
    eu_scope: Tri='unknown'
    personal_data: Tri='unknown'
    ai_role: Literal['unknown','provider','deployer','both','neither']='unknown'
    gdpr_role: Literal['unknown','controller','processor','both','neither']='unknown'
    model_refs: list[OpaqueId]=Field(default_factory=list,max_length=16)
    system_refs: list[OpaqueId]=Field(default_factory=list,max_length=16)
    digital_product: Tri='unknown'
    critical_ict_designation: Tri='unknown'
    cra_role: Literal['unknown','manufacturer','distributor','importer','neither']='unknown'
    ai_risk: Literal['unknown','annex_i_declared','annex_iii_declared','other_declared']='unknown'
    nis2_in_scope: Tri='unknown'
    dora_financial_entity: Tri='unknown'
    dora_ict_provider: Tri='unknown'
    ens_public_scope: Tri='unknown'
    legal_basis_ref: OpaqueId|None=None
    retention_days: int|None=Field(default=None,ge=1,le=3650)
    data_categories: list[Literal['technical_metadata','personal','sensitive','financial']]=Field(default_factory=list,max_length=4)
    providers: list[Provider]=Field(default_factory=list,max_length=16)
class DateClaim(Model):
    milestone: Literal['ai_general','ai_high_risk_annex_iii','ai_high_risk_annex_i','cra_reporting','cra_general','dora_general']
    claimed_date: date
    evidence_ref: OpaqueId
class Assessment(Model):
    inventory_id: ResourceId
    source_bundle_hash: Hash
    date_claims: list[DateClaim]=Field(default_factory=list,max_length=10)
class Control(Model):
    assessment_id: ResourceId
    regime: Literal['ai_act','gdpr','cra','nis2','dora','ens']
    control_ref: Literal['access_control','evidence_integrity','incident_response','retention_policy','ai_inventory']
    owner_ref: OpaqueId
    evidence_ids: list[ResourceId]=Field(default_factory=list,max_length=10)

class Legal:
    def __init__(self,service,*,catalogue=None,clock=utcnow):
        self.service=service;self.clock=clock;self.cases=Cases(service,clock=clock)
        self.catalogue=catalogue or json.loads(Path(__file__).with_name('legal_sources.json').read_text(encoding="utf-8"));self.bundle_hash=digest(self.catalogue)
    def sources(self,actor,tenant):
        self.service.authorize(actor,tenant,'governance.read');return {**self.catalogue,'source_bundle_hash':self.bundle_hash,'legal_certification':False}
    def inventory(self,actor,tenant,body,correlation):
        self.service.authorize(actor,tenant,'governance.propose');self.cases.owner(tenant,body.owner_ref)
        with self.service.db.connection(readonly=True) as db:self.service._asset(db,tenant,body.resource_id)
        return self.cases.create(actor,tenant,'inventory',body.model_dump(mode='json'),correlation)
    def assess(self,actor,tenant,body,correlation):
        inventory=self.cases.get(actor,tenant,body.inventory_id,correlation)
        if inventory['kind']!='inventory':reject('assessment_source','Se requiere inventario',422)
        if body.source_bundle_hash!=self.bundle_hash:reject('legal_source_stale','Catálogo no vigente',409)
        facts=inventory['fields'];matrix={};missing=not facts['purpose_refs'] or facts['eu_scope']=='unknown'
        def status(value):return 'insufficient_information' if value=='unknown' else 'candidate_applicable' if value=='yes' else 'candidate_not_applicable'
        if missing:matrix={r:'insufficient_information' for r in ('ai_act','gdpr','cra','nis2','dora','ens')}
        else:
            matrix['ai_act']=status('unknown' if facts['ai_role']=='unknown' else 'no' if facts['eu_scope']=='no' or facts['ai_role']=='neither' else 'yes')
            matrix['gdpr']=status('no' if facts['personal_data']=='no' else 'unknown' if facts['personal_data']=='unknown' or facts['gdpr_role'] in ('unknown','neither') else 'yes')
            matrix['cra']=status('no' if facts['cra_role']=='neither' or facts['eu_scope']=='no' or facts['digital_product']=='no' else 'unknown' if facts['cra_role']=='unknown' or facts['digital_product']=='unknown' else 'yes')
            matrix['nis2']=status(facts['nis2_in_scope'])
            matrix['dora']=status('yes' if facts['dora_financial_entity']=='yes' or (facts['dora_ict_provider']=='yes' and facts['critical_ict_designation']=='yes') else 'no' if facts['dora_financial_entity']==facts['dora_ict_provider']=='no' else 'unknown')
            matrix['ens']=status(facts['ens_public_scope'])
        conflicts=[claim.milestone for claim in body.date_claims if claim.claimed_date.isoformat()!=self.catalogue['milestones'][claim.milestone]['date']]
        stale=self.clock().date()>date.fromisoformat(self.catalogue['review_valid_until'])
        result={'inventory_id':inventory['id'],'inventory_hash':digest(inventory),'source_bundle_hash':self.bundle_hash,'source_version':self.catalogue['version'],
                'matrix':matrix,'source_conflicts':conflicts,'source_freshness':'expired_review_window' if stale else 'observed_on_'+self.catalogue['observed_on'],
                'preparation_status':'source_conflict' if conflicts else 'insufficient_information' if missing or stale or 'insufficient_information' in matrix.values() else 'human_applicability_review_required',
                'milestones':self.catalogue['milestones'],'deadline_automation_enabled':False,'compliance_verdict':'not_provided','nis2_national_transposition':'not_verified',
                'limitations':['Roles and scope are declared, not inferred.','A candidate_not_applicable is not a legal exemption.','Official text and competent review govern; preparation only.']}
        return self.cases.create(actor,tenant,'assessment',result,correlation)
    def view(self,actor,tenant,record_id,correlation):
        record=self.cases.get(actor,tenant,record_id,correlation)
        if record['kind'] not in ('assessment','control','inventory'):reject('assessment_source','Registro no legal',422)
        stale=False
        if record['kind']=='assessment':
            with self.service.db.connection(readonly=True) as db:source=self.cases.row(db,tenant,record['fields']['inventory_id'],'inventory')
            stale=record['fields']['source_bundle_hash']!=self.bundle_hash or digest(source)!=record['fields']['inventory_hash'] or self.clock().date()>date.fromisoformat(self.catalogue['review_valid_until'])
        if record['review']:
            try:self.cases.current_review(record)
            except DomainError:stale=True
        return {**record,'effective_review_state':'stale_sources' if stale else record['state'],'legal_certification':False}
    def control(self,actor,tenant,body,correlation):
        assessment=self.cases.get(actor,tenant,body.assessment_id,correlation)
        if assessment['kind']!='assessment':reject('control_scope','Se requiere assessment',422)
        self.cases.owner(tenant,body.owner_ref);states=[]
        for evidence_id in body.evidence_ids:states.append(Vault(self.service).metadata(actor,tenant,evidence_id)['state'])
        status='evidence_pending' if not states else 'evidence_reviewed' if all(s=='reviewed' for s in states) else 'evidence_present_unreviewed'
        return self.cases.create(actor,tenant,'control',{**body.model_dump(mode='json'),'evidence_state_at_capture':status,'control_effectiveness':'not_certified','source_bundle_hash':self.bundle_hash},correlation)
