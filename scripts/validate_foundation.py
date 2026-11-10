"""Validate documentation/configuration only; does not execute a security scan."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

def check(condition,message):
    if not condition:raise SystemExit(message)

def main():
    plans=json.loads((ROOT/'config/plans.json').read_text())
    check(plans['state']=='DESIGN_ONLY_NOT_ENFORCED','Plan status must remain explicit until runtime exists')
    for name,cap in [('Lite',30),('L',70),('XL',300)]:
        plan=plans['plans'][name]
        check(plan['monthly_cap_eur']==cap,'Unexpected plan cap: '+name)
        amounts=plan['allocations_eur'].values()
        check(all(type(x) in (int,float) and x>=0 for x in amounts),'Invalid budget allocation')
        check(sum(amounts)<=cap,'Budget allocations exceed cap: '+name)
    records=json.loads((ROOT/'docs/research/repositories.json').read_text())['repositories']
    check(len(records)==31,'Expected 31 researched repository records')
    check(len({r['repository'] for r in records})==len(records),'Duplicate canonical repository')
    for record in records:
        check(record.get('url','').startswith('https://github.com/'),'Missing canonical source URL')
        check(record.get('license_spdx') is not None,'Missing SPDX metadata state')
        check('not audited' in record.get('verification',''),'Metadata scope must not imply source audit')
    for path in ROOT.rglob('*.json'):
        if '.git' not in path.parts:json.loads(path.read_text())
    markdown=[ROOT/'README.md',ROOT/'AGENTS.md',ROOT/'SECURITY.md',*sorted((ROOT/'docs').rglob('*.md'))]
    for path in markdown:
        check(path.exists(),'Missing documentation: '+str(path))
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('https://','http://','mailto:','#')):continue
            check((path.parent/target.split('#')[0]).exists(),'Broken local link: '+str(path)+' -> '+target)
    files=[{'path':str(p.relative_to(ROOT)),'words':len(p.read_text().split()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in markdown]
    print(json.dumps({'status':'PASS','scope':'documentation, repository metadata and planned budget consistency only','markdown_files':len(files),'repository_metadata_records':len(records),'security_scans_executed':0,'words':sum(f['words'] for f in files)},ensure_ascii=False))

if __name__=='__main__':main()
