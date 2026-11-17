"""Append-only ledger of lab backup attempts, and a reader that fails closed.

The quiesced lab backup runs as its own process, so its outcome has to survive that
process before an alert can trust it. The ledger holds only the outcome, the digest of
the encrypted bundle and a bounded reason code: no key reference, no path, no tenant, no
evidence content.

Absence and corruption are reported as unknown, never as a recent success. A backup that
fails silently is exactly the failure this file exists to make visible.
"""
import argparse
from collections import deque
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re

OUTCOMES=('success','failure')
REASON=re.compile(r'^[a-z][a-z0-9_]{0,39}$')
DIGEST=re.compile(r'^[a-f0-9]{64}$')
MAX_LINES=4096

def _now(clock):
    return float((clock or (lambda:datetime.now(timezone.utc).timestamp()))())

def record(path,outcome,*,reason=None,digest=None,clock=None):
    """Append one attempt. A success without a bundle digest is not evidence; refuse it."""
    if outcome not in OUTCOMES:raise ValueError('Invalid backup outcome')
    if reason is not None and (not isinstance(reason,str) or not REASON.fullmatch(reason)):
        raise ValueError('Invalid backup reason code')
    if digest is not None and (not isinstance(digest,str) or not DIGEST.fullmatch(digest)):
        raise ValueError('Invalid backup digest')
    if outcome=='success' and digest is None:raise ValueError('A successful backup must carry its bundle digest')
    if outcome=='failure' and digest is not None:raise ValueError('A failed backup has no bundle to digest')
    entry={'schema_version':1,'outcome':outcome,'timestamp':_now(clock)}
    if reason is not None:entry['reason']=reason
    if digest is not None:entry['digest']=digest
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    line=json.dumps(entry,sort_keys=True,separators=(',',':'))+'\n'
    handle=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
    try:
        os.write(handle,line.encode('utf-8'));os.fsync(handle)
    finally:os.close(handle)
    return entry

def _valid(entry):
    if not isinstance(entry,dict) or entry.get('schema_version')!=1:return False
    if entry.get('outcome') not in OUTCOMES:return False
    timestamp=entry.get('timestamp')
    if type(timestamp) not in (int,float) or timestamp<0:return False
    outcome=entry['outcome']
    if outcome=='success':
        return isinstance(entry.get('digest'),str) and bool(DIGEST.fullmatch(entry['digest']))
    reason=entry.get('reason')
    return reason is None or (isinstance(reason,str) and bool(REASON.fullmatch(reason)))

def summarize(path,clock=None):
    """Return what the ledger actually supports. Never turns silence into a success."""
    path=Path(path);entries=[];corrupt=0;records=0
    if path.is_file():
        with path.open('r',encoding='utf-8',errors='replace') as handle:
            for line in deque(handle,maxlen=MAX_LINES):
                if not line.strip():continue
                records+=1
                try:entry=json.loads(line)
                except ValueError:corrupt+=1;continue
                if not _valid(entry):corrupt+=1;continue
                entries.append(entry)
    successes=[entry for entry in entries if entry['outcome']=='success']
    last_success=max(entry['timestamp'] for entry in successes) if successes else None
    last_attempt=max(entry['timestamp'] for entry in entries) if entries else None
    consecutive=0
    for entry in reversed(entries):
        if entry['outcome']!='failure':break
        consecutive+=1
    now=_now(clock)
    return {'schema_version':1,'records':records,'valid_records':len(entries),'corrupt':corrupt,
            'last_success':last_success,'last_attempt':last_attempt,'consecutive_failures':consecutive,
            'age_seconds':None if last_success is None else round(max(0.0,now-last_success),3)}

def main(argv=None):
    parser=argparse.ArgumentParser(description='Record or read lab backup attempts; holds no key and no path.')
    commands=parser.add_subparsers(dest='command',required=True)
    append=commands.add_parser('record');append.add_argument('--path',required=True)
    append.add_argument('--outcome',required=True,choices=OUTCOMES);append.add_argument('--reason')
    append.add_argument('--digest')
    status=commands.add_parser('status');status.add_argument('--path',required=True)
    options=parser.parse_args(argv)
    if options.command=='record':
        try:print(json.dumps(record(options.path,options.outcome,reason=options.reason,digest=options.digest),ensure_ascii=False))
        except ValueError as error:raise SystemExit(str(error))
    else:print(json.dumps(summarize(options.path),ensure_ascii=False))

if __name__=='__main__':main()
