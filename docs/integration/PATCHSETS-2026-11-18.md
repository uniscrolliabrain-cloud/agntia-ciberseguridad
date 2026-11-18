# Registro de patchsets — 2026-11-18

**Repos:** `agntia-ciberseguridad` (hijo, cambios aplicados en árbol de trabajo) y `agente` (padre, cambios **propuestos, no aplicados**).
**Regla:** nada se commitea, fusiona ni despliega sin autorización expresa. El clon de `agente` es de solo lectura; su patchset es especificación para su equipo, no un cambio realizado.

## A. Patchsets aplicados en el hijo

Todos viven en el árbol de trabajo de `main@525769a` sin commit. El artefacto de referencia es `@agntia/ciberseguridad@0.1.0-alpha.3`.

### PS-H1 · Superficie de delegaciones en el SDK (I-04)

| Campo | Valor |
|---|---|
| Repo | `agntia-ciberseguridad` |
| Estado | **Aplicado en árbol** |
| Ficheros | `typescript/src/client.ts`, `typescript/package.json`, `typescript/package-lock.json` |
| Cambio | `createManifest`, `approveManifest`, `issueDelegation`, `revokeDelegation`; validación cerrada, solo servidor; bump a `0.1.0-alpha.3` |
| Pruebas | `typescript/test/client.test.mjs`, `typescript/test/agent-contract.test.mjs`, `tests/contracts/test_agent_sdk_live.py` |
| Evidencia | SDK 10 pass / 2 skip; contrato vivo loopback completo |
| Rollback | Revertir los cuatro métodos y volver a `alpha.2`; el padre no consume `alpha.3` todavía |
| Riesgo | Cambio de superficie: consumidores deben fijar `0.1.0-alpha.3` explícitamente |

### PS-H2 · `tenant_id` en la proyección de findings (I-09)

| Campo | Valor |
|---|---|
| Repo | `agntia-ciberseguridad` |
| Estado | **Aplicado en árbol** |
| Ficheros | `agntia_ciberseguridad/agents/capabilities.py`, `tests/security/test_agent_gateway.py` |
| Cambio | La lectura de findings incluye `tenant_id`; prueba `DelegationProjectionTests` |
| Pruebas | `tests.security.test_agent_gateway` (22 casos) |
| Rollback | Quitar el campo; el consumidor ya tolera su ausencia |
| Riesgo | Bajo; añade un campo, no lo quita |

### PS-H3 · Deriva de `Job.state` (I-10)

| Campo | Valor |
|---|---|
| Repo | `agntia-ciberseguridad` |
| Estado | **Aplicado en árbol** |
| Ficheros | `agntia_ciberseguridad/contracts.py`, `docs/implementation/schemas/Job.json` |
| Cambio | `Literal['completed','partial']`, sin `succeeded` |
| Pruebas | Suite completa; exportación de 13 esquemas |
| Rollback | Restaurar el literal anterior y regenerar esquema |
| Riesgo | Bajo; alinea contrato con el store, que ya escribía esos estados |

### PS-H4 · Artefacto determinista y procedencia (I-07)

| Campo | Valor |
|---|---|
| Repo | `agntia-ciberseguridad` |
| Estado | **Aplicado en árbol** |
| Ficheros | `typescript/scripts/pack.mjs`, `typescript/scripts/provenance.mjs`, `typescript/PROVENANCE.json`, `typescript/package.json`, `typescript/test/pack.test.mjs`, `.github/workflows/runtime.yml`, `.gitignore`, `typescript/README.md` |
| Cambio | Normalización tar (mtime/uid/gid/uname/gname/checksum) + gzip fijo; salida `.pack/`; digest de contenido; `pack:deterministic`, `provenance:write`, `provenance:check`; CI ejecuta el check |
| Pruebas | Dos packs con SHA `09c94d52…`; `provenance:check` verde; prueba de determinismo en `npm test` |
| Rollback | Quitar scripts y el paso de CI; el paquete sigue siendo instalable por workspace |
| Riesgo | `PROVENANCE.json` debe regenerarse al cambiar `dist`, `README.md` o `package.json`; el CI lo detecta |

### PS-H5 · Documentación de la resolución

| Campo | Valor |
|---|---|
| Repo | `agntia-ciberseguridad` |
| Estado | **Aplicado en árbol** |
| Ficheros | `docs/integration/AUDITORIA-INSTALACION-AGENTE-2026-11-18.md`, `docs/integration/PATCHSET-AGENTE.md`, `docs/auditoria-runtime/AUDITORIA-COMPLETA-2026-11-18.md`, este registro |
| Cambio | Estado de I-04/I-07/I-09/I-10, campañas, límites y patchsets fechados |
| Pruebas | `validate_foundation.py` PASS |
| Rollback | Revertir documentos; no afecta código |

**Orden de aplicación del hijo:** PS-H3 → PS-H2 → PS-H1 → PS-H4 → PS-H5. Los tres primeros son independientes entre sí; PS-H4 asume el build final y PS-H5 documenta el conjunto.

---

## B. Patchsets propuestos para el padre (`agente`)

**No aplicados.** Cada uno indica archivos esperados en `agente`; las rutas pueden variar y deben confirmarse contra `main@3f15ca8` antes de editar. Dependencia dura: PS-P3 requiere PS-P1; PS-P4 requiere PS-P2 y PS-P3; PS-P5 requiere PS-P3; PS-P6 requiere todos.

### PS-P1 · Configuración y secretos por referencia (I-02)

| Campo | Valor |
|---|---|
| Repo | `agente` |
| Estado | **Propuesto — no aplicado** |
| Superficie | `.env.example`, `apps/server/src/config.ts` |
| Cambio | `CYBER_BASE_URL`, `CYBER_APPROVED_ORIGIN`, `CYBER_TENANT_MAP`, `CYBER_AGENT_BINDING_REF`, `CYBER_HUMAN_ISSUER_REF`, `CYBER_AGENT_READER_REF`, `CYBER_ENABLED=false`; validación al arranque; secretos por referencia, nunca en claro |
| Pruebas exigidas | Config inválida aborta el arranque; origen no aprobado rechazado; sin secretos en logs |
| Rollback | Flag apagado por defecto; retirar variables |
| Aceptación | Arranque limpio sin `CYBER_*` sigue funcionando; con `CYBER_ENABLED=true` y config inválida falla cerrado |

### PS-P2 · PDP real y broker de delegación just-in-time (I-03, I-08)

| Campo | Valor |
|---|---|
| Repo | `agente` |
| Estado | **Propuesto — no aplicado** |
| Superficie | `apps/server/src/engine/security-v2/sdk-adapter.ts`, módulo de autorización existente |
| Cambio | Implementar `current()` sobre membresía/actor/tenant; `delegation()` con aprobación humana y `POST /delegations` vía SDK; verificar `result.delegation_id === grant.grantId`, `flows` vacíos en lecturas y `limit` |
| Pruebas exigidas | Dos tenants; aprobación denegada; delegación revocada; `delegation_id` distinto rechazado; timeout sin reintento ciego |
| Rollback | Mantener el flag apagado; el bridge no se compone |
| Aceptación | Ninguna lectura sin delegación vigente; fallo cerrado ante respuesta inconsistente |

### PS-P3 · Migración idempotente al arranque (I-01)

| Campo | Valor |
|---|---|
| Repo | `agente` |
| Estado | **Propuesto — no aplicado** |
| Superficie | `apps/server/src/index.ts`, migraciones del motor |
| Cambio | Registrar la migración de `cognition_v2_cyber_cursors` e `cognition_v2_cyber_inbox`, idempotente, solo con el flag activo |
| Pruebas exigidas | Arranque limpio crea tablas; segundo arranque no falla; base existente no se altera |
| Rollback | Migración aditiva; no borrar tablas |
| Aceptación | Reinicio real deja el esquema listo sin pasos manuales |

### PS-P4 · Ruta autenticada y tools del modelo (I-05)

| Campo | Valor |
|---|---|
| Repo | `agente` |
| Estado | **Propuesto — no aplicado** |
| Superficie | `apps/server/src/app.ts`, `CapabilityRegistry`, `buildToolExecutors()` |
| Cambio | Ruta que sirve las tres lecturas con tenant resuelto en servidor; registrar `security.assets.read`, `security.findings.read`, `security.jobs.read` con `sideEffects: ["delegation.consume"]`, `at-most-once`, `retryable:false`; input cerrado y recurso elegido por servidor |
| Pruebas exigidas | Allowlist de prompt; input no vacío rechazado; inyección de tenant/URL/token rechazada; UI sin selector de tenant |
| Rollback | Retirar ruta y registro de capacidades |
| Aceptación | El modelo solo puede invocar las tres lecturas; ningún parámetro de autorización viene del cliente |

### PS-P5 · Relay, cursor y alertas (I-06)

| Campo | Valor |
|---|---|
| Repo | `agente` |
| Estado | **Propuesto — no aplicado** |
| Superficie | Scheduler/worker, `event-relay.ts`, `infra/observability/alerts.yaml` |
| Cambio | Job periódico por tenant con `consumer_id` estable y cursor durable; proyección transaccional antes del ACK; alertas para `CHILD_ACK_PENDING`, `SECURITY_EVENT_HASH_CONFLICT`, `SECURITY_EVENT_INVALID` |
| Pruebas exigidas | ACK perdido y reintento; reinicio con cursor; duplicado no reproyecta; evento inválido alerta |
| Rollback | Apagar el job; el cursor se conserva |
| Aceptación | Un job del hijo aparece una sola vez en cognición, con ACK confirmado o pendiente visible |

### PS-P6 · Certificación de integración (I-11, C14)

| Campo | Valor |
|---|---|
| Repo | `agente` (+ hijo desplegado) |
| Estado | **Propuesto — no aplicado** |
| Superficie | Entorno de staging, runbook, gate C14 |
| Cambio | Batería: dos tenants, revocación en vuelo, expiración, hijo caído, desfase de reloj, ACK perdido, RLS Postgres real; runbook y rollback con evidencia |
| Pruebas exigidas | Todas las anteriores ejecutadas y archivadas; `reconciliation_required` mapeado y probado |
| Rollback | Procedimiento documentado y ensayado |
| Aceptación | Solo entonces reevaluar C14; no cambiar `BLOCKED_CONFIGURATION` por documentación |

---

## C. Orden, gates y límites

1. Aplicar PS-H1…PS-H4 en el hijo, commitear y verificar CI (incluido `provenance:check` y el gate de esquemas).
2. Publicar o entregar el artefacto `alpha.3` con su `PROVENANCE.json`; actualizar el vendor y el lock del padre.
3. Aplicar PS-P1 → PS-P2 → PS-P3 → PS-P4 → PS-P5, cada uno con su PR y pruebas; el flag permanece apagado hasta PS-P6.
4. PS-P6 en staging con dos tenants; solo después tocar C14.

**Gate G1 (seguridad):** ninguna lectura sin delegación humana vigente; tenant y recurso elegidos en servidor; fallo cerrado.
**Gate G2 (evidencia):** cada paso con comando, salida, SHA y rollback; lo no ejecutado se declara `NOT_VERIFIED`.

**Fuera de alcance:** no se aplicó nada en `agente`, no se publicó el paquete, no se desplegó y no se modificó el estado de release. `docs/release/status.json` conserva 2 PASS / 40 PARTIAL e `independent_review: PENDING`.

**Fecha:** 2026-11-18. Cambios del hijo en árbol de trabajo, sin commit por falta de autorización.
