"""Gitleaks8.30.1 dir-mode JSON contract. Credentials are neither retained nor tested."""
from .common import InvalidReport, check_run, failure, load_json, safe_identifier, safe_path
from ..util import digest

VERSION='8.30.1'

def parse(run,snapshot_id, *, manifest_paths=None):
    if not check_run(run,'gitleaks',VERSION):return failure('gitleaks',VERSION,run.error_code or 'unsupported_contract')
    try:
        leaks=load_json(run.output)
        if not isinstance(leaks,list) or len(leaks)>10000:raise InvalidReport('Expected leak list')
        findings=[];seen=set()
        for leak in leaks:
            if not isinstance(leak,dict):raise InvalidReport('Invalid finding')
            rule=safe_identifier(leak.get('RuleID'))
            path=safe_path(leak.get('File'))
            if manifest_paths is not None and path not in manifest_paths:raise InvalidReport('Path outside snapshot')
            line,end=leak.get('StartLine'),leak.get('EndLine')
            if type(line) is not int or type(end) is not int or not 1<=line<=end<=10_000_000:raise InvalidReport('Invalid line range')
            fingerprint=digest({'snapshot_id':snapshot_id,'tool':'gitleaks','rule_id':rule,'path':path,'start':line,'end':end})
            if fingerprint in seen:continue
            seen.add(fingerprint)
            # Ignore Secret/Match/Description/Message/Author/Commit; any can contain credential data.
            findings.append({'fingerprint':fingerprint,'rule_id':rule,'path':path,'start_line':line,'end_line':end,
                             'severity':'unknown','confidence':'tool_reported','state':'unverified',
                             'title':'Posible credencial expuesta','secret_value_retained':False,
                             'recommendation':'Revisar exposición y proponer revocación/rotación con el titular; no comprobar la credencial contra servicios.'})
        if (run.exit_code==0 and leaks) or (run.exit_code==10 and not leaks) or run.exit_code not in (0,10):raise InvalidReport('Contradictory exit status')
        return {'schema_version':1,'tool':'gitleaks','tool_version':VERSION,'status':'findings' if findings else 'no_findings',
                'findings':findings,'scan_clean':False,'coverage':'directory_snapshot_only',
                'snapshot_id':snapshot_id,'policy_hash':run.policy_hash,'image':run.image,
                'limitations':['No Git history or credential validity check. No findings is not a security guarantee.']}
    except (InvalidReport,KeyError,TypeError):return failure('gitleaks',VERSION,'invalid_report')
