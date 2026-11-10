"""Stable, tenant-scoped identity, separate from each snapshot observation."""
from typing import Literal
from pydantic import Field,StrictInt
from ..contracts import Model,Hash,ResourceId
from ..adapters.common import safe_identifier,safe_path,InvalidReport
from ..util import digest

class Observation(Model):
    schema_version: Literal[1]=1
    finding_id: Hash
    relation_id: Hash|None=None
    tenant_id: str
    asset_id: ResourceId
    snapshot_id: ResourceId
    job_id: ResourceId
    tool: Literal['gitleaks','osv','semgrep','trivy']
    tool_version: str=Field(min_length=1,max_length=100)
    policy_hash: Hash
    rule_id: str=Field(min_length=1,max_length=200)
    cve: str|None=Field(default=None,pattern=r"^CVE-[0-9]{4}-[0-9]{4,12}$")
    cwe: str|None=Field(default=None,pattern=r"^CWE-[0-9]{1,7}$")
    path: str=Field(min_length=1,max_length=512)
    start_line: StrictInt|None=None
    component_id: str|None=None
    severity: Literal['info','low','medium','high','critical','unknown']='unknown'
    confidence: Literal['tool_reported','unknown']='tool_reported'
    state: Literal['suspected']='suspected'
    exposure: Literal['unknown']='unknown'
    reachability: Literal['unknown']='unknown'

def normalize(job,result):
    tool=job['tool']
    if result.get('tool')!=tool or result.get('policy_hash')!=job['policy_hash']:raise InvalidReport('Result provenance mismatch')
    version=safe_identifier(result.get('tool_version'))
    items=result.get('findings')
    if not isinstance(items,list) or len(items)>10000:raise InvalidReport('Finding count')
    normalized={}
    for item in items:
        if not isinstance(item,dict):raise InvalidReport('Invalid observation')
        rule=safe_identifier(item.get('rule_id') or item.get('advisory_id'))
        path=safe_path(item.get('path'));line=item.get('start_line')
        if line is not None and (type(line)is not int or not 1<=line<=10000000):raise InvalidReport('Invalid observation location')
        component=item.get('component_id')
        if component is not None:safe_identifier(component,256)
        identity={'version':1,'tenant':job['tenant_id'],'asset':job['asset_id'],'tool':tool,
                  'policy_hash':job['policy_hash'],'rule':rule,'path':path,'line':line,'component':component}
        import re
        cve=rule if re.fullmatch(r"CVE-[0-9]{4}-[0-9]{4,12}",rule) else None
        candidate=item.get('cwe')
        cwe=candidate if isinstance(candidate,str) and re.fullmatch(r"CWE-[0-9]{1,7}",candidate) else None
        finding_id=digest(identity)
        relation=digest({'tenant':job['tenant_id'],'asset':job['asset_id'],'advisory':rule,'component':component}) if component and rule.startswith(('CVE-','GHSA-','AGNTIA-')) else None
        severity=str(item.get('severity','unknown')).lower()
        if severity not in {'info','low','medium','high','critical','unknown'}:severity='unknown'
        observation=Observation(finding_id=finding_id,relation_id=relation,tenant_id=job['tenant_id'],asset_id=job['asset_id'],
            snapshot_id=job['snapshot_id'],job_id=job['id'],tool=tool,tool_version=version,policy_hash=job['policy_hash'],
            rule_id=rule,cve=cve,cwe=cwe,path=path,start_line=line,component_id=component,severity=severity)
        normalized[finding_id]=observation.model_dump(mode='json')
    return list(normalized.values())
