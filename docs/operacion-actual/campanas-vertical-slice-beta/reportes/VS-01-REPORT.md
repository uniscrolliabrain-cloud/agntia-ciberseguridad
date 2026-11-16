# VS-01 — Contrato del slice y amenaza

**Base SHA:** `2da922ff8ae33bfb0824ae2a6dcec3f3b00e1c93`
**Branch:** `feat/cyber-vs-01-contracts`
**Fecha:** 2026-11-16
**Estado:** P0/P1 completos. P2 (código) **BLOCKED** por diseño de persistencia y revisión.

> **Corrección (VS-01A, PR #16):** el hallazgo 3 estaba invertido. `RemediationPlan.finding_id: Hash`
> es correcto y el hash de 64 es el id canónico; el defecto estaba en el contrato `Finding`, ya
> corregido y probado. El hallazgo 2 (`causation_id`) es real pero de impacto bajo: nadie
> reconstruye el grafo con esa columna. Ver `VS-01A-CORRECCION-IMPACTO.md`.

## Resultado principal

Los ocho contratos que pedía la campaña **no faltan en bloque**: seis existen con otro nombre y dos
no tienen contrato versionado. Añadir campos a ciegas habría duplicado comportamiento ya probado.
El mapeo completo está en [VS-01-CONTRACT-MAP.md](VS-01-CONTRACT-MAP.md).

| Propuesto | Real | Estado |
|---|---|---|
| `AuditScopeV1` | `AssetPublic` + `GrantCreate` + `Profile` | EXISTE COMPUESTO |
| `AuditRunRequestV1` | `AuditJobCreate` + header `Idempotency-Key` + `X-Correlation-Id` | EXISTE, clave fuera del body |
| `AuditRunStatusV1` | `Job` + `jobs/store.public()` + `Job` del SDK | EXISTE |
| `FindingV1` | `Finding` | EXISTE |
| `EvidenceRefV1` | `Evidence` | EXISTE |
| `ApprovalRefV1` | `Approval` | EXISTE |
| `RetestRequestV1` | flujo en `governance/remediation.py` y `reviews.py` | **GAP de contrato** |
| `AuditEventV1` | `db.audit(...)` sin modelo versionado | **GAP de contrato** |

## Hallazgos

1. **Idempotencia real, no documentada en el contrato.** `jobs/store.py` exige clave de 8–100
   caracteres, la liga a `tenant_id + operation + key`, guarda `request_hash` y `binding_id`, y
   responde `replayed: true` en repetición. El body no lleva la clave: va en cabecera. Correcto para
   seguridad, pero el contrato del slice debe declararlo explícitamente.
2. **`causation_id` se rellena con la correlación.** En `_submit`, `causation_id` recibe el mismo
   valor que `correlation_id`, lo que pierde la cadena causal. No se corrige sin revisar el modelo
   de eventos: puede afectar auditoría y replay.
3. **`finding_id` es un hash en remediación.** `RemediationPlan.finding_id` usa `Hash`, mientras
   `Finding.id` es `ResourceId`. Dos identificadores para la misma entidad; hay que fijar cuál es
   canónico antes de un retest contractual.
4. **No hay contrato de evento de auditoría.** Los eventos se escriben con `db.audit`, con tenant,
   actor, acción y correlación, pero sin esquema versionado ni hash de payload exportable.
5. **El “scope” no es un objeto.** Cliente y kernel deben componer activo, grant, perfil y ventana.
   Es defendible, pero el SDK no expone un helper que impida olvidar `expires_at`.

## Delta recomendado (no aplicado)

1. Documentar en el contrato del SDK que la idempotencia es cabecera obligatoria y que el body no la
   lleva.
2. Introducir `AuditEventV1` como contrato de solo lectura sobre la tabla de auditoría, sin cambiar
   la escritura.
3. Introducir `RetestRequestV1` cuando exista persistencia de retest ligada a finding canónico.
4. Decidir `finding_id`: `ResourceId` o fingerprint, no ambos.

Aplicar 2–4 exige migración o cambio de esquema y revisión independiente; por eso P2 queda BLOCKED
en esta campaña y no se convierte en un parche cosmético.

## Gates

| Gate | Estado |
|---|---|
| G0 baseline | PASS (VS-00) |
| G1 autorización | N/A: no se ejecutaron acciones |
| G6 integración | **BLOCKED**: falta autorización de `/agente` y aprobación del contrato |
| Revisión independiente | **PENDING** |

## Siguiente

VS-02 (runner OCI y herramientas) puede empezar con el host actual: el job OCI de CI ya demostró
aislamiento; falta fijar versiones/digests y ejecutar Gitleaks/OSV/Semgrep/Trivy reales sobre el
fixture sintético.
