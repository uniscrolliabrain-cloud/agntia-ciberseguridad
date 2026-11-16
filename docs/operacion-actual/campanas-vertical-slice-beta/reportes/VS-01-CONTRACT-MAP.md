# VS-01 — Mapa de contratos reales

**SHA:** `2da922ff8ae33bfb0824ae2a6dcec3f3b00e1c93`

## Campos transversales

| Campo propuesto | Dónde está hoy | Observación |
|---|---|---|
| `schemaVersion` | `schema_version: Literal[1]` en `AssetPublic`, `Job`, `Evidence`, `Finding`, `Approval`, `AuditJobCreate` | Nombre canónico en snake_case; el SDK TS usa el mismo |
| `tenantId` | `tenant_id` en modelos públicos; en jobs se deriva de la ruta autenticada | El body no acepta tenant: correcto, no se confía en el cliente |
| `actorId` | `actor_id` en `Job` público y `Approval`; en creación se deriva del principal | No se acepta actor en body |
| `assetId` | `AssetPublic.id`, `AuditJobCreate.asset_id` | `ResourceId` de 32 hex |
| `scopeId` | No existe como id único; el alcance es `grant_id` + `asset_id` + `profile` | Composición documentada, no agregado |
| `approvalId` | `Approval.id` con `proposal_hash`, `expires_at`, `state` | Aprobación por hash de propuesta |
| `runId` | `Job.id` | Se devuelve como `id` |
| `correlationId` | `Job.correlation_id`; columna en `jobs`; `db.audit` | Presente end-to-end |
| `causationId` | Columna `jobs.causation_id`, rellenada con la correlación | Inconsistencia semántica sin consumidor; ver VS-01A |
| `idempotencyKey` | Header obligatorio validado en `jobs/store.py`; tabla `job_idempotency` | No viaja en el body |
| `requestedAt` | `created_at` | Nombre distinto, misma semántica |
| `expiresAt` | `GrantCreate.expires_at`, `Approval.expires_at` | El job no tiene expiración propia; la hereda del grant |
| `status` | `Job.state` | Ocho estados terminales/no terminales |
| `evidenceRefs` | `Finding.evidence_ids`, `Evidence.id/sha256` | Cadena por hash |

## Contratos por nombre propuesto

### `AuditScopeV1` → composición existente
`AssetPublic` (activo), `GrantCreate` (ventana, perfil, límites, propósito), `Profile`
(`static_read`, `passive_web`, `active_lab`). No hay objeto único; el cliente debe componerlo.

### `AuditRunRequestV1` → `jobs/contracts.py::AuditJobCreate`
Campos: `asset_id`, `grant_id`, `snapshot_id`, `snapshot_hash`, `expected_grant_revision`,
`profile=static_read`, `tool`, `max_attempts` (1–3), `maximum_cost_cents=0`.
Fuera del body: `Idempotency-Key` (8–100, `[A-Za-z0-9_-]`) y correlación.

### `AuditRunStatusV1` → `contracts.py::Job` y `jobs/store.public()`
`id`, `tenant_id`, `asset_id`, `grant_id`, `snapshot_id`, `actor_id`, `tool`, `state`, `revision`,
`attempts`, `max_attempts`, `cancel_requested`, `error_code`, `result_hash`, `correlation_id`,
`created_at`, `updated_at`. El SDK TS valida `JOB_STATES`.

### `FindingV1` → `contracts.py::Finding`
`id`, `tenant_id`, `job_id`, `fingerprint` (SHA-256), `rule_id`, `tool_id`, `tool_version`,
`severity`, `title`, `evidence_ids`, `state`.

### `EvidenceRefV1` → `contracts.py::Evidence`
`id`, `tenant_id`, `job_id`, `sha256`, `storage_ref`, `size_bytes`, `media_type`, `created_at`.
La subida usa `EvidenceUpload` con base64 y tipos permitidos.

### `ApprovalRefV1` → `contracts.py::Approval`
`id`, `tenant_id`, `proposal_hash`, `actor_id`, `expires_at`, `state`.

### `RetestRequestV1` → **GAP**
Existe flujo de remediación (`RemediationPlan`, casos y revisiones) y revisión de evidencias, pero
no un contrato de petición de retest ligado a un finding canónico. No se crea hasta decidir el
identificador canónico (ver hallazgo 3).

### `AuditEventV1` → **GAP**
Los eventos se escriben con `db.audit(db, tenant, actor, action, resource, correlation, payload)` en
la tabla de auditoría. No hay modelo Pydantic ni esquema TS que versionen ese evento.

## Tipos y validación

- `OpaqueId`: `^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$`.
- `ResourceId`: 32 hex. `Hash`: 64 hex. `Cents`: entero 0–1.000.000.
- Todos los modelos usan `extra="forbid"`, `allow_inf_nan=False`.
- SDK TS replica cierres de objeto y regex; rechaza campos extra en `asset`, `budget`, `delegated`.
