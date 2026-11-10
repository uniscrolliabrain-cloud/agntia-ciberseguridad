"""Append-only observations and current projection. Absence is never remediation."""
import json
from ..errors import not_found
from ..util import canonical,digest,now,uid
from .normalize import normalize

class FindingStore:
    def __init__(self,service):self.service=service;self.db=service.db
    @staticmethod
    def record(db,job,result):
        timestamp=now()
        for observation in normalize(job,result):
            old=db.execute('SELECT body FROM finding_current WHERE tenant_id=? AND id=?',(job['tenant_id'],observation['finding_id'])).fetchone()
            if old:
                current=json.loads(old['body'])
                current.update(last_seen=timestamp,last_job_id=job['id'],last_snapshot_id=job['snapshot_id'],
                    severity=observation['severity'],observation_count=current['observation_count']+1)
                if current['state'] in ('remediated','verified_fixed'):current['state']='suspected';current['reappeared']=True
            else:
                current={'id':observation['finding_id'],'asset_id':job['asset_id'],'tool':job['tool'],'rule_id':observation['rule_id'],
                    'path':observation['path'],'state':'suspected','severity':observation['severity'],'confidence':'tool_reported',
                    'first_seen':timestamp,'last_seen':timestamp,'observation_count':1,'reappeared':False,
                    'last_job_id':job['id'],'last_snapshot_id':job['snapshot_id'],'relation_id':observation['relation_id'],
                    'exposure':'unknown','exception':None}
            db.execute('INSERT INTO finding_current VALUES(?,?,?,?) ON CONFLICT(tenant_id,id) DO UPDATE SET body=excluded.body',
                (job['tenant_id'],observation['finding_id'],job['asset_id'],canonical(current)))
            db.execute('INSERT INTO finding_observations VALUES(?,?,?,?,?,?,?)',
                (job['tenant_id'],uid(),observation['finding_id'],job['id'],job['snapshot_id'],canonical(observation),digest(observation)))
    def list(self,actor,tenant,*,limit=100,after=''):
        self.service.authorize(actor,tenant,'findings.read')
        if type(limit)is not int or not 1<=limit<=100:raise ValueError('Invalid page size')
        with self.db.connection(readonly=True) as db:
            rows=db.execute('SELECT id,body FROM finding_current WHERE tenant_id=? AND id>? ORDER BY id LIMIT ?',(tenant,after,limit)).fetchall()
            return {'items':[json.loads(r['body']) for r in rows],'next_cursor':rows[-1]['id'] if len(rows)==limit else None}
    def history(self,actor,tenant,finding_id,*,limit=100,after=''):
        self.service.authorize(actor,tenant,'findings.read')
        if type(limit)is not int or not 1<=limit<=100:raise ValueError('Invalid page size')
        with self.db.connection(readonly=True) as db:
            current=db.execute('SELECT body FROM finding_current WHERE tenant_id=? AND id=?',(tenant,finding_id)).fetchone()
            if not current:not_found()
            cursor=0
            if after:
                previous=db.execute('SELECT rowid FROM finding_observations WHERE tenant_id=? AND finding_id=? AND id=?',(tenant,finding_id,after)).fetchone()
                if not previous:not_found()
                cursor=previous[0]
            rows=db.execute('SELECT id,body,content_hash FROM finding_observations WHERE tenant_id=? AND finding_id=? AND rowid>? ORDER BY rowid LIMIT ?',(tenant,finding_id,cursor,limit)).fetchall()
            observations=[]
            for row in rows:
                observation=json.loads(row['body'])
                if digest(observation)!=row['content_hash']:raise ValueError('Observation integrity failure')
                observations.append(observation)
            return {'finding':json.loads(current['body']),'observations':observations,'next_cursor':rows[-1]['id'] if len(rows)==limit else None,'notice':'Observations, not proof of exploitation or verified remediation.'}
