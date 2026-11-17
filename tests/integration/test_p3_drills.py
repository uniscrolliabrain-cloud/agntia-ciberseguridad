"""P3 fire drills: scanner down, backup failure and exhausted attempt budget.

Each drill reproduces a failure through the real code path, derives the rule predicate from
the bounded counters the API actually exposes, delivers the signed alert to the local receiver
and records explicitly what is *not* covered. A drill that has no signal path to page a human is
reported as blocked, never as passed.
"""
import asyncio
import json
from pathlib import Path
import re
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.jobs.worker import Worker
from agntia_ciberseguridad.recovery import backup_lab
from scripts.alert_sink import AlertSink
from tests.integration.test_jobs import Setup

ROOT=Path(__file__).resolve().parents[2]
SECRET='synthetic-drill-secret-not-a-real-credential'
RULES=ROOT/'infra/observability/alerts.yaml'

def rule(name):
    text=RULES.read_text()
    block=re.search(r'- alert:\s*'+name+r'\s*\n(.*?)(?=\n\s+- alert:|\Z)',text,re.S)
    if not block:raise AssertionError('Rule not declared: '+name)
    return {'name':name,'expr':re.search(r'expr:\s*(.+)',block.group(1)).group(1).strip(),
            'severity':re.search(r'severity:\s*(\w+)',block.group(1)).group(1)}

def declare(text):
    return re.findall(r'- alert:\s*(\w+)',text)

def post(port,body,*,signature=None):
    headers={'Content-Type':'application/json','X-Agntia-Signature':signature or ''}
    request=urllib.request.Request(f'http://127.0.0.1:{port}/alerts',data=body,method='POST',headers=headers)
    try:
        with urllib.request.urlopen(request,timeout=10) as response:return response.status,json.loads(response.read())
    except urllib.error.HTTPError as error:return error.code,json.loads(error.read())

class Drill(Setup,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.directory=tempfile.TemporaryDirectory();self.state=Path(self.directory.name)/'receipts.jsonl'
        self.sink=AlertSink(SECRET,state=self.state);self.server=self.sink.server();self.port=self.server.server_port
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.metrics=self.f.service.telemetry.metrics
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=5)
        self.directory.cleanup();super().tearDown()
    def page(self,name,job_id,status='firing'):
        declared=rule(name)
        body=json.dumps({'alertname':declared['name'],'status':status,'severity':declared['severity'],
            'job_id':job_id,'tenant':'tenantA','traceparent':None}).encode()
        code,response=post(self.port,body,signature=self.sink.signature(body))
        self.assertEqual(code,202,response)
        receipt=response['receipt']
        self.assertTrue(receipt['acknowledged'])
        self.assertFalse(receipt['contained'],'an acknowledgement is not containment')
        self.assertEqual(receipt['job_id'],job_id)
        return receipt

    def test_drill_scanner_down_retries_then_pages_incomplete_coverage(self):
        declared=rule('AgntiaDeclaredScanCoverageIncomplete')
        self.assertIn('agntia_scan_coverage_total',declared['expr'])
        receipt=self.submit()
        scanner=self.scanner({'status':'error','error_code':'runner_unavailable'})
        first=asyncio.run(Worker(self.store,scanner,'drill-worker',lease_seconds=4).run_once())
        self.assertEqual((first['state'],first['error_code']),('pending','runner_unavailable'))
        self.instant[0]+=10
        done=asyncio.run(Worker(self.store,scanner,'drill-worker',lease_seconds=4).run_once())
        self.assertEqual((done['state'],done['error_code']),('failed','runner_unavailable'))
        # One incomplete-coverage sample per failed attempt: the retry is counted too.
        self.assertEqual(self.metrics.coverage.get('incomplete'),2)
        self.assertEqual(self.metrics.jobs.get(('gitleaks','failed')),1)
        with self.f.service.db.connection(readonly=True) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM job_results').fetchone()[0],0)
        receipt=self.page('AgntiaDeclaredScanCoverageIncomplete',receipt['id'])
        self.assertEqual(receipt['alertname'],'AgntiaDeclaredScanCoverageIncomplete')
        self.assertNotEqual(receipt['receipt_id'],'')
        repeated=self.page('AgntiaDeclaredScanCoverageIncomplete',done['id'])
        self.assertTrue(repeated['deduplicated'])
        self.assertEqual(len(self.state.read_text().splitlines()),1)

    def test_drill_backup_failure_fails_closed_and_reports_no_signal_path(self):
        target=Path(self.directory.name)/'drill-backup.bin'
        with self.assertRaises(DomainError) as not_quiesced:
            backup_lab(self.f.service,target,'CYBER_DRILL_BACKUP_KEY',quiesced=False)
        self.assertEqual(not_quiesced.exception.code,'lab_only')
        with self.assertRaises(DomainError) as no_key:
            backup_lab(self.f.service,Path(self.directory.name)/'drill-backup-2.bin','CYBER_DRILL_BACKUP_KEY',quiesced=True)
        self.assertEqual(no_key.exception.code,'backup_key_unavailable')
        self.assertFalse(target.exists())
        self.assertEqual([name for name in declare(RULES.read_text()) if 'Backup' in name],[])
        exposed={line.split('{')[0].split(' ')[0] for line in self.metrics.export().splitlines() if line.startswith('agntia_')}
        self.assertFalse([name for name in exposed if 'backup' in name],
            'a backup signal appeared: repeat the drill and page instead of blocking')
        self.assertEqual(self.sink.deliveries(),[])

    def test_drill_budget_exhausted_pages_before_the_next_admission(self):
        declared=rule('AgntiaAttemptBudgetExhausted')
        self.assertIn('agntia_job_admission_rejections_total',declared['expr'])
        self.assertIn('reason="quota"',declared['expr'])
        admitted=[self.submit('budget-key-%02d'%index,self.body.model_copy(update={'max_attempts':5})) for index in range(20)]
        with self.assertRaises(DomainError) as refused:
            self.submit('budget-key-99',self.body.model_copy(update={'max_attempts':1}))
        self.assertEqual((refused.exception.code,refused.exception.status),('quota',429))
        self.assertEqual(self.metrics.admissions.get('quota'),1)
        self.assertIn('agntia_job_admission_rejections_total{reason="quota"} 1',self.metrics.export())
        with self.f.service.db.connection(readonly=True) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM jobs').fetchone()[0],20)
            self.assertEqual(db.execute('SELECT sum(units) FROM job_reservations').fetchone()[0],100)
        self.page('AgntiaAttemptBudgetExhausted',admitted[0]['id'])

if __name__=='__main__':unittest.main()
