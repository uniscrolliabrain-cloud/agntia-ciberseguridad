"""Closed deterministic action policy. Missing/stale/unavailable policy always denies."""
from datetime import datetime
import json
import hashlib
from pathlib import Path
from ..errors import reject
from ..util import digest,utcnow

RULES={'schema_version':1,'version':'agntia-actions-v1','reads':['assets.read','findings.read','jobs.read'],
       'proposal':'notes.propose','external_egress':False,'human_approval':'two_distinct_principals',
       'max_token_seconds':300,'mcp_protocol':'2025-11-25','executor':'local_metadata_only'}
_ROOT=Path(__file__).resolve().parents[1]
_SOURCE_PATHS=['auth.py','network_policy.py']+['agents/'+name+'.py' for name in ('policy','context','capabilities','controls','effects','flows','tools','registry','routes')]
SOURCE_HASHES={name:hashlib.sha256((_ROOT/name).read_bytes()).hexdigest() for name in _SOURCE_PATHS}
POLICY_HASH=digest({'rules':RULES,'source_hashes':SOURCE_HASHES})
class ActionPolicy:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.clock=clock
    def active(self):
        settings=self.service.settings
        if settings.agent_policy_hash!=POLICY_HASH or not settings.agent_policy_expires_at or settings.agent_policy_expires_at<=self.clock():
            reject('agent_policy_unavailable','Política ausente, distinta o caducada',424)
    @staticmethod
    def epoch(db,tenant):
        row=db.execute('SELECT epoch FROM agent_epochs WHERE tenant_id=?',(tenant,)).fetchone()
        return row[0] if row else 0
    def validate(self,db,tenant,*,binding_id,grant_id=None,tool_id='governed_read',expected_epoch=None):
        self.active();current=self.epoch(db,tenant)
        if expected_epoch is not None and current!=expected_epoch:reject('agent_policy_stale','Contexto de autorización modificado',409)
        for kind,identifier in [('tenant',tenant),('agent',binding_id),('tool',tool_id),('grant',grant_id)]:
            if not identifier:continue
            row=db.execute('SELECT body FROM agent_controls WHERE tenant_id=? AND kind=? AND scope_id=?',(tenant,kind,identifier)).fetchone()
            if row and json.loads(row[0])['stopped']:reject('agent_stopped','Acción detenida por control vigente',403)
        return current
    def explain(self,db,tenant,actor,body,*,destination_ref=None):
        self.validate(db,tenant,binding_id=actor.binding_id,grant_id=body['id'],expected_epoch=body.get('policy_epoch'))
        if body.get('policy_hash')!=POLICY_HASH:reject('agent_policy_stale','Hash de política no vigente',409)
        if destination_ref:reject('egress_denied','Salida externa no habilitada',403)
        return {'allowed':True,'policy_hash':POLICY_HASH,'policy_epoch':self.epoch(db,tenant),'executor':'local_metadata_only','external_effect':False}
