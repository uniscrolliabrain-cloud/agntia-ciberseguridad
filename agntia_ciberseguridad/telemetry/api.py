"""Public traceparent/baggage are data, never identity or a cross-tenant trace parent."""
import hashlib
import hmac
import os
import time
from fastapi.responses import PlainTextResponse,JSONResponse
from ..errors import DomainError

class ObserveRequests:
    def __init__(self,app,telemetry):self.app=app;self.telemetry=telemetry
    async def __call__(self,scope,receive,send):
        if scope['type']!='http':return await self.app(scope,receive,send)
        start=time.perf_counter();status=500;path=scope.get('path','')
        operation='health' if path.startswith('/health/') else 'metrics' if path=='/metrics' else 'read' if scope.get('method')=='GET' else 'write'
        async def observed_send(message):
            nonlocal status
            if message['type']=='http.response.start':status=message['status']
            await send(message)
        # External baggage and traceparent are intentionally not extracted here.
        with self.telemetry.span('api.request',root=True,component='api',operation=operation):
            try:return await self.app(scope,receive,observed_send)
            finally:self.telemetry.metrics.request(operation,status,time.perf_counter()-start)

def metrics_response(request,service):
    reference=service.settings.metrics_token_env
    if not reference:raise DomainError('not_found','Recurso no disponible',404)
    value=os.getenv(reference,'');header=request.headers.get('Authorization','')
    if len(value)<24:raise DomainError('metrics_unavailable','Credencial operativa no disponible',503)
    hashed=hashlib.sha256(value.encode()).hexdigest()
    for binding in service.settings.principals:
        try:
            if hmac.compare_digest(service.auth.current(binding.id).credential_fingerprint,hashed):
                raise DomainError('metrics_credential_scope','Credencial operativa debe estar separada',503)
        except DomainError as error:
            if error.code=='metrics_credential_scope':raise
            continue
    if not hmac.compare_digest(header.encode(),('Bearer '+value).encode()):raise DomainError('auth','Autenticación operativa requerida',401)
    return PlainTextResponse(service.telemetry.metrics.export(),media_type='text/plain; version=0.0.4')
