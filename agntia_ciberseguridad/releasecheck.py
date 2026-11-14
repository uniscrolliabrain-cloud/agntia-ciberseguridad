"""Installed-artifact synthetic smoke; no scanners, public targets or environment dumps."""
import asyncio
import hashlib
from importlib.resources import files
import json
import os
from pathlib import Path
import secrets
import tempfile

async def check():
    import httpx
    from .app import create_app
    from .config import Settings
    resources={}
    for path in ('web/console.html','web/console.js','governance/legal_sources.json','data/cyclonedx/bom-1.5.schema.json'):
        data=files('agntia_ciberseguridad').joinpath(path).read_bytes()
        if not data:raise RuntimeError('Missing package resource')
        resources[path]=hashlib.sha256(data).hexdigest()
    names=['CYBER_RELEASE_A','CYBER_RELEASE_B','CYBER_RELEASE_VIEWER']
    previous={n:os.environ.get(n) for n in names}
    tokens={n:secrets.token_urlsafe(32) for n in names}
    os.environ.update(tokens)
    app=None
    try:
        with tempfile.TemporaryDirectory(prefix='agntia-installed-smoke-') as temporary:
            root=Path(temporary);repo=root/'fixture';repo.mkdir()
            settings=Settings(data_dir=root/'state',lab_mode=True,approved_workspace_roots=[root],
                principals=[{'id':name,'actor_id':name,'role':role,'tenants':[tenant],'token_env':env} for name,role,tenant,env in [('ownerA','owner','releaseA',names[0]),('ownerB','owner','releaseB',names[1]),('viewerA','viewer','releaseA',names[2])]],
                targets={'fixture':{'tenant_id':'releaseA','kind':'repository','location':str(repo)}})
            app=create_app(settings)
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic.invalid') as client:
                own={'Authorization':'Bearer '+tokens[names[0]]};foreign={'Authorization':'Bearer '+tokens[names[1]]};viewer={'Authorization':'Bearer '+tokens[names[2]]}
                assert (await client.get('/health/ready')).status_code==200
                assert (await client.get('/v1/tenants/releaseA/assets')).status_code==401
                response=await client.post('/v1/tenants/releaseA/assets',headers=own,json={'target_ref':'fixture','kind':'repository','display_name':'Synthetic installed-package fixture'})
                assert response.status_code==201
                assert (await client.get('/v1/tenants/releaseA/assets',headers=foreign)).status_code==404
                assert (await client.post('/v1/tenants/releaseA/assets',headers=viewer,json={'target_ref':'fixture','kind':'repository','display_name':'denied'})).status_code==403
                workspace=(await client.get('/v1/tenants/releaseA/workspace',headers=viewer)).json()
                assert workspace['coverage']=='not_tested' and workspace['security_guarantee'] is False
                assert workspace['budget_status']=='not_configured'
                assert (await client.get('/v1/tenants/releaseA/audit/integrity',headers=own)).json()['valid']
        return {'installed_artifact_smoke':'PASS','package_path':str(Path(__file__).resolve()),'resources':resources,'synthetic_only':True,'scanner_executed':False,'production_accepted':False}
    finally:
        if app:app.state.service.telemetry.close()
        for name,value in previous.items():
            if value is None:os.environ.pop(name,None)
            else:os.environ[name]=value

def main():
    try:print(json.dumps(asyncio.run(check())))
    except Exception:
        print(json.dumps({'installed_artifact_smoke':'FAIL','error':'package_smoke_failed','production_accepted':False}));raise SystemExit(1) from None
if __name__=='__main__':main()
