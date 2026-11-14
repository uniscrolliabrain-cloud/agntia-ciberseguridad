from fastapi import Depends, Request, Query
from pydantic import Field, StrictInt
from ..contracts import Model, OpaqueId, ResourceId
from ..events.outbox import Outbox, Ack
from .reservations import Ledger, ReservationRequest, Settlement

class Revision(Model):
    expected_revision: StrictInt = Field(ge=0)

def register_billing(app,service,principal):
    ledger=Ledger(service); outbox=Outbox(service)
    app.state.budget=ledger;app.state.outbox=outbox
    @app.get('/v1/tenants/{tenant}/budget')
    async def budget(tenant:OpaqueId,actor=Depends(principal)):return ledger.summary(actor,tenant)
    @app.post('/v1/tenants/{tenant}/budget/reservations',status_code=201)
    async def reserve(tenant:OpaqueId,body:ReservationRequest,request:Request,actor=Depends(principal)):
        return ledger.reserve(actor,tenant,body,request.state.correlation_id)
    # Closed actions, not a free action or provider endpoint.
    for action in ('start','cancel','uncertain'):
        def endpoint(selected):
            async def transition(tenant:OpaqueId,reservation_id:ResourceId,body:Revision,request:Request,actor=Depends(principal)):
                return ledger.transition(actor,tenant,reservation_id,body.expected_revision,selected,request.state.correlation_id)
            return transition
        app.post('/v1/tenants/{tenant}/budget/reservations/{reservation_id}/'+action,name='budget_'+action)(endpoint(action))
    @app.post('/v1/tenants/{tenant}/budget/reservations/{reservation_id}/settle')
    async def settle(tenant:OpaqueId,reservation_id:ResourceId,body:Settlement,request:Request,actor=Depends(principal)):
        return ledger.settle(actor,tenant,reservation_id,body,request.state.correlation_id)
    @app.get('/v1/tenants/{tenant}/outbox')
    async def poll(tenant:OpaqueId,consumer_id:OpaqueId,after:int=Query(0,ge=0),limit:int=Query(50,ge=1,le=100),actor=Depends(principal)):
        return outbox.poll(actor,tenant,consumer_id,after,limit)
    @app.post('/v1/tenants/{tenant}/outbox/{event_id}/ack')
    async def ack(tenant:OpaqueId,event_id:ResourceId,body:Ack,request:Request,actor=Depends(principal)):
        return outbox.ack(actor,tenant,event_id,body,request.state.correlation_id)
