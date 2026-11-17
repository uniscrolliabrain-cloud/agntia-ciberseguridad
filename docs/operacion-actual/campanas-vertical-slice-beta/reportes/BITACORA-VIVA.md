# Bitácora viva — programa VS-CY

Registro acumulativo. Cada entrada se escribe al cerrar una campaña y no se reescribe: las
correcciones se añaden como entrada nueva.

## VS-00 — Baseline y trazabilidad · 2026-11-16

- **Base:** `2da922f`. **Rama:** `feat/cyber-vs-00-baseline`. **PR:** #14.
- **Medido:** 196 tests middleware OK (8 skipped), 117 laboratorio, 6/7 SDK; 88 decoradores de ruta,
  278 archivos Python, 23 ramas, 7 workflows.
- **Defecto corregido:** `CyberError` usaba parameter properties y rompía el contract test en Node 26.
- **Gates:** G0 PASS; G2–G5 PARTIAL; G6/G7 BLOCKED; G8 NO-GO.
- **Pendiente:** revisión independiente.

## VS-01 — Contratos del slice · 2026-11-16

- **Base:** `2da922f`. **Rama:** `feat/cyber-vs-01-contracts`. **PR:** #15.
- **Resultado:** seis de ocho contratos existen con otro nombre; idempotencia ya implementada por
  cabecera; dos contratos sin esquema versionado (`AuditEventV1`, `RetestRequestV1`).
- **Corregido después:** el hallazgo sobre `finding_id` estaba invertido (ver VS-01A).

## VS-01A — Corrección de impacto · 2026-11-16

- **Rama:** `feat/cyber-vs-01a-finding-contract`. **PR:** #16.
- **Hecho:** `Finding` alineado con la proyección real (`Hash` de 64, `risk`, `context`,
  `exception`) y prueba sobre un finding escaneado. `RemediationPlan.finding_id: Hash` era correcto.
- **Acotado:** `causation_id = correlation_id` es inconsistencia semántica sin consumidor; no
  vulnerabilidad. Delta propuesto: cabecera opcional `X-Causation-Id`.
- **Verificación:** 197 tests OK (8 skipped); validador PASS.

## VS-02 — Herramientas reales en CI · 2026-11-16 · PASS sintético

- **Evidencia:** run **43982858508**, job `docker-contracts` `133703454341`, **success**.
- **Ejecutado:** Gitleaks (canario pese a supresión del repo), OSV (vulnerable/limpio/caducado/ausente),
  Semgrep (eval con `nosemgrep`), Trivy (DS-0002) y sandbox (UID, red, timeout, PIDs, limpieza).
- **Límites:** solo fixtures; digests resueltos en build y publicados como artefacto, no fijados en
  el repo; sin feeds en vivo ni licencias.
- **Gates:** G2 y G3 pasan en sintético; auditoría externa sigue pendiente.
- **Informe:** `VS-02-REPORT.md`.

## VS-03 — Secretos e identidad · 2026-11-16 · PARTIAL

- **P0/P1:** inventario de 6 tipos de referencia (`token_env`, `key_refs`, `key_env`,
  `metrics_token_env`, `delegation_key_env`, `emergency_token_env`), todos sin valor en repo, con
  validadores que impiden compartir referencias operativas.
- **P3:** revocación, expiración, tenant cruzado y replay ya cubiertos por tests citados.
- **Huecos:** sin gestor (P2 BLOCKED), sin TTL por token; la fuga en logs ya tiene prueba
  (`test_secret_leakage.py`).
- **Decisión:** no se crea un `SecretStore` nuevo porque duplicaría el patrón existente sin aportar
  revocación.
- **Informe:** `VS-03-REPORT.md`.

## VS-04 — Custodia, backup y restore · 2026-11-16 · BLOCKED en externo

- **P0:** el middleware cifra con AES-GCM, AAD por tenant y clave desde `EnvRef`, pero **no tiene
  backup ni restore**; el laboratorio sí tiene `backup`/`restore` con hashes y rotación de claves,
  solo en local.
- **P1:** envelope de clave con `key_version`, almacén externo por tenant, manifiesto de backup y
  RPO/RTO medibles.
- **Gate:** `BLOCKED` hasta que el founder elija storage/KMS y apruebe coste. No se simula restore
  externo con disco local.
- **Informe:** `VS-04-REPORT.md`.

## VS-05 — Jobs, leases y cancelación · 2026-11-17 · PARTIAL

- **Ya implementado:** idempotencia tenant-scoped, fencing por lease, lease vencida → reconciliación,
  backoff con jitter y cupos por tenant/herramienta.
- **Delta:** prueba de cancelación en vuelo, sin resultado persistido.
- **Integración:** se trajo el fix de `CyberError` de VS-00 a esta rama.
- **Verificación:** 197 OK (8 skipped).
- **Huecos:** multiproceso real, SIGTERM, cancelación tras efecto externo, DLQ.
- **Informe:** `VS-05-REPORT.md`.

## VS-06 — Release fail-closed · 2026-11-17 · BLOCKED

- **Pasa:** smoke instalado, bundle + SBOM CycloneDX válido, gate de integridad del laboratorio.
- **Falla cerrado:** `--production` exit 1 por firma local sin atestación externa.
- **Hallazgo P0:** `pip-audit` detecta 14 vulnerabilidades; `opentelemetry-api==1.38.0` tiene CVE
  con fix 1.45.2, pero el upgrade rompe la propagación de trazas y se revirtió.
- **P1:** ningún workflow ejecuta `pip-audit`.
- **Gate:** BLOCKED; suite 197 OK tras revertir.
- **Informe:** `VS-06-REPORT.md`.

## VS-07 — Observabilidad y alertas · 2026-11-17 · PARTIAL

- **Inventario:** métricas por operación/estado, histograma, cobertura, logs acotados y 5 reglas en
  `alerts.yaml`; colector fijado por digest y CI propio.
- **Medido:** p50 6,04 ms / p95 7,02 ms (200 req); p95 7,19 ms con concurrencia 10; 0 errores
  inesperados; 71 señales de logs descartadas bajo carga.
- **Bloqueos:** `verify_observability.py` requiere Docker (no disponible aquí) y no hay receptor
  real ni acuse.
- **Gate:** PARTIAL; entrega de alarmas BLOCKED.
- **Informe:** `VS-07-REPORT.md`.

## VS-08 — Adaptador /agente · 2026-11-17 · BLOCKED

- **Inventario:** SDK server-only; se añadieron `submitAudit` (idempotencia en cabecera) y
  `cancelJob`; siguen faltando evidencia, historial y retest.
- **Verificación:** SDK 7/8 pass (1 skip de contrato vivo), suite 197 OK.
- **Mapeo:** status, findings y report cubiertos; request, evidencia y cancelación requieren método;
  retest no tiene ruta.
- **Entregable:** `VS-08-AGENTE-PATCHSET.md` con contrato, idempotencia y errores.
- **Gate:** BLOCKED; no se tocó `/agente` ni se pidieron privilegios.
- **Informe:** `VS-08-REPORT.md`.

## VS-06B — Cierre del bloqueo de dependencias · 2026-11-17

- **Base:** `1946f8c`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
- **Corregido el diagnóstico de VS-06:** el upgrade a OpenTelemetry 1.45.2 no rompía el SDK; el
  propagador emite flags `03` y nuestro `TRACEPARENT` solo aceptaba `0[01]`, así que el worker
  descartaba el padre guardado. Corregido con `trusted_parent()` (versión `00`, ids no nulos, bit de
  muestreo) y test de regresión.
- **Pins:** `opentelemetry-sdk==1.45.2`, `opentelemetry-exporter-otlp-proto-http==1.45.2`.
- **`pip-audit`:** 14 vulnerabilidades → **0** (`pip` 24.0 → 26.3 y OTel 1.38.0 → 1.45.2).
- **P1 cerrado:** `.github/workflows/dependency-audit.yml` con `pip-audit==2.10.1` (`--local` y
  `pip-audit .`); aún **sin run de CI**.
- **Verificación:** 205 tests OK (8 skipped); validador documental PASS.
- **Release:** bundle PASS en `5c12bbd` (39 wheels, smoke PASS, integridad PASS);
  `releasecheck.py --production` sigue **exit 1** (fail-closed, sin relajar controles).
- **Gate con dientes:** con el pin anterior el auditor devuelve 2 CVE y exit 1.
- **Sigue abierto:** atestación externa (`--production` falla cerrado por diseño) y el primer run
  real de `dependency-audit.yml` en GitHub Actions.

## VS-07A — Entrega y acuse de alertas · 2026-11-17 · PARTIAL alto

- **Base:** `1946f8c`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
- **Construido:** `scripts/alert_sink.py`, receptor local firmado (HMAC-SHA256), con dedupe por
  huella, proyección de 6 campos y acuse explícito `contained: false`; secreto solo por entorno.
- **Probado:** 6 tests; las 5 reglas de `alerts.yaml` se entregan y se ligan a su `job_id`;
  firma ausente/alterada → 401; 8 duplicados concurrentes → 1 acuse.
- **Sin fuga:** texto libre del emisor (incluido canario) no aparece ni en el acuse ni en el estado.
- **Sigue bloqueado:** proveedor real, escalado a persona y runbook. El acuse no es contención.

## VS-05A — Parada ordenada del worker · 2026-11-17 · PARTIAL alto

- **Base:** `acccf0d`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
- **Construido:** `agntia_ciberseguridad/jobs/runner.py` con `serve()` (un intento por iteración) y
  `ShutdownWatch` para `SIGTERM`/`SIGINT`, con restauración de handlers.
- **Semántica:** parada entre iteraciones no reclama nada; parada con intento en vuelo espera una
  gracia acotada y, si expira, cancela → el job queda `reconciliation_required` /
  `worker_cancelled`, sin resultado persistido y sin reintento ciego.
- **Probado:** 7 tests, incluido `SIGTERM` real entre procesos (exit 0, `cancelled: 1`,
  `results: []`) y persistencia con `job_results` vacío.
- **Sigue abierto:** binario/cola de worker, multiproceso real con dos workers y DLQ.
- **Gate:** cierra el hueco SIGTERM de VS-05; no se marca PASS de operación.
- **Informe:** `VS-05A-REPORT.md`.

## VS-07B — Simulacros P3 · 2026-11-17 · PARTIAL

- **Base:** `acccf0d`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
- **D1 escáner caído:** PASS; dos intentos fallidos → `failed`, cobertura incompleta, alerta
  `AgntiaDeclaredScanCoverageIncomplete` entregada y acusada (`contained: false`), duplicado deduplicado.
- **D2 backup fallido:** **BLOCKED**; el fallo es cerrado (`lab_only`, `backup_key_unavailable`) pero
  no existe métrica ni regla de backup, así que nadie se entera. Declarado, no maquillado.
- **D3 presupuesto agotado:** PASS tras cerrar un punto ciego real: el rechazo `quota`/429 ocurría
  antes de crear el job y no tocaba ninguna métrica. Añadidos `agntia_job_admission_rejections_total`
  (etiqueta acotada `reason`) y la regla `AgntiaAttemptBudgetExhausted` (6.ª regla del grupo).
- **Probado:** 3 simulacros OK, 6 tests de entrega OK, suite **215 OK (8 skipped)**, validador PASS.
- **Sigue bloqueado:** proveedor, guardia, runbook y exportador de backup.
- **Informe:** `VS-07B-REPORT.md`.

## Cola y dependencias

| Campaña | Carril | Bloqueo |
|---|---|---|
| VS-02 | autónomo (CI) | ninguno técnico; requiere push del workflow |
| VS-03 | autónomo parcial | gestor real y credenciales |
| VS-04 custodia/KMS | P0/P1 hechos, P2 bloqueado | proveedor, clave y RPO/RTO |
| VS-05A SIGTERM | hecho en sintético | cola y host del worker |
| VS-05+ DLQ y multiproceso | autónomo | decisión de despliegue |
| VS-06B dependencias | hecho en local | falta run de CI |
| VS-07A entrega de alertas | hecho en sintético | proveedor, guardia y runbook |
| VS-07B simulacros P3 | 2 PASS / 1 BLOCKED | exportador de backup, Prometheus real |
| `/agente` | founder | autorización expresa |
| Activos propios / ROE | founder | inventario y permiso |
| Beta / cliente | founder | despliegue y aceptación |
| Revisión independiente | externo | revisor |

## Reanudación

1. Leer esta bitácora y `docs/ESTADO-VIGENTE.md`.
2. Revisar PR #14, #15 y #16; no fusionar sin revisión.
3. Empezar por VS-02 en CI, que no depende de decisiones del founder.
4. No marcar PASS sin receipt de CI o comando local con exit 0.
