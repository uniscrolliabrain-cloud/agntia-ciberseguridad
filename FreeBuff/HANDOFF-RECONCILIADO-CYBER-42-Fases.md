# FreeBuff — handoff reconciliado de la fábrica Ciberseguridad

**2026-11-14 · PLAN / NO EJECUTADO**. Este documento no reemplaza las 42 fases originales ni las 12 campañas CY-R01..R12 existentes. Ramas auditadas: recovery y nueve feature, todas ahead=0 respecto de main; no hay commits pendientes. PR #10 y #11 ya integradas. No crear vertical nueva, no resetear código.

## Autoridad

1. Código HEAD, `docs/release/status.json`, `docs/release/PILOT-ACCEPTANCE.md`, `docs/release/FOUNDER-REPORT.md`.
2. Manifiestos, 42 campañas y scaffolds originales, checkpoints 01..09 y sus reportes.
3. `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md` y `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md` como programa de **delta adicional**, no reemplazo.
4. `docs/factory/HANDOFF-FREEBUFF.md`: la auditoría conceptual Astra/reconciliación es gate previo; si no consta aprobación, detener antes de escribir código y pedir decisión founder.

## Baseline y código existente

Demo FastAPI Python, autenticación con principal/capabilities, tenants, snapshots, jobs, evidencia cifrada, cuatro escáneres offline Gitleaks/Semgrep/OSV/Trivy, gateway MCP/agentes, reportes, governance, ledger, observabilidad, SDK TS/Hono, UI browser y release. Código a inspeccionar: `agntia_ciberseguridad/app.py`, `auth.py`, `config.py`, `agents/routes.py`, `features.py`, `typescript/package.json`, `.github/workflows/runtime.yml`, `scanner-contracts.yml`, `browser.yml`, `release.yml`. No asumir rutas adicionales sin verificar. CI de rama de implementación reejecutada en Python 3.11/3.12, scanner Docker y browser con SUCCESS, no es pentest ni validación de main actualizado.

**Estado oficial:** 2 fases PASS, 40 PARTIAL; 80 tareas PASS, 214 PARTIAL; `owner_acceptance=PENDING`, `independent_review=PENDING`, `production_enabled=false`. `/health/ready` declara `foundation_only`, no escáneres productivos. La auditoría independiente, backups/restores, DPA, autenticación del padre, licencias y operación siguen siendo gates.

## Matriz de reconciliación de las 42 fases

Cada fase original mantiene ID, siete tareas y estado. No cambiar status sin prueba reproducible y revisión. Lista actual:

- **D1P1 — Baseline, alcance y contrato de servicio**: PASS; 7/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D1P2 — Paquete, configuración y contratos tipados**: PASS; 7/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D1P3 — Identidad, tenancy y capacidades**: PARTIAL; 5/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D1P4 — Persistencia, migraciones y auditoría**: PARTIAL; 5/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D1P5 — Inventario de activos y autorización de trabajo**: PARTIAL; 5/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D1P6 — Threat model y revisión de fronteras**: PARTIAL; 5/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D2P1 — Adquisición de snapshots sin ejecutar código**: PARTIAL; 5/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D2P2 — Runner y sandbox de herramientas**: PARTIAL; 7/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D2P3 — Adaptador Gitleaks y protección de secretos**: PARTIAL; 7/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D2P4 — OSV, inventario de dependencias y SBOM**: PARTIAL; 5/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D2P5 — Semgrep CE y reglas propias revisadas**: PARTIAL; 6/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D2P6 — Trivy para imágenes e IaC del piloto**: PARTIAL; 2/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D3P1 — Jobs, idempotencia y estados fiables**: PARTIAL; 6/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D3P2 — Worker con leases, fencing y retries**: PARTIAL; 4/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D3P3 — Normalización, deduplicación y contexto**: PARTIAL; 4/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D3P4 — Custodia, redacción y cadena de evidencia**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D3P5 — Priorización, excepciones y revisión humana**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D3P6 — Reportes y primera vertical AppSec**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D4P1 — OpenTelemetry y correlación extremo a extremo**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D4P2 — Métricas, SLIs y presupuesto de error**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D4P3 — Logs estructurados y privacidad de telemetría**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D4P4 — Dashboards y navegación de investigación**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D4P5 — Ingestión de eventos y conectores pasivos**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D4P6 — Carga, retención y resiliencia de observabilidad**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D5P1 — Registro de agentes, tools y capacidades delegadas**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D5P2 — Policy engine y control determinista de acciones**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D5P3 — Flujos de datos, egress y cuarentena**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D5P4 — MCP, skills y cambios de supply chain**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D5P5 — Evaluaciones adversariales con utilidad**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D5P6 — Revocación, kill switch y aprobación de efectos**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D6P1 — Aplicabilidad legal y controles de cumplimiento**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D6P2 — Privacidad, retención y brechas de datos**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D6P3 — Antifraude y verificación por contexto**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D6P4 — Incidentes y contención propuesta**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D6P5 — Remediación revisable y retest**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D6P6 — Reservas económicas y servicios comerciales**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D7P1 — SDK TypeScript/Hono y contrato hacia /agente**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D7P2 — Interfaz operativa y experiencia humana**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D7P3 — E2E de dos tenants y recorridos de referencia**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D7P4 — Hardening, rendimiento y recuperación**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D7P5 — Empaquetado, Windows/Linux y supply chain de release**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.
- **D7P6 — Aceptación, reporte al founder y próximos90días**: PARTIAL; 0/7 tareas PASS. Releer manifiesto original, código, tests, reporte y dependencia antes de proponer patchset.

## Prompt de ejecución obligatoria

> Eres Freebuff Cloud, ejecutor de la fábrica Ciberseguridad ya existente. NO reconstruyas un MVP, NO sustituyas las 42 fases ni declares todo pendiente. Lee todos los manifiestos, código, docs originales, 9 checkpoints, reportes y programa CY-R01..R12. Fija SHA y ejecuta baseline. Reconcílialo con la matriz de 42 fases y con el código. Pide autorización founder si Astra conceptual sigue pendiente. Después aplica CY-R01..R12 como **delta**: por cada campaña, escribe primero mapa de archivos exactos y pseudocódigo/código orientativo adaptado al repo, tests positivos/negativos, fixtures de dos tenants, criterios y rollback; implementa en rama aislada, entrega reporte y solicita Codex review. No avanzar con FAIL/BLOCKED. Mantén arquitectura FastAPI+TS/Hono y scanners offline; no instalar Doppler ni modificar padre/gestoría ni escanear clientes.

## Secuencia, reportes y gates

Para cada CY-R01..R12 del programa existente: 1) SHA y scripts; 2) leer fase y dependencias originales; 3) matriz CODE_PRESENT/PARTIAL/ABSENT; 4) patchset por rutas reales; 5) tests adversariales, idempotencia, cross-tenant y fallos; 6) CI/rollback y evidencia; 7) reporte `docs/auditoria-runtime/reportes/CY-Rxx-REPORT.md` con PR, SHA, comandos, exit codes, passed/failed/skipped, seguridad y riesgos; 8) Codex/arquitecto/founder. Preservar las 42 fases y sus IDs en los reportes; no inventar PASS.

**Doppler-ready** (documentar, no conectar): `FreeBuff/DOPPLER-READY.md` con secret inventory, nombres, owners, env dev/stg/prod, rotación, bootstrap fail-closed, sin valores. **Integración padre** (proponer, no aplicar): `FreeBuff/INTEGRATION-AGENTE-PROPOSAL.md` con JWT, twins, capabilities, SDK, Hono, MCP, outbox, schemas, smoke y rollback. **Cierre:** `FreeBuff/FOUNDER-FINAL-REPORT.md` con 42 fases × tareas, 12 reportes, CI, restores, licencia, seguridad independiente, deuda y gate founder. Sin autorización de producción.
