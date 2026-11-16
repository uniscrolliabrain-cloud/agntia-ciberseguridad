# Contratos, gates y handoff maestro de FreeBuff

## Contrato del slice (diseño a verificar, no afirmación de endpoints existentes)

```text
Owner / LAIA / Pedro (UI de /agente)
  -> Kernel: tenant + capability + scope + approval + audit event
  -> Adapter TS server-only (versioned, no direct DB access)
  -> Cyber API /v1/tenants/{tenant}/... (paths reales a descubrir)
  -> Job/outbox + worker + allowlist + OCI scanner
  -> Findings normalizados + evidence vault + ledger
  -> Report + approval + retest + audit events -> UI
```

**Campos contractuales mínimos a proponer:** `schemaVersion`, `tenantId`, `actorId`, `assetId`, `scopeId`, `approvalId`, `runId`, `correlationId`, `causationId`, `idempotencyKey`, `requestedAt`, `expiresAt`, `status`, `evidenceRefs`. La autorización se verifica en cada transición, no se hereda de un prompt. Identificadores ajenos a tenant devuelven denegación sin filtrar existencia. Los campos son propuesta de contrato: mapear primero los equivalentes existentes.

## Gates transversales

| Gate | Condición demostrable | Rechazo |
|---|---|---|
| G0 baseline | SHA, código y test por capacidad | Roadmap antiguo usado como prueba |
| G1 autorización | ROE/allowlist + tenant + capacidad + aprobación | Cualquier acción sin scope |
| G2 aislamiento | OCI real, sin red, límites y sin rutas arbitrarias | Sandbox local para código no confiable |
| G3 integridad | Scanner real, receipts, provenance, SBOM/audit | BLOCKED presentado como PASS |
| G4 custodia | Cifrado, claves, backup externo, restore medido | Master key sin plan y restore imposible |
| G5 resiliencia | Idempotencia, fencing, kill switch, alertas | Efectos duplicados o ejecución revocada |
| G6 integración | Contrato Python↔TS↔/agente y eventos | LLM con privilegios directos |
| G7 dogfood | 1 activo propio, 2 tenants sintéticos, informe y retest | Escaneo fuera de scope o fuga |
| G8 beta | Review independiente, coste, rollback, owner GO | Despliegue o cliente sin permiso |

## Matriz de decisiones del founder

`DEC-01` hosting OCI y región UE; `DEC-02` gestor de secretos; `DEC-03` almacenamiento externo; `DEC-04` custodia/KMS; `DEC-05` destino alertas y receptor; `DEC-06` IdP/roles; `DEC-07` presupuesto mensual y por run; `DEC-08` activos propios/ROE; `DEC-09` autorización de patchset /agente; `DEC-10` autorización de deploy beta; `DEC-11` revisor independiente; `DEC-12` privacidad/ROE/DPA para cliente futuro. **No pedir tokens en documentos o chats.** Registrar `PENDING` con alternativa local hasta resolver.

## Plantilla de reporte obligatoria

```md
# VS-XX — Reporte
Base SHA: | Final SHA: | Branch/PR: | Fecha: | Actor:
Paths reales inspeccionados:
Estado previo / código existente:
Delta mínimo implementado:
Patchset por archivo (add/modify/delete):
Comandos / exit / CI links / skips:
Negativos y failure injection:
Evidencia redactada / hashes:
Tenancy, autorización y secretos:
Coste / latencia / límites:
Gates PASS/PARTIAL/BLOCKED/NOT_VERIFIED:
Riesgos / deuda / incompatibilidades:
Rollback y compatibilidad:
Dependencias founder:
Revisión independiente:
Siguiente campaña:
```

## Prompt de handoff para FreeBuff

> Trabaja en `uniscrolliabrain-cloud/agntia-ciberseguridad`. Lee íntegramente `docs/operacion-actual/campanas-vertical-slice-beta/README.md`, `01-CAMPANAS-BASE-Y-SEGURIDAD.md`, `02-CAMPANAS-INTEGRACION-Y-DOGFOODING.md` y `03-CONTRATOS-GATES-HANDOFF.md`, además de las fuentes enlazadas. Ejecuta las campañas VS-00→VS-13 secuencialmente, cada una en rama nueva desde main actualizado y con PR, sin merge ni despliegue automático. Primero audita implementación real, evita duplicar trabajo y aplica solo deltas demostrados. En cada campaña deja REPORT/EVIDENCE/PATCHSET/ROLLBACK y tests positivos/negativos. Cuando falte cuenta, token, autorización o acceso a /agente, documenta BLOCKED y sigue solo con tareas seguras independientes. No inventes PASS ni modifiques `docs/release/status.json` sin evidencia. No ejecutes escaneos sobre terceros. Para acciones externas, integraciones en /agente, deploy beta o merge, solicita aprobación del founder. Objetivo: beta privada dogfooding de ciberseguridad sobre activos propios con aprobación humana, informes, evidencias y retest; nunca activar cliente por defecto.

## Orden de review

FreeBuff implementa; Codex/revisor comprueba SHA, diff, tests y seguridad. Founder aprueba gates externos. Las campañas no presuponen que un test sintético sustituya el pilotaje. Registrar todos los desvíos y nuevos hallazgos, sin reescribir los reportes históricos.
