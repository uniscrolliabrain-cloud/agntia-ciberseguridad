# SDK outbox ACK — delta C14

Fecha: 2026-11-15. Base: `main@c3a87cd7991e18a89cb5d8bae938be4ace5b9ae6`.
Rama: `feat/cognition-v2-sdk-ack`. Alcance: SDK servidor y pruebas; no endpoints ni permisos nuevos.

## Problema y cambio

El servicio Python ya ofrece `POST /v1/tenants/{tenant}/outbox/{event_id}/ack`, con RBAC `events.ack`, identidad actual, tenant, hash exacto y ACK idempotente. El SDK alpha.1 permitía poll pero no ACK, por lo que el consumidor durable de AgntiaPro no podía cerrar entregas usando el SDK existente.

`CyberClient.ackOutbox(eventId, {consumer_id,content_hash})` reutiliza el transporte server-only cerrado. Valida ID/ruta, consumer y hash; rechaza campos extra y recibos inconsistentes. La respuesta contiene `id`, `acknowledged:true` y `duplicate`. Un POST con resultado de red incierto conserva `reconciliation_required` y no hace retry automático. La repetición controlada del mismo ID/hash está permitida por el contrato idempotente del servidor.

Versionado: `@agntia/ciberseguridad@0.1.0-alpha.2`; lock npm alineado. El método no se expone como herramienta de modelo ni ruta del BFF Hono y no permite aprobar grants, crear jobs, ejecutar scans o ampliar políticas.

## Validación ejecutada

- `npm test --prefix typescript`: exit 0; checker TypeScript y 8 tests SDK, 7 pass / 1 skip (caso live solo se activa desde Python).
- `CI=1 python -m unittest tests.contracts.test_python_ts tests.integration.test_budget_concurrency`: exit 0; 9 tests pass, sin skips, 5.884 s. Contrato SDK real→FastAPI loopback con fixture audit/outbox sintético: viewer no puede ACK; reviewer confirma, mismo ACK devuelve duplicate; tenantB devuelve not_found; poll no repite el evento confirmado. Incluye pruebas existentes de rollback/outbox/budget sintético.
- No activo externo, scanner, remediación, base de producción o cuenta real fue utilizado.

## Autoridad y estado

El consumidor debe confirmar su efecto local antes de llamar ACK; el SDK no decide si esa condición se cumple. El servidor continúa siendo autoridad de RBAC y tenant. No se ha hecho merge, push ni deploy. La licencia sigue `UNLICENSED`, el producto `production_enabled=false`; este delta no certifica el piloto ni cambia el estado de las campañas del hijo.
