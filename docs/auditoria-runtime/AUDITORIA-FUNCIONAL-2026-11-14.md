# Auditoría funcional preliminar y ejecución CI — 2026-11-14

**Repositorio:** uniscrolliabrain-cloud/agntia-ciberseguridad. **Main tras merges:** 998fd1bad9ef04abf8cb2d95fb71533485a53d52. **Tipo:** revisión estática selectiva del código y documentación + rerun de GitHub Actions en el SHA 85c8b879e28b746bb367ff249c7e3ba78eeb23e3 (código de la rama de implementación). **NO** equivale a una auditoría de seguridad independiente completa, pentest ni ejecución local del checkout; el runner local no pudo resolver github.com.

## Evidencia CI de esta revisión
- Foundation runtime run 43649725633, re-run: Python 3.11 y 3.12 SUCCESS. Paso `npm test`, `npm audit --omit=dev --audit-level=high --json`, `unittest discover`, esquemas, distribución, evaluación gateway y stop SUCCESS en job Python 3.12.
- Scoped observability browser run 43649725660, re-run: SUCCESS; Playwright Chromium y scripts browser_observability.py/browser_pilot.py SUCCESS.
- Offline scanner contracts run 43649725611, re-run: **IN_PROGRESS en la última consulta**, build/probe images SUCCESS; prueba Docker real pendiente de resultado definitivo.
- Seis workflows de la rama de implementación tenían SUCCESS histórico (runtime, scanner, browser, observabilidad, docs, release). No inferir que el merge SHA fue ensayado de nuevo; las dos fusiones conservaron código, pero el estado documental fue actualizado y hay un nuevo commit de planificación.
- La evidencia histórica del checkpoint 09 declara 190 casos Python distintos (182 núcleo y 8 Docker), sin confundir con conteo de la reejecución actual.

## Código y capacidades comprobados por inspección
- `agntia_ciberseguridad/app.py`: FastAPI, middleware de tamaño/tiempo de request, correlación, autenticación, assets/grants/snapshots/jobs/findings, rutas de evidencias, observabilidad, agentes, gobernanza, billing y workspace. Readiness explícitamente `scope=foundation_only`, `security_scanners_ready=false`: no equivale a preparación productiva.
- `agntia_ciberseguridad/auth.py`: principales explícitos, token hash/compare_digest, comprobación de revocación, roles/capacidades y guard de agente. Requiere revisión adversarial de todas las rutas y transiciones, no solo de auth.py.
- `agntia_ciberseguridad/agents/routes.py`: herramientas y flujos nominados, MCP y aprobaciones, sin proxy HTTP/shell genérico expuesto por este módulo.
- `agntia_ciberseguridad/features.py`: evidencias, originales con motivo, retención/hold, revisiones, reportes y operaciones. Los originales requieren auditoría de custodia y rotación/restore.
- `typescript/package.json`: SDK privado `@agntia/ciberseguridad` con Hono y tests Node. `docs/integration/PATCHSET-AGENTE.md` aclara que NO está cableado al repo padre.
- `docs/release/status.json`: 2 fases PASS, 40 PARTIAL; 80 tareas PASS, 214 PARTIAL. Estado SYNTHETIC_DEMO_NOT_PRODUCTION.
- `docs/release/PILOT-ACCEPTANCE.md`: licencia, divulgación privada, DPA, backup/restore, revisión independiente, operadores, BFF y conexión con AgntiaPro pendientes.

## Diagnóstico diferencial priorizado
P0: reconciliar documentación de ramas antiguas y baseline actual; ejecutar CI y registrar skips; revisión independiente de auth/cross-tenant, snapshots/sandbox, agent delegation/egress, cifrado/restore, idempotencia y workers. No datos reales.
P1: cuantificar cobertura real por herramienta/lenguaje/asset; medir falsos negativos; endurecer incidentes/retest, observabilidad/alertas, outbox/consumidor, contratos SDK y pruebas adversariales.
P2: licencias OSS y reglas/feeds, DPA, privacidad/retención, costes reales y capacidad operativa; piloto aislado únicamente tras gates y autorización.
No hay DAST/cloud posture/EDR/SOC real integrado por el simple hecho de tener cuatro scanners offline; no hay integración verificada en `/agente`.

## Hallazgos de documentación
- README, RUNBOOK y FOUNDER-REPORT todavía dicen que la implementación vive en ramas/PRs sin merge; tras PR #10/#11 ya es obsoleto.
- docs/factory/06-READINESS-AUDIT.md parte del baseline documental previo y requiere reconciliación con la demo implementada; no reemplazar `docs/release/status.json` por afirmaciones optimistas.
- La declaración de 42 fases recorridas no equivale a 42 gates aprobados.

## Programa de ejecución
Ver [PROGRAMA-DIFERENCIAL-12-CAMPANAS.md](PROGRAMA-DIFERENCIAL-12-CAMPANAS.md). Freebuff crea reporte por campaña; Codex valida; no se fusionan fixes sin CI y no se despliega ni toca `/agente` sin autorización.
