"""Optional Trivy config-only offline profile. Image advisories remain not_tested."""
from .common import check_run,failure,load_json,safe_path,safe_identifier,InvalidReport
from ..util import digest
VERSION='0.76.2'

def parse(run,snapshot_id,*,manifest_paths=None):
    if not check_run(run,'trivy',VERSION):return failure('trivy',VERSION,run.error_code or 'unsupported_contract')
    try:
        report=load_json(run.output)
        if not isinstance(report,dict) or report.get('SchemaVersion')!=2:raise InvalidReport('Unknown schema')
        groups=report.get('Results',[])
        if not isinstance(groups,list) or len(groups)>10000:raise InvalidReport('Result count')
        findings=[];tested=0
        for group in groups:
            path=safe_path(group.get('Target'));items=group.get('Misconfigurations',[])
            if manifest_paths is not None and path not in manifest_paths:raise InvalidReport('Outside snapshot')
            if group.get('Class')!='config' or not isinstance(items,list):raise InvalidReport('Unsupported profile')
            tested+=1
            for item in items:
                if item.get('Status')!='FAIL':continue
                rule=safe_identifier(item.get('ID'))
                severity=str(item.get('Severity','unknown')).lower()
                if severity not in {'low','medium','high','critical'}:severity='unknown'
                line=item.get('CauseMetadata',{}).get('StartLine')
                if line is not None and (type(line)is not int or line<1):line=None
                findings.append({'fingerprint':digest({'snapshot':snapshot_id,'rule':rule,'path':path,'line':line}),
                    'rule_id':rule,'path':path,'start_line':line,'severity':severity,'state':'unverified',
                    'title':'Configuración requiere revisión','confidence':'tool_reported'})
        if run.exit_code not in (0,10) or (run.exit_code==10 and not findings) or (run.exit_code==0 and findings):raise InvalidReport('Exit mismatch')
        return {'schema_version':1,'tool':'trivy','tool_version':VERSION,
            'status':('findings' if findings else 'no_findings') if tested else 'partial','findings':findings,
            'scan_clean':False,'policy_hash':run.policy_hash,'image':run.image,
            'coverage':{'config_files_reported':tested,'image_vulnerabilities':'not_tested','advisory_database':'not_used'},
            'limitations':['Configuration only. No workload launch, deployment or image vulnerability equivalence claim.']}
    except (InvalidReport,AttributeError,TypeError):return failure('trivy',VERSION,'invalid_report')
