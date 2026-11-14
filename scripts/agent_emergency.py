"""Local, authenticated emergency CLI. Credentials are env references, never CLI values."""
import argparse
import json
import os
from pathlib import Path
import re
from uuid import uuid4
from agntia_ciberseguridad.auth import Authenticator
from agntia_ciberseguridad.config import Settings
from agntia_ciberseguridad.agents.controls import Controls,ControlChange
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.service import Service
from agntia_ciberseguridad.storage import Database

def env(reference):
    if not re.fullmatch('[A-Z][A-Z0-9_]{2,100}',reference):raise ValueError('Invalid environment reference')
    return os.getenv(reference,'')
def main():
    parser=argparse.ArgumentParser(description='Stop/resume governed agent actions in an existing local database')
    parser.add_argument('--config',required=True);parser.add_argument('--tenant',required=True)
    parser.add_argument('--actor-token-env',required=True);parser.add_argument('--stepup-env',required=True)
    parser.add_argument('--kind',choices=['tenant','agent','tool','grant'],required=True);parser.add_argument('--scope',required=True)
    parser.add_argument('--state',choices=['stopped','active'],required=True);parser.add_argument('--expected-epoch',type=int,required=True)
    parser.add_argument('--reason',required=True);parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    service=None
    try:
        settings=Settings.model_validate_json(Path(args.config).read_text())
        actor=Authenticator(settings).authenticate('Bearer '+env(args.actor_token_env))
        if not (settings.data_dir/'cyber.sqlite3').is_file():raise ValueError('An initialized database is required')
        service=Service(settings,Database(settings.data_dir,settings.db_timeout_seconds));controls=Controls(service)
        body=ControlChange(kind=args.kind,scope_id=args.scope,stopped=args.state=='stopped',expected_epoch=args.expected_epoch,reason=args.reason)
        if args.dry_run:result={'dry_run':True,'current':controls.list(actor,args.tenant),'requested':body.model_dump(exclude={'reason'}),'changed':False}
        else:result=controls.change(actor,args.tenant,body,str(uuid4()),env(args.stepup_env))
        print(json.dumps(result));return 0
    except DomainError as error:print(json.dumps(error.public(str(uuid4()))));return 2
    except Exception:print(json.dumps({'code':'emergency_unavailable','message':'Configuration, scope or storage unavailable; no fallback principal.'}));return 2
    finally:
        if service:service.telemetry.close()
if __name__=='__main__':raise SystemExit(main())
