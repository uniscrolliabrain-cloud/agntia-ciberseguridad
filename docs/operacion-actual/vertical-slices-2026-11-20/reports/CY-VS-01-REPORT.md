# CY-VS-01 — Contrato de instalación y paquete reproducible

**Fecha:** 2026-11-20
**Base SHA:** `eaf7da0d60a5adc7302c977cdabdfd3900c922be` (main)
**HEAD SHA:** `52855ea...` (rama `feat/cyber-vertical-slices-installable-20261120`)
**Rama:** `feat/cyber-vertical-slices-installable-20261120`
**Objetivo:** Reutilizar F0–F2 antes de escribir. Congelar `@agntia/ciberseguridad` versión/artefacto/digest/provenance; generar manifest `cyber-capabilities.v1.json`; verificar instalación local reproducible desde tarball.

## Resumen ejecutivo

F0–F2 ya estaban implementados (install.py, scripts/install_manifest.py, scripts/verify_artifact.py, schemas/InstallManifest.json, tests unitarios). Se agregó `cyber-capabilities.v1.json` con el contrato completo de capacidades: 13 capacidades, sideEffects, scopes, risk, approvals, input/output, idempotency, timeouts, error codes, feature flags, fail-closed behavior.

No hay `node`/`npm` en este entorno de ejecución, por lo que `npm pack` y la instalación desde tarball no se pudieron ejecutar directamente. Se documentó como `BLOCKED_FOUNDER` con acción concreta.

## Componentes reutilizados (F0–F2, no se reescribió)

| Componente | Ruta | Estado |
|------------|------|--------|
| InstallManifest modelo | `agntia_ciberseguridad/install.py` | Implementado, Pydantic, fail-closed |
| CLI build/check | `scripts/install_manifest.py` | Implementado |
| CLI verify | `scripts/verify_artifact.py` | Implementado |
| JSON Schema | `docs/implementation/schemas/InstallManifest.json` | Implementado |
| Tests install_artifact | `tests/unit/test_install_artifact.py` | 36 tests (verifican digest, tar entries, provenance) |
| Tests install_manifest | `tests/unit/test_install_manifest.py` | CLI build/check round-trip |
| Tests config_rollout | `tests/unit/test_config_rollout.py` | RolloutConfig, fail-closed |
| Provenance | `typescript/PROVENANCE.json` | `@agntia/ciberseguridad@0.1.0-alpha.3` |
| SDK package.json | `typescript/package.json` | versión 0.1.0-alpha.3, Node >=22, private, UNLICENSED |

## Nuevo archivo: cyber-capabilities.v1.json

**Ruta:** `docs/implementation/schemas/cyber-capabilities.v1.json`

Contenido:
- `schema_version`: "1.0.0"
- `package`: "@agntia/ciberseguridad"
- `version`: "0.1.0-alpha.3"
- `source_sha`: "eaf7da0d60a5adc7302c977cdabdfd3900c922be"
- `status`: "SYNTHETIC_DEMO_NOT_PRODUCTION"
- `production_enabled`: false
- `schemas`: mapeo a contratos existentes (InstallManifest, AssetCreate, GrantCreate, etc.)
- `capabilities`: 13 capacidades con id, name, sideEffects, scopes, risk, approvals, input, output, idempotent, timeout_seconds, error_codes, feature_flags
- `feature_flags`: lab_mode (default false), CYBER_ENABLED (default false)
- `risk_levels`: low/medium/high
- `approval_matrix`: viewer/analyst/operator/reviewer/owner
- `side_effects`: 12 efectos documentados
- `error_codes`: 31 códigos de error con descripción y HTTP status
- `timeouts`: default 30s, scanner_max 300s, delegation_max_ttl 300s, grant_max_days 30
- `idempotency`: header Idempotency-Key, scope tenant+operation
- `fail_closed`: no_credentials → PROVIDER_NOT_CONFIGURED, no_network, no_approval, expired_identity, cross_tenant → 404

## Capacidades definidas (13)

| ID | Riesgo | Aprobaciones | Idempotente | Timeout |
|----|--------|--------------|-------------|---------|
| assets.read | low | viewer | sí | 30s |
| assets.register | medium | analyst/operator/reviewer/owner | sí | 30s |
| grants.propose | medium | analyst/operator/reviewer/owner | no | 30s |
| grants.approve | high | reviewer/owner | no | 30s |
| grants.revoke | high | reviewer/owner | no | 30s |
| audits.preview | low | analyst/operator/reviewer/owner | sí | 30s |
| audits.submit | high | analyst/operator/reviewer/owner | sí | 300s |
| jobs.read | low | viewer/analyst/operator/reviewer/owner | sí | 30s |
| jobs.cancel | medium | analyst/operator/reviewer/owner | no | 30s |
| findings.read | low | viewer/analyst/operator/reviewer/owner | sí | 30s |
| evidence.create | medium | analyst/operator/reviewer/owner | no | 30s |
| reports.create | medium | analyst/operator/reviewer/owner | no | 30s |
| agents.manage | high | owner | no | 30s |
| agents.delegate | high | owner | sí | 300s |
| events.ack | low | reviewer/owner | sí | 30s |

## Gate de instalación (BLOCKED_FOUNDER)

**Requisito:** Instalación local reproducible desde tarball, firma/digest comprobado, sin red/credenciales, 2 ejecuciones idénticas.

**Estado:** No se pudo ejecutar en este entorno porque no hay `node`/`npm` disponibles. `npm pack` y `npm run pack:deterministic` no se pudieron probar.

**Acción concreta para el founder:** Instalar Node.js >=22 y ejecutar en `typescript/`:
```
npm run build && npm run pack:deterministic
```
Verificar que dos ejecuciones producen el mismo SHA256 del tarball.

## Diferencias con comportamiento existente

Ninguna. No se modificó ningún archivo existente. Solo se agregó `cyber-capabilities.v1.json` como documento de contrato declarativo.

## Archivos nuevos/modificados

| Archivo | Acción |
|---------|--------|
| `docs/implementation/schemas/cyber-capabilities.v1.json` | Creado |

## Tests ejecutados

No se agregaron tests nuevos en esta campaña. Los tests existentes de instalación (`test_install_artifact.py`, `test_install_manifest.py`, `test_config_rollout.py`) no se pudieron ejecutar por falta de dependencias (pydantic/fastapi) en este entorno.

## Siguiente campaña

CY-VS-02 — Identidad, tenancy y delegación.

## Archivos relacionados

- `docs/operacion-actual/vertical-slices-2026-11-20/reports/CY-VS-01-EVIDENCE.md`
- `docs/operacion-actual/vertical-slices-2026-11-20/reports/CY-VS-01-ROLLBACK.md`
- `docs/implementation/schemas/InstallManifest.json`
- `agntia_ciberseguridad/install.py`