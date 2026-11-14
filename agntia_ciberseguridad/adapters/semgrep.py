"""Pinned Semgrep CE local rules, never retain snippets or source-controlled messages."""
from .common import check_run,failure,load_json,safe_path,safe_identifier,InvalidReport
from ..util import digest
VERSION='1.185.0'
RULES={'agntia.python.dynamic-eval','agntia.javascript.dynamic-eval'}

def parse(run,snapshot_id,*,manifest_paths=None):
    if not check_run(run,'semgrep',VERSION):return failure('semgrep',VERSION,run.error_code or 'unsupported_contract')
    try:
        report=load_json(run.output)
        if not isinstance(report,dict) or not isinstance(report.get('results'),list) or len(report['results'])>10000:raise InvalidReport('Invalid results')
        if report.get('version')!=VERSION:raise InvalidReport('Unknown version')
        findings=[];seen=set()
        for item in report['results']:
            rule=safe_identifier(item.get('check_id'))
            known=next((r for r in RULES if rule==r or rule.endswith('.'+r)),None)
            if not known:raise InvalidReport('Unknown rule')
            path=safe_path(item.get('path'))
            if manifest_paths is not None and path not in manifest_paths:raise InvalidReport('Outside snapshot')
            line=item.get('start',{}).get('line');end=item.get('end',{}).get('line')
            if type(line)is not int or type(end)is not int or not 1<=line<=end<=10000000:raise InvalidReport('Invalid range')
            fingerprint=digest({'snapshot':snapshot_id,'rule':known,'path':path,'line':line})
            if fingerprint in seen:continue
            seen.add(fingerprint)
            findings.append({'fingerprint':fingerprint,'rule_id':known,'path':path,'start_line':line,'end_line':end,
                'severity':'medium','confidence':'tool_reported','state':'unverified','cwe':'CWE-95',
                'title':'Evaluación dinámica requiere revisión de confianza de entrada'})
        if run.exit_code not in (0,1) or (run.exit_code==1 and not findings) or (run.exit_code==0 and findings):raise InvalidReport('Exit mismatch')
        errors=report.get('errors',[])
        if not isinstance(errors,list):raise InvalidReport('Invalid errors')
        return {'schema_version':1,'tool':'semgrep','tool_version':VERSION,'status':'partial' if errors else ('findings' if findings else 'no_findings'),
            'findings':findings,'scan_clean':False,'policy_hash':run.policy_hash,'image':run.image,'snapshot_id':snapshot_id,
            'coverage':{'languages':['python','javascript','typescript'],'rules':sorted(RULES),'error_count':len(errors)},
            'limitations':['Small CE bundle only; no registry, Pro or interfile coverage guarantee.']}
    except (InvalidReport,AttributeError,TypeError):return failure('semgrep',VERSION,'invalid_report')
