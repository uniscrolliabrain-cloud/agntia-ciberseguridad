# Auditoría de instalación — `agntia-ciberseguridad` → `agente`

Fecha: 2026-11-18 · Alcance: los dos repositorios del ecosistema · Estado: **NO INSTALADO** (fundación presente, runtime ausente).

Auditoría consolidada del día con campañas completas, evidencia y límites: [`AUDITORIA-COMPLETA-2026-11-18.md`](../auditoria-runtime/AUDITORIA-COMPLETA-2026-11-18.md). Patchsets aplicados y propuestos: [`PATCHSETS-2026-11-18.md`](./PATCHSETS-2026-11-18.md).

| Repo | Ref auditada | Estado observado |
|---|---|---|
| `uniscrolliabrain-cloud/agntia-ciberseguridad` | `main@525769a` + cambios locales sin commitear (23 modificados, 11 nuevos) | Middleware y SDK funcionando; 22 tests de gateway reejecutados OK; SDK actual sin método de emisión de delegaciones |
| `uniscrolliabrain-cloud/agente` | `main@3f15ca8` (clon shallow de solo lectura) | CI `success` (run 44163625011); SDK vendorizado y 5 módulos de puente presentes; **cero wiring de producción**; gate C14 en `BLOCKED_CONFIGURATION` |

**Actualización del mismo día:** el bloqueo I-04 del lado del hijo ya está resuelto con el SDK `0.1.0-alpha.3` (manifiesto + emisión/revocación de delegación). El estado global sigue **NO INSTALADO** porque faltan las seis piezas de runtime del padre. Detalle en §10.

**Respuesta corta:** no falta instalar un paquete. `agente` ya tiene `@agntia/ciberseguridad` vendorizado, cinco módulos de puente y siete pruebas. Lo que falta es el **runtime**: configuración, credenciales, PDP, emisión de delegaciones de un uso, ruta HTTP, registro de tools para el modelo, migración al arranque y scheduler del relay. Sin eso, hoy el puente solo se ejecuta dentro de tests y el reinicio del servidor no activa nada.

## 1. Método y evidencia

La auditoría no se hizo por lectura: se ejecutaron sondas reproducibles sobre los dos árboles.

1. Clon shallow de `agente` en `/tmp/agente-audit` (`HEAD 3f15ca8`, 26 MB) y búsqueda de callsites de `CyberSdkBridge`, `CyberEventRelay`, `installSecurityBridgeV2`, `governedSecurityTools`, `cognitiveSecurityProjector` y `createScopedCyberClient` fuera de `apps/server/src/engine/security-v2/`.
2. Extracción del tarball vendorizado y reconstrucción con `npm ci --ignore-scripts && npm run build && npm pack` en tres referencias del hijo: `0a809a1` (SHA declarado en el reporte C14), `main@525769a` y el árbol de trabajo actual. Comparación con `diff -r` y SHA256.
3. Sonda de canonicalización: mismo envelope calculado con `agntia_ciberseguridad.util.digest` (Python) y con la función `hash()` de `event-relay.ts` (Node).
4. Reejecución de la suite de gateway del hijo: `PYTHONPATH=. .venv/bin/python -m unittest tests.security.test_agent_gateway`.
5. Consulta de las ejecuciones de CI de `agente` en `main`.
6. Lectura de contratos, rutas y pruebas de ambos repos para confirmar o descartar cada hallazgo.

Resultados:

| Comprobación | Resultado |
|---|---|
| Tests de gateway del hijo | `Ran 22 tests ... OK` (exit 0) |
| Canonicalización Python ↔ Node | idéntica: `a60eca9974284f961362ac529aa7232ec5b120de2db28b5ff10d87dc8028ae7f` |
| `diff -r` vendor vs. reconstrucción de `0a809a1` | contenido idéntico; SHA256 del tar distinto (`1cc2fceb…` vs. `72067a45…`): `npm pack` no es byte-reproducible |
| `diff -r` vendor vs. `main@525769a` | difiere: `main` añade `submitAudit` y `cancelJob`, con la **misma** versión `0.1.0-alpha.2` (`68a05222…`) |
| CI de `agente` en `main` | `success`, run `44163625011`, head `3f15ca824af29ce15680c561fed3d7134c49b812` |
| Callsites de producción del puente en `agente` | ninguno; solo tests y documentación |

## 2. Lo que ya existe

### 2.1 Hijo (`agntia-ciberseguridad`)

- Rutas de agente gobernado: `POST /v1/tenants/{t}/delegations`, `POST /v1/tenants/{t}/delegations/use`, `POST /v1/tenants/{t}/delegations/{id}/revoke`, `POST /v1/tenants/{t}/agents/manifests`, `POST .../manifests/{id}/approve` (`agntia_ciberseguridad/observability_routes.py:45-54`).
- Emisión de delegaciones de un uso, firmadas y persistidas, con cadena atenuada, época de política, manifiesto aprobado y TTL máximo de 5 minutos (`agntia_ciberseguridad/agents/capabilities.py`).
- Bloqueo del camino heredado para `kind=agent`: cualquier capacidad distinta de `agents.read` exige el contexto verificado de `delegations.use` (`agntia_ciberseguridad/auth.py:78-84`). Verificado por test: un bearer de agente recibe 403 en `/assets`, `/findings`, `/logs`, `/dashboard` y `/reports/{id}`, y 200 solo en `/delegations/use`.
- Outbox transaccional con `content_hash`, ACK con `consumer_id` y receipts append-only (`agntia_ciberseguridad/events/outbox.py`, tablas en `billing/schema.py:12-22`).
- SDK TypeScript servidor: `governedRead`, `outbox`, `ackOutbox`, `submitAudit`, `cancelJob`, páginas de assets/findings, budget y policy; sin transporte genérico.

### 2.2 Padre (`agente`)

- Dependencia vendorizada `@agntia/ciberseguridad@0.1.0-alpha.2` (`package.json:72`, `pnpm-lock.yaml:17`).
- Cinco módulos: `contracts.ts`, `sdk-adapter.ts`, `capabilities.ts`, `event-relay.ts`, `cognition-adapter.ts`.
- Siete casos: 5 en `tests/cognition-v2-cyber-bridge.test.ts`, 1 en `cognition-v2-security-context.test.ts`, 1 en `cognition-v2-rls-modules.test.ts`.
- El propio repo ya es honesto sobre el estado: `scripts/gate-cognition-v2.ts:16` marca C14 `BLOCKED_CONFIGURATION` con el motivo «Real parent PDP, credential broker and human child delegations remain unconfigured; synthetic contracts only», y `docs/campaigns/runtime-cognitivo-dogfooding/BASELINE.md:73` reconoce que no hay wiring de producción.

## 3. Matriz capacidad por capacidad

| Capacidad | Endpoint del hijo | Código en `agente` | Contrato probado | Runtime instalado |
|---|---|---|---|---|
| `assets.read` | `POST /delegations/use` | `CyberSdkBridge.read` | Sí (fetch sintético) | **No** |
| `findings.read` | `POST /delegations/use` | `CyberSdkBridge.read` | Sí | **No** |
| `jobs.read` | `POST /delegations/use` | `CyberSdkBridge.read` | Sí | **No** |
| Eventos de job/budget | `GET /outbox`, `POST /outbox/{id}/ack` | `CyberEventRelay` | Sí (inbox/cursor) | **No** |
| Proyección cognitiva | — | `cognitiveSecurityProjector` | Sí (transacción local) | **No** |
| Emisión de delegación | `POST /delegations` | — | No | **No** |

Conclusión de la matriz: el contrato de lectura está probado con transporte sintético; lo que falta es todo lo que convierte esos módulos en una capacidad del producto.

## 4. Hallazgos

### I-01 · P0 · El puente no está conectado a ningún arranque

**Evidencia.** `installSecurityBridgeV2`, `CyberEventRelay`, `CyberSdkBridge`, `governedSecurityTools` y `cognitiveSecurityProjector` solo aparecen en `tests/` (y en documentación). `apps/server/src/index.ts` no los importa ni ejecuta migración alguna.

**Impacto.** Un despliegue real no crea `cognition_v2_cyber_cursors` ni `cognition_v2_cyber_inbox`; no existe relay, ni tools, ni proyección. El primer uso fallaría por tabla ausente o por falta de instancia.

**Arreglo.** Registrar la migración en el arranque (idempotente) y componer el relay en el worker/scheduler con un flag de feature apagado por defecto.

### I-02 · P0 · No hay configuración ni secretos para el hijo

**Evidencia.** `.env.example` de `agente` no contiene ninguna variable `CYBER_*`; `apps/server/src/config.ts` no lee base URL, origen aprobado, tenant mapping ni referencias de credenciales.

**Impacto.** El cliente no se puede construir sin hardcodear origen, tenant y credenciales, que es exactamente lo que el contrato prohíbe.

**Arreglo.** Añadir configuración explícita y validada al arranque: `CYBER_BASE_URL`, `CYBER_APPROVED_ORIGIN`, `CYBER_TENANT_MAP`, `CYBER_AGENT_BINDING_REF`, `CYBER_HUMAN_ISSUER_REF`, `CYBER_AGENT_READER_REF`, `CYBER_ENABLED=false`. Los valores sensibles, por referencia a secret manager, nunca en claro.

### I-03 · P0 · No hay PDP ni broker de credenciales

**Evidencia.** `SecurityAuthorization` (`sdk-adapter.ts`) es una interfaz con dos callbacks: `current()` y `delegation()`. Ninguna implementación existe fuera de los tests. `CyberRelayAuthorization` tiene el mismo problema.

**Impacto.** No hay forma de comprobar membresía/actor/política vigente ni de resolver una delegación humana real. Sin esto, el puente no puede autorizar nada y no debe activarse.

**Arreglo.** Implementar `current()` sobre el motor de autorización existente del padre (membresía + actor activo + tenant no suspendido) y `delegation()` como emisión just-in-time: aprobación humana → `POST /delegations` con credencial humana (`agents.delegate`) → token de un uso al cliente del agente. Recordar que el hijo limita el TTL a 5 minutos y consume el token en el primer uso.

### I-04 · P0 · El SDK no expone la emisión de delegaciones

**Evidencia.** `typescript/src/client.ts` expone `governedRead`, `outbox`, `ackOutbox`, `submitAudit`, `cancelJob` y lecturas, pero **no** `delegations.issue` ni `revoke`. El padre prohíbe transporte HTTP genérico (`docs/integration/PATCHSET-AGENTE.md`), así que no puede llamar a `POST /delegations` por su cuenta.

**Impacto.** Bloqueo cruzado: aunque el padre implemente su aprobación, no tiene un método cerrado para pedir la delegación al hijo.

**Arreglo.** En el hijo: añadir `issueDelegation()` y `revokeDelegation()` al SDK con validación cerrada, pruebas de contrato y bump a `0.1.0-alpha.3` (o `0.2.0` si se considera cambio de superficie). En el padre: actualizar vendor y lock.

### I-05 · P0 · No hay superficie de producto ni tools para el modelo

**Evidencia.** Ninguna ruta de `apps/server/src/app.ts` sirve `security.*`. `SECURITY_READ_CAPABILITIES` y `governedSecurityTools` no se registran en `CapabilityRegistry` ni en `buildToolExecutors()`; el modelo no puede verlas y el humano no tiene UI.

**Impacto.** Aunque el runtime existiera, nadie podría invocarlo: ni el usuario ni el agente.

**Arreglo.** Registrar las tres capacidades en el registro con `sideEffects: ["delegation.consume"]`, `idempotency: at-most-once`, `retryable: false` y `requiresApproval` según política; añadir executor cerrado (input vacío, recurso elegido por servidor) y una ruta/UI que pida la lectura sin permitir elegir tenant, activo, URL ni credencial.

### I-06 · P0 · El relay no se ejecuta ni se observa

**Evidencia.** `CyberEventRelay.run()` no se invoca en ningún scheduler; no hay `consumer_id` configurado por tenant ni alertas para `CHILD_ACK_PENDING`, `SECURITY_EVENT_HASH_CONFLICT` o `SECURITY_EVENT_INVALID`.

**Impacto.** Sin relay no hay eventos de job/budget en el padre; si se arranca sin métricas, un ACK perdido queda pendiente para siempre sin señal operativa.

**Arreglo.** Job periódico por tenant con cursor durable, métricas de committed/acknowledged/blocked y alerta cuando `blocked` persista. La proyección debe seguir siendo transaccional y previa al ACK.

### I-07 · P1 · Artefacto vendorizado obsoleto y colisión de versión

**Evidencia.** El vendor es `72067a451731e384542dbd153843da687605b26d1a823c3826663e15bcab895b`, documentado en `docs/implementation/cognition-v2/C14/REPORT-W0-W6.md`. Al reconstruirlo desde su SHA declarado (`0a809a1`) el **contenido** coincide exactamente, pero el tarball resultante tiene otro SHA256 (`1cc2fceb…`): el `npm pack` no es byte-reproducible por metadatos del tar. Además, `main@525769a` —ya commiteado, sin los cambios locales de esta sesión— añade `submitAudit`/`cancelJob` y sigue declarando `0.1.0-alpha.2`; su reconstrucción da otro contenido (`68a05222…`).

**Impacto.** Tres artefactos con la misma versión y superficies distintas. Si el hijo corrige una lectura, el padre no lo recibe y nada lo detecta. El hash del tarball no sirve como identidad estable si el empaquetado no es reproducible.

**Arreglo.** Versionar cada artefacto una sola vez (`alpha.3`), publicar un `SDK-PROVENANCE.json` con SHA del hijo, digest del **contenido** (dist + package.json), fecha y comando, y hacer el `pack` determinista (fecha de fuente fija). El check de CI debe comparar contenido reconstruido, no solo el SHA del tar. Actualizar `pnpm-lock.yaml` con el nuevo integrity.

### I-08 · P1 · El bridge no comprueba la identidad de la delegación devuelta

**Evidencia.** `sdk-adapter.ts` valida tenant, actor, agente, política, recurso y expiración del grant local, pero acepta `result.delegation_id` sin compararlo con `grant.grantId`. Tampoco valida `flows` ni el `limit` de la respuesta.

**Impacto.** Un hijo comprometido o un error de enrutado podría devolver datos bajo otra delegación y el padre los aceptaría como propios. Es defensa en profundidad, no una brecha demostrada.

**Arreglo.** Exigir `result.delegation_id === grant.grantId`, y rechazar `flows` no vacíos si la capacidad es de metadatos.

### I-09 · P2 · `findings.read` no permite verificar tenant en el padre

**Evidencia.** `Delegations.use` devuelve para findings solo `id`, `state`, `severity` y `revision` (`agents/capabilities.py`), sin `tenant_id`. La comprobación cross-tenant del bridge (`raw.tenant_id !== identity.tenantId`) se omite cuando el campo no viene.

**Impacto.** El aislamiento depende solo del path y del scope de la delegación, no de una comprobación redundante en el consumidor.

**Arreglo.** Añadir `tenant_id` a la proyección de findings (o documentar explícitamente que el aislamiento es por ruta y delegación) y una prueba negativa que lo cubra.

### I-10 · P2 · Deriva del contrato `Job.state` en el hijo

**Evidencia.** `agntia_ciberseguridad/contracts.py:125` declara `state: Literal['pending','running','succeeded',...]`, mientras que el store escribe `completed` o `partial` (`jobs/store.py:187`). El SDK (`JOB_STATES` en `typescript/src/contracts.ts`) y el runtime sí coinciden en `completed|partial`, y por eso `jobs.read` funciona.

**Impacto.** Cualquier consumidor que genere tipos desde `contracts.py` rechazará jobs reales. Hoy el padre no lo sufre porque lee la fila cruda, pero es una trampa para el siguiente cliente.

**Arreglo.** Corregir el literal a `completed|partial` (sin `succeeded`), regenerar el esquema afectado y añadir un test que valide una fila real contra el modelo.

### I-11 · P2 · Sin política de reloj ni reconciliación para el uso de un token

**Evidencia.** El hijo exige `expires_at > now` y consume el token en el primer uso; el padre usa timeout de 5 s y comenta que no reintenta a ciegas, pero no hay mapeo explícito de `reconciliation_required` ni de desfase de reloj entre servidores.

**Impacto.** Un timeout deja al operador sin saber si la lectura se consumió; un desfase de reloj puede invalidar delegaciones de 5 minutos.

**Arreglo.** Documentar y probar la semántica: timeout ⇒ no reintentar, emitir nueva delegación previa aprobación; sincronización NTP y margen de reloj verificado en el gate.

## 5. Lo que sí está verificado (para no sobrecorregir)

- **Procedencia del vendor:** su contenido coincide exactamente con una reconstrucción de `0a809a1`. La deriva es de versión y de superficie posterior, no de un artefacto desconocido.
- **Canonicalización del `content_hash`:** idéntica entre Python y Node sobre el mismo envelope. El relay no rechazará eventos legítimos por formato.
- **Estados de job:** `completed`/`partial` del store coinciden con el enum del padre; `succeeded` es solo deriva documental (I-10).
- **Formas de respuesta:** `governedRead` devuelve `delegation_id`, `data`, `flows`, `limit` y `security_guarantee:false`; los IDs (32/64 hex), estados y severidades que consume el padre existen en la respuesta real.
- **Aislamiento de agente:** el bearer de agente no puede usar rutas heredadas; el único camino es `delegations/use` (22 tests de gateway, incluido el 403 en rutas legacy).
- **Minimización:** el padre descarta nombre, evidencia y flujos; solo conserva IDs, estado, revisión y severidad.
- **Entrada cerrada:** `governedSecurityTools` rechaza cualquier input no vacío; el modelo no elige recurso.

## 6. Plan de instalación

### Ola 0 — Habilitar el contrato (hijo)

1. `CyberClient.issueDelegation()` y `revokeDelegation()` cerrados, con pruebas contra FastAPI real.
2. Bump de versión y `SDK-PROVENANCE.json` con digest de contenido; `npm pack` determinista y check de CI que reconstruya y compare contenido (no solo el SHA del tar).
3. Corregir `Job.state`; opcionalmente añadir `tenant_id` a la proyección de findings.
4. Actualizar `docs/integration/PATCHSET-AGENTE.md` con la superficie nueva.

**DoD:** un consumidor puede emitir una delegación y usarla sin HTTP genérico, con evidencia de tests y artefacto reproducible.

### Ola 1 — Instalación read-only sin LLM (padre)

1. Configuración y secretos por referencia; flag `CYBER_ENABLED=false`.
2. Dos clientes: emisor humano y lector agente; nunca el mismo token.
3. `current()` real sobre el PDP del padre; `delegation()` just-in-time con aprobación humana.
4. Migración idempotente al arranque y ruta HTTP autenticada con tenant resuelto en servidor.
5. Métricas y logs sin contenido; errores mapeados (`delegation_inactive`, `delegation_scope`, `reconciliation_required`).

**DoD:** el fundador puede pedir una lectura de assets/findings/jobs desde la UI y ver datos minimizados, con dos tenants aislados y revocación probada.

### Ola 2 — Tools para el modelo

1. Registrar `security.assets.read`, `security.findings.read`, `security.jobs.read` en el registro de capacidades y en los executors.
2. Allowlist de prompt y pruebas de inyección: el modelo no elige tenant, activo, URL ni token.
3. `requiresApproval` coherente con la política; sin aprobación automática.

**DoD:** el modelo solo puede invocar las tres lecturas; un intento de inyectar parámetros devuelve error cerrado.

### Ola 3 — Relay y proyección

1. Scheduler por tenant con `consumer_id` estable.
2. Alertas para ACK pendiente, conflicto de hash y evento inválido.
3. Registro del evento corporativo versionado antes de proyectar a cognición.
4. Pruebas de ACK perdido, reinicio, cursor y duplicado (ya existen a nivel de módulo; faltan en runtime).

**DoD:** un job real del hijo aparece como registro cognitivo una sola vez, con ACK confirmado o pendiente visible.

### Ola 4 — Certificación

1. Dos tenants, revocación en vuelo, expiración, hijo caído, desfase de reloj, ACK perdido, RLS Postgres real.
2. Runbook, rollback y restauración con evidencia.
3. Solo entonces reevaluar el gate C14; no cambiar `BLOCKED_CONFIGURATION` por documentación.

## 7. Checklist de «instalado»

- [ ] `CYBER_*` validado al arranque y secreto por referencia.
- [ ] `issueDelegation` en el SDK y vendor actualizado con procedencia.
- [ ] `current()` y `delegation()` reales, sin default permisivo.
- [ ] Migración idempotente ejecutada en arranque limpio y en base existente.
- [ ] Ruta autenticada con tenant de servidor y aprobación humana.
- [ ] Tres tools registradas y allowlist de prompt.
- [ ] Relay con cursor, ACK y alertas.
- [ ] Pruebas de dos tenants, revocación, expiración y ACK perdido.
- [ ] Métricas visibles y logs sin secretos ni evidencia cruda.
- [ ] Gate C14 actualizado con evidencia ejecutada, no con documentación.

## 8. Decisiones humanas pendientes

- Licencia `UNLICENSED` y distribución del paquete: no es un artefacto comercial.
- `production_enabled=false` en el hijo y 2 PASS / 40 PARTIAL: el puente no eleva ese estado.
- DPA/consentimiento y retención de evidencia antes de datos reales.
- Autorización expresa para escribir en `uniscrolliabrain-cloud/agente`; esta auditoría no lo modificó.
- Aprobación separada para desplegar; no se ha desplegado nada.

## 9. Límites de esta auditoría

- No se ejecutó la suite completa de `agente` en local; se cita el CI verde de `main` y la lectura de los tests. No equivale a certificación end-to-end.
- No hay despliegue del hijo ni credenciales reales, así que no se ejecutó un `governedRead` real contra un servidor: el contrato se verificó por tests del hijo, sonda de hash y lectura de formas de respuesta.
- No se modificó `/agente` ni su checkout; el clon fue de solo lectura en `/tmp`.
- No se fusionó, desplegó ni se cambió el estado de ningún gate.

---

**Veredicto:** la integración está a mitad de camino y bien encaminada: contrato y módulos correctos, pruebas honestas y gate bloqueado a propósito. Para instalar de verdad faltan seis piezas de runtime en `agente` y una pieza de SDK en el hijo. Ninguna es un rediseño; todas son trabajo acotado y verificable.

## 10. Resolución aplicada (2026-11-18)

Cambios en `agntia-ciberseguridad`, sin tocar `/agente`:

| Hallazgo | Estado | Evidencia |
|---|---|---|
| I-04 SDK sin emisión de delegaciones | **Resuelto en el hijo** | `CyberClient.createManifest`, `approveManifest`, `issueDelegation`, `revokeDelegation`; contrato vivo `tests/contracts/test_agent_sdk_live.py` + `typescript/test/agent-contract.test.mjs` |
| I-07 colisión de versión | **Resuelto** | `0.1.0-alpha.3`; `npm run pack:deterministic` produce SHA256 estable (`09c94d52…`) y `PROVENANCE.json` fija el digest de contenido (`07220f66…`); CI ejecuta `provenance:check` |
| I-09 findings sin tenant | **Resuelto** | `tenant_id` en la proyección + `DelegationProjectionTests` |
| I-10 deriva `Job.state` | **Resuelto** | literal `completed\|partial`; `Job.json` regenerado |
| I-01, I-02, I-03, I-05, I-06, I-08, I-11 | **Abiertos** | pertenecen al runtime del padre |

Verificación de esta resolución: **228 tests Python OK (8 skips)**, **10 pass / 2 skip / 0 fail** en el SDK (12 casos), 13 esquemas exportados de forma idempotente y `validate_foundation` PASS. Los dos tests vivos nuevos se ejecutaron contra FastAPI en loopback, no contra un despliegue. El artefacto determinista se generó dos veces con el mismo SHA256 y el contenido empaquetado se verificó contra `PROVENANCE.json`.
