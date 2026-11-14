"""Closed operational log schema: discard external message/header/exception content."""
from datetime import timedelta
import json
import re
from ..auth import require_human
from ..errors import reject
from ..util import canonical,uid,utcnow

LEVELS={'info','warning','error'}
EVENTS={'request.completed','request.rejected','retention.changed','source.received','source.rejected'}
COMPONENTS={'api','events','retention','other'}
CODES={'ok','auth','forbidden','not_found','validation','internal','storage_busy','request_too_large','request_timeout','other'}
UUID=re.compile(r'^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$')

class OperationalLogs:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.clock=clock
    def record(self,tenant,*,event='request.completed',component='api',level='info',code='ok',correlation_id=None,**discarded):
        # Caller supplies tenant only after authenticated server scope resolution.
        instant=self.clock();body={'schema_version':1,'id':uid(),'timestamp':instant.isoformat(),
            'level':level if level in LEVELS else 'warning','component':component if component in COMPONENTS else 'other',
            'event':event if event in EVENTS else 'request.rejected','code':code if code in CODES else 'other',
            'correlation_id':correlation_id if isinstance(correlation_id,str) and UUID.fullmatch(correlation_id) else None}
        serialized=canonical(body);config=self.service.settings
        with self.service.db.transaction() as db:
            db.execute('DELETE FROM operational_logs WHERE tenant_id=? AND expires_at<=? AND legal_hold=0',(tenant,instant.isoformat()))
            count,size=db.execute('SELECT count(*),coalesce(sum(bytes),0) FROM operational_logs WHERE tenant_id=?',(tenant,)).fetchone()
            if count>=config.log_max_records or size+len(serialized.encode())>config.log_max_bytes:
                self.service.telemetry.metrics.signal('logs','dropped');return False
            db.execute('INSERT INTO operational_logs(tenant_id,id,created_at,expires_at,legal_hold,bytes,body) VALUES(?,?,?,?,?,?,?)',(tenant,body['id'],body['timestamp'],(instant+timedelta(days=config.log_retention_days)).isoformat(),0,len(serialized.encode()),serialized))
        return True
    def search(self,actor,tenant,*,after=0,limit=50):
        self.service.authorize(actor,tenant,'logs.read')
        if type(limit)is not int or not 1<=limit<=100:reject('validation','Límite inválido',422)
        with self.service.db.connection(readonly=True) as db:
            rows=db.execute('SELECT sequence,body,legal_hold FROM operational_logs WHERE tenant_id=? AND sequence>? AND (expires_at>? OR legal_hold=1) ORDER BY sequence LIMIT ?',(tenant,after,self.clock().isoformat(),limit)).fetchall()
        return [{**json.loads(row['body']),'legal_hold':bool(row['legal_hold']),'sequence':row['sequence']} for row in rows]
    def hold(self,actor,tenant,enabled,correlation):
        require_human(self.service,actor,tenant,'logs.manage')
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'logs.manage')
            db.execute('UPDATE operational_logs SET legal_hold=? WHERE tenant_id=?',(int(enabled),tenant))
            self.service.db.audit(db,tenant,actor.actor_id,'logs.hold_changed',tenant,correlation,{'enabled':enabled})
    def purge(self,actor,tenant,correlation):
        require_human(self.service,actor,tenant,'logs.manage')
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'logs.manage')
            count=db.execute('DELETE FROM operational_logs WHERE tenant_id=? AND expires_at<=? AND legal_hold=0',(tenant,self.clock().isoformat())).rowcount
            self.service.db.audit(db,tenant,actor.actor_id,'logs.expired_purged',tenant,correlation,{'count':count})
        return count

class SafeRequestLogs:
    def __init__(self,app,service):self.app=app;self.service=service
    async def __call__(self,scope,receive,send):
        if scope['type']!='http':return await self.app(scope,receive,send)
        status=500
        async def capture(message):
            nonlocal status
            if message['type']=='http.response.start':status=message['status']
            await send(message)
        try:return await self.app(scope,receive,capture)
        finally:
            state=scope.get('state',{});tenant=state.get('authenticated_log_tenant')
            if tenant:
                try:self.service.logs.record(tenant,event='request.completed' if status<400 else 'request.rejected',level='info' if status<400 else 'warning',code='ok' if status<400 else 'other',correlation_id=state.get('correlation_id'))
                except Exception:self.service.telemetry.metrics.signal('logs','dropped')
