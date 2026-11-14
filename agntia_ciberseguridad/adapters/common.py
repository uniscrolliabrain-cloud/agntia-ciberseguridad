"""Strict, minimized result boundary. Never publish raw tool stdout/stderr."""
import json
from pathlib import PurePosixPath
import re
from ..util import digest

class InvalidReport(ValueError):pass

def load_json(raw,maximum=2*1024*1024):
    if not isinstance(raw,bytes) or len(raw)>maximum:raise InvalidReport('Report size/type')
    def finite(value):raise InvalidReport('Non-finite JSON')
    def unique(pairs):
        out={}
        for key,value in pairs:
            if key in out:raise InvalidReport('Duplicate JSON field')
            out[key]=value
        return out
    try:return json.loads(raw,parse_constant=finite,object_pairs_hook=unique)
    except (ValueError,UnicodeError,RecursionError) as exc:raise InvalidReport('Invalid JSON report') from None

def safe_identifier(value,maximum=160):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/+-]{0,'+str(maximum-1)+'}',value):raise InvalidReport('Invalid identifier')
    return value

def safe_path(value):
    if not isinstance(value,str) or len(value.encode())>512:raise InvalidReport('Invalid path')
    if value.startswith('/input/'):value=value[len('/input/'):]
    p=PurePosixPath(value)
    if not value or p.is_absolute() or any(part in ('.','..','') for part in value.split('/')) or '\\' in value or ':' in value or any(ord(c)<32 or ord(c)==127 for c in value):raise InvalidReport('Invalid path')
    return value

def failure(tool,version,code):
    return {'schema_version':1,'tool':tool,'tool_version':version,'status':'error',
            'error_code':code,'findings':[],'scan_clean':False,'coverage':'unknown'}

def check_run(run,tool,version):
    return run.tool.value==tool and run.version==version and run.status=='completed' and run.cleanup_verified
