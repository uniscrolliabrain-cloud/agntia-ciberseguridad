"""API foundation: inventory, human-reviewed grants and non-executing preflight."""
import asyncio
import json
import logging
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from . import __version__
from .auth import Principal
from .config import Settings
from .contracts import AssetCreate, AuditPreview, GrantApproval, GrantCreate, GrantRevocation, OpaqueId, ResourceId
from .errors import DomainError
from .service import Service
from .storage import Database, CURRENT_SCHEMA
from .snapshots import SnapshotStore
from .jobs.store import JobStore
from .jobs.contracts import AuditJobCreate,CancelJob
from .findings.store import FindingStore


class RequestBoundary:
    """Bound bytes before parsing; header/body contents never enter error responses."""
    def __init__(self, app, maximum):
        self.app = app
        self.maximum = maximum

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = scope.get("headers", [])
        correlations = [v for k, v in headers if k.lower() == b"x-correlation-id"]
        try:
            corr = str(UUID(correlations[0].decode())) if len(correlations) == 1 else str(uuid4())
        except (ValueError, UnicodeError):
            corr = str(uuid4())
        scope.setdefault("state", {})["correlation_id"] = corr
        async def respond(error):
            logging.getLogger("agntia.security").warning(json.dumps({"event": "request.rejected", "code": error.code, "correlation_id": corr}))
            await JSONResponse(error.public(corr), status_code=error.status, headers={"X-Correlation-ID": corr})(scope, receive, send)
        for name in (b"authorization", b"content-length"):
            if sum(k.lower() == name for k, _ in headers) > 1:
                return await respond(DomainError("validation", "Cabeceras ambiguas", 400))
        lengths = [v for k, v in headers if k.lower() == b"content-length"]
        if lengths:
            try:
                value = int(lengths[0])
                if value < 0:
                    raise ValueError()
            except ValueError:
                return await respond(DomainError("validation", "Longitud de entrada inválida", 400))
            if value > self.maximum:
                return await respond(DomainError("request_too_large", "Entrada demasiado grande", 413))
        messages = []
        total = 0
        try:
            async with asyncio.timeout(5):
                while True:
                    event = await receive()
                    if event["type"] == "http.disconnect":
                        return
                    total += len(event.get("body", b""))
                    if total > self.maximum or len(messages) >= 256:
                        return await respond(DomainError("request_too_large", "Entrada demasiado grande", 413))
                    messages.append(event)
                    if not event.get("more_body", False):
                        break
        except TimeoutError:
            return await respond(DomainError("request_timeout", "Entrada no recibida a tiempo", 408))
        offset = 0
        async def buffered_receive():
            nonlocal offset
            if offset < len(messages):
                result = messages[offset]
                offset += 1
                return result
            return await receive()
        async def correlated_send(message):
            if message["type"] == "http.response.start":
                message = {**message, "headers": [*message.get("headers", []), (b"x-correlation-id", corr.encode())]}
            await send(message)
        return await self.app(scope, buffered_receive, correlated_send)


def create_app(settings: Settings | None = None):
    settings = settings or Settings.from_env()
    database = Database(settings.data_dir, settings.db_timeout_seconds)
    database.migrate()
    database.provision_tenants(t for p in settings.principals for t in p.tenants)
    service = Service(settings, database)
    app = FastAPI(title="Agntia Ciberseguridad", version=__version__, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.service = service
    jobs = JobStore(service)
    app.state.jobs = jobs
    findings = FindingStore(service)
    snapshots = SnapshotStore(service)
    app.state.snapshots = snapshots
    app.state.settings = settings
    app.state.db = database
    app.add_middleware(RequestBoundary, maximum=settings.max_request_bytes)

    async def principal(request: Request):
        return service.auth.authenticate(request.headers.get("Authorization"))

    def correlation(request):
        return request.state.correlation_id

    def failure_audit(request, code):
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return
        logging.getLogger("agntia.security").warning(json.dumps({"event": "request.rejected", "code": code, "correlation_id": correlation(request)}))
        tenant = request.path_params.get("tenant", "")
        try:
            actor = service.auth.authenticate(request.headers.get("Authorization"))
            service.authorize(actor, tenant, "assets.read")
        except DomainError:
            return  # No trustworthy principal/tenant exists for a per-tenant audit entry.
        with database.transaction() as db:
            database.audit(db, tenant, actor.actor_id, "request.rejected", tenant, correlation(request), {"code": code})

    @app.exception_handler(DomainError)
    async def domain_failure(request, exc):
        try:
            failure_audit(request, exc.code)
        except Exception:
            exc = DomainError("audit_unavailable", "No se pudo registrar el resultado; operación denegada", 503)
        return JSONResponse(exc.public(correlation(request)), status_code=exc.status)

    @app.exception_handler(RequestValidationError)
    async def validation_failure(request, exc):
        return await domain_failure(request, DomainError("validation", "Entrada inválida para esta capacidad", 422))

    @app.exception_handler(HTTPException)
    async def http_failure(request, exc):
        return await domain_failure(request, DomainError("not_found" if exc.status_code == 404 else "request_rejected", "Recurso o método no disponible", exc.status_code))

    @app.exception_handler(Exception)
    async def unexpected_failure(request, exc):
        logging.getLogger("agntia.security").error(json.dumps({"event": "request.failed", "code": "internal", "correlation_id": correlation(request)}))
        error = DomainError("internal", "La operación no pudo completarse; verificar estado antes de repetir", 500)
        result = error.public(correlation(request))
        result["reconciliation_required"] = request.method in ("POST", "PUT", "PATCH", "DELETE")
        return JSONResponse(result, status_code=500, headers={"X-Correlation-ID": correlation(request)})

    @app.get("/health/live")
    async def live():
        return {"status": "alive", "version": __version__}

    @app.get("/health/ready")
    async def ready():
        try:
            with database.connection(readonly=True) as db:
                schema = db.execute("SELECT max(version) FROM schema_migrations").fetchone()[0] == CURRENT_SCHEMA
            credentials = False
            for binding in settings.principals:
                try:
                    service.auth.current(binding.id)
                    credentials = True
                except DomainError:
                    continue
            ok = bool(schema and credentials)
        except Exception:
            ok = False
        return JSONResponse({"ready": ok, "scope": "foundation_only", "security_scanners_ready": False}, status_code=200 if ok else 503)

    @app.get("/v1/tenants/{tenant}/assets")
    async def assets(tenant: OpaqueId, actor: Principal = Depends(principal), limit: int = Query(100, ge=1, le=100), after: str = Query("", max_length=32)):
        return service.list_assets(actor, tenant, limit, after)

    @app.post("/v1/tenants/{tenant}/assets", status_code=201)
    async def create_asset(tenant: OpaqueId, body: AssetCreate, request: Request, actor: Principal = Depends(principal)):
        return service.create_asset(actor, tenant, body, correlation(request))

    @app.get("/v1/tenants/{tenant}/assets/{asset_id}")
    async def asset(tenant: OpaqueId, asset_id: ResourceId, actor: Principal = Depends(principal)):
        return service.get_asset(actor, tenant, asset_id)

    @app.post("/v1/tenants/{tenant}/grants", status_code=201)
    async def propose(tenant: OpaqueId, body: GrantCreate, request: Request, actor: Principal = Depends(principal)):
        return service.propose_grant(actor, tenant, body, correlation(request))

    @app.get("/v1/tenants/{tenant}/grants/{grant_id}")
    async def grant(tenant: OpaqueId, grant_id: ResourceId, actor: Principal = Depends(principal)):
        return service.get_grant(actor, tenant, grant_id)

    @app.post("/v1/tenants/{tenant}/grants/{grant_id}/approve")
    async def approve(tenant: OpaqueId, grant_id: ResourceId, body: GrantApproval, request: Request, actor: Principal = Depends(principal)):
        return service.approve_grant(actor, tenant, grant_id, body, correlation(request))

    @app.post("/v1/tenants/{tenant}/grants/{grant_id}/revoke")
    async def revoke(tenant: OpaqueId, grant_id: ResourceId, body: GrantRevocation, request: Request, actor: Principal = Depends(principal)):
        return service.revoke_grant(actor, tenant, grant_id, body, correlation(request))

    @app.post("/v1/tenants/{tenant}/audits/preview")
    async def preview(tenant: OpaqueId, body: AuditPreview, request: Request, actor: Principal = Depends(principal)):
        return service.preview(actor, tenant, body, correlation(request))

    @app.post("/v1/tenants/{tenant}/snapshots", status_code=201)
    async def acquire_snapshot(tenant: OpaqueId, body: AuditPreview, request: Request, actor: Principal = Depends(principal)):
        # IO is bounded by server limits; grant/principal revalidation occurs during the copy.
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(snapshots.acquire, actor, tenant, body, correlation(request))

    @app.get("/v1/tenants/{tenant}/snapshots/{snapshot_id}")
    async def snapshot(tenant: OpaqueId, snapshot_id: ResourceId, actor: Principal = Depends(principal)):
        from starlette.concurrency import run_in_threadpool
        manifest, _ = await run_in_threadpool(snapshots.verify, actor, tenant, snapshot_id)
        return manifest

    @app.post("/v1/tenants/{tenant}/audits", status_code=202)
    async def submit_audit(tenant: OpaqueId, body: AuditJobCreate, request: Request, actor: Principal = Depends(principal)):
        from starlette.concurrency import run_in_threadpool
        return await run_in_threadpool(jobs.submit,actor,tenant,body,request.headers.get("Idempotency-Key"),correlation(request))

    @app.get("/v1/tenants/{tenant}/jobs/{job_id}")
    async def job_status(tenant: OpaqueId, job_id: ResourceId, actor: Principal = Depends(principal)):
        return jobs.get(actor,tenant,job_id)

    @app.post("/v1/tenants/{tenant}/jobs/{job_id}/cancel")
    async def cancel_job(tenant: OpaqueId, job_id: ResourceId, body: CancelJob, request: Request, actor: Principal = Depends(principal)):
        return jobs.cancel(actor,tenant,job_id,body.expected_revision,correlation(request))

    @app.get("/v1/tenants/{tenant}/findings")
    async def list_findings(tenant: OpaqueId, actor: Principal = Depends(principal), limit: int = Query(100,ge=1,le=100), after: str = Query("",pattern=r"^(?:[a-f0-9]{64})?$")):
        return findings.list(actor,tenant,limit=limit,after=after)

    @app.get("/v1/tenants/{tenant}/findings/{finding_id}/history")
    async def finding_history(tenant: OpaqueId, finding_id: str, actor: Principal = Depends(principal), limit: int = Query(100,ge=1,le=100), after: str = Query("",pattern=r"^(?:[a-f0-9]{32})?$")):
        import re
        if not re.fullmatch("[a-f0-9]{64}",finding_id):raise DomainError("validation","Identificador inválido",422)
        return findings.history(actor,tenant,finding_id,limit=limit,after=after)

    @app.get("/v1/tenants/{tenant}/audit/integrity")
    async def integrity(tenant: OpaqueId, actor: Principal = Depends(principal)):
        return service.audit_integrity(actor, tenant)

    from .features import register_features
    register_features(app,service,principal)
    return app
