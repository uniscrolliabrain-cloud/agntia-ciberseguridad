"""Data has provenance and never supplies control fields. No network transport enabled."""
from datetime import timedelta,datetime
import json
from typing import Annotated
from pydantic import Field,AwareDatetime
from ..contracts import Model,ResourceId,OpaqueId,Hash
from ..auth import require_human
from ..evidence.vault import Vault
from ..errors import reject,not_found
from ..network_policy import pin_target
from ..util import canonical,digest,uid,utcnow

class PackageFact(Model):
    name: Annotated[str,Field(pattern=r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}$')]
    version: Annotated[str,Field(pattern=r'^[0-9][0-9a-zA-Z.+_-]{0,39}$')]
class DocumentFacts(Model):
    packages: list[PackageFact]=Field(default_factory=list,max_length=20)
class FlowCreate(Model):
    evidence_id: ResourceId
    resource_id: ResourceId
class ReleaseProposal(Model):
    destination_ref: OpaqueId
    content_hash: Hash
    expires_at: AwareDatetime

class DataFlows:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.clock=clock
    @staticmethod
    def row(db,tenant,flow_id):
        row=db.execute('SELECT body FROM data_flows WHERE tenant_id=? AND id=?',(tenant,flow_id)).fetchone()
        if not row:not_found()
        return json.loads(row[0])
    def create(self,actor,tenant,body,correlation):
        self.service.authorize(actor,tenant,'evidence.read');self.service.authorize(actor,tenant,'assets.read')
        vault=Vault(self.service);meta=vault.metadata(actor,tenant,body.evidence_id)
        content=vault.read(actor,tenant,body.evidence_id,correlation)
        facts=None
        if meta['media_type']=='application/json' and len(content)<=16000:
            try:facts=DocumentFacts.model_validate_json(content).model_dump(mode='json')
            except ValueError:pass
        record={'id':uid(),'resource_id':body.resource_id,'evidence_id':body.evidence_id,'content_hash':meta['redacted_sha256'],
            'origin':'custodied_evidence','trust':'untrusted_data','classification':'confidential',
            'allowed_audiences':['agntia.local.review'],'facts':facts,'state':'normalized' if facts is not None else 'quarantined',
            'policy_inputs_from_content':False,'created_at':self.clock().isoformat()}
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'evidence.read')
            if db.execute('SELECT count(*) FROM data_flows WHERE tenant_id=?',(tenant,)).fetchone()[0]>=1000:reject('flow_quota','Registro de fuentes lleno',429)
            if not db.execute('SELECT 1 FROM assets WHERE tenant_id=? AND id=?',(tenant,body.resource_id)).fetchone():not_found()
            current=json.loads(db.execute('SELECT body FROM evidence WHERE tenant_id=? AND id=?',(tenant,body.evidence_id)).fetchone()[0])
            if current['state'] in ('deleted','purge_pending') or (not current['legal_hold'] and datetime.fromisoformat(current['expires_at'])<=self.clock()):reject('flow_source_unavailable','Fuente no disponible',410)
            db.execute('INSERT INTO data_flows VALUES(?,?,?,?,?)',(tenant,record['id'],body.resource_id,body.evidence_id,canonical(record)))
            self.service.db.audit(db,tenant,actor.actor_id,'flow.created',record['id'],correlation,{'content_hash':record['content_hash'],'state':record['state']})
        return record
    def project(self,db,tenant,resource_id,flow_ids):
        result=[]
        for flow_id in flow_ids:
            record=self.row(db,tenant,flow_id)
            if record['resource_id']!=resource_id:reject('flow_scope','Fuente fuera de recurso',403)
            source=db.execute('SELECT body FROM evidence WHERE tenant_id=? AND id=?',(tenant,record['evidence_id'])).fetchone()
            if not source:not_found()
            source=json.loads(source[0])
            if source['state'] in ('deleted','purge_pending') or (not source['legal_hold'] and datetime.fromisoformat(source['expires_at'])<=self.clock()):reject('flow_source_unavailable','Fuente fuera de retención',410)
            if source['redacted_sha256']!=record['content_hash']:reject('flow_integrity','Fuente modificada',409)
            if record['state']!='normalized':reject('flow_quarantined','Contenido no normalizado',424)
            result.append(record)
        return result
    def propose_release(self,actor,tenant,flow_id,body,correlation):
        require_human(self.service,actor,tenant,'agents.manage')
        target=self.service.settings.targets.get(body.destination_ref)
        if body.destination_ref not in self.service.settings.approved_egress_refs or not target or target.tenant_id!=tenant:reject('egress_destination','Destino no aprobado en servidor',403)
        if not self.clock()<body.expires_at<=self.clock()+timedelta(minutes=15):reject('release_expiry','Caducidad máxima quince minutos',422)
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'agents.manage');flow=self.row(db,tenant,flow_id)
            if flow['content_hash']!=body.content_hash:reject('conflict','Hash de contenido no coincide',409)
            record={'id':uid(),'flow_id':flow_id,**body.model_dump(mode='json'),'state':'proposed','proposer':actor.actor_id,
                    'origin_preserved':True,'original_classification':flow['classification'],'audience':'agntia.egress.'+body.destination_ref}
            record['proposal_hash']=digest(record)
            db.execute('INSERT INTO flow_releases VALUES(?,?,?,?)',(tenant,record['id'],flow_id,canonical(record)))
            self.service.db.audit(db,tenant,actor.actor_id,'flow.release_proposed',record['id'],correlation,{'proposal_hash':record['proposal_hash']})
        return record
    def approve_release(self,actor,tenant,release_id,proposal_hash,correlation):
        require_human(self.service,actor,tenant,'agents.manage')
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'agents.manage')
            row=db.execute('SELECT body FROM flow_releases WHERE tenant_id=? AND id=?',(tenant,release_id)).fetchone()
            if not row:not_found()
            record=json.loads(row[0])
            if record['state']!='proposed' or record['proposal_hash']!=proposal_hash or datetime.fromisoformat(record['expires_at'])<=self.clock():reject('release_stale','Propuesta no vigente',409)
            if record['proposer']==actor.actor_id:reject('separation_of_duties','Otro humano debe aprobar',403)
            self.project(db,tenant,self.row(db,tenant,record['flow_id'])['resource_id'],[record['flow_id']])
            record.update(state='approved',approved_by=actor.actor_id)
            db.execute('UPDATE flow_releases SET body=? WHERE tenant_id=? AND id=?',(canonical(record),tenant,release_id))
            self.service.db.audit(db,tenant,actor.actor_id,'flow.release_approved',release_id,correlation,{'proposal_hash':proposal_hash})
        return record
    def egress_preflight(self,actor,tenant,release_id,*,resolver=None):
        require_human(self.service,actor,tenant,'agents.manage')
        with self.service.db.connection(readonly=True) as db:
            row=db.execute('SELECT body FROM flow_releases WHERE tenant_id=? AND id=?',(tenant,release_id)).fetchone()
            if not row:not_found()
            release=json.loads(row[0]);flow=self.row(db,tenant,release['flow_id'])
            if release['state']!='approved' or datetime.fromisoformat(release['expires_at'])<=self.clock() or flow['content_hash']!=release['content_hash']:reject('release_stale','Release no vigente',409)
            self.project(db,tenant,flow['resource_id'],[flow['id']])
        target=self.service.settings.targets.get(release['destination_ref'])
        if release['destination_ref'] not in self.service.settings.approved_egress_refs or not target or target.tenant_id!=tenant:reject('egress_destination','Destino revocado',403)
        pin_target(target,self.service.settings,resolver)
        return {'destination_ref':release['destination_ref'],'audience':release['audience'],'content_hash':flow['content_hash'],
                'network_preflight':'passed','transport':'unsupported','bytes_sent':0,'allowed_to_send':False,'original_classification':flow['classification']}
