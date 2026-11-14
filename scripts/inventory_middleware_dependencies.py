"""Installed distribution inventory. Does not query vulnerability feeds or grant licenses."""
import importlib.metadata as metadata
import json
from pathlib import Path
import hashlib
DIRECT=['fastapi','pydantic','uvicorn','jsonschema','cryptography','opentelemetry-sdk','opentelemetry-exporter-otlp-proto-http','httpx','prometheus-client']
records=[]
for name in DIRECT:
    try:
        d=metadata.distribution(name);m=d.metadata
        records.append({'name':name,'version':d.version,'license_expression':m.get('License-Expression'),'license_metadata':(m.get('License') or '')[:200],'verification':'installed package metadata only, not legal approval'})
    except metadata.PackageNotFoundError:records.append({'name':name,'status':'not_installed'})
root=Path(__file__).resolve().parents[1]
for name in ('package.json','package-lock.json'):
    path=root/'typescript'/name
    if path.exists():records.append({'artifact':'typescript/'+name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
print(json.dumps({'schema_version':1,'scope':'direct Python distributions and TS manifests, not full transitive SBOM','dependencies':records,'vulnerability_scan':'NOT_EXECUTED','legal_review':'PENDING','release_blockers':['Project license not chosen','Independent review pending','Provider commercial terms not approved']}))
