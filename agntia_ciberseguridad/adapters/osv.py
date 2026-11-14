"""OSV2.7.1 offline parser with explicit DB freshness, coverage and advisory uncertainty."""
from datetime import datetime,timezone,timedelta
from .common import InvalidReport,check_run,failure,load_json,safe_identifier,safe_path
from ..sbom import build,purl
from ..util import digest,utcnow

VERSION='2.7.1'

def parse(run,snapshot_id, *, database, manifest_paths=None, clock=utcnow):
    if not check_run(run,'osv',VERSION):return failure('osv',VERSION,run.error_code or 'unsupported_contract')
    try:
        from ..offline_database import validate_metadata
        db=validate_metadata(database,clock())
        payload=load_json(run.output)
        if not isinstance(payload,dict) or not isinstance(payload.get('results'),list):raise InvalidReport('Expected result groups')
        components={};findings={};coverage=[]
        for group in payload['results']:
            if not isinstance(group,dict) or not isinstance(group.get('packages'),list) or len(group['packages'])>10000:raise InvalidReport('Invalid packages')
            source=group.get('source',{})
            path=safe_path(source.get('path'))
            if manifest_paths is not None and path not in manifest_paths:raise InvalidReport('Source outside snapshot')
            coverage.append(path)
            for entry in group['packages']:
                package=entry.get('package',{});ecosystem=safe_identifier(package.get('ecosystem'))
                name=safe_identifier(package.get('name'),200);version=safe_identifier(package.get('version'),100)
                if any(c in version for c in '<>=*^~') or version in ('latest','unknown'):raise InvalidReport('Unpinned version')
                identity=digest({'ecosystem':ecosystem,'name':name,'version':version})
                component={'id':identity,'ecosystem':ecosystem,'name':name,'version':version,
                           'purl':purl(ecosystem,name,version),'licenses':'unknown','relationship':'unknown'}
                components[identity]=component
                vulnerabilities=entry.get('vulnerabilities',[])
                if not isinstance(vulnerabilities,list) or len(vulnerabilities)>10000:raise InvalidReport('Invalid advisories')
                for advisory in vulnerabilities:
                    advisory_id=safe_identifier(advisory.get('id'))
                    fixed=[]
                    for affected in advisory.get('affected',[]):
                        ap=affected.get('package',{})
                        if ap.get('name')!=name or ap.get('ecosystem')!=ecosystem:continue
                        for span in affected.get('ranges',[]):
                            for event in span.get('events',[]):
                                if 'fixed' in event:fixed.append(safe_identifier(event['fixed'],100))
                    fingerprint=digest({'snapshot':snapshot_id,'component':identity,'advisory':advisory_id,'path':path})
                    findings[fingerprint]={'fingerprint':fingerprint,'component_id':identity,'advisory_id':advisory_id,
                        'source':'https://osv.dev/vulnerability/'+advisory_id,'path':path,'state':'unverified',
                        'severity':'unknown','reachability':'unknown','exploitability':'unknown',
                        'reported_fixed_versions':sorted(set(fixed)),'database_hash':db['sha256']}
        if (run.exit_code==0 and findings) or (run.exit_code==1 and not findings) or run.exit_code not in (0,1):raise InvalidReport('Contradictory exit')
        freshness='stale' if db['stale'] else 'fresh'
        unknown=sorted({c['ecosystem'] for c in components.values()}-set(db['ecosystems']))
        if not coverage or not components or unknown:status='partial'
        elif db['stale']:status='stale'
        else:status='findings' if findings else 'no_findings'
        ordered=[components[k] for k in sorted(components)]
        return {'schema_version':1,'tool':'osv','tool_version':VERSION,'status':status,'scan_clean':False,
                'findings':list(findings.values()),'components':ordered,'sbom':build(ordered,snapshot_id),
                'coverage':{'files':sorted(set(coverage)),'unknown_ecosystems':unknown,'database_freshness':freshness},
                'database':db,'policy_hash':run.policy_hash,'image':run.image,
                'limitations':['Version advisory matching does not prove reachability or exploitation.',
                               'Fixture DB is incomplete; production must use a reviewed, complete data source.']}
    except (InvalidReport,KeyError,TypeError,ValueError,AttributeError):return failure('osv',VERSION,'invalid_report_or_database')
