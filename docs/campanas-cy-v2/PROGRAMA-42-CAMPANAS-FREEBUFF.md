# CY-V2 — Programa de 42 campañas FreeBuff / Codex para ciberseguridad empresarial agéntica

**Fecha:** 2026-11-15. **Estado:** PLANIFICADO / NO EJECUTADO. **Base:** main tras PR #12 (merge 9cf67f88edda677a03bc4fdfbbef05d970d7b1ba). **Owner:** founder. **Orden:** hijo 1/14.

## Decisión de producto y alcance

Construir un middleware empresarial continuo de **auditoría → exposición → correlación → priorización → propuesta → aprobación → remediación → verificación**, con **Pedro** como interfaz especializada y **Laia** como supervisora en AgntiaPro. Aprender de CNAPP, XDR, AppSec, AI Security, Threat Intelligence y SOAR de líderes globales, sin afirmar equivalencia de cobertura. Integrar OSS/proveedores autorizados en lugar de fabricar un EDR/SOC 24/7. Amenazas prioritarias: ransomware, credenciales, supply chain, cloud, IA/MCP/RAG, exfiltración, BEC/deepfakes y continuidad de pymes. **Fuera de alcance ahora:** gobierno, sector hospitalario, fintech especializada, infraestructuras críticas y resiliencia social. La resiliencia aquí es solo continuidad de la empresa cliente.

## Jerarquía documental y compatibilidad

- **No sustituye** las 42 fases históricas, ni `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md` (CY-R01..12), ni `docs/release/status.json`. El programa diferencial es **preflight obligatorio**: ejecutar o demostrar mediante evidencia cada gate aplicable antes de CY-V2-09. CY-V2-01..08 reutilizan y cierran esos deltas, sin duplicar implementaciones.
- Conservar las categorías R01..R10 de `docs/01-vision-y-requisitos.md`; añadir capas de correlación e inteligencia **sin romper API ni semántica**. `not_tested`, `partial`, `suspected`, `confirmed`, `verified_fixed` no son intercambiables.
- `docs/roadmap-integracion-agente-2026-11/ROADMAP.md` rige L0..L8; este plan es el desglose de ejecución de L1..L8. L3 se desarrolla en paralelo por contrato; cambios en repo padre exigen autorización separada.
- Referencias a paths son **superficies candidatas**; FreeBuff debe comprobar el árbol real de HEAD antes de crear/modificar. No inferir módulos inexistentes.

## Protocolo invariante para cada campaña

1. Rama nueva `feat/cy-v2-NN-slug` desde `main` actualizado, SHA base y ownership disjunto; un PR por campaña; no force-push ni tocar legacy. Mantener orden secuencial salvo paralelismo aprobado por superficies disjuntas.
2. **FreeBuff** audita el código existente antes de escribir: inventario de archivos, interfaces, tests, delta exacto, amenazas, alternativas OSS/licencias, patchsets, migración y rollback. No reimplementar capacidades presentes.
3. Implementar contratos tipados (Zod/Pydantic según capa), tenant/principal verificados por servidor, policy deny-by-default, efectos idempotentes, presupuestos y receipts, evidencia minimizada, auditoría y eventos append-only con correlationId/causationId. El LLM propone; kernel/policy dispone.
4. **Codex** revisa diff y ejecuta unit/integration/adversarial, Python 3.11/3.12, SDK TS, Docker scanner/browser cuando aplique, test de tenant isolation, replays, fallos y CI. Registrar comandos, exit codes, SHA, IDs de workflows, skips y cobertura; tests no ejecutados = NOT_VERIFIED.
5. Escribir `docs/campanas-cy-v2/reportes/CY-V2-NN-REPORT.md` con objetivo, baseline, archivos tocados, tests, evidencias, hallazgos, riesgo residual, rollback, siguiente campaña y decisión PASS/FAIL/BLOCKED/NOT_VERIFIED. No cambiar `docs/release/status.json` sin pruebas específicas y aceptación.
6. **Founder approval** para cambios externos, permisos, cuentas, compras, datos reales, parent repo, despliegues, contención y merge/release sensible. No producción por defecto; no explotación ofensiva ni scanning de terceros sin autorización.

## Secuencia y contratos de aceptación

### G0 · Baseline y gates

#### CY-V2-01 — Baseline verificable y reconciliación

- **Superficies candidatas:** `README.md`, `docs/release/status.json`, `docs/auditoria-runtime/`, `.github/workflows/`.
- **Objetivo y patchsets:** Congelar SHA, árbol, PR, tests, skips, cobertura y deuda; preservar histórico. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Matriz commit→CI→evidencia; ninguna fase promocionada sin prueba. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-01-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-02 — Auth adversarial y aislamiento tenant

- **Superficies candidatas:** `agntia_ciberseguridad/auth.py`, `app.py`, `tests/`.
- **Objetivo y patchsets:** Matriz principal/actor/tenant/grant/revocación por endpoint y carreras. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Cross-tenant, token expirado/revocado y actor equivocado denegados. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-02-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-03 — RequestBoundary y snapshots seguros

- **Superficies candidatas:** `app.py`, `config.py`, `adapters/`, `tests/docker/`.
- **Objetivo y patchsets:** Streaming, symlinks/TOCTOU, zip bombs, cuotas, cancelación, sandbox sin red. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Entradas hostiles fallan cerradas; sin ejecución de código del cliente. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-03-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-04 — Scanners y coverage truth

- **Superficies candidatas:** `adapters/`, `tests/docker/`, `docs/release/`.
- **Objetivo y patchsets:** Gitleaks/OSV/Semgrep/Trivy: fixtures, versiones, feeds, formatos, licencias. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Scanner ausente/timeout/feed obsoleto nunca equivale a limpio. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-04-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-05 — Jobs durables y replay

- **Superficies candidatas:** `jobs.py`, `storage.py`, `features.py`, `tests/`.
- **Objetivo y patchsets:** Leases/fencing, idempotency, cancel, DLQ, recovery tras crash. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Replay sin duplicar efectos; estados parciales explícitos. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-05-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-06 — Evidence custody y restore

- **Superficies candidatas:** `features.py`, `docs/operations/`, `tests/`.
- **Objetivo y patchsets:** Cifrado, minimización, retención/hold, rotación de claves, restore ensayado. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Cadena de custodia y restauración verificables. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-06-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-07 — Agent gateway y MCP adversarial

- **Superficies candidatas:** `agents/routes.py`, `auth.py`, `tests/`.
- **Objetivo y patchsets:** Tool provenance, inyección, exfil, scopes, delegación, kill-switch. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Ningún prompt/tool amplía permisos; tests de denegación. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-07-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-08 — SDK, outbox y contrato padre

- **Superficies candidatas:** `docs/09-contrato-con-agente.md`, `SDK TS`, `tests/`.
- **Objetivo y patchsets:** Versionar envelopes, receipts, event bus, retries, dedup, BFF. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Consumidor simulado reanuda sin pérdidas ni efectos duplicados. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-08-REPORT.md` con veredicto independiente de Codex.

### G1 · Asset & Exposure Intelligence

#### CY-V2-09 — Asset inventory normalizado

- **Superficies candidatas:** `app.py`, `features.py`, `schemas`, `tests/`.
- **Objetivo y patchsets:** Inventario autorizado de repos, dominios, cloud, identidades y agentes; ownership. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** IDs estables y coverage por fuente; cero activos externos sin grant. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-09-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-10 — Conectores cloud read-only

- **Superficies candidatas:** `adapters/`, `config.py`, `tests/`.
- **Objetivo y patchsets:** AWS/Azure/GCP por adapters mínimos y credenciales scoped, sin inventar soporte. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Mock contract y sandbox de proveedor; falta de acceso = not_tested. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-10-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-11 — Identity exposure & permissions

- **Superficies candidatas:** `auth.py`, `schemas`, `adapters/`, `tests/`.
- **Objetivo y patchsets:** Representar humanos, service accounts, tokens, permisos y rutas de privilegio. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Detección de exceso de permisos con evidencia, sin secretos. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-11-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-12 — Security Knowledge Graph v1

- **Superficies candidatas:** `features.py`, `storage.py`, `schemas`, `tests/`.
- **Objetivo y patchsets:** Nodos asset/principal/agent/finding/exposure/dependency y edges con procedencia. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Grafo tenant-scoped, deduplicable y reconstruible desde eventos. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-12-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-13 — Attack-path analysis defensivo

- **Superficies candidatas:** `graph`, `findings`, `tests/`.
- **Objetivo y patchsets:** Correlacionar exposición, identidad, exploitability y dependencia; sin explotación. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Ruta explicable con evidencia y confianza; desconocido no es seguro. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-13-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-14 — Risk prioritization contextual

- **Superficies candidatas:** `findings`, `reports`, `schemas`, `tests/`.
- **Objetivo y patchsets:** Combinar criticidad, exposición, KEV/EPSS cuando disponibles, cobertura e impacto. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Ranking reproducible; explicar score y evitar falsa precisión. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-14-REPORT.md` con veredicto independiente de Codex.

### G2 · Threat Intelligence & Detection

#### CY-V2-15 — Threat feed ingestion

- **Superficies candidatas:** `adapters/`, `storage.py`, `tests/`.
- **Objetivo y patchsets:** CVE/NVD, CISA KEV, OSV y MITRE ATT&CK; cache, licencias, timestamps. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Feed stale/caído marcado; ninguna ingesta externa sin policy. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-15-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-16 — Intel-to-asset correlation

- **Superficies candidatas:** `graph`, `findings`, `tests/`.
- **Objetivo y patchsets:** Mapear CPE/purl/CVE y versiones con incertidumbre, no solo texto. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Fixtures positivos, negativos y falsos matches documentados. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-16-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-17 — Security event normalization

- **Superficies candidatas:** `events`, `schemas`, `tests/`.
- **Objetivo y patchsets:** Esquema versionado para auth, cloud, endpoint externo, agent tools y auditoría. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Correlación, causalidad, redacción y outbox at-least-once. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-17-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-18 — Detections as code

- **Superficies candidatas:** `policies`, `rules`, `tests/`.
- **Objetivo y patchsets:** Reglas versionadas y firmadas; ATT&CK mapping, severidad y provenance. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Fixtures benignos/maliciosos y control de falsos positivos. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-18-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-19 — Incident correlation & case lifecycle

- **Superficies candidatas:** `features.py`, `incidents`, `tests/`.
- **Objetivo y patchsets:** Agrupar señales en cases con estado suspected/confirmed y owner. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Replay, dedup, supresión reversible y timeline auditable. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-19-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-20 — SOC integrations read-only

- **Superficies candidatas:** `adapters/`, `SDK`, `tests/`.
- **Objetivo y patchsets:** Integrar alertas de Wazuh/Defender/SIEM existentes sin prometer EDR propio. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Conector deshabilitado por defecto; datos mínimos y cobertura explícita. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-20-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-21 — Threat hunting defensivo autorizado

- **Superficies candidatas:** `jobs`, `queries`, `tests/`.
- **Objetivo y patchsets:** Búsquedas acotadas sobre telemetría consentida y reglas de hipótesis. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Query allowlist, cuotas, tenant isolation, no escaneo ajeno. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-21-REPORT.md` con veredicto independiente de Codex.

### G3 · AI Security & Fraud

#### CY-V2-22 — AI agent inventory & provenance

- **Superficies candidatas:** `agents/routes.py`, `schemas`, `tests/`.
- **Objetivo y patchsets:** Manifests de agents/tools/skills/modelos, hashes, scopes y owners. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Cambios de manifiesto disparan revisión y evento. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-22-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-23 — Prompt injection evaluation harness

- **Superficies candidatas:** `tests/`, `fixtures/`, `agents/`.
- **Objetivo y patchsets:** Benchmarks sintéticos direct/indirect injection y tool-output poisoning. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Métricas de bypass con corpus versionado, sin claims de invulnerabilidad. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-23-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-24 — RAG/memory exfil safeguards

- **Superficies candidatas:** `agents/`, `policies`, `tests/`.
- **Objetivo y patchsets:** Límites de retrieval, etiquetas de confianza, redacción y DLP. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Pruebas de fuga cross-tenant y documentos no confiables. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-24-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-25 — Tool execution policy gateway v2

- **Superficies candidatas:** `agents/routes.py`, `auth.py`, `tests/`.
- **Objetivo y patchsets:** Policy deny-by-default para tool calls, egress, resource IDs y budgets. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Permiso revalidado antes de cada efecto; kill-switch probado. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-25-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-26 — Agent behavior anomaly detection

- **Superficies candidatas:** `events`, `detections`, `tests/`.
- **Objetivo y patchsets:** Secuencias anómalas de tools, spikes, scopes y destinos; señales no veredictos. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Alertas explicables, umbrales reproducibles y tasa de FP. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-26-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-27 — Business fraud / BEC triage

- **Superficies candidatas:** `features.py`, `adapters/`, `tests/`.
- **Objetivo y patchsets:** Factura alterada, cambio de IBAN, phishing y suplantación; verificación fuera de banda. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Nunca autorizar transferencias ni declarar deepfake confirmado por score. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-27-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-28 — Deepfake evidence & escalation

- **Superficies candidatas:** `incidents`, `evidence`, `tests/`.
- **Objetivo y patchsets:** Protocolo de señales voz/video, metadatos, revisión humana y canal confiable. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Resultado suspected/reviewed, sin identidad biométrica infalible. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-28-REPORT.md` con veredicto independiente de Codex.

### G4 · Response & Remediation

#### CY-V2-29 — Remediation plan schema

- **Superficies candidatas:** `remediations`, `schemas`, `tests/`.
- **Objetivo y patchsets:** Plan tipado con diff, impacto, preconditions, approval y rollback. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** No shell libre; dry-run determinista y hash de propuesta. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-29-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-30 — Patch generation sandbox

- **Superficies candidatas:** `remediations`, `jobs`, `tests/`.
- **Objetivo y patchsets:** Parches de código/config en branch efímera aislada y sin secretos. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Build/tests ejecutados, no afirmados; cambios fuera scope denegados. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-30-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-31 — Verification & regression gates

- **Superficies candidatas:** `tests/`, `scanners`, `reports/`.
- **Objetivo y patchsets:** Re-scan y tests negativos/positivos antes/después; distinguir fixed de not_tested. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** verified_fixed solo con evidencia y cobertura suficiente. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-31-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-32 — Incident containment proposals

- **Superficies candidatas:** `incidents`, `policies`, `tests/`.
- **Objetivo y patchsets:** Proponer revocar token, aislar servicio o bloquear egress; simulación. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Ningún efecto en producción sin approval humana y recibo. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-32-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-33 — Backup/restore & business continuity SME

- **Superficies candidatas:** `docs/operations/`, `jobs`, `tests/`.
- **Objetivo y patchsets:** RTO/RPO de servicios empresariales, copias, restores y modo degradado. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Ensayo restore real en entorno autorizado; no promesa de continuidad total. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-33-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-34 — Approval, compensation & rollback

- **Superficies candidatas:** `policy`, `approvals`, `jobs`, `tests/`.
- **Objetivo y patchsets:** Binding de aprobación a tenant/actor/objeto/hash/TTL; compensaciones. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Approval replay y TOCTOU bloqueados; rollback ensayado. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-34-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-35 — SOP library & tabletop SME

- **Superficies candidatas:** `docs/operations/`, `incidents`, `tests/`.
- **Objetivo y patchsets:** Playbooks ransomware, credenciales, BEC, fuga y proveedor caído. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Tabletop sintético con roles, pasos, evidencias y límites. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-35-REPORT.md` con veredicto independiente de Codex.

### G5 · Enterprise Delivery & Integration

#### CY-V2-36 — Security posture & coverage dashboard

- **Superficies candidatas:** `reports`, `workspace`, `SDK`, `tests/`.
- **Objetivo y patchsets:** Vistas ejecutivo/técnico, coverage, unknowns, trend, incidentes. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Ningún semáforo verde por ausencia de datos; tenant isolation. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-36-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-37 — Evidence-backed reports & exports

- **Superficies candidatas:** `features.py`, `reports`, `tests/`.
- **Objetivo y patchsets:** JSON/HTML/SARIF/PDF cuando exista pipeline; redacción y cadena causal. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Cada claim cita finding/scan/snapshot; no certificación automática. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-37-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-38 — Capability bundle /agente

- **Superficies candidatas:** `docs/09-contrato-con-agente.md`, `SDK`, `manifests`, `tests/`.
- **Objetivo y patchsets:** Bundle semver de capabilities, SOPs, effects, scopes, receipts y eventos. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Contrato E2E en fake parent; cambios reales padre solo con aprobación. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-38-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-39 — Pedro/Laia UX + FastConversationV2

- **Superficies candidatas:** `docs/roadmap-integracion-agente-2026-11/ROADMAP.md`, `SDK`, `tests/`.
- **Objetivo y patchsets:** IntentEnvelope→kernel→capability→ProgressProjector; fast no ejecuta efectos. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Estados comunicados solo desde eventos reales; no progreso ficticio. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-39-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-40 — Dogfood 2 empresas y operación humana

- **Superficies candidatas:** `tests/`, `docs/release/`, `runbooks`.
- **Objetivo y patchsets:** E2E de auditoría, aprobación, remediación y reporte sin LLM, 2 tenants. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Founder acepta manualmente; no clientes reales ni producción por defecto. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-40-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-41 — Independent security review & pilot gates

- **Superficies candidatas:** `docs/release/PILOT-ACCEPTANCE.md`, `CI`, `docs/operations/`.
- **Objetivo y patchsets:** Revisión independiente, licencias, DPA, vulnerabilidades, backup, BFF, SLO. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** No pilot/production_enabled sin evidencia y owner acceptance. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-41-REPORT.md` con veredicto independiente de Codex.

#### CY-V2-42 — Release, economics & final founder report

- **Superficies candidatas:** `docs/release/`, `README.md`, `docs/operations/`.
- **Objetivo y patchsets:** Costes reales por tenant, alertas, rollback, semver, release y lecciones. Inspeccionar interfaces reales, añadir schemas/migraciones y fixtures solo cuando falten; mantener compatibilidad con snapshots, jobs, findings, evidence y SDK existentes.
- **Pruebas y gate:** Report consolidado 42/42 con PASS/FAIL/BLOCKED/NOT_VERIFIED; aprobación founder. Añadir test negativo, cross-tenant, error/timeout y regresión específicos; adjuntar evidencia reproducible y rollback.
- **Entregable:** PR, contratos versionados, tests, runbook y `docs/campanas-cy-v2/reportes/CY-V2-42-REPORT.md` con veredicto independiente de Codex.

## Gates transversales y definición de terminado

- **G0 Foundation:** CY-V2-01..08 + CY-R01..12 verificados o bloqueos documentados; CI y evidencia sin saltos; `production_enabled=false`.
- **G1 Exposure:** inventario y grafo reconstruibles, fuente y cobertura por activo, rutas de ataque defensivas explicables; nunca explotar activos.
- **G2 Detection:** feeds con freshness, correlación reproducible, incidentes con sospecha/confirmación separadas y falsos positivos medidos.
- **G3 AI/Fraud:** gateway fail-closed, exfiltration tests, humano confirma pagos/cambios de cuenta, deepfake = señal no veredicto.
- **G4 Remediation:** branch/staging, approval vinculada, re-scan y rollback; `verified_fixed` solo con evidencia.
- **G5 Enterprise:** founder ejecuta vertical slice sin LLM, SDK/parent contract, 2 tenants dogfood, auditoría independiente y checklist de piloto. No comercializar cobertura no validada.

## Instrucción inicial para FreeBuff

Leer en orden `README.md`, `docs/01-vision-y-requisitos.md`, `docs/09-contrato-con-agente.md`, `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md`, `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`, `docs/release/status.json`, `docs/release/PILOT-ACCEPTANCE.md` y el roadmap L0..L8. Antes de CY-V2-01 entregar inventario HEAD real, estado de PR/ramas y matriz de solapamiento CY-R vs CY-V2. **No ejecutar las 42 en modo ciego**: detener en gates fallidos y reportar al founder.

**Estado de autoría:** este documento es un plan de implementación. No se han ejecutado aquí las 42 campañas, auditorías independientes ni pruebas de integración en producción.
