"""One durable worker iteration, no enterprise scheduler or unsafe fallback."""
import asyncio
from ..contracts import AuditPreview
from ..errors import DomainError,reject
from ..util import now

class Worker:
    def __init__(self,store,scanner,owner,*,lease_seconds=30,cache_registry=None):
        self.store=store;self.scanner=scanner;self.owner=owner;self.lease_seconds=lease_seconds
        self.cache_registry=cache_registry or {}

    async def run_once(self):
        row=self.store.claim(self.owner,lease_seconds=self.lease_seconds)
        if row is None:return None
        task=None
        try:
            actor,body=self.store.principal_for(row)
            image=self.scanner.runner.images.get(body.tool)
            if image is None or image.policy_hash!=row['policy_hash']:raise DomainError('policy_changed','Imagen o política no coinciden',409)
            authorization=AuditPreview(asset_id=body.asset_id,grant_id=body.grant_id,profile=body.profile,
                                       requests=body.max_attempts,maximum_cost_cents=0)
            options=self.cache_registry.get(body.tool.value,{})
            if self.store.heartbeat(row['tenant_id'],row['id'],self.owner,row['fence'],self.lease_seconds):
                return self.store.fail(row,self.owner,row['fence'],'cancel_requested')
            async def execute():
                with self.store.service.telemetry.span('job.execute',parent=row.get('trace_parent'),component='worker',
                        job_id=row['id'],correlation_id=row['correlation_id'],causation_id=row.get('causation_id') or row['correlation_id']):
                    return await self.scanner.scan(actor,row['tenant_id'],authorization,body.snapshot_id,body.tool,
                        row['correlation_id'],execution_key=row['id']+'-'+str(row['fence']),**options)
            task=asyncio.create_task(execute())
            while not task.done():
                await asyncio.wait({task},timeout=min(1,self.lease_seconds/3))
                if task.done():break
                self.store.principal_for(row)
                if self.store.heartbeat(row['tenant_id'],row['id'],self.owner,row['fence'],self.lease_seconds):
                    task.cancel()
                    try:await task
                    except asyncio.CancelledError:pass
                    return self.store.fail(row,self.owner,row['fence'],'cancel_requested',cleanup_verified=False)
            result=await task
            if result.get('status')=='error':
                code=result.get('error_code','scanner_error')
                return self.store.fail(row,self.owner,row['fence'],code,
                    retryable=code in ('runner_unavailable','timeout'),cleanup_verified=code not in ('cleanup_unverified','reconciliation_required'))
            return self.store.complete(row,self.owner,row['fence'],result)
        except asyncio.CancelledError:
            if task and not task.done():
                task.cancel()
                try:await task
                except (asyncio.CancelledError,Exception):pass
            self.store.fail(row,self.owner,row['fence'],'worker_cancelled',cleanup_verified=False)
            raise
        except DomainError as error:
            had_effect=task is not None
            if task and not task.done():
                task.cancel()
                try:await task
                except (asyncio.CancelledError,Exception):pass
            if error.code=='stale_lease':raise
            return self.store.fail(row,self.owner,row['fence'],error.code,cleanup_verified=not had_effect)
        except Exception:
            if task and not task.done():
                task.cancel()
                try:await task
                except (asyncio.CancelledError,Exception):pass
            return self.store.fail(row,self.owner,row['fence'],'worker_failure',cleanup_verified=False)

    async def reconcile(self,actor,tenant,job_id,expected_revision):
        """Server cleanup of the persisted execution, never an LLM's boolean."""
        store=self.store
        store.service.authorize(actor,tenant,'jobs.reconcile')
        with store.db.connection(readonly=True) as db:row=store._row(db,tenant,job_id)
        if row['state']!='reconciliation_required' or row['revision']!=expected_revision or not row['execution_name']:
            reject('conflict','Job no requiere esta conciliación',409)
        if row['execution_name']!='agntia-scan-'+row['id']+'-'+str(row['fence']):reject('conflict','Identidad de ejecución inconsistente',409)
        if not await self.scanner.runner._cleanup(row['execution_name']):reject('cleanup_unverified','Limpieza no comprobada; no reintentar',424)
        active=True
        try:store.principal_for(row)
        except DomainError:active=False
        with store.db.transaction() as db:
            store.service.auth.authorize(actor,tenant,'jobs.reconcile')
            current=store._row(db,tenant,job_id)
            if current['revision']!=expected_revision or current['state']!='reconciliation_required':reject('conflict','Job modificado durante conciliación',409)
            retry=active and not current['cancel_requested'] and current['attempts']<current['max_attempts']
            state='pending' if retry else ('cancelled' if current['cancel_requested'] else 'failed')
            db.execute('UPDATE jobs SET state=?,fence=fence+1,error_code=?,next_attempt_at=?,revision=revision+1,updated_at=? WHERE tenant_id=? AND id=?',
                       (state,None if retry else 'reconciled_without_retry',store.clock(),now(),tenant,job_id))
            db.execute('UPDATE job_reservations SET state=? WHERE tenant_id=? AND job_id=?',('reserved' if retry else 'consumed',tenant,job_id))
            store.db.audit(db,tenant,actor.actor_id,'job.reconciled',job_id,current['correlation_id'],{'job_id':job_id,'state':state,'cleanup_verified':True,'fence':current['fence']+1})
            return store.public(store._row(db,tenant,job_id))
