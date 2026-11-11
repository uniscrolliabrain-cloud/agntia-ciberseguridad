"""Local transactional outbox. Poll/ACK are scoped; no remote delivery or scheduler."""
import json
import re
from pydantic import Field
from ..contracts import Model, OpaqueId, Hash
from ..errors import reject, not_found
from ..util import canonical, digest, now

EXPORTED = frozenset({'job.completed','job.partial','job.failed','job.blocked','job.reconciliation_required',
    'budget.reserved','budget.started','budget.released','budget.settled','budget.overrun','budget.reconciliation_required'})

def enqueue_audit(db,event):
    if event['action'] not in EXPORTED: return
    # Supports historical, deliberately pre-outbox migration fixtures.
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='integration_outbox'").fetchone(): return
    tenant=event['tenant_id']; sequence=event['sequence']
    eid=digest({'tenant':tenant,'audit_sequence':sequence})[:32]
    body={'schema_version':1,'id':eid,'tenant_id':tenant,'sequence':sequence,
        'type':'cyber.'+event['action'],'occurred_at':event['at'],'correlation_id':event['correlation_id'],
        'source':'agntia-ciberseguridad','object_id':event['object_id'],'interpretation':'recorded_operation_only'}
    db.execute('INSERT INTO integration_outbox VALUES(?,?,?,?,?)',(tenant,sequence,eid,canonical(body),digest(body)))

class Ack(Model):
    consumer_id: OpaqueId
    content_hash: Hash

class Outbox:
    def __init__(self,service): self.service=service
    def poll(self,actor,tenant,consumer_id,after=0,limit=50):
        self.service.authorize(actor,tenant,'events.read')
        if not isinstance(after,int) or isinstance(after,bool) or after<0 or not 1<=limit<=100 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',consumer_id):
            reject('validation','Cursor de eventos inválido',422)
        with self.service.db.connection(readonly=True) as db:
            rows=db.execute('''SELECT o.* FROM integration_outbox o WHERE o.tenant_id=? AND o.sequence>?
                AND NOT EXISTS(SELECT 1 FROM integration_receipts r WHERE r.tenant_id=o.tenant_id AND r.event_id=o.id AND r.consumer_id=?)
                ORDER BY o.sequence LIMIT ?''',(tenant,after,consumer_id,limit)).fetchall()
        return {'events':[{'envelope':json.loads(r['body']),'content_hash':r['content_hash']} for r in rows],
            'next_after':rows[-1]['sequence'] if rows else None,'delivery':'at_least_once','consumer_id':consumer_id}
    def ack(self,actor,tenant,eid,body,correlation):
        self.service.authorize(actor,tenant,'events.ack')
        with self.service.db.transaction() as db:
            self.service.authorize(actor,tenant,'events.ack')
            row=db.execute('SELECT content_hash FROM integration_outbox WHERE tenant_id=? AND id=?',(tenant,eid)).fetchone()
            if not row: not_found()
            if row['content_hash']!=body.content_hash: reject('event_conflict','Hash de ACK no corresponde',409)
            old=db.execute('SELECT 1 FROM integration_receipts WHERE tenant_id=? AND consumer_id=? AND event_id=?',(tenant,body.consumer_id,eid)).fetchone()
            if not old:
                db.execute('INSERT INTO integration_receipts VALUES(?,?,?,?,?)',(tenant,body.consumer_id,eid,body.content_hash,now()))
                self.service.db.audit(db,tenant,actor.actor_id,'outbox.acknowledged',eid,correlation,{'consumer_hash':digest(body.consumer_id),'content_hash':body.content_hash})
            return {'id':eid,'acknowledged':True,'duplicate':bool(old)}

class SyntheticConsumer:
    """SQLite consumer example: commit dedup+effect locally BEFORE acknowledging the source."""
    def __init__(self,path):
        import sqlite3
        self.path=path
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS inbox(tenant TEXT NOT NULL,id TEXT NOT NULL,hash TEXT NOT NULL,effect TEXT NOT NULL,PRIMARY KEY(tenant,id))')
    def consume(self,item):
        import sqlite3
        body=item['envelope']
        if digest(body)!=item['content_hash']: reject('event_conflict','Evento alterado',409)
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT hash FROM inbox WHERE tenant=? AND id=?',(body['tenant_id'],body['id'])).fetchone()
            if old:
                if old[0]!=item['content_hash']: reject('event_conflict','Evento repetido distinto',409)
                return False
            db.execute('INSERT INTO inbox VALUES(?,?,?,?)',(body['tenant_id'],body['id'],item['content_hash'],body['type']))
            return True
