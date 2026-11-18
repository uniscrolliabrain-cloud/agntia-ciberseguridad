# Auditoría completa de los dos repositorios — 2026-11-18

**Alcance:** `uniscrolliabrain-cloud/agntia-ciberseguridad` (hijo) y `uniscrolliabrain-cloud/agente` (padre).
**Refs medidas:** hijo `main@525769a` + 33 entradas de trabajo sin commitear; padre `main@3f15ca8`, clon de solo lectura.
**Naturaleza:** demo sintética, `production_enabled=false`. No es una revisión independiente ni una certificación.
**Veredicto global:** **integración NO INSTALADA**. El hijo ya expone el contrato completo y un artefacto reproducible; el padre sigue sin runtime de producción.

| Repo | Ref | Estado observado | Lectura |
|---|---|---|---|
| `agntia-ciberseguridad` | `main@525769a` + 23 ficheros modificados y 10 rutas nuevas | 228 tests Python OK (8 skips); SDK 10 pass / 2 skip; 13 esquemas; artefacto determinista | **Listo para consumir**; ningún despliegue |
| `agente` | `main@3f15ca8` (2026-11-17) | CI `success` (run 44163625011); vendor `alpha.2`; cinco módulos de puente; cero wiring | **NO INSTALADO**; gate C14 en `BLOCKED_CONFIGURATION` |

> **Frontera de esta auditoría.** Por instrucción del propietario, `agente` solo se auditó: el clon en `/tmp/agente-audit` es de solo lectura, no se modificó ni se commiteó nada allí. Los patchsets del padre (§B) son especificación aplicable por su equipo, no cambios realizados.

## 1. Método

1. Fijar SHA y estado de cada árbol, incluido el recuento de cambios sin commitear.
2. Ejecutar la suite completa del hijo y los gates de agente con `PYTHONPATH=.` y `.venv/bin/python`, registrando exit codes.
3. Reconstruir el artefacto SDK dos veces y comparar SHA256; verificar el digest de contenido contra `PROVENANCE.json`.
4. Sondear el padre con búsquedas de callsites, inventario del vendor, lectura de configuración y gate.
5. Consultar las ejecuciones de CI de ambos repos en `main` vía API de GitHub.
6. Contrastar cada afirmación con el código; lo no ejecutado se marca `NOT_VERIFIED`, nunca PASS.

## 2. Registro de campañas

Formato de cada campaña: objetivo, superficie, precondiciones, ejecución, resultado, veredicto y límites. Una campaña solo es PASS si se ejecutó y su salida lo demuestra.

| ID | Campaña | Veredicto |
|---|---|---|
| C01 | Baseline, CI y verdad documental | PASS con límites |
| C02 | Regresión funcional del hijo | PASS |
| C03 | Contratos y esquemas publicados | PASS local / gate CI pendiente de commit |
| C04 | SDK TypeScript y contrato vivo | PASS local / cobertura CI parcial |
| C05 | Artefacto reproducible y procedencia | PASS |
| C06 | Gateway adversarial | PASS con límites |
| C07 | Parada de agente y efectos | PASS con límites |
| C08 | Distribución y fundación documental | PASS |
| C09 | Auditoría estática del padre | PASS (auditoría) / hallazgos abiertos |
| C10 | Integración end-to-end | **NOT_VERIFIED** |

---

### C01 — Baseline, CI y verdad documental

**Objetivo.** Fijar qué se está auditando y separar lo commiteado de lo que solo vive en el árbol de trabajo.

**Superficie.** `git rev-parse`, `git status --porcelain`, workflows de ambos repos, `docs/release/status.json`.

**Ejecución.**

```
git -C agntia-ciberseguridad rev-parse HEAD
git -C agntia-ciberseguridad status --porcelain | wc -l
git -C /tmp/agente-audit log -1 --format='%H|%cs|%s'
git -C /tmp/agente-audit status --porcelain | wc -l
```

**Resultado.**

- Hijo: `525769a8e71fdcfc4e534ae4ea87e6ec7a1af84b`; **33 entradas** de estado (23 ficheros modificados y 10 rutas nuevas sin seguimiento, que contienen 11 ficheros).
- Padre: `3f15ca824af29ce15680c561fed3d7134c49b812`, 2026-11-17, árbol **limpio** (0 entradas).
- CI del hijo sobre `525769a` (2026-11-18T12:38:07Z): `Documentation foundation` run `44305795211` **success**; `Synthetic release artifacts` run `44305795376` **success**.
- CI del padre sobre `3f15ca8`: workflow `CI`, run `44163625011`, **success**.
- `docs/release/status.json`: 2 fases PASS, 40 PARTIAL; `independent_review: PENDING`.

**Veredicto.** PASS con límites: la CI verde cubre `525769a`, **no** el árbol de trabajo de esta sesión.

**Límites.** No se ejecutaron localmente `scanner-contracts.yml`, `browser.yml` ni `release.yml`; se citan sus runs remotos, no una reproducción.

---

### C02 — Regresión funcional del hijo

**Objetivo.** Demostrar que el trabajo del SDK, contratos y proyecciones no rompe ninguna suite existente.

**Superficie.** `tests/` completo (unitarios, integración, seguridad, contratos, docker marcados como skip si falta motor).

**Precondiciones.** `.venv` con `pip install -e '.[dev]'`; `PYTHONPATH=.`.

**Ejecución.**

```
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests
```

**Resultado.**

```
Ran 228 tests in 36.089s
OK (skipped=8)
exit 0
```

**Veredicto.** PASS. Cero fallos, cero errores; los 8 skips son los que requieren Docker/navegador o entorno no disponible, y se declaran como tales.

**Límites.** No hay cobertura de un despliegue real ni de Postgres; la suite usa SQLite y dobles locales salvo el contrato vivo en loopback.

---

### C03 — Contratos y esquemas publicados

**Objetivo.** Verificar que los modelos publicados se regeneran sin deriva no intencionada.

**Superficie.** `agntia_ciberseguridad/contracts.py`, `docs/implementation/schemas/*.json`, `scripts/export_schemas.py`.

**Ejecución.**

```
PYTHONPATH=. .venv/bin/python scripts/export_schemas.py
git diff --stat -- docs/implementation/schemas
git diff --exit-code -- docs/implementation/schemas    # esperado != 0 en árbol sucio
```

**Resultado.**

- `{"schemas_exported": 13, "schema_version": 1, "runtime_workers_enabled": false}`, exit 0.
- Diff: `Finding.json` (+2/−1, cambio previo de la revisión H-03/H-06) y `Job.json` (+2/−1, `state: completed|partial` de I-10). Nada más.

**Veredicto.** PASS local con matiz: la exportación es idempotente —repetirla no añade cambios— y el diff se limita a los dos cambios declarados. El gate `git diff --exit-code` del CI **fallará hasta que estos cambios se commiteen**, que es el comportamiento correcto, no un defecto.

**Límites.** El gate de CI no puede validarse sobre el árbol sin commitear.

---

### C04 — SDK TypeScript y contrato vivo

**Objetivo.** Probar la superficie nueva (manifiesto, aprobación, emisión y revocación de delegación) y su uso real contra FastAPI.

**Superficie.** `typescript/src/client.ts`, `typescript/test/client.test.mjs`, `typescript/test/agent-contract.test.mjs`, `tests/contracts/test_agent_sdk_live.py`, `tests/contracts/test_python_ts.py`.

**Ejecución.**

```
cd typescript && npm run build && npm test
# y, dentro de la suite Python:
PYTHONPATH=. .venv/bin/python -m unittest tests.contracts.test_agent_sdk_live
```

**Resultado.**

- `npm test`: **12 casos, 10 pass, 2 skip, 0 fail** (exit 0).
- Skips: el contrato vivo TS cuando lo lanza `test_python_ts`, y el caso que exige servidor Python ya arrancado.
- El contrato vivo se ejecutó desde Python en loopback: manifiesto → aprobación humana → delegación de un uso → lectura → revocación; la delegación revocada deja de servir.
- La emisión exige principal humano con `agents.manage`/`agents.delegate`; el token se consume en el primer uso y caduca en ≤ 5 minutos.

**Veredicto.** PASS local. La superficie cerrada ya permite al padre completar el alta sin transporte HTTP genérico.

**Límites.** El bloque TS del contrato vivo queda `skip` salvo lanzamiento orquestado; en CI con `CI=true` no se ejecuta contra un servidor real. No sustituye una prueba end-to-end de despliegue.

---

### C05 — Artefacto reproducible y procedencia

**Objetivo.** Convertir el artefacto del SDK en una identidad verificable, tras detectar que `npm pack` crudo no es byte-reproducible.

**Superficie.** `typescript/scripts/pack.mjs`, `typescript/scripts/provenance.mjs`, `typescript/PROVENANCE.json`, `typescript/package.json`, `.github/workflows/runtime.yml`.

**Ejecución.**

```
cd typescript
npm run provenance:write
npm run pack:deterministic
npm run pack:deterministic
sha256sum .pack/*.tgz
npm run provenance:check
```

**Resultado.**

- Dos empaquetados consecutivos: `09c94d52a5fa813cb93fc92e3864317abcab5332edc3c5c2f2b8ec98763dbcf7`, 9 272 bytes, **idéntico**.
- Contenido: 11 entradas, incluidas `package/PROVENANCE.json` y los seis pares `dist/*.js|*.d.ts`; sin `.tgz` anidado.
- `PROVENANCE.json`: digest de contenido `07220f66…`, con SHA256 por fichero de `README.md`, `package.json` y `dist`.
- Prueba automatizada `pack.test.mjs`: mismo SHA en dos pasadas.
- Fallo detectado y corregido durante la campaña: la salida por defecto era `dist/`, que forma parte de `files`; el segundo pack se incluía a sí mismo. Ahora la salida es `.pack/` (ignorada por git) y el defecto quedó cubierto por el SHA doble.

**Veredicto.** PASS.

**Límites.** El artefacto no está publicado ni firmado; `PROVENANCE.json` no incluye la firma del commit porque el cambio vive sin commitear. No hay atestación externa (Sigstore/in-toto).

---

### C06 — Gateway adversarial

**Objetivo.** Medir el comportamiento del gateway de agentes frente al corpus adversario y benigno.

**Superficie.** `agntia_ciberseguridad/agents/*`, `scripts/evaluate_agent_gateway.py`.

**Ejecución.**

```
PYTHONPATH=. .venv/bin/python scripts/evaluate_agent_gateway.py
```

**Resultado.**

- 16 candidatos adversarios: **16 rechazados**, 0 completados.
- 8 tareas benignas: **8 completadas** (tasa 1.0).
- `false_positives: 0`, `false_negatives: 0`.
- `gateway_p50_ms: 2.87`, `gateway_p95_ms: 4.36`.
- `corpus_hash: a2a71798…`, `policy_hash: a644ba27…`, `configuration_hash: 9047d8f3…`.
- `external_model_calls: 0`, coste externo 0.

**Veredicto.** PASS con límites.

**Límites.** El propio script declara que el candidato es JSON guionizado, no un LLM real: no es un benchmark de inyección de prompts ni una réplica de AgentDojo. Los códigos de decisión (`schema_rejected`, `flow_quarantined`, `delegation_inactive`, `delegation_scope`, `egress_denied`, `agent_policy_unavailable`) confirman que cada rechazo tiene causa tipada.

---

### C07 — Parada de agente y efectos

**Objetivo.** Verificar que la orden de parada corta llamadas posteriores y que no se deshacen efectos ya comprometidos.

**Superficie.** Controles de agente, ACK de parada, `scripts/measure_agent_stop.py`.

**Ejecución.**

```
PYTHONPATH=. .venv/bin/python scripts/measure_agent_stop.py
```

**Resultado.**

- `stops: 10`, `next_calls_denied_after_ack: 10` (10/10).
- `stop_ack_p50_ms: 5.62`, `stop_ack_p95_ms: 6.65`; comprobación de siguiente llamada p50 2.17 / p95 3.28.
- `already_committed_effects_undone: false` (correcto: la parada no revierte lo ya aplicado).
- `sdk_available: true`, sin llamadas externas.

**Veredicto.** PASS con límites.

**Límites.** Entorno sintético de un solo nodo con SQLite y llamadas directas; sin HTTP/TLS ni procesos remotos. No mide parada distribuida ni latencia de red.

---

### C08 — Distribución y fundación documental

**Objetivo.** Comprobar que los recursos de distribución y el corpus documental siguen íntegros.

**Superficie.** `scripts/check_distribution.py`, `scripts/validate_foundation.py`, `docs/`.

**Ejecución.**

```
PYTHONPATH=. .venv/bin/python scripts/check_distribution.py
PYTHONPATH=. .venv/bin/python scripts/validate_foundation.py
```

**Resultado.**

- `check_distribution`: PASS; 8 recursos con hash verificado (`LICENSE.txt`, `bom-1.5.schema.json`, `governance/legal_sources.json`, `jsf-0.82.schema.json`, `spdx.schema.json`, `web/console.{css,html,js}`), sobre `source_commit 525769a`.
- `validate_foundation`: PASS; **319** ficheros Markdown, 31 registros de metadatos, 187 720 palabras, 0 escaneos de seguridad ejecutados (así se declara).

**Veredicto.** PASS.

**Límites.** `validate_foundation` valida consistencia documental y presupuesto, **no** seguridad ni contenido técnico. `check_distribution` verifica hashes declarados, no firmas.

---

### C09 — Auditoría estática del padre

**Objetivo.** Determinar si el puente de ciberseguridad está instalado en `agente` y qué falta exactamente.

**Superficie.** `/tmp/agente-audit` (`main@3f15ca8`), `apps/server/src`, `vendor/`, `package.json`, `scripts/gate-cognition-v2.ts`, `tests/cognition-v2-*`.

**Ejecución.**

```
find . -name '*ciberseguridad*.tgz' -not -path './node_modules/*'
sha256sum vendor/agntia-ciberseguridad-0.1.0-alpha.2.tgz
grep -rn "installSecurityBridgeV2\|CyberEventRelay\|governedSecurityTools\|cognitiveSecurityProjector\|createScopedCyberClient" \
  apps/server/src --include='*.ts' | grep -v 'engine/security-v2'
grep -rn "CYBER_" .env.example apps/server/src/config.ts
grep -n "BLOCKED_CONFIGURATION" scripts/gate-cognition-v2.ts
```

**Resultado.**

- Vendor único: `vendor/agntia-ciberseguridad-0.1.0-alpha.2.tgz`, SHA256 `72067a45…`, versión declarada `0.1.0-alpha.2`.
- Cinco módulos: `contracts.ts`, `sdk-adapter.ts`, `capabilities.ts`, `event-relay.ts`, `cognition-adapter.ts`.
- Siete casos de prueba: 5 + 1 + 1.
- **Cero callsites** de los cinco símbolos fuera de `engine/security-v2/`: solo tests y documentación.
- **Cero** variables `CYBER_*` en `.env.example` ni en `config.ts`.
- Gate C14: `BLOCKED_CONFIGURATION` con motivo «Real parent PDP, credential broker and human child delegations remain unconfigured; synthetic contracts only».
- CI `success` en `3f15ca8`.

**Veredicto.** PASS como auditoría: el estado está determinado con evidencia. Los hallazgos I-01, I-02, I-03, I-05, I-06, I-08 e I-11 quedan **abiertos** en el padre.

**Límites.** No se ejecutó la suite de `agente` en local; se cita su CI. No se probó el vendor contra el hijo `alpha.3`: el padre sigue en `alpha.2`.

---

### C10 — Integración end-to-end

**Objetivo.** Comprobar si un usuario real puede pedir una lectura gobernada de activos/hallazgos/jobs desde el padre contra un hijo desplegado.

**Superficie.** Ruta HTTP del padre, PDP, broker de credenciales, emisión de delegación, relay y despliegue.

**Ejecución.** No ejecutable: no hay despliegue del hijo, credenciales reales ni wiring en el padre.

**Resultado.** No hay ruta que sirva la lectura, no hay PDP/broker, no hay migración al arranque y el relay no se invoca. Un intento end-to-end no puede ni comenzar.

**Veredicto.** **NOT_VERIFIED** (y el motivo es estructural, no de entorno). No se declara PASS por tests de módulo.

**Límites.** Todo lo que depende de red, TLS, Postgres y dos tenants reales queda sin probar.

---

## 3. Campañas planificadas no ejecutadas en esta fecha

El programa `CY-R01…CY-R12` sigue siendo el plan de auditoría diferencial. Hoy se ejecutaron las campañas C01–C09 de este documento; **no** se ejecutaron:

- **CY-R03** (límites de entrada, snapshots y sandbox): requiere Docker y pruebas de TOCTOU.
- **CY-R04** (cobertura real de escáneres): requiere imágenes y feeds Gitleaks/OSV/Semgrep/Trivy.
- Las campañas de persistencia con Postgres/RLS real, navegador y carga.

Se marcan `NOT_VERIFIED`. No se convierten 40 PARTIAL en PASS por repetir tests ni por CI verde de documentación.

## 4. Hallazgos consolidados

| ID | Severidad | Estado 2026-11-18 | Evidencia |
|---|---|---|---|
| I-01 puente sin arranque | P0 | **Abierto** (padre) | C09: cero callsites; `index.ts` sin migración |
| I-02 sin configuración/secretos | P0 | **Abierto** (padre) | C09: cero `CYBER_*` |
| I-03 sin PDP ni broker | P0 | **Abierto** (padre) | `sdk-adapter.ts` solo interfaces |
| I-04 SDK sin emisión | P0 | **Resuelto en el hijo** | C04: manifiesto→aprobación→delegación→revocación |
| I-05 sin ruta ni tools | P0 | **Abierto** (padre) | C09: sin registro de capacidades |
| I-06 relay sin scheduler | P0 | **Abierto** (padre) | C09: `CyberEventRelay.run()` sin invocación |
| I-07 versión/artefacto | P1 | **Resuelto** | C05: `alpha.3`, pack determinista, provenance en CI |
| I-08 identidad de delegación | P1 | **Abierto** (padre) | `sdk-adapter.ts` no compara `delegation_id` |
| I-09 findings sin tenant | P2 | **Resuelto** | `tenant_id` en proyección + prueba |
| I-10 deriva `Job.state` | P2 | **Resuelto** | `completed\|partial`; `Job.json` regenerado |
| I-11 reloj/reconciliación | P2 | **Abierto** (padre) | sin mapeo explícito de `reconciliation_required` |

La revisión de código del mismo día (`REVISION-INDEPENDIENTE-2026-11-18.md`) cerró H-01…H-08 y añadió H-09 (cuerpo canónico de `submitAudit` rechazado por lista cerrada). Sigue siendo **auto-revisión**: el gate de revisión independiente continúa `PENDING`.

## 5. Matriz de integración

| Capacidad | Endpoint del hijo | Código en `agente` | Contrato probado | Runtime instalado |
|---|---|---|---|---|
| `assets.read` | `POST /delegations/use` | `CyberSdkBridge.read` | Sí | **No** |
| `findings.read` | `POST /delegations/use` | `CyberSdkBridge.read` | Sí + `tenant_id` | **No** |
| `jobs.read` | `POST /delegations/use` | `CyberSdkBridge.read` | Sí | **No** |
| Manifiesto y aprobación | `POST /agents/manifests`, `.../approve` | — | Sí (SDK + vivo) | **No** |
| Emisión de delegación | `POST /delegations` | — | Sí (SDK + vivo) | **No** |
| Revocación | `POST /delegations/{id}/revoke` | — | Sí (SDK + vivo) | **No** |
| Eventos de job/budget | `GET /outbox`, `POST /outbox/{id}/ack` | `CyberEventRelay` | Sí (inbox/cursor) | **No** |
| Proyección cognitiva | — | `cognitiveSecurityProjector` | Sí (transacción local) | **No** |

## 6. Checklist de «instalado»

- [x] SDK con emisión y revocación cerradas, servidor-only.
- [x] Artefacto `alpha.3` reproducible y con digest de contenido verificado en CI.
- [ ] `CYBER_*` validado al arranque y secreto por referencia.
- [ ] `current()` y `delegation()` reales, sin default permisivo.
- [ ] Migración idempotente ejecutada en arranque limpio y en base existente.
- [ ] Ruta autenticada con tenant de servidor y aprobación humana.
- [ ] Tres tools registradas y allowlist de prompt.
- [ ] Relay con cursor, ACK y alertas.
- [ ] Dos tenants, revocación en vuelo, expiración, ACK perdido y desfase de reloj probados.
- [ ] Gate C14 reevaluado con evidencia ejecutada.

## 7. Riesgos y límites de esta auditoría

- **Sin despliegue ni credenciales reales:** C10 es estructuralmente inejecutable hoy.
- **Sin Postgres/RLS real, sin escáneres Docker, sin navegador:** CY-R03/R04 y las pruebas de carga quedan fuera.
- **CI verde ≠ árbol verde:** los runs citados corresponden a `525769a`; los cambios de esta sesión son locales.
- **Auto-revisión:** la revisión de código y esta auditoría las firma el mismo agente que implementó. No sustituyen al gate independiente.
- **Padre intocado:** los patchsets del padre son propuesta; nada se aplicó ni se commiteó allí.
- **Licencia:** paquete `UNLICENSED`; nada de esto es distribución comercial.

## 8. Reproducción

```
# Hijo
cd agntia-ciberseguridad
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests
PYTHONPATH=. .venv/bin/python scripts/export_schemas.py
PYTHONPATH=. .venv/bin/python scripts/evaluate_agent_gateway.py
PYTHONPATH=. .venv/bin/python scripts/measure_agent_stop.py
PYTHONPATH=. .venv/bin/python scripts/check_distribution.py
PYTHONPATH=. .venv/bin/python scripts/validate_foundation.py
cd typescript && npm ci --ignore-scripts && npm test
npm run provenance:write && npm run pack:deterministic && npm run pack:deterministic
npm run provenance:check

# Padre (solo lectura)
git clone --depth 1 https://github.com/uniscrolliabrain-cloud/agente /tmp/agente-audit
git -C /tmp/agente-audit rev-parse HEAD
```

Salidas esperadas: 228 OK / 8 skips; 13 esquemas; 16/16 adversarios y 8/8 benignos; 10/10 paradas; PASS de distribución y fundación; 10 pass / 2 skip del SDK; mismo SHA256 en los dos packs y `provenance:check` verde.

## 9. Decisiones humanas pendientes

- Licencia y canal de distribución del paquete.
- DPA, consentimiento y retención antes de datos reales.
- Autorización para escribir en `agente` y para desplegar.
- Revisión independiente (gate `PENDING`).

## 10. Fecha y control de cambios

- **2026-11-18.** Auditoría completa de los dos repos, diez campañas con evidencia, estado de I-01…I-11, checklist y límites. Registro de patchsets: [`PATCHSETS-2026-11-18.md`](../integration/PATCHSETS-2026-11-18.md). Detalle de instalación: [`AUDITORIA-INSTALACION-AGENTE-2026-11-18.md`](../integration/AUDITORIA-INSTALACION-AGENTE-2026-11-18.md).
- Cambios en el árbol de trabajo del hijo, **sin commit**: el propietario no ha autorizado commit, push ni despliegue.
