"""Scoped, versioned records with separate human review and append-only history."""
from datetime import timedelta,datetime
import json
from pydantic import Field,StrictInt
from ..contracts import Model,OpaqueId,ResourceId,Hash
from ..auth import require_human
from ..evidence.vault import Vault
from ..errors import reject,not_found
from ..util import canonical,digest,uid,utcnow

SENSITIVE={'privacy_request','breach'}
KINDS={'inventory','assessment','control','privacy_request','breach','fraud','incident','containment','remediation'}
class CaseReview(Model):
    expected_revision: StrictInt=Field(ge=0)
    record_hash: Hash
    evidence_ids: list[ResourceId]=Field(min_length=1,max_length=10)
    competence_ref: OpaqueId

class Cases:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.db=service.db;self.clock=clock
    @staticmethod
    def row(db,tenant,record_id,kind=None):
        row=db.execute('SELECT body FROM governance_records WHERE tenant_id=? AND id=?',(tenant,record_id)).fetchone()
        if not row:not_found()
        body=json.loads(row[0])
        if kind and body['kind']!=kind:not_found()
        return body
    def _read_authorize(self,actor,tenant,record):
        if record['kind'] in SENSITIVE and actor.role.value not in ('owner','reviewer'):
            self.service.authorize(actor,tenant,'privacy.propose')
            if actor.actor_id not in (record['created_by'],record['fields'].get('owner_ref')):reject('privacy_need_to_know','Acceso no asignado',403)
        else:self.service.authorize(actor,tenant,'privacy.read' if record['kind'] in SENSITIVE else 'governance.read')
    def save(self,db,tenant,record):
        db.execute('UPDATE governance_records SET revision=?,body=? WHERE tenant_id=? AND id=?',(record['revision'],canonical(record),tenant,record['id']))
        db.execute('INSERT INTO governance_history VALUES(?,?,?,?)',(tenant,record['id'],record['revision'],canonical(record)))
    def create(self,actor,tenant,kind,fields,correlation,*,key=None):
        if kind not in KINDS:reject('unsupported','Tipo no permitido',422)
        capability='privacy.propose' if kind in SENSITIVE else 'governance.propose'
        self.service.authorize(actor,tenant,capability)
        request_hash=digest(fields)
        with self.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,capability)
            if key:
                old=db.execute('SELECT * FROM governance_keys WHERE tenant_id=? AND kind=? AND key=?',(tenant,kind,key)).fetchone()
                if old:
                    if old['request_hash']!=request_hash:reject('idempotency_conflict','Origen repetido con contenido distinto',409)
                    return self.row(db,tenant,old['record_id'],kind)
            if db.execute('SELECT count(*) FROM governance_records WHERE tenant_id=?',(tenant,)).fetchone()[0]>=5000:reject('governance_quota','Registro requiere mantenimiento',429)
            record={'schema_version':1,'id':uid(),'kind':kind,'tenant_id':tenant,'revision':0,'state':'proposed','fields':fields,
                'created_by':actor.actor_id,'created_at':self.clock().isoformat(),'review':None,'external_action':False}
            record['record_hash']=digest(record)
            db.execute('INSERT INTO governance_records VALUES(?,?,?,?,?)',(tenant,record['id'],kind,0,canonical(record)))
            db.execute('INSERT INTO governance_history VALUES(?,?,?,?)',(tenant,record['id'],0,canonical(record)))
            if key:db.execute('INSERT INTO governance_keys VALUES(?,?,?,?,?)',(tenant,kind,key,record['id'],request_hash))
            self.db.audit(db,tenant,actor.actor_id,'governance.proposed',record['id'],correlation,{'kind':kind,'record_hash':record['record_hash']})
        return record
    def get(self,actor,tenant,record_id,correlation='governance-read'):
        self.service.auth._role_authorize(actor,tenant,'governance.read')
        with self.db.connection(readonly=True) as db:record=self.row(db,tenant,record_id)
        self._read_authorize(actor,tenant,record)
        with self.db.transaction() as db:self.db.audit(db,tenant,actor.actor_id,'governance.read',record_id,correlation,{'kind':record['kind']})
        return record
    def review(self,actor,tenant,record_id,body,correlation):
        require_human(self.service,actor,tenant,'governance.review')
        vault=Vault(self.service,clock=self.clock)
        sources=[]
        for evidence_id in body.evidence_ids:
            meta=vault.metadata(actor,tenant,evidence_id)
            if meta['state']!='reviewed':reject('evidence_unreviewed','Evidencia requiere revisión separada',422)
            vault.read(actor,tenant,evidence_id,correlation);sources.append(meta)
        with self.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'governance.review');record=self.row(db,tenant,record_id)
            if record['kind'] in SENSITIVE:self.service.auth.authorize(actor,tenant,'privacy.manage')
            if record['revision']!=body.expected_revision or record['record_hash']!=body.record_hash or record['state']!='proposed':reject('conflict','Registro modificado o ya revisado',409)
            if digest({k:v for k,v in record.items() if k!='record_hash'})!=body.record_hash:reject('integrity','Hash del registro no coincide',409)
            if record['created_by']==actor.actor_id:reject('separation_of_duties','Otro humano debe revisar',403)
            for source in sources:
                current=Vault._row(db,tenant,source['id'])
                if current['revision']!=source['revision'] or current['state']!='reviewed':reject('conflict','Evidencia modificada',409)
            record.update(state='reviewed',revision=1,review={'by':actor.actor_id,'binding':actor.binding_id,'principal_stamp':digest(actor.__dict__),
                'evidence_snapshots':{m['id']:{'revision':m['revision'],'redacted_sha256':m['redacted_sha256']} for m in sources},
                'at':self.clock().isoformat(),'expires_at':(self.clock()+timedelta(days=30)).isoformat(),'competence_ref':body.competence_ref,'evidence_ids':body.evidence_ids})
            self.save(db,tenant,record);self.db.audit(db,tenant,actor.actor_id,'governance.reviewed',record_id,correlation,{'kind':record['kind'],'record_hash':body.record_hash})
        return record
    def current_review(self,record):
        review=record['review']
        if not review or datetime.fromisoformat(review['expires_at'])<=self.clock():reject('review_required','Revisión ausente o caducada',409)
        actor=self.service.auth.current(review['binding']);self.service.auth.authorize(actor,record['tenant_id'],'governance.review')
        if self.service.auth.kind(actor)!='human' or digest(actor.__dict__)!=review['principal_stamp']:reject('review_stale','Revisor no vigente',403)
        from .privacy_guard import ensure_readable
        with self.db.connection(readonly=True) as db:
            for evidence_id,snapshot in review.get('evidence_snapshots',{}).items():
                ensure_readable(db,record['tenant_id'],evidence_id,self.clock())
                current=Vault._row(db,record['tenant_id'],evidence_id)
                if current['revision']!=snapshot['revision'] or current['redacted_sha256']!=snapshot['redacted_sha256'] or current['state']!='reviewed':reject('review_stale','Evidencia de aprobación modificada',409)
    def owner(self,tenant,owner_ref):
        if not any(p.actor_id==owner_ref and tenant in p.tenants and p.enabled for p in self.service.settings.principals):not_found()
