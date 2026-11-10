"""Short-lived signed, server-persisted, one-use read grants with attenuated delegation."""
import base64
import hashlib
import hmac
import json
import os
from datetime import timedelta,datetime
from typing import Literal
from pydantic import AwareDatetime,Field
from .registry import Registry
from ..auth import require_human
from ..contracts import Model,ResourceId
from ..errors import reject,not_found
from ..util import canonical,digest,uid,utcnow

AUDIENCE='agntia-ciberseguridad.read'
POLICY='delegated-read-v1'
class GrantRequest(Model):
    manifest_id: ResourceId
    capabilities: list[Literal['assets.read','findings.read','jobs.read']]=Field(min_length=1,max_length=3)
    resource_ids: list[ResourceId]=Field(min_length=1,max_length=20)
    expires_at: AwareDatetime
    parent_token: str|None=Field(default=None,max_length=12000)
class UseRequest(Model):
    token: str=Field(min_length=50,max_length=12000)
    capability: Literal['assets.read','findings.read','jobs.read']
    resource_id: ResourceId

class Delegations:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.registry=Registry(service);self.clock=clock
    def _key(self):
        ref=self.service.settings.delegation_key_env;key=os.getenv(ref,'') if ref else ''
        if len(key)<32:reject('delegation_unavailable','Clave de delegación no configurada',424)
        return key.encode()
    def _encode(self,body):
        payload=base64.urlsafe_b64encode(canonical(body).encode()).decode().rstrip('=')
        return payload+'.'+hmac.new(self._key(),payload.encode(),hashlib.sha256).hexdigest()
    def _decode(self,token):
        try:
            if not isinstance(token,str) or len(token)>12000:raise ValueError()
            payload,signature=token.split('.')
            expected=hmac.new(self._key(),payload.encode(),hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected,signature):raise ValueError()
            decoded=json.loads(base64.b64decode(payload+'='*((-len(payload))%4),altchars=b'-_',validate=True))
            if not isinstance(decoded,dict) or decoded.get('audience')!=AUDIENCE or decoded.get('policy_version')!=POLICY:raise ValueError()
            return decoded
        except (ValueError,TypeError,UnicodeError,KeyError):reject('delegation_auth','Sobre de delegación inválido',401)
    def _row(self,db,tenant,token):
        body=self._decode(token)
        if body.get('tenant_id')!=tenant:reject('delegation_scope','Tenant de delegación incorrecto',403)
        row=db.execute('SELECT * FROM delegations WHERE tenant_id=? AND id=?',(tenant,body.get('id'))).fetchone()
        if not row or not hmac.compare_digest(row['token_hash'],digest(token)) or canonical(body)!=row['body']:reject('delegation_auth','Delegación no registrada',401)
        return row,body
    def _validate_chain(self,db,tenant,row,body):
        visited=set()
        while True:
            if body['id'] in visited or len(visited)>=4:reject('delegation_scope','Cadena inválida',403)
            visited.add(body['id'])
            if row['revoked'] or row['used_at'] or datetime.fromisoformat(body['expires_at'])<=self.clock():reject('delegation_inactive','Delegación inactiva',403)
            manifest=self.registry.get_row(db,tenant,body['manifest_id'])
            if manifest['state']!='approved' or manifest['manifest_hash']!=body['manifest_hash'] or manifest['revision']!=body['manifest_revision']:reject('delegation_inactive','Manifest no vigente',403)
            subject=self.registry.binding(body['subject_binding'],tenant)
            issuer=self.service.auth.current(body['issuer_binding'])
            if digest({'subject':subject.__dict__,'issuer':issuer.__dict__})!=body['principal_stamp']:reject('delegation_inactive','Principal modificado',403)
            for capability in body['capabilities']:self.service.auth.authorize(subject,tenant,capability)
            if not body['parent_id']:break
            row=db.execute('SELECT * FROM delegations WHERE tenant_id=? AND id=?',(tenant,body['parent_id'])).fetchone()
            if not row:reject('delegation_scope','Cadena ausente',403)
            body=json.loads(row['body'])
    def issue(self,actor,tenant,request,correlation):
        self.service.authorize(actor,tenant,'agents.read')
        if request.parent_token is None:require_human(self.service,actor,tenant,'agents.delegate')
        instant=self.clock()
        if not instant<request.expires_at<=instant+timedelta(minutes=5):reject('delegation_expiry','Caducidad máxima cinco minutos',422)
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'agents.read')
            manifest=self.registry.get_row(db,tenant,request.manifest_id)
            subject=self.registry.binding(manifest['agent_binding'],tenant)
            if manifest['state']!='approved':reject('manifest_unapproved','Manifest pendiente de revisión',403)
            if not set(request.capabilities)<=set(manifest['capabilities']) or not set(request.resource_ids)<=set(manifest['resource_ids']):reject('delegation_scope','Delegación fuera de manifest',403)
            for capability in request.capabilities:self.service.auth.authorize(subject,tenant,capability)
            parent_id=None;depth=0
            if request.parent_token:
                parent_row,parent=self._row(db,tenant,request.parent_token);self._validate_chain(db,tenant,parent_row,parent)
                if actor.binding_id!=parent['subject_binding']:reject('delegation_scope','Solo el titular puede delegar',403)
                if not set(request.capabilities)<=set(parent['capabilities']) or not set(request.resource_ids)<=set(parent['resource_ids']) or request.expires_at>datetime.fromisoformat(parent['expires_at']):reject('delegation_scope','No se permite ampliar permisos',403)
                parent_id=parent['id'];depth=parent['depth']+1
                if depth>=4:reject('delegation_scope','Profundidad máxima',403)
                if db.execute('SELECT count(*) FROM delegations WHERE tenant_id=? AND parent_id=?',(tenant,parent_id)).fetchone()[0]>=8:reject('delegation_quota','Máximo ocho hijos',429)
            if db.execute('SELECT count(*) FROM delegations WHERE tenant_id=?',(tenant,)).fetchone()[0]>=10000:reject('delegation_quota','Registro requiere mantenimiento',429)
            body={'schema_version':1,'id':uid(),'tenant_id':tenant,'audience':AUDIENCE,'policy_version':POLICY,
                  'subject_binding':subject.binding_id,'issuer_binding':actor.binding_id,'manifest_id':manifest['id'],
                  'manifest_hash':manifest['manifest_hash'],'manifest_revision':manifest['revision'],'parent_id':parent_id,'depth':depth,
                  'capabilities':sorted(set(request.capabilities)),'resource_ids':sorted(set(request.resource_ids)),
                  'issued_at':instant.isoformat(),'expires_at':request.expires_at.isoformat(),
                  'principal_stamp':digest({'subject':subject.__dict__,'issuer':actor.__dict__}),'nonce':uid()}
            token=self._encode(body)
            db.execute('INSERT INTO delegations(tenant_id,id,parent_id,body,token_hash) VALUES(?,?,?,?,?)',(tenant,body['id'],parent_id,canonical(body),digest(token)))
            self.service.db.audit(db,tenant,actor.actor_id,'delegation.issued',body['id'],correlation,{'manifest_hash':body['manifest_hash'],'parent_id':parent_id,'scope_hash':digest(request.model_dump(mode='json',exclude={'parent_token'}))})
        return {'id':body['id'],'token':token,'expires_at':body['expires_at'],'one_use':True,'executor':'governed_read_only'}
    def revoke(self,actor,tenant,delegation_id,correlation):
        require_human(self.service,actor,tenant,'agents.delegate')
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'agents.delegate')
            if not db.execute('UPDATE delegations SET revoked=1 WHERE tenant_id=? AND id=?',(tenant,delegation_id)).rowcount:not_found()
            self.service.db.audit(db,tenant,actor.actor_id,'delegation.revoked',delegation_id,correlation,{})
        return {'revoked':True,'descendants_invalidated_on_use':True}
    def use(self,actor,tenant,request,correlation):
        self.service.authorize(actor,tenant,request.capability)
        with self.service.db.transaction() as db:
            row,body=self._row(db,tenant,request.token);self._validate_chain(db,tenant,row,body)
            if actor.binding_id!=body['subject_binding'] or request.capability not in body['capabilities'] or request.resource_id not in body['resource_ids']:reject('delegation_scope','Actor o recurso fuera de scope',403)
            asset=db.execute('SELECT body FROM assets WHERE tenant_id=? AND id=?',(tenant,request.resource_id)).fetchone()
            if not asset:not_found()
            if request.capability=='assets.read':data=[self.service.public_asset(json.loads(asset['body']))]
            elif request.capability=='jobs.read':
                data=[dict(r) for r in db.execute('SELECT id,state,tool,result_hash FROM jobs WHERE tenant_id=? AND asset_id=? ORDER BY id LIMIT 100',(tenant,request.resource_id))]
            else:
                data=[{k:json.loads(r['body']).get(k) for k in ('id','state','severity','revision')} for r in db.execute('SELECT body FROM finding_current WHERE tenant_id=? AND json_extract(body,\'$.asset_id\')=? ORDER BY id LIMIT 100',(tenant,request.resource_id))]
            db.execute('UPDATE delegations SET used_at=? WHERE tenant_id=? AND id=?',(self.clock().isoformat(),tenant,body['id']))
            self.service.db.audit(db,tenant,actor.actor_id,'delegation.used',body['id'],correlation,{'capability':request.capability,'resource_id':request.resource_id})
        return {'delegation_id':body['id'],'data':data,'limit':100,'security_guarantee':False}
