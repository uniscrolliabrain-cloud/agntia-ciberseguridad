"""Versioned, deterministic triage. Unknown is not low and an advisory is not exploitation."""
from datetime import datetime
from .util import utcnow

POLICY_VERSION='triage-v1'
BASE={'info':5,'low':20,'medium':50,'high':80,'critical':95}

def effective(current,instant=None):
    instant=instant or utcnow();value={**current};exception=value.get('exception')
    expired=bool(exception and exception.get('expires_at') and datetime.fromisoformat(exception['expires_at'])<=instant)
    if expired and value['state'] in ('accepted_risk','suppressed','false_positive'):value['state']='suspected'
    context=value.get('context') or {};severity=value.get('severity','unknown');score=BASE.get(severity)
    if score is not None:
        score=min(100,score+(10 if context.get('exposure')=='public' else 0)+(5 if context.get('sensitivity')=='sensitive' else 0))
    priority='needs_context' if score is None else ('P0' if score>=90 else 'P1' if score>=70 else 'P2' if score>=40 else 'P3')
    value.update(exception_expired=expired,risk={'policy_version':POLICY_VERSION,'score':score,'priority':priority,
        'context_complete':context.get('exposure','unknown')!='unknown' and context.get('sensitivity','unknown')!='unknown',
        'exposure':context.get('exposure','unknown'),'exploitation':'unknown',
        'intelligence':{'kev':'unknown','epss':None,'cvss':None,'source_date':None},
        'source':'tool_reported_severity_and_human_declared_context'})
    return value
