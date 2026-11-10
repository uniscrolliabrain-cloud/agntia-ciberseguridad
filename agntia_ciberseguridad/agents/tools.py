"""Closed MCP resource-server subset; descriptions and skill hashes never become code."""
from datetime import datetime,timedelta
import json
from typing import Literal
from pydantic import Field,StrictInt,model_validator
from .capabilities import UseRequest,Delegations
from .registry import Registry
from .policy import ActionPolicy
from ..auth import require_human
from ..contracts import Model,ResourceId,OpaqueId,Hash
from ..errors import reject,not_found
from ..util import canonical,digest,uid,utcnow

PROTOCOL='2025-11-25'
TOOL_NAME='agntia.metadata.read'
class ToolDescriptor(Model):
    protocol_version: Literal['2025-11-25']=PROTOCOL
    name: Literal['agntia.metadata.read']=TOOL_NAME
    version: OpaqueId
    description: str=Field(min_length=1,max_length=500)
    input_schema: dict
    skill_hash: Hash
    dependency_hashes: list[Hash]=Field(default_factory=list,max_length=8)
    @model_validator(mode='after')
    def closed_schema(self):
        if self.input_schema!=UseRequest.model_json_schema():raise ValueError('Only built-in governed-read schema is admitted')
        return self
class RPC(Model):
    jsonrpc: Literal['2.0']
    id: StrictInt|None=Field(default=None,ge=0,le=2147483647)
    method: Literal['initialize','notifications/initialized','tools/list','tools/call']
    params: dict=Field(default_factory=dict,max_length=10)
    @model_validator(mode='after')
    def request_identity(self):
        if (self.method=='notifications/initialized')!=(self.id is None):raise ValueError('Notification has no ID; requests require an integer ID')
        return self
class ClientInfo(Model):
    name: OpaqueId
    version: OpaqueId
class Initialize(Model):
    protocolVersion: Literal['2025-11-25']
    capabilities: dict=Field(default_factory=dict,max_length=0)
    clientInfo: ClientInfo
class Call(Model):
    name: Literal['agntia.metadata.read']
    arguments: UseRequest

class ToolRegistry:
    def __init__(self,service):self.service=service
    @staticmethod
    def row(db,tenant,tool_id):
        r=db.execute('SELECT body FROM governed_tools WHERE tenant_id=? AND id=?',(tenant,tool_id)).fetchone()
        if not r:not_found()
        return json.loads(r[0])
    @classmethod
    def current(cls,db,tenant,tool_id):
        record=cls.row(db,tenant,tool_id)
        if record['state']!='approved':reject('tool_unapproved','Tool pendiente o con drift',403)
        return record
    def propose(self,actor,tenant,descriptor,correlation,*,tool_id=None,expected_revision=None):
        require_human(self.service,actor,tenant,'agents.manage')
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'agents.manage')
            if db.execute('SELECT count(*) FROM tool_versions WHERE tenant_id=?',(tenant,)).fetchone()[0]>=10000:reject('tool_quota','Historial requiere mantenimiento',429)
            if tool_id:
                old=self.row(db,tenant,tool_id)
                if old['revision']!=expected_revision:reject('conflict','Revisión de tool modificada',409)
                if old['descriptor_hash']==digest(descriptor.model_dump(mode='json')):return {**old,'unchanged':True}
                revision=old['revision']+1
            else:tool_id=uid();revision=0
            record={'id':tool_id,'revision':revision,'descriptor_hash':digest(descriptor.model_dump(mode='json')),
                'schema_hash':digest(descriptor.input_schema),'skill_hash':descriptor.skill_hash,'dependency_hashes':descriptor.dependency_hashes,
                'protocol_version':PROTOCOL,'name':TOOL_NAME,'version':descriptor.version,
                'description_handling':'hashed_untrusted_not_used_as_instructions','state':'pending_review','proposer':actor.actor_id,
                'previous_descriptor_hash':old['descriptor_hash'] if expected_revision is not None else None}
            db.execute('INSERT INTO governed_tools VALUES(?,?,?) ON CONFLICT(tenant_id,id) DO UPDATE SET body=excluded.body',(tenant,tool_id,canonical(record)))
            db.execute('INSERT INTO tool_versions VALUES(?,?,?,?)',(tenant,tool_id,revision,canonical(record)))
            epoch=ActionPolicy.epoch(db,tenant)+1
            db.execute('INSERT INTO agent_epochs VALUES(?,?) ON CONFLICT(tenant_id) DO UPDATE SET epoch=excluded.epoch',(tenant,epoch))
            self.service.db.audit(db,tenant,actor.actor_id,'tool.version_proposed',tool_id,correlation,{'descriptor_hash':record['descriptor_hash'],'previous_hash':record['previous_descriptor_hash'],'epoch':epoch})
        return record
    def approve(self,actor,tenant,tool_id,expected_revision,descriptor_hash,correlation):
        require_human(self.service,actor,tenant,'agents.manage')
        with self.service.db.transaction() as db:
            self.service.auth.authorize(actor,tenant,'agents.manage');record=self.row(db,tenant,tool_id)
            if record['state']!='pending_review' or record['revision']!=expected_revision or record['descriptor_hash']!=descriptor_hash:reject('conflict','Descriptor no coincide',409)
            if record['proposer']==actor.actor_id:reject('separation_of_duties','Otro humano debe aprobar tool',403)
            record.update(state='approved',approved_by=actor.actor_id)
            db.execute('UPDATE governed_tools SET body=? WHERE tenant_id=? AND id=?',(canonical(record),tenant,tool_id))
            epoch=ActionPolicy.epoch(db,tenant)+1
            db.execute('INSERT INTO agent_epochs VALUES(?,?) ON CONFLICT(tenant_id) DO UPDATE SET epoch=excluded.epoch',(tenant,epoch))
            self.service.db.audit(db,tenant,actor.actor_id,'tool.approved',tool_id,correlation,{'descriptor_hash':descriptor_hash,'epoch':epoch})
        return record

class MCP:
    def __init__(self,service,*,clock=utcnow):self.service=service;self.clock=clock
    def handle(self,actor,tenant,manifest_id,tool_id,request,correlation,*,session_id=None,protocol=None,origin=None):
        self.service.authorize(actor,tenant,'agents.read')
        if origin is not None:reject('mcp_origin','Transporte reservado a backend sin Origin',403)
        with self.service.db.transaction() as db:
            manifest=Registry.get_row(db,tenant,manifest_id)
            if manifest['state']!='approved' or manifest['agent_binding']!=actor.binding_id or tool_id not in manifest.get('tool_ids',[]):reject('mcp_scope','Manifest o tool fuera de scope',403)
            Registry(self.service).binding(actor.binding_id,tenant)
            tool=ToolRegistry.current(db,tenant,tool_id)
            epoch=ActionPolicy(self.service,clock=self.clock).validate(db,tenant,binding_id=actor.binding_id,tool_id=tool_id)
            if request.method=='initialize':
                Initialize.model_validate(request.params)
                if session_id:reject('mcp_session','No reutilizar sesión al inicializar',409)
                if db.execute('SELECT count(*) FROM mcp_sessions WHERE tenant_id=?',(tenant,)).fetchone()[0]>=5000:reject('mcp_quota','Sesiones requieren mantenimiento',429)
                session_id=uid();session={'id':session_id,'actor_stamp':digest(actor.__dict__),'manifest_id':manifest_id,'manifest_hash':manifest['manifest_hash'],
                    'tool_id':tool_id,'descriptor_hash':tool['descriptor_hash'],'epoch':epoch,'initialized':False,'expires_at':min(self.clock()+timedelta(minutes=2),self.service.settings.agent_policy_expires_at).isoformat()}
                db.execute('INSERT INTO mcp_sessions VALUES(?,?,?,?)',(tenant,session_id,canonical(session),request.id))
                result={'protocolVersion':PROTOCOL,'capabilities':{'tools':{'listChanged':False}},'serverInfo':{'name':'agntia-closed-read','version':'1'}}
            else:
                if protocol!=PROTOCOL:reject('mcp_protocol','Versión MCP no admitida',422)
                row=db.execute('SELECT body,last_request_id FROM mcp_sessions WHERE tenant_id=? AND id=?',(tenant,session_id)).fetchone()
                if not row:reject('mcp_session','Sesión no disponible',403)
                session=json.loads(row[0])
                if session['actor_stamp']!=digest(actor.__dict__) or session['manifest_id']!=manifest_id or session['manifest_hash']!=manifest['manifest_hash'] or session['tool_id']!=tool_id or session['descriptor_hash']!=tool['descriptor_hash'] or session['epoch']!=epoch or datetime.fromisoformat(session['expires_at'])<=self.clock():reject('mcp_stale','Sesión no vigente',403)
                if request.method=='notifications/initialized':
                    if session['initialized'] or request.params:reject('mcp_replay','Notificación inicial ya recibida o parámetros inválidos',409)
                    session['initialized']=True
                    db.execute('UPDATE mcp_sessions SET body=? WHERE tenant_id=? AND id=?',(canonical(session),tenant,session_id))
                    result=None
                else:
                    if not session['initialized']:reject('mcp_uninitialized','Falta notifications/initialized',409)
                    if request.id<=row['last_request_id']:reject('mcp_replay','ID de petición ya usado',409)
                    db.execute('UPDATE mcp_sessions SET last_request_id=? WHERE tenant_id=? AND id=?',(request.id,tenant,session_id))
                    if request.method=='tools/list':
                        if request.params:reject('mcp_params','No se admiten cursores externos',422)
                        result={'tools':[{'name':TOOL_NAME,'description':'Read scoped metadata through a verified one-use grant.','inputSchema':UseRequest.model_json_schema()}]}
                    else:call=Call.model_validate(request.params);result=None
            self.service.db.audit(db,tenant,actor.actor_id,'mcp.request',session_id,correlation,{'method':request.method,'tool_id':tool_id,'descriptor_hash':tool['descriptor_hash'],'request_id':request.id})
        if request.method=='tools/call':
            # No upstream request or bearer passthrough. Delegations rechecks policy/epoch again.
            content=Delegations(self.service,clock=self.clock).use(actor,tenant,call.arguments,correlation)
            result={'content':[{'type':'text','text':'Scoped metadata returned; no external tool executed.'}],'structuredContent':content,'isError':False}
        return (None if request.method=='notifications/initialized' else {'jsonrpc':'2.0','id':request.id,'result':result}),session_id
