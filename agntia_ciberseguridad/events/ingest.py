import hashlib
import hmac
import json
import os
import re
from datetime import timedelta,datetime
from typing import Literal
from pydantic import AwareDatetime,Field,StrictInt
from ..contracts import Model,OpaqueId
from ..errors import reject,not_found
from ..util import canonical,digest,utcnow

AUDIENCE='agntia-ciberseguridad.events'
class PassiveEvent(Model):
    schema_version: Literal[1]=1
    tenant_id: OpaqueId
    source_id: OpaqueId
    event_id: OpaqueId
    audience: Literal['agntia-ciberseguridad.events']=AUDIENCE
    sent_at: AwareDatetime
    occurred_at: AwareDatetime
    type: Literal['heartbeat','deployment','security_observation']
    target_ref: OpaqueId
    severity: Literal['unknown','info','low','medium','high','critical']='unknown'
    rule_ref: OpaqueId|None=None
    count: StrictInt=Field(default=1,ge=0,le=1000000)

class Ingest:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.clock=clock
    def accept(self,tenant,source_id,body,signature):
        source=self.service.settings.event_sources.get(source_id)
        if not source or source.tenant_id!=tenant or not source.enabled:not_found()
        if source.tenant_id!=body.tenant_id or body.source_id!=source_id:reject('source_scope','Fuente fuera de scope',403)
        if body.target_ref not in source.target_refs:reject('source_scope','Recurso no autorizado',403)
        key=os.getenv(source.key_env,'')
        if len(key)<32:reject('source_unavailable','Credencial de fuente no disponible',503)
        expected=hmac.new(key.encode(),canonical(body.model_dump(mode='json')).encode(),hashlib.sha256).hexdigest()
        if not isinstance(signature,str) or not re.fullmatch('[a-f0-9]{64}',signature) or not hmac.compare_digest(signature,expected):reject('source_auth','Firma inválida',401)
        instant=self.clock();occurred=body.occurred_at.astimezone(instant.tzinfo)
        if abs((instant-body.sent_at).total_seconds())>300:reject('source_clock','Firma fuera de ventana',422)
        if occurred>instant+timedelta(minutes=5) or occurred<instant-timedelta(days=30):reject('source_clock','Fecha de observación fuera de ventana',422)
        content_hash=digest(body.model_dump(mode='json'));window=instant.strftime('%Y-%m-%dT%H:%M')
        with self.service.db.transaction() as db:
            # Source configuration is checked again under the write transaction.
            if self.service.settings.event_sources.get(source_id)!=source or not source.enabled:reject('source_scope','Fuente revocada',403)
            old=db.execute('SELECT sequence,source_hash,state FROM passive_events WHERE tenant_id=? AND source_id=? AND event_id=?',(tenant,source_id,body.event_id)).fetchone()
            if old:
                if old['source_hash']!=content_hash:reject('event_conflict','Identificador repetido con contenido distinto',409)
                return {'sequence':old['sequence'],'status':'duplicate','observation_only':True}
            state=db.execute('SELECT * FROM source_state WHERE tenant_id=? AND source_id=?',(tenant,source_id)).fetchone()
            received=state['received'] if state and state['window']==window else 0
            if received>=source.max_per_minute:reject('source_rate_limit','Cuota de fuente agotada',429,retryable=True)
            count,size=db.execute('SELECT count(*),coalesce(sum(length(body)),0) FROM passive_events WHERE tenant_id=?',(tenant,)).fetchone()
            pending=db.execute("SELECT count(*) FROM passive_events WHERE tenant_id=? AND state='pending'",(tenant,)).fetchone()[0]
            if count>=self.service.settings.event_max_records or size+1500>self.service.settings.event_max_bytes or pending>=self.service.settings.event_pending_limit:reject('event_backpressure','Capacidad de ingestión agotada',429,retryable=True)
            watermark=state['watermark'] if state else None
            normalized={'schema_version':1,'tenant_id':tenant,'source_id':source_id,'event_id':body.event_id,
                'type':body.type,'target_ref':body.target_ref,'severity':body.severity,'rule_ref':body.rule_ref,'count':body.count,
                'occurred_at':occurred.isoformat(),'received_at':instant.isoformat(),'source_hash':content_hash,
                'out_of_order':bool(watermark and occurred<datetime.fromisoformat(watermark)),
                'clock_status':'producer_reported','interpretation':'unverified_observation','raw_content_stored':False}
            sequence=db.execute('INSERT INTO passive_events(tenant_id,source_id,event_id,source_hash,received_at,body) VALUES(?,?,?,?,?,?)',(tenant,source_id,body.event_id,content_hash,instant.isoformat(),canonical(normalized))).lastrowid
            latest=max(watermark,occurred.isoformat()) if watermark else occurred.isoformat()
            db.execute('INSERT INTO source_state VALUES(?,?,?,?,?) ON CONFLICT(tenant_id,source_id) DO UPDATE SET watermark=excluded.watermark,window=excluded.window,received=excluded.received',(tenant,source_id,latest,window,received+1))
            self.service.db.audit(db,tenant,'source:'+source_id,'event.received',body.event_id,body.event_id,{'source_hash':content_hash,'sequence':sequence})
            self.service.db.after_commit(lambda:self.service.telemetry.metrics.signal('events','accepted'))
        return {'sequence':sequence,'status':'accepted','observation_only':True}
    def list(self,actor,tenant,after=0,limit=50):
        self.service.authorize(actor,tenant,'events.read')
        with self.service.db.connection(readonly=True) as db:
            rows=db.execute('SELECT sequence,body,state FROM passive_events WHERE tenant_id=? AND sequence>? ORDER BY sequence LIMIT ?',(tenant,after,limit)).fetchall()
        return [{**json.loads(r['body']),'sequence':r['sequence'],'state':r['state']} for r in rows]
    def acknowledge(self,actor,tenant,sequence,correlation):
        self.service.authorize(actor,tenant,'events.ack')
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'events.ack')
            row=db.execute('SELECT state FROM passive_events WHERE tenant_id=? AND sequence=?',(tenant,sequence)).fetchone()
            if not row:not_found()
            db.execute("UPDATE passive_events SET state='acknowledged' WHERE tenant_id=? AND sequence=?",(tenant,sequence))
            self.service.db.audit(db,tenant,actor.actor_id,'event.acknowledged',str(sequence),correlation,{'incident_confirmed':False})
        return {'state':'acknowledged','incident_confirmed':False}
