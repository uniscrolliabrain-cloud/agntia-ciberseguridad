"""Durable admission, scoped replay, fenced leases, zero-cost local attempt reservations."""
from dataclasses import asdict
import json
import re
import time
from ..contracts import AuditPreview
from ..errors import DomainError,reject,not_found
from ..safety import ReleaseGates
from ..snapshots import SnapshotStore
from ..util import canonical,digest,now,uid
from .contracts import AuditJobCreate,TERMINAL

def authorization_stamp(actor):
    # Revocation handle, not a usable bearer or its direct authentication fingerprint.
    return digest(asdict(actor))

class JobStore:
    def __init__(self,service,*,gates=None,clock=time.time):
        self.service=service;self.db=service.db;self.gates=gates or ReleaseGates();self.clock=clock

    def _authorize(self,actor,tenant,body):
        self.service.authorize(actor,tenant,'jobs.submit')
        preview=AuditPreview(asset_id=body.asset_id,grant_id=body.grant_id,profile=body.profile,
                             requests=body.max_attempts,maximum_cost_cents=0)
        _,grant,_=self.service.validate_authorization(actor,tenant,preview)
        if grant['revision']!=body.expected_grant_revision:reject('conflict','Revisión de autorización modificada',409)
        manifest,_=SnapshotStore(self.service).verify(actor,tenant,body.snapshot_id)
        if (manifest['asset_id']!=body.asset_id or manifest['grant_id']!=body.grant_id
                or manifest['grant_revision']!=grant['revision'] or manifest['manifest_hash']!=body.snapshot_hash):
            reject('snapshot_scope','Snapshot no corresponde a la propuesta',409)
        policy=self.service.settings.tool_policy_hashes.get(body.tool.value)
        if not policy:reject('unsupported','Política de herramienta no configurada en servidor',424)
        return policy

    @staticmethod
    def _row(db,tenant,job_id):
        row=db.execute('SELECT * FROM jobs WHERE tenant_id=? AND id=?',(tenant,job_id)).fetchone()
        if not row:not_found()
        return dict(row)

    @staticmethod
    def public(row):
        return {key:row[key] for key in ('id','tenant_id','asset_id','grant_id','snapshot_id','actor_id','tool','state',
                'revision','attempts','max_attempts','cancel_requested','error_code','result_hash','created_at','updated_at','correlation_id')}

    def submit(self,actor,tenant,body,key,correlation):
        self.service.authorize(actor,tenant,'jobs.submit')
        if not isinstance(key,str) or not re.fullmatch('[A-Za-z0-9_-]{8,100}',key):reject('idempotency_key','Clave estable requerida',400)
        policy=self._authorize(actor,tenant,body)
        request_hash=digest({'payload':body.model_dump(mode='json'),'actor_id':actor.actor_id,'binding_id':actor.binding_id})
        job_id=uid();state='pending';error=None
        try:self.gates.require_customer_execution()
        except DomainError:state='blocked';error='release_gate_blocked'
        with self.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'jobs.submit')
            existing=db.execute('SELECT * FROM job_idempotency WHERE tenant_id=? AND operation=? AND key=?',(tenant,'audit',key)).fetchone()
            if existing:
                if existing['request_hash']!=request_hash or existing['binding_id']!=actor.binding_id:reject('idempotency_conflict','Clave usada con otra propuesta',409)
                return {**self.public(self._row(db,tenant,existing['job_id'])),'replayed':True,'audit_completed':False}
            grant=self.service._grant(db,tenant,body.grant_id)
            if grant['state']!='approved' or grant['revision']!=body.expected_grant_revision:reject('conflict','Autorización modificada',409)
            used=db.execute("SELECT coalesce(sum(r.units),0) FROM job_reservations r JOIN jobs j ON j.tenant_id=r.tenant_id AND j.id=r.job_id WHERE j.tenant_id=? AND j.grant_id=? AND r.state IN ('reserved','consumed','reconciliation_required')",(tenant,body.grant_id)).fetchone()[0]
            if state=='pending' and used+body.max_attempts>grant['max_requests']:reject('quota','Presupuesto local de intentos agotado',429)
            timestamp=now()
            db.execute('''INSERT INTO jobs(tenant_id,id,asset_id,grant_id,snapshot_id,actor_id,binding_id,authorization_stamp,
                payload,request_hash,tool,policy_hash,state,max_attempts,error_code,created_at,updated_at,correlation_id)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (tenant,job_id,body.asset_id,body.grant_id,body.snapshot_id,actor.actor_id,actor.binding_id,authorization_stamp(actor),
                 canonical(body.model_dump(mode='json')),request_hash,body.tool.value,policy,state,body.max_attempts,error,timestamp,timestamp,correlation))
            db.execute('INSERT INTO job_idempotency VALUES(?,?,?,?,?,?)',(tenant,'audit',key,request_hash,job_id,actor.binding_id))
            db.execute('INSERT INTO job_reservations VALUES(?,?,?,?,?)',(tenant,job_id,body.max_attempts,0,'reserved' if state=='pending' else 'released'))
            self.db.audit(db,tenant,actor.actor_id,'job.admitted',job_id,correlation,{'job_id':job_id,'state':state,'request_hash':request_hash,'tool':body.tool.value})
            return {**self.public(self._row(db,tenant,job_id)),'replayed':False,'audit_completed':False}

    def get(self,actor,tenant,job_id):
        self.service.authorize(actor,tenant,'jobs.read')
        with self.db.connection(readonly=True) as db:return self.public(self._row(db,tenant,job_id))

    def cancel(self,actor,tenant,job_id,expected_revision,correlation):
        self.service.authorize(actor,tenant,'jobs.cancel')
        with self.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'jobs.cancel');row=self._row(db,tenant,job_id)
            if row['revision']!=expected_revision:reject('conflict','Revisión de job modificada',409)
            if row['state'] in TERMINAL:return self.public(row)
            new_state='cancelled' if row['state']=='pending' else row['state']
            db.execute('UPDATE jobs SET state=?,cancel_requested=1,revision=revision+1,updated_at=? WHERE tenant_id=? AND id=?',(new_state,now(),tenant,job_id))
            if new_state=='cancelled':db.execute("UPDATE job_reservations SET state='released' WHERE tenant_id=? AND job_id=?",(tenant,job_id))
            self.db.audit(db,tenant,actor.actor_id,'job.cancel_requested',job_id,correlation,{'job_id':job_id,'effective':new_state=='cancelled'})
            return self.public(self._row(db,tenant,job_id))

    def principal_for(self,row):
        actor=self.service.auth.current(row['binding_id'])
        if authorization_stamp(actor)!=row['authorization_stamp'] or actor.actor_id!=row['actor_id']:reject('principal_revoked','Identidad de admisión revocada',403)
        body=AuditJobCreate.model_validate_json(row['payload'])
        policy=self._authorize(actor,row['tenant_id'],body)
        if policy!=row['policy_hash']:reject('policy_changed','Política modificada desde admisión',409)
        return actor,body

    def _terminal(self,db,row,state,error):
        db.execute('UPDATE jobs SET state=?,error_code=?,lease_owner=NULL,lease_until=NULL,revision=revision+1,updated_at=? WHERE tenant_id=? AND id=?',(state,error,now(),row['tenant_id'],row['id']))
        reservation='reconciliation_required' if state=='reconciliation_required' else ('released' if row['attempts']==0 else 'consumed')
        db.execute('UPDATE job_reservations SET state=? WHERE tenant_id=? AND job_id=?',(reservation,row['tenant_id'],row['id']))
        self.db.audit(db,row['tenant_id'],row['actor_id'],'job.'+state,row['id'],row['correlation_id'],{'job_id':row['id'],'code':error})

    def claim(self,owner,*,lease_seconds=30,global_limit=2,tenant_limit=1,tool_limit=1):
        self.gates.require_customer_execution()
        if not re.fullmatch('[A-Za-z0-9_-]{1,64}',owner) or not 1<=lease_seconds<=300 or min(global_limit,tenant_limit,tool_limit)<1:raise ValueError('Invalid worker policy')
        instant=self.clock()
        with self.db.transaction() as db:
            expired=db.execute("SELECT * FROM jobs WHERE state='running' AND lease_until<=?",(instant,)).fetchall()
            for row in expired:self._terminal(db,dict(row),'reconciliation_required','lease_expired')
        with self.db.connection(readonly=True) as db:
            candidates=db.execute("SELECT * FROM jobs WHERE state='pending' AND next_attempt_at<=? ORDER BY created_at,id LIMIT 50",(instant,)).fetchall()
        for candidate in candidates:
            row=dict(candidate)
            try:self.principal_for(row)
            except DomainError as error:
                with self.db.transaction() as db:
                    current=self._row(db,row['tenant_id'],row['id'])
                    if current['state']=='pending':self._terminal(db,current,'blocked',error.code)
                continue
            with self.db.transaction() as db:
                current=self._row(db,row['tenant_id'],row['id'])
                if current['state']!='pending' or current['next_attempt_at']>instant:continue
                active=db.execute("SELECT tenant_id,tool FROM jobs WHERE state IN ('running','reconciliation_required')").fetchall()
                if len(active)>=global_limit:return None
                if sum(r['tenant_id']==row['tenant_id'] for r in active)>=tenant_limit or sum(r['tool']==row['tool'] for r in active)>=tool_limit:continue
                actor=self.service.auth.current(row['binding_id']);self.service.auth.authorize(actor,row['tenant_id'],'jobs.submit')
                if authorization_stamp(actor)!=row['authorization_stamp']:continue
                grant=self.service._grant(db,row['tenant_id'],row['grant_id'])
                if grant['state']!='approved':continue
                db.execute("UPDATE jobs SET state='running',lease_owner=?,execution_name=?,lease_until=?,fence=fence+1,attempts=attempts+1,revision=revision+1,updated_at=? WHERE tenant_id=? AND id=?",
                    (owner,'agntia-scan-'+current['id']+'-'+str(current['fence']+1),instant+lease_seconds,now(),row['tenant_id'],row['id']))
                self.db.audit(db,row['tenant_id'],row['actor_id'],'job.claimed',row['id'],row['correlation_id'],{'job_id':row['id'],'fence':current['fence']+1})
                return self._row(db,row['tenant_id'],row['id'])
        return None

    def _lease(self,db,tenant,job_id,owner,fence):
        row=self._row(db,tenant,job_id)
        if row['state']!='running' or row['lease_owner']!=owner or row['fence']!=fence or row['lease_until']<=self.clock():reject('stale_lease','Lease antigua o vencida',409)
        return row

    def heartbeat(self,tenant,job_id,owner,fence,lease_seconds=30):
        if not 1<=lease_seconds<=300:raise ValueError('Invalid lease interval')
        with self.db.transaction() as db:
            row=self._lease(db,tenant,job_id,owner,fence)
            db.execute('UPDATE jobs SET lease_until=? WHERE tenant_id=? AND id=?',(self.clock()+lease_seconds,tenant,job_id))
            return bool(row['cancel_requested'])

    def fail(self,row,owner,fence,code,*,retryable=False,cleanup_verified=True):
        with self.db.transaction() as db:
            current=self._lease(db,row['tenant_id'],row['id'],owner,fence)
            if not cleanup_verified:state='reconciliation_required'
            elif current['cancel_requested']:state='cancelled'
            elif retryable and current['attempts']<current['max_attempts']:state='pending'
            else:state='failed'
            if state=='pending':
                delay=2**current['attempts']+(int(current['id'][:4],16)%100)/100
                db.execute("UPDATE jobs SET state='pending',error_code=?,lease_owner=NULL,lease_until=NULL,next_attempt_at=?,revision=revision+1,updated_at=? WHERE tenant_id=? AND id=?",(code,self.clock()+delay,now(),row['tenant_id'],row['id']))
                self.db.audit(db,row['tenant_id'],row['actor_id'],'job.retry_scheduled',row['id'],row['correlation_id'],{'job_id':row['id'],'code':code})
            else:self._terminal(db,current,state,code)
            return self.public(self._row(db,row['tenant_id'],row['id']))

    def complete(self,row,owner,fence,result):
        from ..findings.store import FindingStore
        actor,body=self.principal_for(row)
        with self.db.transaction() as db:
            current=self._lease(db,row['tenant_id'],row['id'],owner,fence)
            self.service.auth.authorize(actor,row['tenant_id'],'jobs.submit')
            grant=self.service._grant(db,row['tenant_id'],row['grant_id'])
            if grant['state']!='approved' or grant['revision']!=body.expected_grant_revision:reject('principal_revoked','Autorización modificada',403)
            if current['cancel_requested']:
                self._terminal(db,current,'cancelled','cancel_requested')
                return self.public(self._row(db,row['tenant_id'],row['id']))
            if result.get('status') not in ('findings','no_findings','partial','stale'):raise ValueError('Invalid completed result state')
            state='partial' if result['status'] in ('partial','stale') or result.get('snapshot_coverage')=='partial' else 'completed'
            content_hash=digest(result)
            db.execute('INSERT INTO job_results VALUES(?,?,?,?,?)',(row['tenant_id'],row['id'],canonical(result),content_hash,now()))
            FindingStore.record(db,current,result)
            db.execute('UPDATE jobs SET result_hash=? WHERE tenant_id=? AND id=?',(content_hash,row['tenant_id'],row['id']))
            self._terminal(db,current,state,None)
            return self.public(self._row(db,row['tenant_id'],row['id']))
