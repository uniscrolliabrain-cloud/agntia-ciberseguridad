"""Hash-bound, separately approved human decisions; tool output cannot approve itself."""
from datetime import datetime,timedelta
import json
from typing import Annotated,Literal
from pydantic import Field,StrictInt,model_validator
from .auth import require_human
from .contracts import Model,Hash,ResourceId,OpaqueId,Revision
from .evidence.vault import Vault
from .evidence.redaction import text
from .errors import reject,not_found
from .util import canonical,digest,uid,utcnow,now

class ReviewProposal(Model):
    finding_id: Hash
    expected_finding_revision: Annotated[StrictInt,Field(ge=0)]
    action: Literal['confirm','false_positive','accept_risk','suppress','mark_remediated','verify_fixed','set_context']
    reason: str=Field(min_length=5,max_length=1000)
    evidence_ids: list[ResourceId]=Field(min_length=1,max_length=20)
    expires_at: str|None=Field(default=None,max_length=40)
    retest_job_id: ResourceId|None=None
    owner_ref: OpaqueId|None=None
    due_at: str|None=Field(default=None,max_length=40)
    exposure: Literal['unknown','internal','public']='unknown'
    sensitivity: Literal['unknown','ordinary','sensitive']='unknown'

    @model_validator(mode='after')
    def dates(self):
        for value in (self.expires_at,self.due_at):
            if value and datetime.fromisoformat(value).tzinfo is None:raise ValueError('Timezone required')
        return self

class ReviewApproval(Revision):
    proposal_hash: Hash

class Reviews:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.db=service.db;self.clock=clock;self.vault=Vault(service,clock=clock)
    @staticmethod
    def _finding(db,tenant,finding_id):
        row=db.execute('SELECT body FROM finding_current WHERE tenant_id=? AND id=?',(tenant,finding_id)).fetchone()
        if not row:not_found()
        return json.loads(row['body'])
    def _evidence(self,actor,tenant,ids):
        for evidence_id in ids:
            metadata=self.vault.metadata(actor,tenant,evidence_id)
            if metadata['state']!='reviewed':reject('evidence_unreviewed','Se requiere evidencia revisada',422)
            self.vault.read(actor,tenant,evidence_id,'review-evidence')
    def propose(self,actor,tenant,body,correlation):
        self.service.authorize(actor,tenant,'reviews.propose');self._evidence(actor,tenant,body.evidence_ids)
        instant=self.clock()
        if body.action in ('accept_risk','suppress','false_positive') and not body.expires_at:reject('expiry_required','Excepción requiere caducidad',422)
        if body.expires_at and not instant<datetime.fromisoformat(body.expires_at)<=instant+timedelta(days=30):reject('expiry','Ventana de excepción inválida',422)
        if body.due_at and not instant<datetime.fromisoformat(body.due_at)<=instant+timedelta(days=90):reject('deadline','Plazo inválido',422)
        if body.owner_ref and not any(p.actor_id==body.owner_ref and tenant in p.tenants and p.enabled for p in self.service.settings.principals):not_found()
        with self.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'reviews.propose');finding=self._finding(db,tenant,body.finding_id)
            if finding.get('revision',0)!=body.expected_finding_revision:reject('conflict','Finding modificado',409)
            payload={**body.model_dump(mode='json'),'reason':text(body.reason)}
            proposal={'schema_version':1,'id':uid(),'tenant_id':tenant,'finding_id':body.finding_id,
                'created_by':actor.actor_id,'created_at':instant.isoformat(),'approval_expires_at':(instant+timedelta(minutes=15)).isoformat(),
                'source_hash':digest(finding),'payload':payload,'revision':0,'state':'proposed'}
            proposal['proposal_hash']=digest(proposal)
            db.execute('INSERT INTO review_proposals VALUES(?,?,?,?,?)',(tenant,proposal['id'],body.finding_id,canonical(proposal),0))
            self.db.audit(db,tenant,actor.actor_id,'review.proposed',proposal['id'],correlation,{'proposal_id':proposal['id'],'proposal_hash':proposal['proposal_hash']})
        return proposal
    def approve(self,actor,tenant,proposal_id,body,correlation):
        with self.service.telemetry.span('review.approve',component='review',correlation_id=correlation):
            return self._approve(actor,tenant,proposal_id,body,correlation)

    def _approve(self,actor,tenant,proposal_id,body,correlation):
        require_human(self.service,actor,tenant,'reviews.approve')
        with self.db.connection(readonly=True) as db:
            row=db.execute('SELECT body FROM review_proposals WHERE tenant_id=? AND id=?',(tenant,proposal_id)).fetchone()
            if not row:not_found()
            proposal=json.loads(row['body'])
        self._evidence(actor,tenant,proposal['payload']['evidence_ids'])
        with self.db.transaction() as db:
            require_human(self.service,actor,tenant,'reviews.approve')
            row=db.execute('SELECT body FROM review_proposals WHERE tenant_id=? AND id=?',(tenant,proposal_id)).fetchone();current=json.loads(row['body'])
            if current['revision']!=body.expected_revision or current['state']!='proposed' or current['proposal_hash']!=body.proposal_hash:reject('conflict','Propuesta modificada',409)
            original={k:v for k,v in current.items() if k!='proposal_hash'}
            if digest(original)!=body.proposal_hash:reject('conflict','Hash de propuesta no coincide',409)
            if actor.actor_id==current['created_by']:reject('separation_of_duties','Otro humano debe aprobar',403)
            if datetime.fromisoformat(current['approval_expires_at'])<=self.clock():reject('approval_expired','Propuesta caducada',409)
            payload=current['payload'];finding=self._finding(db,tenant,current['finding_id'])
            if digest(finding)!=current['source_hash']:reject('conflict','La evidencia del finding cambió',409)
            job=db.execute('SELECT actor_id FROM jobs WHERE tenant_id=? AND id=?',(tenant,finding['last_job_id'])).fetchone()
            if job and job['actor_id']==actor.actor_id:reject('separation_of_duties','El ejecutor no revisa su propio hallazgo',403)
            if payload['expires_at'] and datetime.fromisoformat(payload['expires_at'])<=self.clock():reject('expiry','Excepción ya caducada',409)
            action=payload['action']
            if action=='verify_fixed':self._verify_retest(db,tenant,finding,payload['retest_job_id'])
            mapping={'confirm':'confirmed','false_positive':'false_positive','accept_risk':'accepted_risk','suppress':'suppressed','mark_remediated':'remediated','verify_fixed':'verified_fixed'}
            if action=='set_context':finding['context']={'exposure':payload['exposure'],'sensitivity':payload['sensitivity'],'source':'human_declared','evidence_ids':payload['evidence_ids']}
            else:finding['state']=mapping[action]
            if action in ('false_positive','accept_risk','suppress'):finding['exception']={'expires_at':payload['expires_at'],'evidence_ids':payload['evidence_ids'],'proposal_id':proposal_id}
            elif action in ('confirm','mark_remediated','verify_fixed'):finding['exception']=None
            if payload['owner_ref']:finding['owner_ref']=payload['owner_ref']
            if payload['due_at']:finding['due_at']=payload['due_at']
            finding.update(revision=finding.get('revision',0)+1,reviewed_at=self.clock().isoformat(),reviewed_by=actor.actor_id)
            decision_id=uid();finding['last_decision_id']=decision_id
            decision={'id':decision_id,'finding_id':finding['id'],'proposal_id':proposal_id,'action':action,'reviewer_id':actor.actor_id,
                'at':finding['reviewed_at'],'proposal_hash':body.proposal_hash,'evidence_ids':payload['evidence_ids'],'finding_hash':digest(finding)}
            db.execute('INSERT INTO review_decisions VALUES(?,?,?,?,?,?)',(tenant,decision['id'],proposal_id,finding['id'],canonical(decision),digest(decision)))
            current.update(state='approved',revision=1,decision_id=decision['id'])
            db.execute('UPDATE review_proposals SET body=?,revision=1 WHERE tenant_id=? AND id=?',(canonical(current),tenant,proposal_id))
            db.execute('UPDATE finding_current SET body=? WHERE tenant_id=? AND id=?',(canonical(finding),tenant,finding['id']))
            self.db.audit(db,tenant,actor.actor_id,'review.approved',decision['id'],correlation,{'proposal_id':proposal_id,'finding_id':finding['id'],'action':action,'finding_hash':digest(finding)})
        return decision
    @staticmethod
    def _verify_retest(db,tenant,finding,job_id):
        if finding['state']!='remediated' or not job_id:reject('retest_required','Se requiere remediación y retest nuevo',422)
        row=db.execute('SELECT j.*,r.body AS result_body,r.content_hash AS result_content_hash FROM jobs j JOIN job_results r ON r.tenant_id=j.tenant_id AND r.job_id=j.id WHERE j.tenant_id=? AND j.id=?',(tenant,job_id)).fetchone()
        if not row or row['state']!='completed' or row['asset_id']!=finding['asset_id'] or row['tool']!=finding['tool'] or row['snapshot_id']==finding['last_snapshot_id']:reject('retest_required','Retest fuera de ámbito o incompleto',422)
        result=json.loads(row['result_body'])
        if digest(result)!=row['result_content_hash'] or row['result_hash']!=row['result_content_hash']:reject('retest_integrity','Retest alterado',409)
        if result.get('status') not in ('no_findings','findings') or result.get('snapshot_coverage')!='captured_local_files' or datetime.fromisoformat(row['created_at'])<datetime.fromisoformat(finding['reviewed_at']):reject('retest_required','Retest no demuestra cobertura posterior',422)
        observation=db.execute('SELECT body,content_hash FROM finding_observations WHERE tenant_id=? AND finding_id=? ORDER BY rowid DESC LIMIT 1',(tenant,finding['id'])).fetchone()
        if not observation or digest(json.loads(observation['body']))!=observation['content_hash'] or json.loads(observation['body'])['policy_hash']!=row['policy_hash']:reject('retest_policy','Política de retest diferente',422)
        for item in result.get('findings',[]):
            if (item.get('rule_id') or item.get('advisory_id'))==finding['rule_id'] and item.get('path')==finding['path']:reject('retest_present','La misma regla sigue reportada',422)
