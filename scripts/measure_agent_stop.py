"""Ten synthetic stop/next-call checks; no remote process cancellation or SLA claim."""
import json
import statistics
import time
from tests.security.test_agent_gateway import GatewaySetup
from agntia_ciberseguridad.errors import DomainError
from agntia_ciberseguridad.agents.policy import POLICY_HASH

def main():
    fixture=GatewaySetup();fixture.setUp();stops=[];checks=[];denied=0
    try:
        for _ in range(10):
            _,request=fixture.read_grant();started=time.perf_counter()
            fixture.change('agent','agentA');stops.append((time.perf_counter()-started)*1000)
            started=time.perf_counter()
            try:fixture.delegations.use(fixture.agent,'tenantA',request,'stop-measurement')
            except DomainError as error:
                assert error.code in ('agent_policy_stale','agent_stopped');denied+=1
            checks.append((time.perf_counter()-started)*1000)
            fixture.change('agent','agentA',False)
        assert denied==10
        with fixture.f.service.db.connection(readonly=True) as db:assert db.execute('SELECT count(*) FROM delegations WHERE used_at IS NOT NULL').fetchone()[0]==0
        print(json.dumps({'scope':'Synthetic single-node SQLite direct business calls; no HTTP/TLS/remote processes','policy_hash':POLICY_HASH,
            'stops':10,'next_calls_denied_after_ack':denied,'stop_ack_p50_ms':statistics.median(stops),'stop_ack_p95_ms':sorted(stops)[8],
            'next_call_check_p50_ms':statistics.median(checks),'next_call_check_p95_ms':sorted(checks)[8],
            'already_committed_effects_undone':False,'external_model_calls':0,'sdk_available':fixture.f.service.telemetry.available}))
    finally:fixture.tearDown()
if __name__=='__main__':main()
