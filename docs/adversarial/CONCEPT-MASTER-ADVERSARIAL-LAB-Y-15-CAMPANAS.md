# AGNTIA ADVERSARIAL LAB — Concept Master técnico y programa de 15 campañas
**Fecha:** 2026-11-15 · **Repo:** uniscrolliabrain-cloud/agntia-ciberseguridad · **Baseline auditado:** main aedf6f22e7cbdfe42af5dd8608af34a366bfb3b4 · **Estado:** DISEÑO; NO IMPLEMENTADO.

## 1. Producto y objetivo
Crear un **red team autónomo y supervisado, agnóstico de agente de programación**, que ejecute pruebas de seguridad éticas y continuas contra representaciones aisladas de sistemas de clientes y, en perfiles expresamente autorizados, pruebas limitadas sobre sistemas reales. Codex, Antigravity, Cline, Freebuff u otros son **workers intercambiables**; el broker determinista del repo decide qué pueden leer, ejecutar, escribir o transmitir. Los agentes leen campañas declarativas versionadas y producen evidencias, no se confía en su autoevaluación. Pedro coordina ciberseguridad; Laia informa; Marcos ejecuta tareas autorizadas. Humano experto participa en diseño, validación y escalado.

**Dos planos distintos**:
- **Lab clone:** repositorios y topología reproducidos, datos sintéticos, credenciales ficticias, aislamiento y egress denegado. Permite pruebas activas y destructivas confinadas.
- **Customer authorized:** acceso real limitado, por defecto observacional/pasivo; pruebas activas solo con contrato y alcance precisos, ventanas, rate limits, autorización vigente, stop y rollback. Nunca asumir que un sandbox autoriza ataques al sistema real.

**Ritmo:** ciclo diario de discovery→threat modeling→plan→preflight→test→evidence→triage→blue team→independent retest→report→learning. Una ejecución diaria no implica escanear todas las superficies diariamente: priorizar cambios, riesgo, límites y ventanas.

## 2. Auditoría de código: límites y puntos de integración
Inspección estática selectiva en GitHub de: `agents/registry.py`, `agents/capabilities.py`, `agents/policy.py`, `agents/tools.py`, `agents/routes.py`, `runners/container.py`, `network_policy.py`, `config.py`, `snapshots.py`, `safety.py`, además de `storage.py`, `events/outbox.py`, `jobs/worker.py`, `reports.py`, `reviews.py`, `evidence/vault.py` y docs previos. No se ejecutó test local ni pentest.
1. **Gateway actual read-only**: `agents/registry.py` permite assets.read/findings.read/jobs.read/notes.propose; `agents/capabilities.py` emite delegaciones atenuadas de lectura; `agents/tools.py` solo ofrece `agntia.metadata.read`; `agents/policy.py` fija `external_egress=False`, `executor=local_metadata_only`. **No convertirlo en shell/HTTP proxy ofensivo**. Crear servicio adversarial aislado con contratos propios.
2. **Runner existente**: `runners/container.py` lanza herramientas cerradas, sin socket Docker en contenedor no confiable, sin fallback a binarios host. Su semántica de scanner no equivale a ejecutar agentes de código con herramientas interactivas; crear broker dedicado y probar su aislamiento.
3. **Scope**: `network_policy.py` valida y fija destinos, pero es preflight puro sin transporte. Para lab y customer se necesita un enforcement de egress en capa de red, no confiar en validación de URL.
4. **Snapshots**: `snapshots.py` copia árboles locales autorizados sin ejecutar hooks. No es un clon funcional de infraestructura; no afirmar duplicación completa sin blueprint e integraciones.
5. **Gates**: `safety.py` contiene ReleaseGates con independent_review_verified, sandbox_verified, identity_worker_verified, por defecto false. Nunca activarlos mediante texto de un agente.
6. **Persistencia**: SQLite single-node, migraciones 1–8, outbox local poll/ACK; scheduler distribuido y aislamiento de ejecución adversarial aún no existen.
7. **Custodia**: Vault AES-GCM con vistas minimizadas, retención/hold y límite 2 MiB por evidencia; reusar y particionar por tenant.
8. **Estado**: `docs/release/status.json` declara SYNTHETIC_DEMO_NOT_PRODUCTION, 2 fases PASS/40 PARTIAL, 80 tareas PASS/214 PARTIAL. CY-R01..12 deben cerrar los gates correspondientes antes de piloto.

## 3. Arquitectura objetivo
```text
Cliente / owner + Pedro / Laia
    -> Engagement y autorización verificable
    -> Inventario + threat model + digital twin
    -> Campaign Planner (plantillas declarativas firmadas)
    -> Policy Decision Point (scope, budgets, approval, stop)
    -> Agent Provider Registry (Codex / Antigravity / Cline / Freebuff / otros)
    -> Adversarial Tool Broker (allowlist, tokens efímeros, quotas)
    -> Lab Executor (aislamiento fuerte, sin egress por defecto)
       -> herramientas de análisis de código, dependencias, IaC, APIs, IA y chaos
    -> Evidence Vault + Event Outbox + Finding Store
    -> Triage humano / Blue team / Retest independiente
    -> Reports + Autodoc AD-01..15 + SOPs + programación diaria
```
No acoplar al kernel principal de AgntiaPro ni tocar /agente hasta contrato aprobado. El control plane nunca entrega credenciales de producción a los agentes; el execution plane recibe tokens de alcance mínimo y TTL corto. El agente propone estrategias; el sistema autoriza cada efecto.

## 4. Capacidades y técnicas
**Repositorios y supply chain:** SAST, secretos, SCA/SBOM, IaC, dependencias, CI/CD, permisos, firmas, provenance y vulnerabilidades de configuración. Aprovechar Semgrep, Gitleaks, OSV-Scanner y Trivy ya adaptados. Investigar CodeQL, OpenSSF Scorecard, Syft/Grype, Checkov, OPA/Conftest como opciones futuras, sujeto a licencias, disponibilidad y límites.
**Web/API/identidad:** contratos OpenAPI, authn/authz, IDOR/BOLA, sesiones, roles, exposición de secretos, rate limits, lógica de negocio, API fuzzing en lab; evaluar ZAP, Schemathesis y herramientas equivalentes en sandbox autorizado.
**Cloud/containers:** IAM, configuraciones, Kubernetes y dependencias; evaluar Prowler, kube-bench, Falco/Tetragon como adaptadores, sin confundir configuración con EDR real.
**Agentes IA:** prompt injection, tool abuse, MCP, RAG/memory poisoning, fuga simulada, agent-to-agent trust, scopes y evals; evaluar Promptfoo, PyRIT, AgentDojo/garak como referencia, verificar licencias y uso comercial.
**Resiliencia/antivisiones:** fallos en cascada, corrupción de backup, pérdida de DNS/red/identidad, proveedores caídos, restore, RTO/RPO, continuidad offline. Simulación primero; no ejecutar caos sobre clientes sin autorización adicional.
**Red team humano:** el experto diseña objetivos, revisa hallazgos de impacto alto y decide pruebas que puedan alterar estado. Modelos múltiples pueden debatir hipótesis, pero su consenso no es prueba.

## 5. Modelo de campaña legible por cualquier IA
```yaml
schema_version: 1
campaign_id: ADV-LAB-EXAMPLE
title: Control de autorización horizontal en API sintética
mode: lab_clone
tenant_ref: tenant-synthetic
asset_refs: [asset-synthetic-api]
authorization_ref: signed-engagement-ref
target_fingerprint: expected-hash
agent_profile: generic-code-agent
required_capabilities: [repo.read, sandbox.test, evidence.write]
technique_tags: [api-authorization, negative-test]
preconditions: [sandbox-isolated, synthetic-data, approval-valid]
limits:
  max_duration_seconds: 900
  max_requests: 200
  max_cost_cents: 100
  network_egress: deny
stop_conditions: [scope_changed, authorization_revoked, unexpected_egress, budget_exceeded]
expected_artifacts: [test-result, sanitized-trace, finding-or-no-finding, coverage, limitations]
retest_required: true
```
**El YAML es un ejemplo de contrato futuro, no un parser ya existente.** El planner puede proponer; el validador comprueba firma, esquema, alcance, hashes, límites, identidad, permiso, tipo de prueba y efectos. Cada transición emite evento y evidencia. No almacenar secretos o datos de cliente en instrucciones del agente.

## 6. Operación diaria
00 inventario de cambios; 01 priorización basada en cambios/riesgo; 02 selección de campañas; 03 comprobación de consentimiento y ventana; 04 aprovisionamiento de lab; 05 asignación de agente y herramientas; 06 ejecución con supervisión y stop; 07 verificación de artefactos; 08 deduplicación y triage; 09 propuesta blue team; 10 retest independiente; 11 reporte diario y backlog; 12 destrucción verificable de lab. Si no hay autorización o lab fiable: BLOCKED, no ejecutar.

**Escalera de confianza:** T0 offline/static → T1 lab sintético aislado → T2 staging del cliente con permiso → T3 producción limitada y expresamente autorizada. No pasar de nivel por score de IA. Para T3, controles adicionales, operador humano, límites y rollback; prohibir pruebas destructivas por defecto.

## 7. Paquete de handoff por campaña de implementación
Cada ADV-XX tiene **F0** auditoría de SHA/código/contratos, **F1** threat model + pruebas negativas, **F2** contratos/fixtures, **F3** patchset mínimo, **F4** wiring + migración/rollback, **F5** unit/integration/security/E2E, **F6** auditoría Codex independiente, **F7** reporte `docs/adversarial/reports/ADV-XX-REPORT.md` y PR. La lista de rutas es propuesta, no prueba de existencia. Crear rama `feat/cyber-ADV-XX` por campaña, rebase desde main, no tocar /agente, no desplegar ni fusionar sin aprobación. Si CY-R02/R03/R05/R06/R07 falla, bloquear campañas dependientes.

## 8. Programa secuencial de 15 campañas de implementación

### ADV-01 — Contratos de autorización adversarial
**Rama:** `feat/cyber-ADV-01`. **Dependencia:** CY-R01 y revisión de permisos; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/contracts.py`, `adversarial/authorization.py`, `tests/security/test_adversarial_authorization.py`; `docs/adversarial/reports/ADV-01-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/config.py`, `agntia_ciberseguridad/service.py` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Engagement, ScopeManifest, AuthorizationGrant, TargetFingerprint, AttackBudget, StopSignal. Consentimiento firmado y acotado por tenant, asset, método, ventana y límites; revocación inmediata; perfil de solo lectura por defecto.
**Pruebas concretas:** Tests expiración, actor suplantado, tenant cruzado, target cambiado, revocación durante job, deny-by-default.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-02 — Modelo de amenazas y superficie viva
**Rama:** `feat/cyber-ADV-02`. **Dependencia:** ADV-01; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/surface.py`, `adversarial/threat_model.py`, `tests/unit/test_adversarial_surface.py`; `docs/adversarial/reports/ADV-02-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/snapshots.py`, `agntia_ciberseguridad/findings/store.py` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Ingerir snapshots aprobados, SBOM, findings y configuración; grafo de trust boundaries, datos, identidad y dependencias; hipótesis con precondiciones y evidencias, no inferir acceso real.
**Pruebas concretas:** Fixtures de repos sintéticos, paths maliciosos, datos faltantes, riesgo de dependencia circular.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-03 — Sandbox de alta fidelidad y datasets sintéticos
**Rama:** `feat/cyber-ADV-03`. **Dependencia:** ADV-02; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/lab/blueprint.py`, `adversarial/lab/provision.py`, `adversarial/lab/synthetic_data.py`, `tests/security/test_adversarial_lab.py`; `docs/adversarial/reports/ADV-03-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/runners/container.py`, `agntia_ciberseguridad/infra/compose.yaml` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Clonar arquitectura permitida, no secretos ni datos reales; datos sintéticos preservando distribuciones y restricciones sin reidentificación; contenedores efímeros, DNS/egress deny, cuotas, kill switch, credenciales canary, snapshots de rollback. Diferenciar clone de producción y simulación de integración.
**Pruebas concretas:** Probar egress bloqueado, escape lógico, aislamiento de filesystem, expiración de credenciales, teardown y limpieza.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-04 — Interfaz agnóstica de agentes de programación
**Rama:** `feat/cyber-ADV-04`. **Dependencia:** ADV-03; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/providers/base.py`, `adversarial/providers/registry.py`, `adversarial/providers/cli_bridge.py`, `tests/contracts/test_adversarial_providers.py`; `docs/adversarial/reports/ADV-04-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/agents/registry.py`, `agntia_ciberseguridad/agents/policy.py (mediante nueva policy, nunca ampliar la existente silenciosamente)` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Adapter protocol plan/execute/observe/report, perfiles Codex/Antigravity/Cline/Freebuff/CLI genérico, capabilities negociadas y autenticación por proveedor. El agente NO recibe docker socket ni credenciales de cliente; bridge a herramientas aprobadas. Soporte real de cada proveedor sujeto a verificación API/CLI/licencia.
**Pruebas concretas:** Contract tests con fake adapters, timeout, provider unavailable, injection, budget, cancel.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-05 — Broker determinista de herramientas y ejecuciones
**Rama:** `feat/cyber-ADV-05`. **Dependencia:** ADV-04; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/tool_broker.py`, `adversarial/tool_policy.py`, `tests/security/test_adversarial_broker.py`; `docs/adversarial/reports/ADV-05-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/runners/base.py`, `agntia_ciberseguridad/runners/container.py`, `agntia_ciberseguridad/agents/tools.py (sin exponer shell genérico en MCP actual)` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Catálogo cerrado de herramientas; permitlist por campaña; validación de argumentos, rutas, targets, efectos, presupuesto y timeout; proxy de ejecución separado del API; comandos libres prohibidos salvo sandbox aislado con controles del broker.
**Pruebas concretas:** Pruebas de path traversal, target switch, egress, shell injection, resource exhaustion, cancel.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-06 — Catálogo de campañas adversariales versionadas
**Rama:** `feat/cyber-ADV-06`. **Dependencia:** ADV-05; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/campaigns/schema.py`, `adversarial/campaigns/loader.py`, `adversarial/campaigns/catalog/README.md`, `tests/unit/test_adversarial_campaigns.py`; `docs/adversarial/reports/ADV-06-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/docs/engineering/ (enlace)` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** YAML/JSON declarativo versionado: objetivos, precondiciones, técnicas, evidencias, stop, coste, rollback, criterios de éxito y no-éxito; plantillas legibles por cualquier agente; no permitir instrucciones remotas sin firma/hash.
**Pruebas concretas:** Schema validation, schema downgrade, malformed playbook, missing scope, duplicate IDs, tamper.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-07 — Orquestador diario, cola y scheduling
**Rama:** `feat/cyber-ADV-07`. **Dependencia:** ADV-06; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/orchestrator.py`, `adversarial/scheduler.py`, `tests/integration/test_adversarial_schedule.py`; `docs/adversarial/reports/ADV-07-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/jobs/store.py`, `agntia_ciberseguridad/jobs/worker.py`, `agntia_ciberseguridad/events/outbox.py` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Planificación por ventanas autorizadas; idempotency keys, lease/fence, checkpoints, pausas, retries con backoff, circuit breakers y kill switch. Cron externo o worker dedicado, NO tarea en request HTTP; priorizar alcance y coste.
**Pruebas concretas:** Simular doble worker, reloj, cancel, crash/replay, autorización caducada, outbox duplicado.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-08 — Red team automatizado y colaboración humana
**Rama:** `feat/cyber-ADV-08`. **Dependencia:** ADV-07; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/redteam/roles.py`, `adversarial/redteam/strategy.py`, `adversarial/redteam/review.py`, `tests/evaluations/test_adversarial_redteam.py`; `docs/adversarial/reports/ADV-08-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/reviews.py (reusar aprobación humana)` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Separar planner, challenger, operator y experto humano; generar hipótesis, elegir pruebas autorizadas, registrar límites y reproducibilidad; técnicas de código, identidad, configuración, API, IA y supply chain, sin lanzar acciones fuera del scope.
**Pruebas concretas:** Evaluar alucinaciones, evidencia fabricada, estrategia repetida, riesgo no autorizado y juicio humano.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-09 — Evaluación de agentes IA y prompt injection
**Rama:** `feat/cyber-ADV-09`. **Dependencia:** ADV-08; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/ai_security/fixtures.py`, `adversarial/ai_security/evaluator.py`, `tests/security/test_adversarial_ai.py`; `docs/adversarial/reports/ADV-09-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/agents/flows.py`, `agntia_ciberseguridad/tests/evaluations/runner.py` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Benchmarks de tool misuse, prompt injection, memory/RAG poisoning, scope creep, exfiltración simulada, MCP trust boundaries y separación de instrucciones/datos; únicamente en laboratorio con datos falsos.
**Pruebas concretas:** Golden tests, denegación de permisos, fuga canary, falsos positivos y resultados no concluyentes.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-10 — Simulaciones de fallo, caos y antivisiones
**Rama:** `feat/cyber-ADV-10`. **Dependencia:** ADV-09; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/chaos/scenarios.py`, `adversarial/chaos/executor.py`, `tests/integration/test_adversarial_chaos.py`; `docs/adversarial/reports/ADV-10-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/recovery.py`, `agntia_ciberseguridad/scripts/backup_restore_lab.py` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Ensayos de caída de DB, worker, proveedor, DNS, red, backup corrupto, colas, timeout y pérdida de credenciales; definir RTO/RPO objetivos vs medidos, cascadas y SOP de continuidad; prohibido caos en producción por defecto.
**Pruebas concretas:** Chaos fixtures, restauración, integridad, degradación, RTO/RPO, no false-green.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-11 — Triaging, scoring y prueba de explotabilidad segura
**Rama:** `feat/cyber-ADV-11`. **Dependencia:** ADV-10; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/findings.py`, `adversarial/triage.py`, `tests/integration/test_adversarial_findings.py`; `docs/adversarial/reports/ADV-11-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/findings/normalize.py`, `agntia_ciberseguridad/findings/store.py`, `agntia_ciberseguridad/risk.py` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Distinguir hipótesis, observación, reproducción controlada y vulnerabilidad confirmada; dedupe y riesgo según exposición, impacto, evidencia y confianza; reproducir solo en targets autorizados, no escalar por mera severidad.
**Pruebas concretas:** Falsos positivos, evidencia contradictoria, hallazgo obsoleto, duplicate fingerprint, tenant cruzado.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-12 — Blue team y retest independiente
**Rama:** `feat/cyber-ADV-12`. **Dependencia:** ADV-11; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/blue_team.py`, `adversarial/retest.py`, `tests/security/test_adversarial_retest.py`; `docs/adversarial/reports/ADV-12-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/governance/remediation.py`, `agntia_ciberseguridad/reviews.py` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Propuestas de parche como PR privado, jamás despliegue directo; pruebas de regresión y retest con agente distinto y controles deterministas; las dos reglas existentes siguen siendo lab-only; no prometer remediación genérica.
**Pruebas concretas:** Patch malicioso, tests skipped, falso retest, cambio de alcance, aprobación ausente.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-13 — Expedientes de ataque y reportes continuos
**Rama:** `feat/cyber-ADV-13`. **Dependencia:** ADV-12; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/reporting.py`, `adversarial/evidence.py`, `tests/integration/test_adversarial_reporting.py`; `docs/adversarial/reports/ADV-13-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/evidence/vault.py`, `agntia_ciberseguridad/reports.py`, `agntia_ciberseguridad/docs/autodoc/PROGRAMA-15-CAMPANAS-ULTRAGRANULARES.md (enlace opcional)` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Cada sesión produce run manifest, hipótesis, técnica, alcance, evidencia, resultados, fallos, costo, riesgo residual y retest; usar Vault AES-GCM y reportes existentes; versión ejecutiva y técnica sanitizada; nunca almacenar payloads sensibles en logs.
**Pruebas concretas:** Integridad hash, redaction, hold/retention, leak, render HTML, evidencia incompleta.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-14 — Observabilidad, presupuestos y controles de parada
**Rama:** `feat/cyber-ADV-14`. **Dependencia:** ADV-13; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `adversarial/telemetry.py`, `adversarial/budget.py`, `adversarial/kill_switch.py`, `tests/security/test_adversarial_stop.py`; `docs/adversarial/reports/ADV-14-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/telemetry/metrics.py`, `agntia_ciberseguridad/billing/reservations.py`, `agntia_ciberseguridad/agents/controls.py` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** Métricas por tenant/campaña, coste por agente y herramienta, timeout, CPU/memoria, egress intentado, hallazgos reproducidos, coverage; parada global por anomalía, revocación o riesgo de impacto.
**Pruebas concretas:** Budget exhaustion, kill switch concurrente, alert lost, stop under crash, no secretos.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

### ADV-15 — Validación independiente y piloto cerrado
**Rama:** `feat/cyber-ADV-15`. **Dependencia:** ADV-14; gates de seguridad CY-R según superficie. **Estado:** PENDIENTE.
**Crear:** `tests/e2e/test_adversarial_lab_journey.py`, `scripts/adversarial_e2e.py`, `docs/adversarial/READINESS.md`, `docs/adversarial/HANDOFF-OPERATIONS.md`; `docs/adversarial/reports/ADV-15-REPORT.md`.
**Inspeccionar/modificar si procede:** `agntia_ciberseguridad/docs/release/PILOT-ACCEPTANCE.md (solo enlaces/estado verificado)`, `agntia_ciberseguridad/.github/workflows/runtime.yml (gates mínimos)` (rutas relativas fuera del paquete, como infra/docs, se verifican antes de editar). **No sobrescribir contratos existentes.**
**Patchset y capacidades:** E2E cliente ficticio→consentimiento→sandbox→agente→hallazgo→reporte→PR→retest→SOP; revisión por humano experto, evaluación independiente y auditoría de aislamiento antes de cualquier piloto real.
**Pruebas concretas:** Tests Python/TS/Docker, adversarial negative, restore, supply chain, licensing, performance, cost, privacy, stop/replay.
**F0:** checkout limpio, SHA, diff de APIs y amenazas, localizar funciones exactas, baseline test. **F1:** tests negativos reproducibles y criterios de aceptación. **F2:** modelos Pydantic/fixtures, schemas versionados. **F3:** implementar adaptador/servicio con feature flag off. **F4:** conectar solo interfaces aprobadas, transacciones y auditoría, rollback/migración. **F5:** ejecutar unit, integration, security, E2E, fail/retry, tenant y resource bounds; registrar skips. **F6:** revisión Codex independiente del diff, límites de confianza y pruebas. **F7:** reporte con SHA, rutas, comandos, exit codes, pruebas, riesgos, decisiones, evidencias, rollback y gate PASS/FAIL/BLOCKED/NOT_VERIFIED. **Stop:** cualquier acceso fuera de alcance, filtración, escape del lab, CI no reproducible o revocación.

## 9. Integraciones externas: investigación previa, no instalación automática
Codex y Antigravity pueden variar en API/CLI, permisos, licencia, sandbox y automatización; cada proveedor exige prueba de concepto y contrato del adaptador. Investigar herramientas OSS por familias, con ADR de versión, licencia comercial, dependencias, mantenimiento, telemetría, consumo, confianza, imágenes firmadas y restricciones. **No descargar repos externos y ejecutarlos en el host**; usar imágenes verificadas y fixtures sintéticos. Reutilizar escáneres existentes antes de ampliar el catálogo.

## 10. Gates de producción y definición de terminado
G0 autorización y alcance; G1 aislamiento y egress; G2 identidad y capacidades; G3 integridad y custodia; G4 resiliencia y stop; G5 cobertura/validación independiente; G6 privacidad, licencias y operación. Un fallo bloquea el nivel correspondiente. **DONE de lab v1:** un tenant ficticio autoriza un repo sintético, el orquestador lanza un agente intercambiable, ejecuta pruebas permitidas sin egress, descubre o descarta hallazgos con evidencia, entrega reporte, propone PR privado, un segundo evaluador retestea, el humano revisa y el sandbox se destruye. No se declara pentest completo ni garantía de seguridad por ausencia de hallazgos.

## 11. Handoff literal para Freebuff/Codex
> Implementa el programa ADV-01..15 en `uniscrolliabrain-cloud/agntia-ciberseguridad`, una campaña por rama y PR. Antes de tocar archivos, reaudita main, AGENTS.md, docs/release/status.json, docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md, el programa AD de autodocumentación y este concepto. La arquitectura actual solo autoriza herramientas MCP de lectura y notas; no amplíes ese gateway a ejecución arbitraria. Crea un execution plane adversarial aislado con broker y políticas separadas, consentimiento verificable y kill switch. Codex, Antigravity, Cline, Freebuff son proveedores intercambiables, nunca autoridades. Reutiliza Vault, jobs, audit, outbox, findings y reports. Empieza exclusivamente con datos sintéticos y targets propios autorizados. Tests antes de código; negativos, tenancy, revocación, aislamiento, crash/retry, egress y rollback obligatorios. Reporta evidencia real, skips y limitaciones; no inventes capacidades, commits, CI ni aprobación. Si un gate falla, BLOCKED. No tocar /agente, clientes ni producción sin autorización.
