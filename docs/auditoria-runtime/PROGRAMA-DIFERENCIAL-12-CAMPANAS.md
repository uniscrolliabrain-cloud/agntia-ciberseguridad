> **ACTUALIZACIÓN 2026-11-15 — LEE ESTO ANTES DEL TEXTO**
> Base medida: `main@dd18f2a` + AD-01 `c57251c` · 196 tests Python OK (8 skips) · SDK 6/1 · 84 rutas `/v1` · esquema 8 · demo sintética, `production_enabled=false` · 2 PASS / 40 PARTIAL · sin PR ni revisión independiente.
> **Vigente aquí:** CY-R02…CY-R12 siguen sin ejecutar; su protocolo y gates siguen vigentes.
> **Corregido/obsoleto:** CY-R01 (congelar baseline) queda cubierto en parte por AD-01: SHA, tests, rutas, migraciones y gates ya están inventariados. No repetir ese trabajo; reconciliar en lugar de duplicar.
> Mapa de ramas, contradicciones y pendientes: [ESTADO-VIGENTE.md](../ESTADO-VIGENTE.md)

---

# Programa de auditoría diferencial y recuperación funcional — CY-R01 a CY-R12

**Fecha:** 2026-11-14. **Baseline:** main tras PR #10 (merge 33c0f83418687cc48412dcd1ae7d4139cb7e5c48) y PR #11 (merge 998fd1bad9ef04abf8cb2d95fb71533485a53d52). **Estado:** PLANIFICADO, NO EJECUTADO por Freebuff. No sustituye las 42 fases históricas ni declara sus gates completos.

## Diagnóstico fuente de verdad

- La demo sintética contiene API FastAPI, principales y tenants, grants, snapshots, scanners offline Gitleaks/OSV/Semgrep/Trivy, jobs, evidencias, reportes, OTel, gateway MCP/agentes, gobernanza, ledger, SDK TS/Hono, UI piloto y bundle de release.
- docs/release/status.json declara 2 fases PASS, 40 PARTIAL; 80 tareas PASS y 214 PARTIAL. No elevar por haber fusionado ramas.
- docs/release/PILOT-ACCEPTANCE.md bloquea clientes reales: revisión independiente, licencia, canal privado, DPA, backup/restore, operador, autenticación/BFF y wiring de /agente.
- La documentación docs/factory/ fue creada contra un baseline documental anterior. Reconciliar con HEAD actual y actualizar README, runbook y referencias a PR apiladas.
- Evidencia histórica del último head de implementación: seis workflows SUCCESS; se solicitaron reruns de foundation, scanner Docker y browser el 2026-11-14. Los resultados de reejecución requieren comprobación posterior. No son pruebas locales en este entorno.

## Protocolo obligatorio de Freebuff + Codex

Para cada CY-Rxx, crear rama independiente desde main actualizado; registrar SHA y comprobar rutas reales antes de editar (las rutas sugeridas pueden cambiar). Freebuff implementa solo el delta confirmado; Codex ejecuta pruebas y revisa diffs, seguridad y no-regresiones. Mantener una sola superficie de escritura por rama, PR y revisión antes de fusionar. Crear `docs/auditoria-runtime/reportes/CY-Rxx-REPORT.md` con SHA base/final, inventario, archivos tocados, comandos y exit codes, conteos de tests/skips, fallos reproducibles, evidencia, decisiones, rollback y estado PASS/FAIL/BLOCKED/NOT_VERIFIED. Todo test no ejecutado es NOT_VERIFIED; nunca PASS por mock o por ausencia de hallazgos. En casos con efectos externos, parar y solicitar aprobación. No tocar el repositorio padre, producción, clientes, redes ajenas ni credenciales reales.

## Orden de ejecución

CY-R01 → CY-R02 → CY-R03 → CY-R04 → CY-R05 → CY-R06 → CY-R07 → CY-R08 → CY-R09 → CY-R10 → CY-R11 → CY-R12. Permitir paralelismo solo con ownership disjunto y baseline reconciliado. Prioridad bloqueante: R02, R03, R05, R06, R07. Para cada campaña, gates G1 seguridad/aislamiento y G2 resiliencia/evidencia. Si un gate falla, no avanzar a pilotos.

## CY-R01 — Congelar baseline, CI y verdad documental

**Superficies a inspeccionar:** `docs/release/status.json`, `docs/implementation/checkpoints/09-phases-41-42/REPORT.md`, `docs/factory/06-READINESS-AUDIT.md`, `README.md`.

**Pruebas y contratos:** `.github/workflows/runtime.yml`, `.github/workflows/scanner-contracts.yml`, `.github/workflows/browser.yml`, `.github/workflows/release.yml`.

**Objetivo diferencial:** Reconciliar el estado histórico de ramas/PR y 42 fases con el HEAD fusionado; inventariar skips, tests, SHA, cobertura real y workflows.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Ejecutar en CI Python 3.11/3.12, npm test, scanner Docker, browser, release Linux/Windows; archivar IDs de jobs y distinguir re-run de nuevo commit.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** No marcar PASS por ejecución anterior ni convertir 40 PARTIAL en PASS.

**Gate G1 (funcional/seguridad):** Matriz de trazabilidad commit→job→test→evidencia; ningún enlace roto; 0 afirmaciones de despliegue ficticio.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R02 — Autenticación y autorización adversarial

**Superficies a inspeccionar:** `agntia_ciberseguridad/auth.py`, `agntia_ciberseguridad/app.py`, `agntia_ciberseguridad/config.py`.

**Pruebas y contratos:** `tests/test_core.py`, `tests/`, `agntia_ciberseguridad/agents/routes.py`.

**Objetivo diferencial:** Inspeccionar dependencia principal() y todas las rutas montadas; probar tenant de path distinto del tenant del token, actor agent en rutas humanas, token revocado y principal deshabilitado.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Añadir tests HTTP para cada operación de escritura, token duplicado, encabezados ambiguos, expiración y cambio de roles concurrente.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** Fail-closed; nunca owner implícito; no secretos ni datos de otro tenant en errores.

**Gate G1 (funcional/seguridad):** Todas las rutas deniegan sin credencial/tenant; matrices de roles y casos adversariales con evidencia.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R03 — Límites de entrada, snapshots y sandbox

**Superficies a inspeccionar:** `agntia_ciberseguridad/app.py`, `agntia_ciberseguridad/config.py`, `agntia_ciberseguridad/adapters/`.

**Pruebas y contratos:** `tests/docker/`, `scripts/prepare_scanner_images.py`, `scripts/build_probe_image.py`.

**Objetivo diferencial:** Auditar RequestBoundary y streaming ASGI, symlinks, TOCTOU, path traversal, archivos especiales, snapshots grandes y fuentes no confiables.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Ensayar cuerpos incompletos, desconexión, gzip/archivos bomba, symlinks cambiantes, timeouts, Docker sin red y cancelación.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** Ningún escáner recibe rutas arbitrarias ni ejecuta código del repositorio auditado.

**Gate G1 (funcional/seguridad):** Reproducción determinista y límites de CPU/memoria/tiempo; negativos demuestran bloqueo.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R04 — Cobertura de escáneres y falsos negativos

**Superficies a inspeccionar:** `agntia_ciberseguridad/adapters/gitleaks.py`, `agntia_ciberseguridad/adapters/osv.py`, `agntia_ciberseguridad/adapters/semgrep.py`, `agntia_ciberseguridad/adapters/trivy.py`.

**Pruebas y contratos:** `tests/docker/test_real_scanners.py`, `tests/docker/test_extended_scanners.py`, `.github/workflows/scanner-contracts.yml`.

**Objetivo diferencial:** Catalogar tipos de activo y formatos realmente soportados, hashes de reglas/feeds/imágenes, versiones, excepciones y licencias.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Fixtures positivos/negativos por Gitleaks/OSV/Semgrep/Trivy; escáner ausente, salida corrupta, timeout, feed obsoleto y hallazgo duplicado.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** Scanner fallido != limpio; cobertura vacía != seguro; no afirmar DAST/EDR.

**Gate G1 (funcional/seguridad):** Matriz por scanner×lenguaje×formato con detección esperada y reportes de no-cobertura.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R05 — Persistencia, jobs, replay y recuperación

**Superficies a inspeccionar:** `agntia_ciberseguridad/app.py`, `agntia_ciberseguridad/features.py`, `agntia_ciberseguridad/jobs.py`, `agntia_ciberseguridad/storage.py`.

**Pruebas y contratos:** `tests/`, `docs/operations/ROLLBACK.md`, `docs/operations/RUNBOOK.md`.

**Objetivo diferencial:** Localizar módulos reales de JobStore/Database y mapear transacciones, leases, fencing, cancelación, idempotency keys y replays.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Inyectar crash antes/después de commit, doble submit concurrente, ACK perdido, lease expirado y rollback restaurable.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** No duplicar efectos ni borrar auditoría para corregir inconsistencia.

**Gate G1 (funcional/seguridad):** Estado recuperable tras fallo y reconciliación visible; test de 2 tenants en paralelo.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R06 — Custodia, cifrado, retención y restauración

**Superficies a inspeccionar:** `agntia_ciberseguridad/evidence/vault.py`, `agntia_ciberseguridad/features.py`, `agntia_ciberseguridad/config.py`.

**Pruebas y contratos:** `docs/release/PILOT-ACCEPTANCE.md`, `docs/operations/RUNBOOK.md`, `tests/`.

**Objetivo diferencial:** Revisar claves por tenant, AAD, lectura original, redacción, hold, purge, auditoría y exportación; inventariar qué datos quedan fuera de backups.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Ensayar rotación y revocación de claves, corrupción de ciphertext, restore en directorio nuevo, legal hold y borrado con evidencia.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** No publicar originales ni secretos; no prometer borrado irreversible sin soporte.

**Gate G1 (funcional/seguridad):** Restore de SQLite+originales+claves probado; RPO/RTO medidos, no supuestos.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R07 — Gateway de agentes, MCP y exfiltración

**Superficies a inspeccionar:** `agntia_ciberseguridad/agents/routes.py`, `agntia_ciberseguridad/agents/`, `agntia_ciberseguridad/auth.py`.

**Pruebas y contratos:** `scripts/evaluate_agent_gateway.py`, `scripts/measure_agent_stop.py`, `tests/`.

**Objetivo diferencial:** Mapear permisos tool/manifest, tokens de un uso, TTL, cambios de política, MCP origin/session y egress permitido.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Tests de prompt injection en resultados de scanners, tool spoofing, replay, doble consumo, revocación durante ejecución, payload excesivo y salida hacia destino no permitido.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** LLM propone; policy valida; nunca shell/HTTP libre ni owner por avatar.

**Gate G1 (funcional/seguridad):** Zero side effects sin aprobación; casos adversariales trazables con razón de denegación.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R08 — Outbox, SDK/Hono e integración contractual

**Superficies a inspeccionar:** `typescript/client.ts`, `typescript/hono.ts`, `typescript/agent-tools.ts`, `docs/integration/PATCHSET-AGENTE.md`.

**Pruebas y contratos:** `typescript/test/`, `agntia_ciberseguridad/`, `docs/09-contrato-con-agente.md`.

**Objetivo diferencial:** Contrastar rutas/contratos y SDK con el repo padre en auditoría de solo lectura; verificar tenant server-side, BFF, secretos, outbox y consumidor at-least-once.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Contract tests HTTP reales con dos tenants; ACK perdido, duplicación, cambio de schemaVersion y consumidor reiniciado.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** No modificar /agente sin aprobación separada; no exponer tokens al browser.

**Gate G1 (funcional/seguridad):** Patchset propuesto archivo-a-archivo y test de integración aislada; sin wiring productivo.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R09 — Observabilidad, alertas y privacidad

**Superficies a inspeccionar:** `agntia_ciberseguridad/observability_routes.py`, `agntia_ciberseguridad/telemetry/`, `agntia_ciberseguridad/features.py`.

**Pruebas y contratos:** `.github/workflows/observability.yml`, `.github/workflows/browser.yml`, `scripts/browser_observability.py`.

**Objetivo diferencial:** Inventariar trazas, logs, métricas, cardinalidad, correlación y filtros PII; distinguir salud API de salud de scanners.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Collector caído, cola saturada, pérdida de exportación, cardinalidad extrema, PII en error y latencia p95.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** No registrar secretos, contenidos originales ni prometer SLA sin operación.

**Gate G1 (funcional/seguridad):** Alertas accionables con thresholds y runbook; tests de fuga y recuperación.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R10 — Incidentes, remediaciones y antifraude

**Superficies a inspeccionar:** `agntia_ciberseguridad/governance/`, `agntia_ciberseguridad/agents/`, `docs/release/FOUNDER-REPORT.md`.

**Pruebas y contratos:** `tests/`, `docs/release/PILOT-ACCEPTANCE.md`.

**Objetivo diferencial:** Revisar máquina de estados, origen de señales, verificación fuera de banda, aprobación humana y retest del mismo activo/snapshot.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Caso falso positivo, duplicado, evidencia caducada, suplantación de aprobador, retest con snapshot diferente y proveedor inalcanzable.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** Sin contención real ni cambios de repos de terceros sin autorización específica.

**Gate G1 (funcional/seguridad):** Cierre exige evidencia posterior comparable, aprobación y trazabilidad; no auto-declarar FIXED.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R11 — Gobernanza, costes, licencias y cumplimiento

**Superficies a inspeccionar:** `agntia_ciberseguridad/governance/`, `agntia_ciberseguridad/billing/`, `config/plans.json`.

**Pruebas y contratos:** `docs/release/status.json`, `docs/release/PILOT-ACCEPTANCE.md`, `docs/05-cumplimiento-europeo.md`.

**Objetivo diferencial:** Separar controles implementados de obligaciones legales; validar licencias de binarios, reglas y feeds, retención por tenant, contratos y límites de coste.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Pruebas de reserva simultánea, coste fuera de ledger, factura proveedor distinta, agotamiento de presupuesto y reintento.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** Sin dictamen legal automático ni promesas de techo externo no controlado.

**Gate G1 (funcional/seguridad):** Matriz legal y comercial con propietario, fuente, aplicabilidad, evidencia y pendientes explícitos.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## CY-R12 — Aceptación de demo y release interno reproducible

**Superficies a inspeccionar:** `scripts/release_bundle.py`, `scripts/release_container.py`, `scripts/verify_lab.sh`, `scripts/verify_lab.ps1`.

**Pruebas y contratos:** `docs/release/PILOT-ACCEPTANCE.md`, `docs/release/COMPATIBILITY.md`, `.github/workflows/release.yml`.

**Objetivo diferencial:** Reproducir instalación fuera del checkout, wheelhouse y tarball, SBOM, provenance, firma y verificación por SO.

**Tareas:**
1. Fijar SHA de main, localizar implementación y verificar qué está ya probado; documentar cobertura y límites.
2. Reproducir el comportamiento vigente con fixtures y registrar resultados y skips antes de editar.
3. Construir matriz de amenaza, permisos, estados, entradas y salidas específica del dominio.
4. Implementar únicamente patchsets justificados, con ownership de archivos y sin romper contratos existentes.
5. Tamper de manifiesto, dependencia ausente, downgrade, restauración y test de dos tenants sintéticos extremo a extremo.
6. Documentar migración/rollback y actualizar contratos, esquemas y runbook si cambian.
7. Codex revisa pruebas, diff, seguridad y regresiones; Freebuff escribe reporte y solicita gate de founder cuando corresponda.

**Invariantes:** No desplegar ni usar clientes reales; bloquear si algún gate de seguridad esencial falla.

**Gate G1 (funcional/seguridad):** Informe founder con PASS/FAIL/BLOCKED/NOT_VERIFIED, SHA, jobs, artefactos y backlog de piloto.

**Gate G2 (recuperación/evidencia):** repetir casos negativos, fallos parciales y reintentos con resultados y SHA verificables; sin cobertura, estado NOT_VERIFIED.

## Cierre

No declarar despliegue ni servicio productivo. Antes de integrar con /agente se requiere autorización específica, test de contrato real y rollback. Cualquier hallazgo crítico de cross-tenant, exfiltración, bypass de permisos, custodia o duplicado detiene la secuencia. El resultado final es un informe de brechas medibles y un plan de piloto condicionado, no una certificación de seguridad.
