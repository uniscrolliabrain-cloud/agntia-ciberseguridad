"""Two worker processes on one database: single ownership under real contention.

Each child is a separate operating-system process with its own SQLite connection, its own
app and its own worker loop; they compete for the same pending jobs. The policy still caps
one running job per tenant and tool, so this does not show parallel throughput. What it does
show is the property the fencing exists for: a job is executed once, by one fence, even when
two processes read the same candidate row and race to claim it.

Fake scanners are used on purpose: the subject is claim/complete contention, not an engine.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.integration.test_jobs import Setup

CHILD=r'''
import asyncio,json,sys
from pathlib import Path
from types import SimpleNamespace
from agntia_ciberseguridad.app import create_app
from agntia_ciberseguridad.config import Settings
from agntia_ciberseguridad.jobs.runner import serve
from agntia_ciberseguridad.jobs.store import JobStore
from agntia_ciberseguridad.jobs.worker import Worker
from agntia_ciberseguridad.runners.base import Tool
from agntia_ciberseguridad.safety import ReleaseGates

settings_path,marker_path,owner,iterations=sys.argv[1],Path(sys.argv[2]),sys.argv[3],int(sys.argv[4])
settings=Settings(**json.loads(Path(settings_path).read_text(encoding='utf-8')))
service=create_app(settings).state.service
store=JobStore(service,gates=ReleaseGates(True,True,True))
RESULT={'schema_version':1,'tool':'gitleaks','tool_version':'8.30.1','status':'no_findings','findings':[],
    'policy_hash':'a'*64,'snapshot_coverage':'captured_local_files','scan_clean':False}

class Scanner:
    runner=SimpleNamespace(images={Tool.gitleaks:SimpleNamespace(policy_hash='a'*64)})
    async def scan(self,actor,tenant,authorization,snapshot,tool,correlation,execution_key=None,**options):
        with marker_path.open('a',encoding='utf-8') as handle:
            handle.write(execution_key+'\n');handle.flush()
        await asyncio.sleep(0.05)
        return RESULT

results=asyncio.run(serve(Worker(store,Scanner(),owner,lease_seconds=30),max_iterations=iterations,interval=0))
print(json.dumps({'results':len(results),'states':[row['state'] for row in results]}),flush=True)
'''

class MultiProcessTests(Setup,unittest.TestCase):
    def test_two_worker_processes_execute_each_claimed_job_exactly_once(self):
        jobs=[self.submit('multi-worker-key-%02d'%index) for index in range(3)]
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup)
        root=Path(directory.name)
        settings=root/'settings.json'
        settings.write_text(json.dumps(self.f.settings.model_dump(mode='json')),encoding='utf-8')
        marker=root/'executions.log'
        processes=[subprocess.Popen([sys.executable,'-c',CHILD,str(settings),str(marker),owner,'10'],
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env={**os.environ}) for owner in ('workerAlpha','workerBeta')]
        reports=[]
        try:
            for process in processes:
                stdout,stderr=process.communicate(timeout=90)
                self.assertEqual(process.returncode,0,stderr)
                reports.append(json.loads(stdout.splitlines()[-1]))
        finally:
            for process in processes:
                if process.poll() is None:process.kill()
        self.assertEqual(sum(report['results'] for report in reports),3,reports)
        executed=[line for line in marker.read_text(encoding='utf-8').splitlines() if line]
        self.assertEqual(len(executed),3,'a job was executed more than once under contention')
        self.assertEqual(len(set(executed)),3,'the same fence executed twice')
        self.assertEqual(len({line.split('-')[0] for line in executed}),3)
        with self.f.service.db.connection(readonly=True) as db:
            rows=db.execute('SELECT id,state,attempts,fence FROM jobs ORDER BY id').fetchall()
            results=db.execute('SELECT count(*) FROM job_results').fetchone()[0]
            audits=db.execute("SELECT count(*) FROM audit WHERE json_extract(body,'$.action')='job.claimed'").fetchone()[0]
        self.assertEqual([row['state'] for row in rows],['completed','completed','completed'])
        self.assertEqual([row['attempts'] for row in rows],[1,1,1])
        self.assertEqual((results,audits),(3,3))
        self.assertEqual({receipt['id'] for receipt in jobs},{row['id'] for row in rows})

if __name__=='__main__':unittest.main()
