"""Delivery and acknowledgement of rule evaluations against a signed local receiver."""
import json
from pathlib import Path
import re
import stat
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from scripts.alert_sink import AlertSink, MAX_BODY

ROOT=Path(__file__).resolve().parents[2]
SECRET='synthetic-sink-secret-not-a-real-credential'
JOB='a'*32
TRACE='00-'+'1'*32+'-'+'2'*16+'-03'

def payload(**overrides):
    return {**{'alertname':'AgntiaScanSignalAbsentOrOld','status':'firing','severity':'info',
               'job_id':JOB,'tenant':'tenantA','traceparent':TRACE},**overrides}

def post(port,body,*,signature=None,path='/alerts'):
    headers={'Content-Type':'application/json'}
    if signature is not None:headers['X-Agntia-Signature']=signature
    request=urllib.request.Request(f'http://127.0.0.1:{port}{path}',data=body,method='POST',headers=headers)
    try:
        with urllib.request.urlopen(request,timeout=10) as response:return response.status,json.loads(response.read())
    except urllib.error.HTTPError as error:return error.code,json.loads(error.read())

class AlertDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.state=Path(self.directory.name)/'receipts.jsonl'
        self.sink=AlertSink(SECRET,state=self.state)
        self.server=self.sink.server();self.port=self.server.server_port
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=5);self.directory.cleanup()
    def deliver(self,body,*,signature=None,path='/alerts'):
        signature=self.sink.signature(body) if signature is None else signature
        return post(self.port,body,signature=signature,path=path)
    def test_signed_alert_is_acknowledged_linked_to_its_job_and_deduplicated(self):
        body=json.dumps(payload()).encode()
        status,first=self.deliver(body);self.assertEqual(status,202)
        receipt=first['receipt'];self.assertTrue(receipt['acknowledged']);self.assertFalse(receipt['contained'])
        self.assertEqual(receipt['job_id'],JOB);self.assertEqual(receipt['traceparent'],TRACE)
        repeated_status,repeated=self.deliver(body);self.assertEqual(repeated_status,202)
        self.assertTrue(repeated['receipt']['deduplicated'])
        self.assertEqual(repeated['receipt']['receipt_id'],receipt['receipt_id'])
        self.assertEqual(len(self.state.read_text().splitlines()),1)
        self.assertEqual(stat.S_IMODE(self.state.stat().st_mode),0o600)
    def test_unsigned_tampered_oversized_and_unknown_paths_are_refused(self):
        body=json.dumps(payload()).encode()
        self.assertEqual(self.deliver(body,signature='')[0],401)
        self.assertEqual(post(self.port,body)[0],401)
        tampered=json.dumps(payload(severity='critical')).encode()
        self.assertEqual(self.deliver(tampered,signature=self.sink.signature(body))[0],401)
        self.assertEqual(self.deliver(b'x'*(MAX_BODY+1))[0],413)
        self.assertEqual(self.deliver(body,path='/hooks')[0],404)
        self.assertEqual(self.sink.deliveries(),[])
    def test_malformed_alert_fields_are_rejected_not_stored(self):
        for overrides in ({'alertname':'NotAnAgntiaRule'},{'status':'unknown'},{'severity':'page'},
                          {'job_id':'not-a-job'},{'tenant':'../../etc'},{'traceparent':'00-'+'0'*32+'-'+'2'*16+'-03'},
                          {'traceparent':'00-'+'1'*32+'-'+'2'*16+'-02'}):
            status,error=self.deliver(json.dumps(payload(**overrides)).encode())
            self.assertEqual(status,400,overrides);self.assertIn('error',error)
        self.assertEqual(self.sink.deliveries(),[])
    def test_sender_free_text_never_reaches_the_receipt_or_the_state_file(self):
        sentinel='AGNTIA_TEST_SECRET_'+'R'*32
        body=json.dumps(payload(summary=sentinel,annotations={'x':sentinel},password=sentinel)).encode()
        status,acknowledged=self.deliver(body);self.assertEqual(status,202)
        self.assertNotIn(sentinel,json.dumps(acknowledged));self.assertNotIn(sentinel,self.state.read_text())
    def test_every_declared_rule_can_be_delivered_and_correlated_to_its_job(self):
        rules=re.findall(r'^\s+- alert:\s*(\w+)\s*$',(ROOT/'infra/observability/alerts.yaml').read_text(),re.M)
        self.assertEqual(len(rules),8)
        for name in rules:
            status,acknowledged=self.deliver(json.dumps(payload(alertname=name)).encode())
            self.assertEqual(status,202,name);self.assertEqual(acknowledged['receipt']['alertname'],name)
            self.assertEqual(acknowledged['receipt']['job_id'],JOB)
    def test_concurrent_duplicate_deliveries_produce_one_acknowledgement(self):
        body=json.dumps(payload()).encode();signature=self.sink.signature(body);results=[]
        def send():results.append(post(self.port,body,signature=signature)[0])
        threads=[threading.Thread(target=send) for _ in range(8)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(timeout=10)
        self.assertEqual(results,[202]*8);self.assertEqual(len(self.sink.deliveries()),1)
        self.assertEqual(len(self.state.read_text().splitlines()),1)

if __name__=='__main__':unittest.main()
