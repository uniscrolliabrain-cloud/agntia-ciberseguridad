"""Consolidate the campaign, without upgrading any gate or inventing human acceptance."""
from collections import Counter
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'docs/campaigns/2026-11-10-seven-days/campaign.json';c=json.loads(path.read_text())
phases=c['phases'];tasks=[t for p in phases for t in p['tasks']]
assert len(phases)==42 and len(tasks)==294 and len({t['id'] for t in tasks})==294
result={'classification':'SYNTHETIC_DEMO_NOT_PRODUCTION','owner_acceptance':'PENDING','independent_review':'PENDING','production_enabled':False,'campaign_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'phase_counts':dict(Counter(p['status'] for p in phases)),'task_counts':dict(Counter(t['status'] for t in tasks)),
    'phases':[{'id':p['id'],'title':p['title'],'status':p['status'],'tasks':{t['id']:t['status'] for t in p['tasks']},'depends_on':p['depends_on']} for p in phases]}
output=ROOT/'docs/release/status.json';output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'phase_count':len(phases),'task_count':len(tasks),'classification':result['classification'],'phase_counts':result['phase_counts']}))
