"""Bounded deterministic minimization, explicitly not a universal DLP classifier."""
import json
import re
from ..adapters.common import load_json

RULES=(
    (re.compile(r'-----BEGIN (?:[A-Z ]{0,30})PRIVATE KEY-----[\s\S]{1,65536}?-----END (?:[A-Z ]{0,30})PRIVATE KEY-----'), '[PRIVATE KEY REDACTED]'),
    (re.compile(r'AGNTIA_TEST_SECRET_[A-Z0-9]{32}'), '[CANARY REDACTED]'),
    (re.compile(r'(?i)Bearer\s+[A-Za-z0-9._~+/=-]{8,2048}'), 'Bearer [REDACTED]'),
    (re.compile(r'(?i)(password|api[_-]?key|secret|token)\s*[:=]\s*[\"\']?[^\s\"\',;]{4,2048}'), '[CREDENTIAL REDACTED]'),
    (re.compile(r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]{1,128}@[A-Za-z0-9.-]{1,128}\.[A-Za-z]{2,30}'), '[EMAIL REDACTED]'),
)
SENSITIVE={'authorization','password','secret','token','api_key','api-key','private_key','access_token','refresh_token'}

def text(value):
    if not isinstance(value,str) or len(value)>2*1024*1024:raise ValueError('Text size/type')
    for pattern,replacement in RULES:value=pattern.sub(replacement,value)
    return value

def structure(value,depth=0):
    if depth>40:raise ValueError('Document depth')
    if isinstance(value,str):return text(value)
    if isinstance(value,list):return [structure(v,depth+1) for v in value]
    if isinstance(value,dict):return {text(k):'[REDACTED]' if k.lower() in SENSITIVE else structure(v,depth+1) for k,v in value.items()}
    return value

def redact(content,media_type):
    if media_type=='application/pdf':return b'[QUARANTINED PDF: extraction and malware review unavailable]', 'quarantined'
    if media_type=='application/json':
        value=structure(load_json(content))
        return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False).encode(),'automatic_unreviewed'
    return text(content.decode('utf-8')).encode(),'automatic_unreviewed'
