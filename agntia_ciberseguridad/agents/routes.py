"""Explicit policy/flow/MCP/local-note routes, no shell or arbitrary HTTP proxy."""
from fastapi import Depends,Header,Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError,Field,StrictInt
from .capabilities import UseRequest,Delegations
from .controls import Controls,ControlChange
from .effects import Effects,NoteProposal,NoteApproval,NoteCommit
from .flows import DataFlows,FlowCreate,ReleaseProposal
from .tools import MCP,RPC,ToolRegistry,ToolDescriptor
from .policy import POLICY_HASH
from ..contracts import Model,OpaqueId,ResourceId,Hash
from ..errors import reject

class HashApproval(Model):
    proposal_hash: Hash
class ToolApproval(Model):
    descriptor_hash: Hash
    expected_revision: StrictInt=Field(ge=0)
class ToolObservation(Model):
    expected_revision: StrictInt=Field(ge=0)
    descriptor: ToolDescriptor

def register_agent_gateway(app,service,principal):
    controls=Controls(service);flows=DataFlows(service);effects=Effects(service);tools=ToolRegistry(service);mcp=MCP(service)
    app.state.agent_controls=controls;app.state.flows=flows;app.state.agent_effects=effects;app.state.agent_tools=tools
    def corr(request):return request.state.correlation_id
    @app.post('/v1/tenants/{tenant}/agent/explain')
    async def explain(tenant:OpaqueId,body:UseRequest,actor=Depends(principal)):
        return Delegations(service).explain(actor,tenant,body)
    @app.get('/v1/tenants/{tenant}/agent/controls')
    async def control_state(tenant:OpaqueId,actor=Depends(principal)):return controls.list(actor,tenant)
    @app.post('/v1/tenants/{tenant}/agent/controls')
    async def control_change(tenant:OpaqueId,body:ControlChange,request:Request,x_operator_stepup:str=Header('',max_length=512),actor=Depends(principal)):
        return controls.change(actor,tenant,body,corr(request),x_operator_stepup)
    @app.post('/v1/tenants/{tenant}/agent/flows',status_code=201)
    async def create_flow(tenant:OpaqueId,body:FlowCreate,request:Request,actor=Depends(principal)):return flows.create(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/agent/flows/{flow_id}/releases',status_code=201)
    async def release(tenant:OpaqueId,flow_id:ResourceId,body:ReleaseProposal,request:Request,actor=Depends(principal)):return flows.propose_release(actor,tenant,flow_id,body,corr(request))
    @app.post('/v1/tenants/{tenant}/agent/releases/{release_id}/approve')
    async def approve_release(tenant:OpaqueId,release_id:ResourceId,body:HashApproval,request:Request,actor=Depends(principal)):return flows.approve_release(actor,tenant,release_id,body.proposal_hash,corr(request))
    @app.post('/v1/tenants/{tenant}/agent/releases/{release_id}/egress-preflight')
    async def egress_preflight(tenant:OpaqueId,release_id:ResourceId,actor=Depends(principal)):return flows.egress_preflight(actor,tenant,release_id)
    @app.post('/v1/tenants/{tenant}/agent/tools',status_code=201)
    async def propose_tool(tenant:OpaqueId,body:ToolDescriptor,request:Request,actor=Depends(principal)):return tools.propose(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/agent/tools/{tool_id}/observe')
    async def tool_observe(tenant:OpaqueId,tool_id:ResourceId,body:ToolObservation,request:Request,actor=Depends(principal)):
        return tools.propose(actor,tenant,body.descriptor,corr(request),tool_id=tool_id,expected_revision=body.expected_revision)
    @app.post('/v1/tenants/{tenant}/agent/tools/{tool_id}/approve')
    async def approve_tool(tenant:OpaqueId,tool_id:ResourceId,body:ToolApproval,request:Request,actor=Depends(principal)):return tools.approve(actor,tenant,tool_id,body.expected_revision,body.descriptor_hash,corr(request))
    @app.post('/v1/tenants/{tenant}/agent/mcp/{manifest_id}/{tool_id}')
    async def mcp_call(tenant:OpaqueId,manifest_id:ResourceId,tool_id:ResourceId,body:RPC,request:Request,
                       mcp_session_id:str|None=Header(None,max_length=64),mcp_protocol_version:str|None=Header(None,max_length=32),origin:str|None=Header(None,max_length=1024),actor=Depends(principal)):
        try:result,session=mcp.handle(actor,tenant,manifest_id,tool_id,body,corr(request),session_id=mcp_session_id,protocol=mcp_protocol_version,origin=origin)
        except ValidationError:reject('mcp_validation','Parámetros fuera del subconjunto MCP admitido',422)
        return JSONResponse(result,headers={'Mcp-Session-Id':session,'Cache-Control':'no-store'})
    @app.post('/v1/tenants/{tenant}/agent/effects/proposals',status_code=201)
    async def propose_effect(tenant:OpaqueId,body:NoteProposal,request:Request,actor=Depends(principal)):return effects.propose(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/agent/effects/{proposal_id}/approve')
    async def approve_effect(tenant:OpaqueId,proposal_id:ResourceId,body:NoteApproval,request:Request,actor=Depends(principal)):return effects.approve(actor,tenant,proposal_id,body,corr(request))
    @app.post('/v1/tenants/{tenant}/agent/effects/{proposal_id}/commit')
    async def commit_effect(tenant:OpaqueId,proposal_id:ResourceId,body:NoteCommit,request:Request,idempotency_key:str=Header('',max_length=80),actor=Depends(principal)):return effects.commit(actor,tenant,proposal_id,body,idempotency_key,corr(request))
