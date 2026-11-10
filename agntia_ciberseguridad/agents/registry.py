import json
from typing import Literal
from pydantic import Field
from ..auth import require_human
from ..contracts import Model,OpaqueId,ResourceId,Hash
from ..errors import reject,not_found
from ..util import canonical,digest,uid,now

CAPABILITIES={'assets.read','findings.read','jobs.read','notes.propose'}
class Manifest(Model):
    schema_version: Literal[1]=1
    agent_binding: OpaqueId
    version: OpaqueId
    artifact_hash: Hash
    provider: Literal['self_hosted','external_declared']='self_hosted'
    capabilities: list[Literal['assets.read','findings.read','jobs.read','notes.propose']]=Field(min_length=1,max_length=4)
    resource_ids: list[ResourceId]=Field(min_length=1,max_length=20)
    data_classification: Literal['redacted_metadata']='redacted_metadata'
    network: list[OpaqueId]=Field(default_factory=list,max_length=0)
    tool_ids: list[ResourceId]=Field(default_factory=list,max_length=8)
    schema_ref: Literal['agntia.governed-read.v1']='agntia.governed-read.v1'

class Registry:
    def __init__(self,service):self.service=service
    def binding(self,binding_id,tenant):
        current=self.service.auth.current(binding_id)
        setting=next(p for p in self.service.settings.principals if p.id==binding_id)
        if setting.kind!='agent' or tenant not in current.tenants:reject('agent_scope','Principal agéntico fuera de scope',403)
        return current
    def create(self,actor,tenant,body,correlation):
        require_human(self.service,actor,tenant,'agents.manage');self.binding(body.agent_binding,tenant)
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'agents.manage')
            for resource in body.resource_ids:
                if not db.execute('SELECT 1 FROM assets WHERE tenant_id=? AND id=?',(tenant,resource)).fetchone():not_found()
            for tool_id in body.tool_ids:
                from .tools import ToolRegistry
                ToolRegistry.current(db,tenant,tool_id)
            record={**body.model_dump(mode='json'),'id':uid(),'state':'pending_review','revision':0,'created_by':actor.actor_id,'created_at':now()}
            record['manifest_hash']=digest(body.model_dump(mode='json'))
            db.execute('INSERT INTO agent_manifests VALUES(?,?,?,?,?)',(tenant,record['id'],body.agent_binding,0,canonical(record)))
            self.service.db.audit(db,tenant,actor.actor_id,'agent.manifest_proposed',record['id'],correlation,{'manifest_hash':record['manifest_hash']})
        return record
    def approve(self,actor,tenant,manifest_id,expected,correlation):
        require_human(self.service,actor,tenant,'agents.manage')
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'agents.manage');record=self.get_row(db,tenant,manifest_id)
            self.binding(record['agent_binding'],tenant)
            if record['revision']!=expected or record['state']!='pending_review':reject('conflict','Manifest modificado',409)
            if record['created_by']==actor.actor_id:reject('separation_of_duties','Otro humano debe aprobar',403)
            record.update(state='approved',revision=expected+1,reviewed_by=actor.actor_id,reviewed_at=now())
            db.execute('UPDATE agent_manifests SET revision=?,body=? WHERE tenant_id=? AND id=?',(record['revision'],canonical(record),tenant,manifest_id))
            self.service.db.audit(db,tenant,actor.actor_id,'agent.manifest_approved',manifest_id,correlation,{'manifest_hash':record['manifest_hash']})
        return record
    @staticmethod
    def get_row(db,tenant,manifest_id):
        row=db.execute('SELECT body FROM agent_manifests WHERE tenant_id=? AND id=?',(tenant,manifest_id)).fetchone()
        if not row:not_found()
        return json.loads(row['body'])
    def list(self,actor,tenant):
        self.service.authorize(actor,tenant,'agents.read')
        with self.service.db.connection(readonly=True) as db:
            rows=db.execute('SELECT body FROM agent_manifests WHERE tenant_id=?'+(' AND agent_binding=?' if self.service.auth.kind(actor)=='agent' else '')+' ORDER BY id LIMIT 100',(tenant,actor.binding_id) if self.service.auth.kind(actor)=='agent' else (tenant,)).fetchall()
        return {'manifests':[json.loads(r['body']) for r in rows],
                'coverage':'Agents require governed paths within this API; activity outside this service is not observed','general_executor':False}
