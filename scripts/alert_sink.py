"""Synthetic alert receiver: HMAC signature, dedupe and acknowledgement over real HTTP.

Not an alerting provider. It proves that a rule evaluation can be delivered, signed,
deduplicated and acknowledged, and that an acknowledgement is not containment. The secret
is read from the environment, never from argv, so it does not appear in the process list.

Receipts are metadata about a customer job, so the state file is created 0o600 and every
line is fsynced before the 202 is returned: an acknowledgement this process reports must
survive a restart. The dedupe window is bounded, so a sender cannot grow memory without end.
"""
import argparse
import collections
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_BODY=65536
MAX_RECEIPTS=4096
SIGNATURE=re.compile(r'^sha256=[a-f0-9]{64}$')
ALERT=re.compile(r'^Agntia[A-Za-z]{3,60}$')
JOB=re.compile(r'^[a-f0-9]{32}$')
TENANT=re.compile(r'^tenant[A-Za-z0-9_-]{0,40}$')
TRACEPARENT=re.compile(r'^00-[a-f0-9]{32}-[a-f0-9]{16}-[0-9a-f]{2}$')
SEVERITIES=('info','warning','critical')
STATUSES=('firing','resolved')

def traceparent_is_usable(value):
    """Same rule as the service: version 00, non-zero identifiers and the sampled bit set."""
    if not TRACEPARENT.fullmatch(value):return False
    _,trace_id,span_id,flags=value.split('-')
    return trace_id!='0'*32 and span_id!='0'*16 and bool(int(flags,16)&1)

class Rejected(Exception):
    def __init__(self,status,code):
        super().__init__(code);self.status=status;self.code=code

class AlertSink:
    def __init__(self,secret,*,state=None,clock=None):
        if not isinstance(secret,str) or len(secret)<16:raise ValueError('sink secret must be at least 16 characters')
        self.secret=secret.encode();self.state=Path(state) if state else None
        self.clock=clock or (lambda:datetime.now(timezone.utc))
        self._lock=threading.Lock();self._receipts=collections.OrderedDict()
    def signature(self,body):
        return 'sha256='+hmac.new(self.secret,body,hashlib.sha256).hexdigest()
    def verify(self,body,signature):
        if not isinstance(signature,str) or not SIGNATURE.fullmatch(signature):return False
        return hmac.compare_digest(signature.encode(),self.signature(body).encode())
    def parse(self,body):
        try:payload=json.loads(body.decode('utf-8'))
        except (UnicodeDecodeError,ValueError):raise Rejected(400,'invalid_json')
        if not isinstance(payload,dict):raise Rejected(400,'invalid_shape')
        if not isinstance(payload.get('alertname'),str) or not ALERT.fullmatch(payload['alertname']):raise Rejected(400,'invalid_alertname')
        if payload.get('status') not in STATUSES:raise Rejected(400,'invalid_status')
        if payload.get('severity') not in SEVERITIES:raise Rejected(400,'invalid_severity')
        if not isinstance(payload.get('job_id'),str) or not JOB.fullmatch(payload['job_id']):raise Rejected(400,'invalid_job')
        if not isinstance(payload.get('tenant'),str) or not TENANT.fullmatch(payload['tenant']):raise Rejected(400,'invalid_tenant')
        trace=payload.get('traceparent')
        if trace is not None and (not isinstance(trace,str) or not traceparent_is_usable(trace)):
            raise Rejected(400,'invalid_traceparent')
        return {'alertname':payload['alertname'],'status':payload['status'],'severity':payload['severity'],
                'job_id':payload['job_id'],'tenant':payload['tenant'],'traceparent':trace}
    def accept(self,body):
        event=self.parse(body)
        fingerprint=hashlib.sha256(json.dumps(event,sort_keys=True).encode()).hexdigest()
        with self._lock:
            existing=self._receipts.get(fingerprint)
            if existing:
                self._receipts.move_to_end(fingerprint)
                return {**existing,'deduplicated':True}
            receipt={'receipt_id':fingerprint[:32],'alertname':event['alertname'],'status':event['status'],
                     'severity':event['severity'],'job_id':event['job_id'],'traceparent':event['traceparent'],
                     'received_at':self.clock().isoformat(),'acknowledged':True,'contained':False,'deduplicated':False}
            self._receipts[fingerprint]=receipt
            while len(self._receipts)>MAX_RECEIPTS:self._receipts.popitem(last=False)
            if self.state:self._append(receipt)
        return receipt
    def _append(self,receipt):
        """Durable, private append: the 202 must not outlive the record it promises."""
        path=Path(self.state);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        line=json.dumps(receipt,sort_keys=True)+'\n'
        handle=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
        try:
            os.write(handle,line.encode('utf-8'));os.fsync(handle)
        finally:os.close(handle)
        os.chmod(path,0o600)
    def deliveries(self):
        with self._lock:return list(self._receipts.values())
    def server(self,host='127.0.0.1',port=0):
        sink=self
        class Handler(BaseHTTPRequestHandler):
            protocol_version='HTTP/1.1'
            def do_POST(self):
                if self.path!='/alerts':return self.reply(404,{'error':'unknown_path'})
                try:length=int(self.headers.get('Content-Length') or 0)
                except ValueError:return self.reply(400,{'error':'invalid_length'})
                if length<1 or length>MAX_BODY:return self.reply(413,{'error':'invalid_length'})
                body=self.rfile.read(length)
                if not sink.verify(body,self.headers.get('X-Agntia-Signature')):return self.reply(401,{'error':'invalid_signature'})
                try:receipt=sink.accept(body)
                except Rejected as error:return self.reply(error.status,{'error':error.code})
                return self.reply(202,{'receipt':receipt})
            def reply(self,status,payload):
                data=json.dumps(payload,sort_keys=True).encode()
                self.send_response(status);self.send_header('Content-Type','application/json')
                self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
            def log_message(self,*arguments):pass
        return ThreadingHTTPServer((host,port),Handler)

def main():
    parser=argparse.ArgumentParser(description='Synthetic signed alert receiver (local only).')
    parser.add_argument('--port',type=int,default=0);parser.add_argument('--state');parser.add_argument('--secret-env',default='CYBER_ALERT_SINK_SECRET')
    options=parser.parse_args();secret=os.environ.get(options.secret_env)
    if not secret:raise SystemExit('missing secret in environment variable '+options.secret_env)
    sink=AlertSink(secret,state=options.state);server=sink.server(port=options.port)
    print(json.dumps({'alert_sink':server.server_address[:2],'endpoint':'/alerts','containment':False}))
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
