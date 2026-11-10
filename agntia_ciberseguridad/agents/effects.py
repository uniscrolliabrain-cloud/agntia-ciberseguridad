"""Human-approved zero-cost local review notes, never a production remediation executor."""
from datetime import datetime,timedelta
import json
import re
from types import SimpleNamespace
from pydantic import Field,StrictInt
from typing import Literal
from .capabilities import Delegations
from .flows import DataFlows
from .policy import ActionPolicy,POLICY_HASH
from ..auth import require_human
from ..contracts import Model,ResourceId,Hash
from ..evidence.redaction import text
from ..errors import reject,not_found
from ..util import canonical,digest,uid,utcnow

class NoteProposal(Model):
    token: str=Field(min_length=50,max_length=12000)
    resource_id: ResourceId
    category: Literal['review_required','remediation_candidate']
    text: str=Field(min_length=5,max_length=500)
    flow_ids: list[ResourceId]=Field(default_factory=list,max_length=5)
    expected_policy_hash: Hash
class NoteApproval(Model):
    proposal_hash: Hash
    expected_revision: StrictInt=Field(ge=0)
class NoteCommit(Model):
    token: str=Field(min_length=50,max_length=12000)
    proposal_hash: Hash

class Effects:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.clock=clock
    @staticmethod
    def row(db,tenant,proposal_id):
        r=db.execute('SELECT body FROM effect_proposals WHERE tenant_id=? AND id=?',(tenant,proposal_id)).fetchone()
        if not r:not_found()
        return json.loads(r[0])
    def propose(self,actor,tenant,body,correlation):
        self.service.authorize(actor,tenant,'agents.read')
        if body.expected_policy_hash!=POLICY_HASH:reject('agent_policy_stale','Política no coincide',409)
        request=SimpleNamespace(token=body.token,capability='notes.propose',resource_id=body.resource_id)
        with self.service.db.transaction() as db:
            if db.execute('SELECT count(*) FROM effect_proposals WHERE tenant_id=?',(tenant,)).fetchone()[0]>=1000:reject('effect_quota','Registro de propuestas lleno',429)
            _,grant=Delegations(self.service,clock=self.clock).checked(db,actor,tenant,request)
            flows=DataFlows(self.service,clock=self.clock).project(db,tenant,body.resource_id,body.flow_ids)
            record={'id':uid(),'resource_id':body.resource_id,'category':body.category,'text':text(body.text),
                'flow_refs':[{'id':f['id'],'hash':f['content_hash'],'classification':f['classification'],'trust':f['trust']} for f in flows],
                'proposer':actor.actor_id,'proposer_binding':actor.binding_id,'grant_issuer':grant['issuer_binding'],
                'grant_id':grant['id'],'grant_hash':digest(body.token),'policy_hash':POLICY_HASH,'policy_epoch':grant['policy_epoch'],
                'expires_at':min(datetime.fromisoformat(grant['expires_at']),self.clock()+timedelta(minutes=5)).isoformat(),
                'state':'proposed','revision':0,'reserved_cents':0,'effect':'local_review_note_only','external_effect':False}
            record['proposal_hash']=digest(record)
            db.execute('INSERT INTO effect_proposals VALUES(?,?,?,?)',(tenant,record['id'],body.resource_id,canonical(record)))
            self.service.db.audit(db,tenant,actor.actor_id,'effect.proposed',record['id'],correlation,{'proposal_hash':record['proposal_hash'],'reserved_cents':0})
        return record
    def approve(self,actor,tenant,proposal_id,body,correlation):
        require_human(self.service,actor,tenant,'agents.manage')
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'agents.manage');record=self.row(db,tenant,proposal_id)
            ActionPolicy(self.service,clock=self.clock).validate(db,tenant,binding_id=record['proposer_binding'],grant_id=record['grant_id'],expected_epoch=record['policy_epoch'])
            if record['state']!='proposed' or record['revision']!=body.expected_revision or record['proposal_hash']!=body.proposal_hash or datetime.fromisoformat(record['expires_at'])<=self.clock():reject('effect_stale','Propuesta modificada o caducada',409)
            if actor.actor_id==record['proposer'] or actor.binding_id==record['grant_issuer']:reject('separation_of_duties','Humano distinto del proponente/emisor debe revisar',403)
            grant_row=db.execute('SELECT * FROM delegations WHERE tenant_id=? AND id=?',(tenant,record['grant_id'])).fetchone()
            if not grant_row:reject('effect_stale','Grant no disponible',409)
            Delegations(self.service,clock=self.clock)._validate_chain(db,tenant,grant_row,json.loads(grant_row['body']))
            DataFlows(self.service,clock=self.clock).project(db,tenant,record['resource_id'],[f['id'] for f in record['flow_refs']])
            record.update(state='approved',revision=1,approved_by=actor.actor_id,approval_binding=actor.binding_id,approval_stamp=digest(actor.__dict__))
            db.execute('UPDATE effect_proposals SET body=? WHERE tenant_id=? AND id=?',(canonical(record),tenant,proposal_id))
            self.service.db.audit(db,tenant,actor.actor_id,'effect.approved',proposal_id,correlation,{'proposal_hash':record['proposal_hash']})
        return record
    def commit(self,actor,tenant,proposal_id,body,key,correlation):
        self.service.authorize(actor,tenant,'agents.read')
        if not isinstance(key,str) or not re.fullmatch('[a-zA-Z0-9_-]{8,80}',key):reject('idempotency_required','Clave idempotente requerida',422)
        request_hash=digest({'proposal_id':proposal_id,'proposal_hash':body.proposal_hash,'grant_hash':digest(body.token),'actor':actor.binding_id})
        with self.service.db.transaction() as db:
            record=self.row(db,tenant,proposal_id)
            if actor.binding_id!=record['proposer_binding']:reject('effect_scope','Propuesta de otro principal',403)
            old=db.execute('SELECT * FROM effect_operations WHERE tenant_id=? AND key=?',(tenant,key)).fetchone()
            if old:
                if old['request_hash']!=request_hash:reject('idempotency_conflict','Clave usada para otra petición',409)
                return {**json.loads(old['result']),'replayed':True,'historical_receipt':True}
            if db.execute('SELECT 1 FROM effect_operations WHERE tenant_id=? AND proposal_id=?',(tenant,proposal_id)).fetchone():reject('idempotency_conflict','Propuesta ya confirmada con otra clave',409)
            if record['state']!='approved' or record['proposal_hash']!=body.proposal_hash or digest(body.token)!=record['grant_hash'] or datetime.fromisoformat(record['expires_at'])<=self.clock():reject('effect_stale','Aprobación no vigente',409)
            approver=self.service.auth.current(record['approval_binding'])
            self.service.auth.authorize(approver,tenant,'agents.manage')
            if self.service.auth.kind(approver)!='human' or digest(approver.__dict__)!=record['approval_stamp']:reject('effect_stale','Revisor modificado',403)
            request=SimpleNamespace(token=body.token,capability='notes.propose',resource_id=record['resource_id'])
            _,grant=Delegations(self.service,clock=self.clock).checked(db,actor,tenant,request)
            ActionPolicy(self.service,clock=self.clock).validate(db,tenant,binding_id=actor.binding_id,grant_id=grant['id'],expected_epoch=record['policy_epoch'])
            DataFlows(self.service,clock=self.clock).project(db,tenant,record['resource_id'],[f['id'] for f in record['flow_refs']])
            result={'note_id':uid(),'proposal_id':proposal_id,'state':'committed','reserved_cents':0,'effect':'local_review_note_only','external_effect':False}
            db.execute('INSERT INTO effect_operations VALUES(?,?,?,?,?,?,?)',(tenant,key,proposal_id,request_hash,'reserved',canonical(result),0))
            note={**record,'id':result['note_id'],'state':'review_note','committed_at':self.clock().isoformat()}
            db.execute('INSERT INTO local_notes VALUES(?,?,?,?)',(tenant,result['note_id'],proposal_id,canonical(note)))
            db.execute("UPDATE effect_operations SET state='committed' WHERE tenant_id=? AND key=?",(tenant,key))
            record.update(state='committed',revision=2)
            db.execute('UPDATE effect_proposals SET body=? WHERE tenant_id=? AND id=?',(canonical(record),tenant,proposal_id))
            db.execute('UPDATE delegations SET used_at=? WHERE tenant_id=? AND id=?',(self.clock().isoformat(),tenant,grant['id']))
            self.service.db.audit(db,tenant,actor.actor_id,'effect.committed',proposal_id,correlation,{'note_id':result['note_id'],'proposal_hash':body.proposal_hash,'reserved_cents':0})
        return {**result,'replayed':False}
