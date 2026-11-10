"""Immutable, minimized JSON/HTML/CSV reports backed by encrypted evidence."""
import csv
from datetime import datetime,timedelta,timezone
import html
import io
import json
import sqlite3
import threading
from typing import Literal
from pydantic import Field,model_validator
from .contracts import Model,ResourceId,OpaqueId
from .evidence.vault import Vault
from .evidence.redaction import structure,text
from .errors import reject,not_found
from .risk import effective,POLICY_VERSION
from .util import canonical,digest,now,uid,utcnow

class ReportRequest(Model):
    asset_id: ResourceId|None=None
    job_ids: list[ResourceId]=Field(default_factory=list,max_length=50)
    owner_ref: OpaqueId|None=None
    start: str|None=Field(default=None,max_length=40)
    end: str|None=Field(default=None,max_length=40)

    @model_validator(mode='after')
    def window(self):
        for value in (self.start,self.end):
            if value and datetime.fromisoformat(value).tzinfo is None:raise ValueError('Timezone required')
        if bool(self.start)!=bool(self.end):raise ValueError('Both period limits required')
        if self.start:
            self.start=datetime.fromisoformat(self.start).astimezone(timezone.utc).isoformat()
            self.end=datetime.fromisoformat(self.end).astimezone(timezone.utc).isoformat()
        if self.start and not datetime.fromisoformat(self.start)<datetime.fromisoformat(self.end)<=datetime.fromisoformat(self.start)+timedelta(days=93):raise ValueError('Invalid period')
        return self

class Reports:
    def __init__(self,service,*,clock=utcnow):
        self.service=service;self.db=service.db;self.clock=clock;self.vault=Vault(service,clock=clock);self.lock=threading.RLock()

    def _snapshot(self,actor,tenant,request):
        self.service.authorize(actor,tenant,'reports.create')
        with self.db.connection(readonly=True) as db:
            db.execute('BEGIN')
            if request.asset_id and not db.execute('SELECT 1 FROM assets WHERE tenant_id=? AND id=?',(tenant,request.asset_id)).fetchone():not_found()
            for job_id in request.job_ids:
                if not db.execute('SELECT 1 FROM jobs WHERE tenant_id=? AND id=?',(tenant,job_id)).fetchone():not_found()
            conditions=['j.tenant_id=?'];params=[tenant]
            if request.asset_id:conditions.append('j.asset_id=?');params.append(request.asset_id)
            if request.job_ids:conditions.append('j.id IN ('+','.join('?' for _ in request.job_ids)+')');params+=request.job_ids
            if request.start:conditions+=['j.created_at>=?','j.created_at<=?'];params+=[request.start,request.end]
            rows=db.execute('SELECT j.*,r.body AS result_body,r.content_hash FROM jobs j LEFT JOIN job_results r ON r.tenant_id=j.tenant_id AND r.job_id=j.id WHERE '+' AND '.join(conditions)+' ORDER BY j.created_at DESC,j.id DESC LIMIT 201',params).fetchall()
            truncated=len(rows)>200;rows=rows[:200];jobs=[];job_ids={r['id'] for r in rows}
            for row in rows:
                result=json.loads(row['result_body']) if row['result_body'] else None
                if result and (digest(result)!=row['content_hash'] or row['result_hash']!=row['content_hash']):reject('report_integrity','Resultado alterado',409)
                database=result.get('database') if result else None
                stale=bool(database and (self.clock()-datetime.fromisoformat(database['fetched_at'])).total_seconds()>database.get('max_age_hours',24)*3600)
                snapshot=db.execute('SELECT manifest_hash,content_hash FROM snapshots WHERE tenant_id=? AND id=?',(tenant,row['snapshot_id'])).fetchone()
                jobs.append({'grant_id':row['grant_id'],'snapshot_manifest_hash':snapshot['manifest_hash'],'snapshot_content_hash':snapshot['content_hash'],'id':row['id'],'asset_id':row['asset_id'],'snapshot_id':row['snapshot_id'],'tool':row['tool'],
                    'state':row['state'],'error_code':row['error_code'],'created_at':row['created_at'],
                    'policy_hash':row['policy_hash'],'result_hash':row['result_hash'],'result_status':result.get('status') if result else 'not_tested',
                    'tool_version':result.get('tool_version') if result else None,'coverage':result.get('coverage','unknown') if result else 'unknown',
                    'snapshot_coverage':result.get('snapshot_coverage','unknown') if result else 'unknown',
                    'data_freshness':'stale' if stale else ('recorded_at_scan' if database else 'unknown'),
                    'image':result.get('image') if result else None})
            findings=[]
            finding_rows=db.execute('SELECT id,body FROM finding_current WHERE tenant_id=? ORDER BY id LIMIT 1001',(tenant,)).fetchall()
            if len(finding_rows)>1000:truncated=True
            for row in finding_rows[:1000]:
                current=json.loads(row['body'])
                if request.asset_id and current['asset_id']!=request.asset_id:continue
                if request.owner_ref and current.get('owner_ref')!=request.owner_ref:continue
                if job_ids:
                    relevant=db.execute('SELECT 1 FROM finding_observations WHERE tenant_id=? AND finding_id=? AND job_id IN ('+','.join('?' for _ in job_ids)+') LIMIT 1',[tenant,current['id'],*job_ids]).fetchone()
                    if not relevant:continue
                else:continue
                findings.append(effective(current,self.clock()))
            if len(findings)>1000:truncated=True;findings=findings[:1000]
            integrity=self.db.verify_audit(db,tenant)
            if not integrity['valid']:reject('audit_integrity','Auditoría alterada; informe bloqueado',409)
            evidence=[]
            for row in db.execute('SELECT body FROM evidence WHERE tenant_id=? ORDER BY id LIMIT 200',(tenant,)):
                meta=json.loads(row['body'])
                if meta.get('source_job_id') in job_ids:evidence.append(Vault.public(meta))
        incomplete=truncated or not jobs or any(j['state']!='completed' or j['result_status'] in ('not_tested','error','partial','stale') or j['snapshot_coverage']!='captured_local_files' or j['data_freshness']=='stale' for j in jobs)
        result={'schema_version':1,'tenant_id':tenant,'policy_version':POLICY_VERSION,'request':request.model_dump(mode='json'),
            'coverage_status':'incomplete_or_unknown' if incomplete else 'declared_scope_complete',
            'security_guarantee':False,'truncated':truncated,'jobs':jobs,'findings':findings,'evidence':evidence,
            'summary':{'jobs':len(jobs),'findings':len(findings),'suspected':sum(f['state']=='suspected' for f in findings),
                       'unknown_severity':sum(f['risk']['score'] is None for f in findings),'failed_or_not_completed':sum(j['state']!='completed' for j in jobs)},
            'not_tested':['Universal security/compliance','Production deployment','Unobserved languages/assets','Human report review'],
            'limitations':['A finding is an observation, not proof of an attack. Absence is not verified remediation.',
                           'Redaction is fallible. Local audit hashes have no independent external anchor.']}
        return structure(result)

    def create(self,actor,tenant,request,correlation):
        with self.service.telemetry.span('report.build',component='report',correlation_id=correlation):
            return self._create(actor,tenant,request,correlation)

    def _create(self,actor,tenant,request,correlation):
        with self.lock:
            content=self._snapshot(actor,tenant,request);source_hash=digest(content)
            parents=[]
            with self.db.connection(readonly=True) as db:
                for job in content['jobs'][:32]:
                    parent=db.execute('SELECT trace_parent FROM jobs WHERE tenant_id=? AND id=?',(tenant,job['id'])).fetchone()
                    if parent:parents.append(parent['trace_parent'])
            # Attach links to the report span after the nested DB span has closed.
            for parent in parents:self.service.telemetry.link_internal(parent)
            with self.db.connection(readonly=True) as db:
                previous=db.execute('SELECT id FROM reports WHERE tenant_id=? AND source_hash=?',(tenant,source_hash)).fetchone()
                if previous:return self.get(actor,tenant,previous['id'],correlation)
            report_id=uid();content.update(id=report_id,source_hash=source_hash,generated_at=self.clock().isoformat(),
                                          generated_by=actor.actor_id,review_status='not_reviewed')
            metadata=self.vault.put(actor,tenant,canonical(content).encode(),'application/json',correlation)
            record={'id':report_id,'tenant_id':tenant,'source_hash':source_hash,'evidence_id':metadata['id'],
                    'generated_at':content['generated_at'],'generated_by':actor.actor_id,'review_status':'not_reviewed'}
            try:
                with self.db.transaction() as db:
                    self.service.auth.authorize(actor,tenant,'reports.create')
                    db.execute('INSERT INTO reports VALUES(?,?,?,?,?)',(tenant,report_id,source_hash,metadata['id'],canonical(record)))
                    self.db.audit(db,tenant,actor.actor_id,'report.created',report_id,correlation,
                                  {'report_id':report_id,'source_hash':source_hash,'evidence_id':metadata['id']})
            except sqlite3.IntegrityError:
                with self.db.connection(readonly=True) as db:
                    prior=db.execute('SELECT id FROM reports WHERE tenant_id=? AND source_hash=?',(tenant,source_hash)).fetchone()
                    if not prior:raise
                return self.get(actor,tenant,prior['id'],correlation)
            return content

    def get(self,actor,tenant,report_id,correlation):
        self.service.authorize(actor,tenant,'reports.read')
        with self.db.connection(readonly=True) as db:
            row=db.execute('SELECT body FROM reports WHERE tenant_id=? AND id=?',(tenant,report_id)).fetchone()
            if not row:not_found()
            record=json.loads(row['body'])
        body=json.loads(self.vault.read(actor,tenant,record['evidence_id'],correlation))
        if body.get('source_hash')!=record['source_hash'] or body.get('id')!=report_id:reject('report_integrity','Informe alterado',409)
        return body

    @staticmethod
    def render_html(report):
        # No links/scripts/active content; even hostile path/notes remain text.
        executive=html.escape(canonical(report['summary']))
        technical=html.escape(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))
        return '<!doctype html><html lang="es"><meta charset="utf-8"><title>Agntia · Informe</title><body><h1>Informe de seguridad</h1><h2>Resumen</h2><pre>'+executive+'</pre><h2>Evidencias, cobertura y límites</h2><pre>'+technical+'</pre></body></html>'

    @staticmethod
    def render_csv(report):
        output=io.StringIO();writer=csv.writer(output,quoting=csv.QUOTE_ALL);writer.writerow(['finding_id','state','severity','path','priority'])
        def safe(value):
            value=str(value or '')
            return "'"+value if value.lstrip(' \t\r\n').startswith(('=','+','-','@')) or value.startswith(('\t','\r','\n')) else value
        for finding in report['findings']:writer.writerow([safe(finding.get(k)) for k in ('id','state','severity','path')]+[safe(finding['risk']['priority'])])
        return output.getvalue()
