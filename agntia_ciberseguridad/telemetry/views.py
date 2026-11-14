"""Tenant-scoped operational views. Missing observations are unknown, not green."""
from datetime import datetime,timedelta
import json
from ..errors import not_found
from ..util import utcnow
from ..risk import effective

class Views:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.clock=clock
    def dashboard(self,actor,tenant):
        self.service.authorize(actor,tenant,'jobs.read');instant=self.clock()
        with self.service.db.connection(readonly=True) as db:
            jobs=[dict(r) for r in db.execute('SELECT id,asset_id,state,tool,created_at,result_hash FROM jobs WHERE tenant_id=? ORDER BY created_at DESC LIMIT 20',(tenant,))]
            result=db.execute('SELECT body,created_at FROM job_results WHERE tenant_id=? ORDER BY created_at DESC LIMIT 1',(tenant,)).fetchone()
            latest=result['created_at'] if result else None
            partial=bool(db.execute("SELECT 1 FROM jobs WHERE tenant_id=? AND state NOT IN ('completed','cancelled') LIMIT 1",(tenant,)).fetchone())
            coverage='not_tested'
            if result:
                body=json.loads(result['body'])
                coverage='incomplete' if partial or body.get('status') in ('error','partial','stale') or body.get('snapshot_coverage')!='captured_local_files' else 'recorded_scope_only'
            stale=bool(latest and instant-datetime.fromisoformat(latest)>timedelta(hours=24))
            events=db.execute("SELECT count(*),sum(state='pending') FROM passive_events WHERE tenant_id=?",(tenant,)).fetchone()
            logs=db.execute('SELECT count(*) FROM operational_logs WHERE tenant_id=? AND (expires_at>? OR legal_hold=1)',(tenant,instant.isoformat())).fetchone()[0]
            findings=[]
            for r in db.execute('SELECT body FROM finding_current WHERE tenant_id=? ORDER BY id LIMIT 20',(tenant,)):
                f=effective(json.loads(r['body']),instant);findings.append({k:f.get(k) for k in ('id','asset_id','state','severity')})
            evidence=[dict(r) for r in db.execute('SELECT id,source_job_id FROM evidence WHERE tenant_id=? ORDER BY id LIMIT 20',(tenant,))]
        from ..billing.reservations import Ledger
        budget=Ledger(self.service,clock=self.clock).summary(actor,tenant)
        return {'budget':budget,'tenant_id':tenant,'as_of':instant.isoformat(),'coverage':coverage,'freshness':'stale' if stale else 'observed_at_scan' if latest else 'unknown',
            'collector_status':'not_monitored','incident_status':'not_evaluated','budget_status':budget['status'],'security_guarantee':False,
            'jobs':jobs,'findings':findings,'evidence':evidence,'signals':{'events':events[0],'pending_events':events[1] or 0,'operational_logs':logs},
            'limitations':['Latest twenty rows are a bounded view, not the complete inventory.','Signals are not confirmed incidents.','No global trace backend is exposed.']}
    def investigation(self,actor,tenant,job_id):
        self.service.authorize(actor,tenant,'jobs.read')
        with self.service.db.connection(readonly=True) as db:
            job=db.execute('SELECT id,asset_id,state,tool,result_hash,trace_parent FROM jobs WHERE tenant_id=? AND id=?',(tenant,job_id)).fetchone()
            if not job:not_found()
            evidence=[r['id'] for r in db.execute('SELECT id FROM evidence WHERE tenant_id=? AND source_job_id=? LIMIT 100',(tenant,job_id))]
        return {'job':{k:job[k] for k in ('id','asset_id','state','tool','result_hash')},'evidence_ids':evidence,
            'trace':{'recorded':bool(job['trace_parent']),'access':'operator_backend_only','external_url':None}}
