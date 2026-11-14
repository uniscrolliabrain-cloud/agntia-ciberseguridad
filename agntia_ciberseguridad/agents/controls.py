"""Audited tenant-scoped stop/resume; second operational credential, not an MFA claim."""
import hmac
import json
import os
from typing import Literal
from pydantic import Field,StrictInt
from ..auth import require_human
from ..contracts import Model,OpaqueId
from ..errors import reject
from ..util import canonical,digest,now
from .policy import ActionPolicy

class ControlChange(Model):
    kind: Literal['tenant','agent','tool','grant']
    scope_id: OpaqueId
    stopped: bool
    expected_epoch: StrictInt=Field(ge=0)
    reason: str=Field(min_length=10,max_length=500)

class Controls:
    def __init__(self,service):self.service=service
    def change(self,actor,tenant,body,correlation,stepup):
        require_human(self.service,actor,tenant,'agents.manage')
        ref=self.service.settings.emergency_token_env;secret=os.getenv(ref,'') if ref else ''
        if len(secret)<32:reject('stepup_unavailable','Credencial operativa no configurada',424)
        if not isinstance(stepup,str) or not hmac.compare_digest(secret.encode(),stepup.encode()):reject('stepup_required','Se requiere segunda credencial operativa',403)
        # Stepup must not silently reuse any ordinary bearer, even through another env reference.
        if any(hmac.compare_digest(secret.encode(),os.getenv(p.token_env,'').encode()) for p in self.service.settings.principals):reject('stepup_unavailable','Credenciales operativas no separadas',424)
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'agents.manage')
            epoch=ActionPolicy.epoch(db,tenant)
            if epoch!=body.expected_epoch:reject('conflict','Epoch modificado',409)
            if body.kind=='tenant' and body.scope_id!=tenant:reject('control_scope','Tenant no coincide',403)
            if body.kind=='agent':
                binding=next((p for p in self.service.settings.principals if p.id==body.scope_id),None)
                if not binding or tenant not in binding.tenants or binding.kind!='agent':reject('control_scope','Agente no disponible',404)
            if body.kind=='grant' and not db.execute('SELECT 1 FROM delegations WHERE tenant_id=? AND id=?',(tenant,body.scope_id)).fetchone():reject('control_scope','Grant no disponible',404)
            if body.kind=='tool' and body.scope_id!='governed_read' and not db.execute('SELECT 1 FROM governed_tools WHERE tenant_id=? AND id=?',(tenant,body.scope_id)).fetchone():reject('control_scope','Tool no disponible',404)
            record={'kind':body.kind,'scope_id':body.scope_id,'stopped':body.stopped,'epoch':epoch+1,'by':actor.actor_id,'at':now(),'reason_hash':digest(body.reason)}
            db.execute('INSERT INTO agent_controls VALUES(?,?,?,?) ON CONFLICT(tenant_id,kind,scope_id) DO UPDATE SET body=excluded.body',(tenant,body.kind,body.scope_id,canonical(record)))
            db.execute('INSERT INTO agent_epochs VALUES(?,?) ON CONFLICT(tenant_id) DO UPDATE SET epoch=excluded.epoch',(tenant,epoch+1))
            self.service.db.audit(db,tenant,actor.actor_id,'agent.control_changed',body.scope_id,correlation,record)
        return {**record,'already_committed_effects_undone':False,'all_old_tenant_grants_invalidated':True}
    def list(self,actor,tenant):
        require_human(self.service,actor,tenant,'agents.manage')
        with self.service.db.connection(readonly=True) as db:
            return {'epoch':ActionPolicy.epoch(db,tenant),'controls':[json.loads(r[0]) for r in db.execute('SELECT body FROM agent_controls WHERE tenant_id=?',(tenant,))]}
