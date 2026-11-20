# 03 · Fases de código propuestas

**Estado:** **F0, F1 y F2 APLICADAS** el 2026-11-20 (código, pruebas y gate de CI en
`agntia-ciberseguridad`); **F3–F10 PROPUESTAS — NO APLICADAS**. Ninguna campaña CY-IP se ha
ejecutado: sigue sin haber instalación en host ni propagación a tenants.
**Regla de escritura:** el código se escribiría solo en `agntia-ciberseguridad`. `agente` aparece
como contrato de host y **no se modifica**; su implementación corresponde a su equipo tras
autorización expresa.

Las rutas son propuestas y deben confirmarse contra el HEAD antes de editar. Las firmas son
contratos ilustrativos, no código para copiar.

## 1. Mapa de fases

| Fase | Objetivo | Campaña | Depende de | Estado |
|---|---|---|---|---|
| F0 | Inventario y manifiesto de instalación | IP-00 | — | APLICADA |
| F1 | Verificación de artefacto y procedencia | IP-01 | F0 | APLICADA |
| F2 | Configuración fail-closed por referencia | IP-01, IP-03 | F0 | APLICADA |
| F3 | Modelo de inscripción y migración de estado | IP-02 | F2 | PROPUESTA |
| F4 | Planificador determinista de olas (sin efectos) | IP-02, IP-08 | F3 | PROPUESTA |
| F5 | Servicio de aplicación, pausa y revocación | IP-03–IP-06 | F4 | PROPUESTA |
| F6 | Superficie de lectura y control para el host | IP-03, IP-07 | F5 | PROPUESTA |
| F7 | SDK servidor: estado de instalación y olas | IP-04–IP-07 | F6 | PROPUESTA |
| F8 | Observabilidad, alertas y deriva | IP-05, IP-06 | F5 | PROPUESTA |
| F9 | Kill switch, desinstalación y ensayo de rollback | IP-08, IP-09 | F5 | PROPUESTA |
| F10 | Evidencia, informe y gate de cierre | IP-10 | Todas | PROPUESTA |

Orden estricto: F0 → F1 → F2 → F3 → F4 → F5 → F6 → F7 → F8 → F9 → F10. F8 puede empezar en
paralelo con F7 si el ownership de archivos es disjunto.

## 2. F0 · Manifiesto de instalación

**Estado:** APLICADA (2026-11-20).
**Archivos reales:** `agntia_ciberseguridad/install.py` (modelo `InstallManifest`), `scripts/install_manifest.py`, `docs/implementation/schemas/InstallManifest.json` (generado por `scripts/export_schemas.py`), `tests/unit/test_install_manifest.py`.

**Contrato:** un documento con `schema_version`, `package`, `version`, `digest`, `host_ref`,
`tenant`, `capabilities`, `created_at`, `source_sha`. Sin secretos, sin valores de entorno.

**Invariantes:**

- El manifiesto no contiene credenciales ni rutas locales absolutas.
- `digest` es el del artefacto, no el del manifiesto.
- `capabilities` solo admite nombres ya existentes en el contrato de agente.

**Pruebas a escribir:** manifiesto con campo faltante falla; digest alterado falla; manifiesto
con una clave de secreto se rechaza; exportación de esquema estable.

**Rollback:** eliminar script y esquema; no hay estado.

## 3. F1 · Verificación de artefacto

**Estado:** APLICADA (2026-11-20).
**Archivos reales:** `agntia_ciberseguridad/install.py` (`verify`), `scripts/verify_artifact.py`, `tests/unit/test_install_artifact.py`; paso nuevo en `.github/workflows/runtime.yml`.

**Contrato:** `verify(path, manifest) -> Result` con `ok`, `checks`, `digest`, `failures`.
Comprueba tamaño, digest, entradas del tar y coherencia con `PROVENANCE.json`.

**Invariantes:**

- Un digest distinto devuelve fallo; nunca "regenera y continúa".
- El verificador no ejecuta scripts del paquete.
- La salida no imprime contenido del paquete ni variables de entorno.

**Pruebas:** pack correcto; byte alterado; entrada extra; `PROVENANCE.json` ausente; dos
ejecuciones del mismo pack dan el mismo digest.

**Rollback:** retirar el script; el pack sigue siendo instalable por workspace.

## 4. F2 · Configuración fail-closed

**Estado:** APLICADA (2026-11-20).
**Archivos reales:** `agntia_ciberseguridad/config.py` (`RolloutConfig` y campo `rollouts` de `Settings`), `docs/implementation/CONFIGURACION.md`, `tests/unit/test_config_rollout.py`.

**Contrato aplicado:** `RolloutConfig` con `tenant_id`, `capability`, `ring`, `previous_ring`,
`state`, `revision`, `consent_ref`, `budget_cents`, `expires_at`, `secret_ref`; validación en el arranque.

**Invariantes:**

- Sin `consent_ref`, sin presupuesto o con `expires_at` vencido, el arranque falla.
- `ring` no puede saltar de A a D sin registro intermedio.
- Ningún valor por defecto habilita una capacidad.
- Los secretos se referencian por nombre de variable, nunca por valor.

**Pruebas:** configuración válida; consentimiento ausente; presupuesto negativo; ring inválido;
caducidad vencida; referencia de secreto con valor embebido rechazada.

**Rollback:** mantener la configuración anterior; las flags nuevas nacen apagadas.

## 5. F3 · Inscripción y migración

**Archivos propuestos:** `agntia_ciberseguridad/storage.py` (migración nueva), `agntia_ciberseguridad/rollout/store.py` (nuevo), `tests/test_rollout_store.py` (nuevo).

**Tabla propuesta:** `rollout(tenant_id, capability, ring, state, revision, consent_ref,
budget_cents, expires_at, updated_at, reason, actor_id)`, con clave compuesta
`(tenant_id, capability)` y `revision` monotónica.

**Invariantes:**

- Toda mutación exige `expected_revision`; una revisión vieja no escribe.
- La auditoría se inserta en la misma transacción que el cambio.
- `state` solo admite `pending`, `enabled`, `paused`, `revoked`.
- El tenant de la fila debe existir; no se crea un tenant desde una ola.

**Pruebas:** alta; mutación con revisión correcta; mutación con revisión vieja rechazada;
rollback transaccional si falla la auditoría; aislamiento entre tenants.

**Rollback:** migración reversible que conserva la tabla y elimina solo la versión nueva.

## 6. F4 · Planificador determinista

**Archivos propuestos:** `agntia_ciberseguridad/rollout/planner.py` (nuevo), `tests/test_rollout_planner.py` (nuevo).

**Contrato:** `plan(current: dict, target: dict, policy: dict) -> Plan` con `steps`, `aborts`,
`warnings`, `revision`. Función pura: no escribe, no llama a red, no lee reloj salvo el inyectado.

**Invariantes:**

- El mismo estado y la misma política producen el mismo plan byte a byte.
- El plan nunca salta un anillo ni mezcla capacidades en una ola.
- Un tenant sin consentimiento aparece como `abort`, no como paso omitido.
- El plan declara el rollback de cada paso antes de proponerlo.

**Pruebas:** determinismo con reloj fijo; salto de anillo rechazado; consentimiento ausente;
ola vacía; plan con 25 % y 100 %; plan que excede presupuesto.

**Rollback:** no hay efecto; se retira el módulo.

## 7. F5 · Servicio de aplicación

**Archivos propuestos:** `agntia_ciberseguridad/rollout/service.py` (nuevo), `agntia_ciberseguridad/rollout/routes.py` (nuevo), `tests/test_rollout_service.py` (nuevo).

**Operaciones:** `advance(plan, idempotency_key)`, `pause(tenant, capability, reason)`,
`resume(...)`, `revoke(...)`, `apply_plan(...)`. Todas con actor humano y auditoría.

**Invariantes:**

- `advance` es idempotente por `idempotency_key`; repetir no duplica el efecto.
- Aplicar un plan con `revision` distinta falla sin escribir.
- Pausar y revocar son posibles incluso si el plan está a medias.
- Ninguna operación toca datos de otro tenant.
- Un fallo a mitad de ola deja el estado en el último paso confirmado, nunca en un estado mixto.

**Pruebas:** avance feliz; reintento idempotente; revisión obsoleta; pausa durante avance;
revocación con delegaciones pendientes; fallo inyectado a mitad de ola.

**Rollback:** apagar la ruta y restaurar la tabla desde la migración anterior.

## 8. F6 · Superficie para el host

**Archivos propuestos:** `agntia_ciberseguridad/features.py` (registro) o `rollout/routes.py`, `docs/implementation/schemas/Rollout.json` (nuevo).

**Rutas propuestas, solo lectura y control acotado:**

| Método y ruta | Capacidad | Efecto |
|---|---|---|
| `GET /v1/tenants/{tenant}/rollout` | `rollout.read` | Estado del tenant, sin datos de otros |
| `POST /v1/tenants/{tenant}/rollout/plan` | `rollout.plan` | Plan determinista, sin aplicar |
| `POST /v1/tenants/{tenant}/rollout/apply` | `rollout.apply` | Aplica un plan con revisión e idempotencia |
| `POST /v1/tenants/{tenant}/rollout/pause` | `rollout.apply` | Pausa; siempre permitido a humano |
| `POST /v1/tenants/{tenant}/rollout/revoke` | `rollout.apply` | Revoca; siempre permitido a humano |

**Invariantes:**

- Ninguna ruta acepta tenant del cuerpo como autorización.
- `apply` exige principal humano y revisión esperada.
- `plan` no escribe ni emite delegaciones.
- Un agente no puede llamar a `apply` ni a `revoke`; su vía sigue siendo la tool gobernada.
- Las respuestas son `no-store` y no incluyen secretos ni contenido de clientes.

**Pruebas:** 401 sin sesión; 403 con tenant ajeno; 403 con principal agente en `apply`;
plan idempotente; revisión obsoleta; lectura de estado solo del tenant propio.

**Rollback:** retirar las rutas; no hay migración de datos nueva.

## 9. F7 · SDK servidor

**Archivos propuestos:** `typescript/src/client.ts`, `typescript/test/rollout.test.mjs` (nuevo), `typescript/package.json` (bump a `0.1.0-alpha.4`).

**Métodos propuestos:** `rolloutStatus(tenant)`, `rolloutPlan(tenant, target)`,
`rolloutApply(tenant, plan, revision, idempotencyKey)`. Solo servidor; sin equivalente en
`agentTools`.

**Invariantes:**

- El cliente fija tenant y origen; no hay `request(path)` genérico.
- `rolloutApply` no se expone como herramienta de modelo ni como ruta del BFF de navegador.
- Los errores no incluyen cuerpos de otros tenants.
- El bump de versión obliga a regenerar `PROVENANCE.json`.

**Pruebas:** estado feliz; plan; apply con revisión; rechazo de tenant ajeno; rechazo de
credencial inválida; el paquete no abre red al importarse.

**Rollback:** revertir el bump y los tres métodos; el host no los consume todavía.

## 10. F8 · Observabilidad

**Archivos propuestos:** `agntia_ciberseguridad/telemetry/` (nuevo módulo de métricas),
`infra/observability/alerts.yaml` (ampliar), `tests/test_rollout_metrics.py` (nuevo).

**Señales:** cobertura por anillo y capacidad, rechazos por motivo, deriva de política,
presupuesto agotado, kill switch activo.

**Invariantes:**

- Ninguna etiqueta contiene tenant, usuario ni contenido; como máximo anillo y capacidad.
- Una alerta sin prueba de disparo se documenta como `NOT_VERIFIED`.
- La métrica no cambia el comportamiento: observa, no decide.

**Pruebas:** contadores por estado; rechazo incrementa la etiqueta correcta; alerta dispara con
la condición inyectada; cardinalidad acotada.

**Rollback:** retirar métricas y alertas; no afecta al flujo.

## 11. F9 · Kill switch y desinstalación

**Archivos propuestos:** `scripts/rollout_killswitch.py` (nuevo), `agntia_ciberseguridad/rollout/service.py` (ampliar), `tests/test_rollout_killswitch.py` (nuevo).

**Contrato:** `kill(capability, reason, actor)` deja todas las filas en `paused` o `revoked`,
emite evento de auditoría y no borra evidencia. `uninstall(host_ref)` documenta la retirada del
paquete y verifica que el host vuelve a su comportamiento previo.

**Invariantes:**

- El kill switch no requiere que el host esté sano para aplicarse.
- No borra auditoría ni evidencia.
- La reanudación exige decisión humana explícita y revisión nueva.
- La desinstalación no deja delegaciones vivas.

**Pruebas:** kill global; kill por capacidad; reanudación sin revisión rechazada; desinstalación
con delegación pendiente; host sin middleware sigue operativo.

**Rollback:** no aplica; la fase es el rollback.

## 12. F10 · Evidencia y cierre

**Archivos propuestos:** `docs/implementation/schemas/Rollout.json`, plantilla de informe en
`docs/campanas-instalacion-propagacion-2026-11-20/plantillas/INFORME-CAMPANA.md` (nueva),
extensión de `scripts/releasecheck.py`.

**Contenido del informe:** campaña, SHA, anillo, tenants, comandos, exit codes, conteos de tests y
skips, fallos reproducibles, incidentes, rollback medido, límites y estado
`SIMULADO | NOT_VERIFIED | FAIL | PASS`.

**Invariantes:**

- `PASS` solo con comando, SHA, salida y revisión independiente.
- Todo lo no ejecutado se marca `NOT_VERIFIED`; no se omite.
- El informe enlaza la evidencia, no la copia dentro del repositorio si contiene datos.

**Rollback:** documento; no afecta código.

## 13. Contrato del host (`agente`) — especificación, no cambio

Obligaciones que el equipo del padre tendría que cumplir; **no se ha escrito nada en su repo**:

1. Resolver de sesión que fije tenant y origen en el servidor.
2. Credencial acotada desde secret manager, leída en cada llamada.
3. Rutas BFF cerradas que no expongan el cliente entero ni `request(path)`.
4. Rechazo de tenant, origen o Authorization enviados por el navegador como identidad.
5. Tools de agente limitadas a lectura, con delegación de un uso.
6. Relay de eventos con deduplicación durable y ACK tras procesar.

Estas obligaciones coinciden con PS-P1…PS-P6 de
[PATCHSETS-2026-11-18.md](../integration/PATCHSETS-2026-11-18.md). Sin ellas, la instalación en
`agente` no pasa G1 por mucho que el paquete hijo esté verificado.

## 14. Lo que esta propuesta no incluye

- Enforcement (N3) ni respuesta automática (N4).
- Herramientas de escritura para agentes.
- Escaneo de infraestructura de terceros.
- Publicación en npm, cobros o auto-upgrades.
- Cambios en `agente`, migraciones en producción o credenciales reales.

## 15. Registro de implementación F0–F2 (2026-11-20)

Aplicado en `agntia-ciberseguridad`, sin tocar `agente`:

| Fase | Archivos reales | Pruebas | Gate |
|---|---|---|---|
| F0 | `agntia_ciberseguridad/install.py` (modelo `InstallManifest`), `scripts/install_manifest.py`, `docs/implementation/schemas/InstallManifest.json` | `tests/unit/test_install_manifest.py` | `unittest discover -s tests` |
| F1 | `agntia_ciberseguridad/install.py` (`verify`), `scripts/verify_artifact.py` | `tests/unit/test_install_artifact.py` | paso nuevo en `.github/workflows/runtime.yml` |
| F2 | `agntia_ciberseguridad/config.py` (`RolloutConfig`), `docs/implementation/CONFIGURACION.md` | `tests/unit/test_config_rollout.py` | arranque fail-closed de `Settings` |

Evidencia local del 2026-11-20 en este árbol:

- `unittest discover -s tests` → **260 OK, 8 skips** (antes 228 OK, 8 skips; 32 nuevas: 19 de F0/F1 y 13 de F2).
- `scripts/install_manifest.py build` y `scripts/verify_artifact.py` sobre el pack real
  `typescript/.pack/agntia-ciberseguridad-0.1.0-alpha.3.tgz` → `PASS`, digest
  `09c94d52a5fa813cb93fc92e3864317abcab5332edc3c5c2f2b8ec98763dbcf7`, 9 272 bytes.
- Fallos inyectados cubiertos por pruebas: byte alterado, entrada extra, enlace simbólico,
  travesía de ruta, `PROVENANCE.json` ausente, procedencia manipulada y digest de manifiesto distinto.
- F2: el arranque rechaza consentimiento ausente o ajeno, presupuesto no positivo, caducidad
  vencida, salto de anillo, binding duplicado y referencia de secreto con valor embebido.

Qué **no** cambia con esto:

- El verificador comprueba un artefacto; no instala, no extrae a disco y no ejecuta scripts del paquete.
- Ninguna campaña IP-00…IP-10 se ha ejecutado: G2 sigue `NOT_VERIFIED` como gate de campaña.
- F2–F10 siguen siendo propuesta y el contrato del host (§13) sigue sin cumplirse.
