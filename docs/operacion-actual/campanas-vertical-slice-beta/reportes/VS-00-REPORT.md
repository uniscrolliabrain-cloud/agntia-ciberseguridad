# VS-00 — Auditoría diferencial y trazabilidad

**Base SHA:** `2da922ff8ae33bfb0824ae2a6dcec3f3b00e1c93`
**Final SHA:** el de esta rama, indicado en el PR.
**Branch:** `feat/cyber-vs-00-baseline`
**Fecha:** 2026-11-16
**Actor:** FreeBuff (ejecutor). Diseño de campañas: ChatGPT.

## Objetivo y alcance

Reconciliar el HEAD real con lo que dicen los documentos, medir el estado con comandos
reejecutados y producir un backlog de **deltas**, no de funcionalidades duplicadas.

Incluido: inventario del árbol, suites Python y SDK, gates del laboratorio, recuento de rutas,
workflows y ramas. Excluido: escaneo de terceros, despliegues, cambios de estado en
`docs/release/status.json` y cualquier modificación de `/agente`.

## Estado previo medido (no heredado de un dump)

| Métrica | Valor real en `2da922f` |
|---|---|
| Commits en `main` | 236 |
| Ramas remotas | 23 |
| Archivos Python versionados | 278 |
| Archivos de test Python | 46 |
| Decoradores de ruta encontrados | 88 (`@app|@router` get/post/put/patch/delete) |
| Workflows | 7 |
| Tests middleware | **196 OK, 8 skipped** (requiere instalar `.[dev]`) |
| Tests SDK | **7 tests, 6 pass, 0 fail** |
| Tests laboratorio | **117 OK** |
| `releasecheck` integridad | PASS, `release_eligible=false` |
| `releasecheck --production` | exit 1, fail-closed por audit BLOCKED |
| Validador documental | PASS |

El documento previo hablaba de 84 rutas; el conteo bruto de decoradores da 88. No se afirma que
sean 88 endpoints efectivos: hay que expandir routers y prefijos para cerrarlo. Esa diferencia queda
como hallazgo de inventario, no como cambio de contrato.

## Hallazgo y delta aplicado

El contract test Python↔TS fallaba de forma reproducible en este entorno:

```
SyntaxError [ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX]:
TypeScript parameter property is not supported in strip-only mode
```

Causa: `typescript/src/client.ts` declaraba `CyberError` con parameter properties
(`constructor(public readonly kind: …)`), sintaxis que el modo strip-only de Node rechaza. Node 26
la ejecuta al cargar el cliente desde el test de contrato.

Delta mínimo: constructor explícito y campos declarados, mismo comportamiento y misma forma pública.
Tras el cambio, el test de contrato y los 7 tests del SDK pasan.

## Matriz resumida

La matriz completa está en [VS-00-MATRIZ-CAPACIDADES.md](VS-00-MATRIZ-CAPACIDADES.md). Resumen:

- **Implementado y con test:** contratos Pydantic, assets/grants, jobs con estados, evidencia,
  findings, aprobaciones, SDK TS, cliente Hono, gates del laboratorio, vault y backup del lab.
- **Parcial:** auth/tenancy en rutas (2/42 fases PASS según `status.json`), scanners del middleware
  con adaptadores pero sin binarios/feeds verificados, observabilidad, custodia con clave en host.
- **Bloqueado:** OCI real en host dedicado (aquí no hay runtime; en CI sí se ejecutó el job OCI),
  proveedores externos, `pip-audit`/atestación externa, pilotaje con activos propios (falta ROE y
  autorización del founder), integración `/agente` (prohibido escribir sin permiso).

## Gates

| Gate | Estado | Evidencia |
|---|---|---|
| G0 baseline | **PASS** | SHA, comandos, exits y matriz adjuntos |
| G1 autorización | No aplica todavía | No se ejecutó ninguna acción sobre activos |
| G2 aislamiento | **PARTIAL** | Job OCI en CI pasó en el commit anterior; este workspace no tiene Docker |
| G3 integridad | **PARTIAL** | Scanner real del middleware no ejecutado; `audit BLOCKED` |
| G4 custodia | **PARTIAL** | Vault HKDF + backup verificado; clave maestra en host |
| G5 resiliencia | **PARTIAL** | Leases y fencing probados; cancelación en vuelo pendiente |
| G6 integración | **BLOCKED** | Sin autorización para `/agente` |
| G7 dogfood | **BLOCKED** | Falta ROE e inventario de activos propios |
| G8 beta | **NO-GO** | Review independiente y aceptación pendientes |

## Riesgos y deuda

- El conteo de rutas y su autorización real necesitan una pasada ruta por ruta; VS-00 solo mide.
- `status.json` sigue en `SYNTHETIC_DEMO_NOT_PRODUCTION`; no se tocó.
- La suite raíz depende de instalar `.[dev]`; el entorno restaurado sin dependencias produce 24
  errores de import que **no** son fallos de código.

## Dependencias del founder

Ninguna para VS-00. Para VS-01 solo revisión del contrato.

## Revisión independiente

**PENDING.** Este informe es autoevaluación del ejecutor y no sustituye la revisión de Codex.

## Siguiente campaña

VS-01: mapa de contratos existentes y huecos exactos (`AuditScopeV1`, `AuditRunRequestV1`,
`AuditRunStatusV1`, `FindingV1`, `EvidenceRefV1`, `ApprovalRefV1`, `RetestRequestV1`,
`AuditEventV1`) antes de añadir un solo campo.
