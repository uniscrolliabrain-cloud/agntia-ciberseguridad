# Programa AD-01 → AD-15 — Ingeniería de autodocumentación, evaluación y publicaciones
**Fecha:** 2026-11-15 · **Repositorio:** `uniscrolliabrain-cloud/agntia-ciberseguridad` · **Base inspeccionada:** `main@aedf6f22e7cbdfe42af5dd8608af34a366bfb3b4` · **Estado:** PLANIFICADO, NO IMPLEMENTADO.
**Propósito:** handoff ejecutable para Freebuff/Codex u otra IA; construir la cadena de hechos→evidencia→evaluación→métricas→documentación→publicación con gates. NO fusionar este plan con las 42 campañas históricas ni con CY-R01..R12.

## Auditoría de código y verdad de baseline
Inspección de árbol GitHub recursivo (584 entradas, sin truncamiento), y lectura selectiva de código: `storage.py`, `events/outbox.py`, `evidence/vault.py`, `evidence/contracts.py`, `evidence/schema.py`, `reports.py`, `reviews.py`, `features.py`, `app.py`, `jobs/worker.py`, `jobs/schema.py`, `agents/flows.py`, `governance/remediation.py`, `telemetry/export.py`, `pyproject.toml`, `typescript/package.json`, tests y auditorías. **Es revisión estática selectiva, NO ejecución local de tests, pentest completo ni prueba independiente.** Antes de editar, la IA ejecutora debe reauditar el SHA de su rama y las funciones completas.
- `storage.py`: SQLite WAL y migraciones **1–8**, audit append-only con hashes encadenados, outbox enlazado a `Database.audit`. No inventar Postgres como almacenamiento existente.
- `events/outbox.py`: outbox **local** con poll/ACK y `SyntheticConsumer`, allowlist de eventos de jobs y presupuesto; **no** entrega remota/scheduler.
- `evidence/vault.py`: AES-GCM, originales cifrados, vistas minimizadas, hold/retención, máximo **2 MiB** por evidencia. Reusar y no construir un vault paralelo.
- `reports.py`: reportes inmutables JSON/HTML/CSV, fuente hash y Vault; **no** pipeline científico ni publicaciones todavía.
- `reviews.py`: propuestas y aprobaciones humanas ligadas a hashes, retest de findings. No confundir con peer review científico ni approval de publicación.
- `jobs/worker.py`: worker iterativo con lease/fence/reconciliación; no scheduler empresarial.
- `governance/remediation.py`: **dos reglas de laboratorio** (`remove_synthetic_canary`, `remove_fixture_eval`), sin cambios en clientes/producción.
- `agents/flows.py`: flujo de datos con procedencia, egress preflight, **sin transporte de red habilitado**.
- `scripts/evaluate_agent_gateway.py`: evaluación sintética sin invocar modelo/proveedor. No atribuirle benchmarks de LLM reales.
- `typescript/package.json`: SDK `@agntia/ciberseguridad` privado, Hono 4.13.18, TypeScript 5.9.3, Node >=22; **no** integrado al repo madre.
- `docs/release/status.json`: **2 PASS / 40 PARTIAL**, **80 PASS / 214 PARTIAL**, `SYNTHETIC_DEMO_NOT_PRODUCTION`, `production_enabled=false`.
- `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`: CY-R01..R12 tienen prioridad para resolver gates de seguridad y calidad. Si AD requiere modificar una superficie con CY-R en curso, bloquear AD hasta reconciliar y rebasar.
- `README.md`, `docs/README.md`, `AGENTS.md`: cabeceras actualizadas prevalecen sobre texto histórico contradictorio.
**Limitación:** no se ha ejecutado CI sobre este nuevo plan. No se afirma ausencia total de contradicciones futuras; se exige comprobación de código, tests y rebase por campaña.

## Protocolo de ejecución obligatorio
1. Por campaña: crear rama `feat/cyber-autodoc-AD-XX` desde `main` actualizado, registrar SHA, comprobar `git status`, `git ls-files` y buscar referencias actuales. No reutilizar resultados de un SHA anterior.
2. Freebuff implementa solo su campaña; Codex audita diff, crea/ejecuta pruebas independientes y revisa vulnerabilidades. Founder supervisa y autoriza fusiones/despliegues. **No merge automático ni cambios en `/agente`.**
3. Crear `docs/autodoc/reports/AD-XX-REPORT.md` con SHA inicial/final, ficheros creados/editados, patchsets, comandos, exit codes, número de tests/skips, artefactos, amenazas, falsos positivos, fallos, rollback y estado PASS/FAIL/BLOCKED/NOT_VERIFIED.
4. La lista de archivos de cada campaña es **plan de escritura sujeto a auditoría**: si el fichero o interfaz cambió, adaptar mediante ADR, nunca escribir a ciegas. Si una ruta sugerida ya existe, modificar conservando compatibilidad, no sobrescribir.
5. Pruebas reales: `python -m unittest discover -s tests`, `python scripts/validate_foundation.py`, `python scripts/release_status.py`, `cd typescript && npm test`; ejecutar los scripts Docker/browser de CI según superficie. No marcar PASS sin ejecución, registrar skips.
6. Deny-by-default, tenant isolation, secrets fuera de prompts/logs, tests offline por defecto, no network externa, no escaneo de terceros, no autopublicación, no datos de clientes reales.
7. Si gate G1 seguridad, G2 funcionalidad, G3 reproducibilidad, G4 privacidad o G5 evidencia falla: BLOCKED. Si no se ejecuta: NOT_VERIFIED.
8. Cambios en SQLite: migración incremental después de versión 8, transacción, backup/restore, pruebas upgrade y rollback documentado (SQLite no permite downgrade ingenuo). Evitar múltiples campañas escribiendo la misma migración en paralelo.
9. Dependencias externas: **no instalar por inercia**. Stack base Python 3.11+ FastAPI/Pydantic/jsonschema/cryptography/OpenTelemetry; TS/Hono. Preferir `hashlib`, `json`, `unittest`, `statistics`. Evaluar `hypothesis` (property-based), `pytest` (ergonomía), `pip-audit`, `cyclonedx-python-lib`, `sigstore` y `cosign` solo mediante ADR de necesidad, licencias, versiones, cadena de suministro, coste y CI. Conceptos a estudiar: SLSA provenance, in-toto attestations, OpenTelemetry semantic conventions, OpenSSF Scorecard, NIST AI RMF, OWASP ASVS/LLM Top 10, MITRE ATT&CK/ATLAS, CycloneDX. No atribuir cumplimiento/certificación por adoptarlos.
10. Prioridad de dependencia: **AD-01→02→03→04→05→06→07→08→09→10→11→12→13→14→15**. AD-01 depende de reconciliación con CY-R01; AD-03/04/07/11/12 dependen de gates pertinentes de CY-R02/05/06/07. Solo paralelismo tras demostrar ownership disjunto.

## Plantilla universal de cada campaña
Cada campaña se ejecuta en seis fases obligatorias: **F0** reauditar código/contratos, **F1** escribir tests que fallen por capacidad ausente, **F2** aplicar patchset mínimo, **F3** integrar contratos/eventos/SDK sin regresión, **F4** tests positivos/negativos y seguridad, **F5** revisión Codex + reporte + rollback + gate. No cambiar ficheros fuera de la superficie declarada sin ADR y aprobación.


## AD-01 — Baseline verificable y mapa de integración
**Dependencia:** baseline y CY-R01. **Rama:** `feat/cyber-autodoc-AD-01`. **Entregable:** `docs/autodoc/reports/AD-01-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `docs/release/status.json`, `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md`, `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`, `AGENTS.md`, `.github/workflows/runtime.yml`, `.github/workflows/docs.yml`.

**Archivos nuevos propuestos:** `docs/autodoc/BASELINE-AUDIT.md`, `docs/autodoc/FILE-OWNERSHIP.md`, `docs/autodoc/TRACEABILITY.md`, `tests/autodoc/test_baseline_inventory.py` y `docs/autodoc/reports/AD-01-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `docs/engineering/AUTODOCUMENTACION-EVIDENCIAS-Y-PUBLICACIONES-TECNICAS.md`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** No tocar runtime. Registrar SHA, migraciones 1–8, rutas, dependencias y estado de gates; comprobar que los reportes no contradicen status.json.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** pytest/unittest discovery, npm test, scripts/validate_foundation.py, scripts/release_status.py; CI histórico separado de CI actual Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** P0: ninguna capacidad declarada como implementada sin test/commit. Revisión de seguridad y licencia del inventario. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-02 — Modelo canónico de run, estado y claims
**Dependencia:** AD-01. **Rama:** `feat/cyber-autodoc-AD-02`. **Entregable:** `docs/autodoc/reports/AD-02-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `agntia_ciberseguridad/contracts.py`, `agntia_ciberseguridad/jobs/contracts.py`, `agntia_ciberseguridad/jobs/schema.py`, `agntia_ciberseguridad/util.py`.

**Archivos nuevos propuestos:** `agntia_ciberseguridad/autodoc/__init__.py`, `agntia_ciberseguridad/autodoc/contracts.py`, `agntia_ciberseguridad/autodoc/claims.py`, `tests/unit/test_autodoc_contracts.py` y `docs/autodoc/reports/AD-02-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `scripts/export_schemas.py`, `docs/implementation/schemas/ (solo esquemas generados)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Pydantic v2: RunManifest, Claim, Evaluation, EvidenceRef; estados PASS/FAIL/INCONCLUSIVE/NOT_RUN; UTC aware, schemaVersion, tenantId, runId, correlationId; nunca mapear skipped→PASS.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Validación de payload inválido, timestamps naïve, IDs cruzados, unknown enums, claims sin evidencia, canonicalización y backwards compatibility. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría de contratos públicos, compatibilidad con job_id existente y clasificación de datos. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-03 — Instrumentación de ciclo de vida y outbox
**Dependencia:** AD-02 + gates CY-R pertinentes. **Rama:** `feat/cyber-autodoc-AD-03`. **Entregable:** `docs/autodoc/reports/AD-03-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `agntia_ciberseguridad/events/outbox.py`, `agntia_ciberseguridad/jobs/store.py`, `agntia_ciberseguridad/jobs/worker.py`, `agntia_ciberseguridad/storage.py`.

**Archivos nuevos propuestos:** `agntia_ciberseguridad/autodoc/capture.py`, `tests/integration/test_autodoc_capture.py` y `docs/autodoc/reports/AD-03-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `agntia_ciberseguridad/events/outbox.py`, `agntia_ciberseguridad/jobs/worker.py`, `agntia_ciberseguridad/storage.py (migración 9 solo si el diseño la exige)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Extender allowlist EXPORTED y proyección en outbox existente; instrumentar started/completed/failed/partial/cancelled con after_commit, correlation y causation; dedupe por event_id; prohibido crear segundo bus.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Rollback de transacción, reintento worker, duplicate delivery, crash entre commit/ACK, tenant A/B, orden por secuencia, audit hash chain. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditar atomicidad de escritura/outbox, replay, consumo sintético y payload sin secretos. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-04 — Custodia y manifiesto criptográfico de evidencias
**Dependencia:** AD-03 + gates CY-R pertinentes. **Rama:** `feat/cyber-autodoc-AD-04`. **Entregable:** `docs/autodoc/reports/AD-04-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `agntia_ciberseguridad/evidence/vault.py`, `agntia_ciberseguridad/evidence/schema.py`, `agntia_ciberseguridad/evidence/redaction.py`, `agntia_ciberseguridad/storage.py`.

**Archivos nuevos propuestos:** `agntia_ciberseguridad/autodoc/evidence_index.py`, `agntia_ciberseguridad/autodoc/sealing.py`, `tests/security/test_autodoc_evidence.py` y `docs/autodoc/reports/AD-04-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `agntia_ciberseguridad/evidence/vault.py`, `agntia_ciberseguridad/evidence/schema.py (migración nueva si hace falta)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Reusar Vault AES-GCM, límites de 2 MiB, hold y retención; manifest de SHA256 por artefacto, enlaces a vault id y versión; hash chain local no es notarización externa; original siempre sujeto a permiso humano.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Tampering de hash, swap de tenant, key missing, purge/hold, redaction leak, fallo de disco, concurrent write, restore; verify_audit. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría de criptografía, cadena de custodia, política de minimización y tratamiento de metadatos. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-05 — Captura de contexto de ejecución reproducible
**Dependencia:** AD-04. **Rama:** `feat/cyber-autodoc-AD-05`. **Entregable:** `docs/autodoc/reports/AD-05-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `agntia_ciberseguridad/runners/container.py`, `agntia_ciberseguridad/scanning.py`, `agntia_ciberseguridad/sbom.py`, `infra/scanners/releases.json`, `infra/scanners/semgrep-image.json`.

**Archivos nuevos propuestos:** `agntia_ciberseguridad/autodoc/environment.py`, `agntia_ciberseguridad/autodoc/provenance.py`, `tests/integration/test_autodoc_provenance.py` y `docs/autodoc/reports/AD-05-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `agntia_ciberseguridad/jobs/worker.py`, `scripts/demo_synthetic.py`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Capturar git SHA, image digest, herramienta, reglas, feed snapshot, fixture hash, seed, Python/Node versions, policy hash, configuración sanitizada; 'unknown' explícito cuando falte dato.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Fixture offline reproducida dos veces, cambio de digest, scanner ausente, feed desactualizado, timestamp distinto; verificar hash estable del manifest normalizado. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría supply-chain y licencias de reglas/feeds; no afirmar reproducibilidad si falta imagen o versión. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-06 — Suite benchmark sintética y golden datasets
**Dependencia:** AD-05. **Rama:** `feat/cyber-autodoc-AD-06`. **Entregable:** `docs/autodoc/reports/AD-06-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `fixtures/dependencies/README.md`, `fixtures/secrets/README.md`, `tests/security/scenario_catalog.json`, `tests/evaluations/gateway_cases.json`, `tests/evaluations/runner.py`.

**Archivos nuevos propuestos:** `benchmarks/cyber-evidence/README.md`, `benchmarks/cyber-evidence/catalog.json`, `benchmarks/cyber-evidence/fixtures/README.md`, `benchmarks/cyber-evidence/golden/expected.json`, `tests/evaluations/test_autodoc_benchmarks.py` y `docs/autodoc/reports/AD-06-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `scripts/create_offline_fixture.py`, `scripts/demo_synthetic.py`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Diseñar 10 escenarios: dependencia vulnerable, secreto ficticio, SAST, IaC simulado, prompt injection, autorización denegada, false positive, fallo de scanner, remediación con regresión, restore fallido; fixtures no operativos fuera sandbox.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Golden tests deterministas, negative control, not_run, contaminación entre train/eval, sin network, reproducibilidad de hashes y métricas por escenario. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría de cobertura, leakage de benchmark, autorización de pruebas y licencias de datasets. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-07 — Evaluación independiente y gates de calidad
**Dependencia:** AD-06 + gates CY-R pertinentes. **Rama:** `feat/cyber-autodoc-AD-07`. **Entregable:** `docs/autodoc/reports/AD-07-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `agntia_ciberseguridad/reviews.py`, `agntia_ciberseguridad/safety.py`, `agntia_ciberseguridad/governance/remediation.py`, `tests/integration/test_reviews_reports.py`.

**Archivos nuevos propuestos:** `agntia_ciberseguridad/autodoc/evaluator.py`, `agntia_ciberseguridad/autodoc/gates.py`, `tests/evaluations/test_autodoc_evaluator.py`, `tests/security/test_autodoc_separation_of_duties.py` y `docs/autodoc/reports/AD-07-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `agntia_ciberseguridad/reviews.py (solo wiring mínimo si necesario)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Evaluador no confía en salida del agente que remedia; verificar finding previo, retest equivalente, regresión funcional, provenance, scope, autorización; PASS solo con evidencias positivas.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Poisoned evaluation, skipped test, LLM fabricated success, fake retest, stale approval, finding fixed con regresión, mismo actor propone/aprueba. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría adversarial de independencia y autorización; revisión de falsos verdes. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-08 — Motor de métricas con denominadores y límites
**Dependencia:** AD-07. **Rama:** `feat/cyber-autodoc-AD-08`. **Entregable:** `docs/autodoc/reports/AD-08-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `agntia_ciberseguridad/telemetry/metrics.py`, `agntia_ciberseguridad/risk.py`, `agntia_ciberseguridad/reports.py`, `scripts/measure_pilot.py`.

**Archivos nuevos propuestos:** `agntia_ciberseguridad/autodoc/metrics.py`, `agntia_ciberseguridad/autodoc/statistics.py`, `tests/unit/test_autodoc_metrics.py` y `docs/autodoc/reports/AD-08-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `agntia_ciberseguridad/telemetry/views.py (si la vista actual necesita un nuevo campo compatible)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Calcular precision, recall solo con ground truth, success remediation, regression, coverage, p50/p95, RTO/RPO, coste por run; 0/0=N/A y denominadores visibles; separar simulated de real.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Tests tabla con 0/0, duplicados, censura, failed, partial, timeouts, reloj, outliers, sample pequeño, tenants y redondeos. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría estadística, riesgo de sesgo, validez externa y honestidad de métricas. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-09 — Generador determinista de paquetes de ejecución
**Dependencia:** AD-08. **Rama:** `feat/cyber-autodoc-AD-09`. **Entregable:** `docs/autodoc/reports/AD-09-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `agntia_ciberseguridad/reports.py`, `agntia_ciberseguridad/evidence/vault.py`, `agntia_ciberseguridad/util.py`.

**Archivos nuevos propuestos:** `agntia_ciberseguridad/autodoc/bundle.py`, `agntia_ciberseguridad/autodoc/render.py`, `tests/integration/test_autodoc_bundle.py` y `docs/autodoc/reports/AD-09-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `agntia_ciberseguridad/reports.py (extensión opt-in, preservar formatos JSON/HTML/CSV existentes)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Generar run-manifest.json, evidence-index.json, evaluation.json, metrics.json, technical-report.md, limitations.md; canon JSON y orden estable; separar contenido privado y sanitizado.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Golden snapshots, escape HTML/Markdown, JSON schema, redacción, reproducibilidad, corrupción de un artifact, repeated run idempotency. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría de cadena claim→evidence y controles de filtración. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-10 — Claim checker y asistencia LLM confinada a evidencias
**Dependencia:** AD-09. **Rama:** `feat/cyber-autodoc-AD-10`. **Entregable:** `docs/autodoc/reports/AD-10-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `agntia_ciberseguridad/agents/flows.py`, `agntia_ciberseguridad/agents/policy.py`, `agntia_ciberseguridad/agents/controls.py`, `agntia_ciberseguridad/evidence/redaction.py`.

**Archivos nuevos propuestos:** `agntia_ciberseguridad/autodoc/claim_checker.py`, `agntia_ciberseguridad/autodoc/draft.py`, `tests/security/test_autodoc_prompt_injection.py`, `tests/unit/test_autodoc_claim_checker.py` y `docs/autodoc/reports/AD-10-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `agntia_ciberseguridad/agents/flows.py (solo interfaz tipada`, `sin egress nuevo)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** LLM opcional redacta sobre dataset sanitizado; validador determinista exige EvidenceRef por afirmación, rechaza números no medidos, citas inexistentes y prompt injection; default offline sin proveedor.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Documento hostil, cita inventada, cifras manipuladas, claim contradictorio, mezcla de tenant, petición de divulgar secreto; LLM unavailable => paquete determinista. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría de prompt injection, trazabilidad de citas, minimización y permisos de salida. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-11 — API de lectura, control de acceso y SDK TS
**Dependencia:** AD-10 + gates CY-R pertinentes. **Rama:** `feat/cyber-autodoc-AD-11`. **Entregable:** `docs/autodoc/reports/AD-11-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `agntia_ciberseguridad/app.py`, `agntia_ciberseguridad/features.py`, `agntia_ciberseguridad/auth.py`, `typescript/src/client.ts`, `typescript/src/hono.ts`, `typescript/src/agent-tools.ts`.

**Archivos nuevos propuestos:** `agntia_ciberseguridad/autodoc/routes.py`, `tests/security/test_autodoc_api.py`, `typescript/test/autodoc.test.mjs` y `docs/autodoc/reports/AD-11-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `agntia_ciberseguridad/app.py`, `typescript/src/client.ts`, `typescript/src/hono.ts`, `typescript/src/agent-tools.ts`, `scripts/export_schemas.py`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Añadir endpoints nominados read-only para manifest, metrics y report sanitized; principal autenticado + tenant, RBAC, paginación, ETag; SDK server-only y herramientas agénticas sin publish.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** 401/403/404 cross tenant, agent impersonation, token revocado, traversal, mass assignment, SDK contract, request size, cache poisoning. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría de superficie HTTP, BFF, compatibilidad API y PII. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-12 — Motor de publicación privada y aprobación triple
**Dependencia:** AD-11 + gates CY-R pertinentes. **Rama:** `feat/cyber-autodoc-AD-12`. **Entregable:** `docs/autodoc/reports/AD-12-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `agntia_ciberseguridad/reviews.py`, `agntia_ciberseguridad/auth.py`, `agntia_ciberseguridad/evidence/vault.py`, `agntia_ciberseguridad/agents/flows.py`.

**Archivos nuevos propuestos:** `agntia_ciberseguridad/autodoc/publication.py`, `agntia_ciberseguridad/autodoc/publication_schema.py`, `tests/security/test_autodoc_publication_gate.py`, `docs/publications/REVIEW-POLICY.md` y `docs/autodoc/reports/AD-12-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `agntia_ciberseguridad/storage.py (migración nueva tras 8/9), agntia_ciberseguridad/features.py (solo endpoints explícitos si requeridos)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Máquina DRAFT→PRIVACY_REVIEW→SECURITY_REVIEW→TECH_REVIEW→OWNER_APPROVED→EXPORTABLE; approvals separadas, hash-bound, expiración; no publicar automáticamente ni usar network por defecto.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Race approval, revoked owner, stale hash, approval reuse, data leak, fail-open, malicious markdown, no consent; export blocked sin todos gates. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría privacidad, derechos sobre datos, divulgación responsable, gobernanza y segregación de funciones. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-13 — Plantillas de papers, model cards y reproducibilidad
**Dependencia:** AD-12. **Rama:** `feat/cyber-autodoc-AD-13`. **Entregable:** `docs/autodoc/reports/AD-13-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `docs/research/07-papers-y-noticias.md`, `docs/11-reportes-y-casos-de-uso.md`, `docs/engineering/AUTODOCUMENTACION-EVIDENCIAS-Y-PUBLICACIONES-TECNICAS.md`.

**Archivos nuevos propuestos:** `docs/publications/README.md`, `docs/publications/templates/technical-paper.md`, `docs/publications/templates/evaluation-card.md`, `docs/publications/templates/model-and-tool-card.md`, `docs/publications/templates/reproducibility-checklist.md`, `tests/autodoc/test_publication_templates.py` y `docs/autodoc/reports/AD-13-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `docs/engineering/AUTODOCUMENTACION-EVIDENCIAS-Y-PUBLICACIONES-TECNICAS.md (enlace a plantillas)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Plantillas con hypothesis, methods, environment, baselines, denominators, CIs, negative results, limitations, data governance, reproducibility; jamás presentar demo como piloto.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Lint de markdown, campos requeridos, links internos, citations, negative-result section, license review, checklist not-run. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría editorial, metodología científica y claims. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-14 — CI automatizada, release evidence y no-regresiones
**Dependencia:** AD-13. **Rama:** `feat/cyber-autodoc-AD-14`. **Entregable:** `docs/autodoc/reports/AD-14-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** ` .github/workflows/runtime.yml`, `.github/workflows/docs.yml`, `.github/workflows/release.yml`, `scripts/release_status.py`, `scripts/release_bundle.py`.

**Archivos nuevos propuestos:** `scripts/autodoc_validate.py`, `scripts/autodoc_generate.py`, `.github/workflows/autodoc.yml`, `tests/integration/test_autodoc_release.py` y `docs/autodoc/reports/AD-14-REPORT.md`.

**Archivos a modificar si el delta se confirma:** ` .github/workflows/docs.yml`, `.github/workflows/release.yml (solo enlaces y checks necesarios)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** CI PR: schema, unit, negative, integration, deterministic report, secret scan, link checker, redaction, no public upload; release bundle firmado cuando viable, pin actions.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Rerun on same SHA, tampered bundle, missing artifact, incomplete gates, missing tool, offline CI, Windows/Linux differences; record exit codes and skips. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría CI supply-chain, permissions mínimos, action pinning y publicación prohibida. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## AD-15 — Piloto sintético E2E, benchmark v1 y handoff de operación
**Dependencia:** AD-14. **Rama:** `feat/cyber-autodoc-AD-15`. **Entregable:** `docs/autodoc/reports/AD-15-REPORT.md`.

**Archivos existentes a inspeccionar (no asumir modificación):** `scripts/demo_synthetic.py`, `scripts/benchmark_foundation.py`, `scripts/measure_pilot.py`, `docs/release/PILOT-ACCEPTANCE.md`, `docs/operations/RUNBOOK.md`.

**Archivos nuevos propuestos:** `scripts/autodoc_e2e.py`, `tests/e2e/test_autodoc_pipeline.py`, `docs/publications/candidates/BENCHMARK-V1-DRAFT.md`, `docs/autodoc/FINAL-AUDIT.md`, `docs/autodoc/HANDOFF-OPERATIONS.md` y `docs/autodoc/reports/AD-15-REPORT.md`.

**Archivos a modificar si el delta se confirma:** `docs/operations/RUNBOOK.md`, `docs/release/PILOT-ACCEPTANCE.md (solo estado real, sin elevar gates)`. Evitar cambios fuera de ownership.

**Patchsets/fixes concretos:** Ejecutar escenario vulnerable→finding→retest→evidence→metric→draft; simular failure, partial, rollback, compromised evidence, reviewer unavailable; paper permanece DRAFT.

**Fases y microtareas:**
- **F0 Diagnóstico:** fijar SHA; leer las funciones y tests reales de cada archivo listado; mapear API, esquema, dependencias, permisos y limitaciones; reproducir comportamiento existente con fixture sintético; escribir matriz actual→deseado y riesgos; abrir ADR si la ruta ya no corresponde.
- **F1 Contratos y tests:** definir inputs/outputs tipados, estados, errores y invariantes; añadir al menos un test positivo, uno negativo, uno cross-tenant si hay datos, uno idempotencia/retry si hay eventos, uno de regresión; comprobar que los tests nuevos fallan por el delta esperado, no por entorno roto.
- **F2 Implementación:** introducir módulos nuevos pequeños, sin segundo runtime, bus, Vault o almacén; aplicar el patchset descrito; limitar escrituras a superficies enumeradas; usar feature flag por defecto deshabilitada cuando afecte ejecución o datos; registrar hashes y fuentes.
- **F3 Integración:** enlazar al servicio/worker/reports/API existente según necesidad; preservar payloads y rutas previas; actualizar schemas exportados y documentación; evitar llamadas externas y secretos en logs; mantener compatibilidad de SDK.
- **F4 Validación:** Python 3.11/3.12, npm test, Docker scanners, browser si aplica, E2E, adversarial, replay, recovery, privacy, performance, cost; publicar solo tras approval humano. Incluir test de fallo parcial, interrupción y reintento cuando proceda; medir cobertura de escenarios y registrar NOT_RUN explícitos.
- **F5 Auditoría/handoff:** Auditoría final independiente de permisos, integridad, estadísticas, seguridad de datos y compatibilidad; no piloto real sin gates existentes. Codex revisa diff y ejecuta tests desde checkout limpio; Freebuff genera reporte con evidencia de ejecución, fallos pendientes, SHA, rollback y decisión. No merge sin gate del founder.

**Criterios de aceptación:** A) capacidad demostrada con evidencia y SHA; B) errores y pruebas omitidas no se convierten en éxito; C) no se rompe auth/tenant/retención; D) reporte verificable y rollback descrito; E) pruebas del módulo anterior permanecen verdes. **Stop conditions:** filtración de datos, acción no autorizada, divergencia de contratos, CI no reproducible, migración insegura o fallo de aislamiento.

## Handoff literal para la IA ejecutora
> Eres el implementador del programa AD-01..AD-15 de `uniscrolliabrain-cloud/agntia-ciberseguridad`. Lee primero `AGENTS.md`, `docs/release/status.json`, `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md`, `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md` y este documento. Comprueba el SHA real, inspecciona el código antes de editar y ejecuta **una sola campaña por rama** en orden. No inventes funciones existentes, resultados de tests, benchmarks, clientes o aprobaciones. Reutiliza Vault, outbox, audit, reports, jobs, SDK y gates. Haz TDD, crea tests negativos y cross-tenant, ejecuta CI y documenta todo con comandos y códigos de salida. Si encuentras contradicción con el código, para, escribe un ADR y adapta el plan. No toques /agente, no escanees objetivos externos, no publiques ni despliegues sin aprobación. Al terminar cada campaña entrega PR, diff, tests, evidencias, riesgos y rollback; Codex revisa independientemente. El producto sigue siendo demo sintética hasta gates reales de aceptación.

## Matriz de verificación transversal y auditorías
| Auditoría | Campañas | Evidencia exigida |
|---|---|---|
| Contratos/schema y compatibilidad | 02,03,09,11,12 | JSON schema, test upgrade, diff SDK |
| Tenancy/RBAC/ABAC | 03,04,07,10,11,12 | pruebas A/B, roles, credenciales revocadas |
| Custodia/privacidad/retención | 04,09,10,12,15 | redacción, hold, purge, key rotation |
| Reproducibilidad/supply chain | 05,06,08,13,14,15 | hashes, imágenes, versiones, scripts |
| Red team defensivo | 06,07,10,12,15 | prompt injection, falsos verdes, poisoning |
| Continuidad y rollback | 03,04,09,14,15 | crash/retry, backup/restore, fail-closed |
| Científica y editorial | 08,10,13,15 | denominadores, baselines, límites, resultados negativos |
| Licencias y publicación | 01,05,06,12,13,15 | OSS, datos, consentimiento, approval |
| CI real | todas | commit→workflow→job→tests/skips→artefacto |

## Exclusiones y no-objetivos
No construir SIEM, SOC 24/7, DAST/EDR, pentesting de clientes, reconstrucción general, certificación acreditada, aseguradora, ejecución ofensiva sin autorización, portal público ni auto-publicación como parte de estas 15 campañas. Son dominios del Concept Master global o programas posteriores. No se modifica el estado de `docs/release/status.json` salvo que la implementación real y la revisión de gates justifiquen una transición, sin confundir progreso AD con gates de las 42 fases.

## Definición de DONE del programa
Un run sintético autorizado genera evidencias cifradas, manifest con procedencia, evaluación independiente con NOT_RUN, métricas correctas, informe técnico con claims trazables y borrador de paper privado. Una prueba fallida, dato ausente, secreto o aprobación revocada bloquea exportación. Otra IA reproduce el resultado en checkout limpio con mismos fixtures y versiones. Toda afirmación externa tiene evidencia y limitaciones. **La publicación permanece manual y expresamente aprobada.**
