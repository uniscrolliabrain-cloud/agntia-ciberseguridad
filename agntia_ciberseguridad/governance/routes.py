from fastapi import Depends,Request
from .store import Cases,CaseReview
from .legal import Legal,Inventory,Assessment,Control
from .privacy import Privacy,RightsRequest,Breach
from .fraud import Fraud,FraudObservation,FraudVerification
from .incidents import Incidents,Incident,IncidentTransition,Containment
from .remediation import Remediation,RemediationPlan
from ..contracts import OpaqueId,ResourceId

def register_governance(app,service,principal):
    cases=Cases(service);legal=Legal(service);privacy=Privacy(service);fraud=Fraud(service);incidents=Incidents(service);remediation=Remediation(service)
    app.state.governance=cases;app.state.legal=legal;app.state.privacy=privacy;app.state.fraud=fraud;app.state.incidents=incidents;app.state.remediation=remediation
    def corr(request):return request.state.correlation_id
    @app.get('/v1/tenants/{tenant}/governance/sources')
    async def sources(tenant:OpaqueId,actor=Depends(principal)):return legal.sources(actor,tenant)
    @app.post('/v1/tenants/{tenant}/governance/inventories',status_code=201)
    async def inventory(tenant:OpaqueId,body:Inventory,request:Request,actor=Depends(principal)):return legal.inventory(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/governance/assessments',status_code=201)
    async def assessment(tenant:OpaqueId,body:Assessment,request:Request,actor=Depends(principal)):return legal.assess(actor,tenant,body,corr(request))
    @app.get('/v1/tenants/{tenant}/governance/assessments/{record_id}')
    async def legal_view(tenant:OpaqueId,record_id:ResourceId,request:Request,actor=Depends(principal)):return legal.view(actor,tenant,record_id,corr(request))
    @app.post('/v1/tenants/{tenant}/governance/controls',status_code=201)
    async def control(tenant:OpaqueId,body:Control,request:Request,actor=Depends(principal)):return legal.control(actor,tenant,body,corr(request))
    @app.get('/v1/tenants/{tenant}/governance/records/{record_id}')
    async def record(tenant:OpaqueId,record_id:ResourceId,request:Request,actor=Depends(principal)):return cases.get(actor,tenant,record_id,corr(request))
    @app.post('/v1/tenants/{tenant}/governance/records/{record_id}/review')
    async def review(tenant:OpaqueId,record_id:ResourceId,body:CaseReview,request:Request,actor=Depends(principal)):return cases.review(actor,tenant,record_id,body,corr(request))
    @app.post('/v1/tenants/{tenant}/privacy/requests',status_code=201)
    async def rights(tenant:OpaqueId,body:RightsRequest,request:Request,actor=Depends(principal)):return privacy.request(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/privacy/requests/{record_id}/apply')
    async def apply_rights(tenant:OpaqueId,record_id:ResourceId,request:Request,actor=Depends(principal)):return privacy.apply(actor,tenant,record_id,corr(request))
    @app.post('/v1/tenants/{tenant}/privacy/breaches',status_code=201)
    async def breach(tenant:OpaqueId,body:Breach,request:Request,actor=Depends(principal)):return privacy.breach(actor,tenant,body,corr(request))
    @app.get('/v1/tenants/{tenant}/privacy/breaches/{record_id}')
    async def breach_view(tenant:OpaqueId,record_id:ResourceId,request:Request,actor=Depends(principal)):return privacy.breach_view(actor,tenant,record_id,corr(request))
    @app.post('/v1/tenants/{tenant}/fraud/observations',status_code=201)
    async def fraud_observation(tenant:OpaqueId,body:FraudObservation,request:Request,actor=Depends(principal)):return fraud.observe(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/fraud/observations/{record_id}/verify')
    async def fraud_verification(tenant:OpaqueId,record_id:ResourceId,body:FraudVerification,request:Request,actor=Depends(principal)):return fraud.verify(actor,tenant,record_id,body,corr(request))
    @app.post('/v1/tenants/{tenant}/incidents',status_code=201)
    async def incident(tenant:OpaqueId,body:Incident,request:Request,actor=Depends(principal)):return incidents.create(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/incidents/{record_id}/transition')
    async def transition(tenant:OpaqueId,record_id:ResourceId,body:IncidentTransition,request:Request,actor=Depends(principal)):return incidents.transition(actor,tenant,record_id,body,corr(request))
    @app.post('/v1/tenants/{tenant}/containments',status_code=201)
    async def containment(tenant:OpaqueId,body:Containment,request:Request,actor=Depends(principal)):return incidents.propose_containment(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/containments/{record_id}/execute-lab')
    async def contain(tenant:OpaqueId,record_id:ResourceId,request:Request,actor=Depends(principal)):return incidents.execute(actor,tenant,record_id,corr(request))
    @app.post('/v1/tenants/{tenant}/containments/{record_id}/reconcile')
    async def reconcile(tenant:OpaqueId,record_id:ResourceId,request:Request,actor=Depends(principal)):return incidents.reconcile(actor,tenant,record_id,corr(request))
    @app.post('/v1/tenants/{tenant}/remediations',status_code=201)
    async def remediate(tenant:OpaqueId,body:RemediationPlan,request:Request,actor=Depends(principal)):return remediation.plan(actor,tenant,body,corr(request))
    @app.post('/v1/tenants/{tenant}/remediations/{record_id}/materialize-lab')
    async def materialize(tenant:OpaqueId,record_id:ResourceId,request:Request,actor=Depends(principal)):return remediation.materialize(actor,tenant,record_id,corr(request))
