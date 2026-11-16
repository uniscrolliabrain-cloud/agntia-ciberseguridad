# Campañas VS-07 a VS-13 — Integración, dogfooding y operación

**Ejecutor:** FreeBuff. Las rutas son candidatas y deben validarse con el árbol actual. Ningún despliegue, merge de código o acceso a /agente sin permiso específico.

## VS-07 — Observabilidad, alertas y límites económicos (CP-09)

**Objetivo:** visibilidad end-to-end por tenant, run, tool, evidencia, aprobación y coste.
**Inspeccionar:** `agntia_ciberseguridad/telemetry/**`, `agents/**`, `adversarial_lab/src/agntia_adversarial/operations/**`, `.github/workflows/**`, `docs/operations/**`.
**P0:** inventario OTel, eventos, logs, dashboards y receptores. **P1:** definir SLIs: tasa de runs, latencia p50/p95, scanner BLOCKED, fallos, cola, RPO/RTO, coste por run, uso por tenant, revocaciones. **P2:** instrumentar correlationId sin PII, dashboards y alertas a receptor autorizado, presupuesto y rate limits. **P3:** simulacro scanner caído, backup fallido, tenant leak sintético, presupuesto excedido, alertas recibidas y acuse. **P4:** runbook y umbrales con propietario.
**Archivos:** telemetry/operations y tests; dashboards/config redactada. **Gate:** alarma real llega y puede relacionarse con run y respuesta. **Rollback:** desactivar exportadores manteniendo auditoría local. **Dependencia:** VS-05, receptor founder.

## VS-08 — Adaptador versionado hacia /agente y Pedro (CP-10)

**Objetivo:** consumir ciberseguridad desde el kernel AgntiaPro sin acoplar imports ni dar privilegios al LLM.
**Inspeccionar:** `typescript/**`, `agntia_ciberseguridad/agents/**`, `docs/09-contrato-con-agente.md`, `docs/operacion-actual/campanas-vertical-slice-beta/03-CONTRATOS-GATES-HANDOFF.md`; del repo `/agente` solo lectura autorizada para diseñar el patchset.
**P0:** inventariar SDK, endpoints, esquemas y las capacidades reales de kernel/approval/event bus; no asumir nombres de rutas. **P1:** contrato `cyber.audit.request/status/findings/report/retest`, scopes y ownership, `schemaVersion`, idempotency, correlationId/causationId, mapeo de eventos. **P2:** adaptar SDK server-only y proponer patchset en documento de integración; **NO aplicar en /agente** sin permiso. **P3:** contract tests contra API, 401/403/409, tenant cruzado, retries, revocación, approval pendiente. **P4:** guía de instalación y rollback.
**Archivos:** `typescript/**`, contratos y tests del middleware; `docs/operacion-actual/campanas-vertical-slice-beta/reportes/VS-08-AGENTE-PATCHSET.md`. **Gate:** SDK validado; E2E en /agente requiere aprobación y ejecución separada. **Dependencia:** VS-01/03/05/06.

## VS-09 — Flujo conversacional y aprobación humana (CP-10/11)

**Objetivo:** LAIA/Pedro presentan acciones reales sin inventar progreso; el owner autoriza scope, auditoría y cualquier efecto.
**P0:** leer UI, API y approval flow actuales de /agente en modo solo lectura; si inaccesible, BLOCKED con contrato propuesto. **P1:** diseñar estados visibles `solicitado→validando→pendiente aprobación→en cola→escaneando→normalizando→informe→retest` derivados de eventos reales; no simular acciones completadas. **P2:** preparar adaptador y patchset segregado; cambios en /agente únicamente tras autorización específica. **P3:** aprobar/rechazar/revocar, sesión caída, reintentos, ausencia de scopes, doble clic, dos tenants. **P4:** capturas de flujos y reportes de accesibilidad.
**Archivos:** propuesta `reportes/VS-09-UI-PATCHSET.md`; implementación real en repo dueño, nunca copiar UI al middleware. **Gate:** ninguna acción activa antes de approval; estados coherentes con backend. **Dependencia:** VS-08.

## VS-10 — Misión real de auditoría sobre activos propios (CP-11)

**Objetivo:** beta dogfooding, un run completo de AppSec con permiso verificable.
**P0:** founder aporta inventario allowlist de repos/dominios **propios** y ROE firmado (objetivos, horarios, técnicas, límites, exclusiones). **P1:** plan de misión de mínimo riesgo: snapshot autorizado, Gitleaks, OSV, Semgrep y Trivy aplicables; sin DAST activo en terceros. **P2:** integrar intake→job→OCI→findings→evidence→report→approval→retest; no auto-remediación. **P3:** ejecutar primero fixtures, después activos propios autorizados; registrar tiempos, cobertura, false positives, costes, no-coverage y errores. **P4:** reporte ejecutivo y técnico, hallazgos confirmados, remediación propuesta, retest y cadena de custodia.
**Archivos:** misión versionada bajo owner real del laboratorio, tests integration/e2e, `reportes/VS-10-*`; no almacenar resultados sensibles en Git. **Gate:** informe reproducible, cero acceso fuera de scope, retest ligado al hallazgo original. **Dependencias:** VS-02…09, autorización founder.

## VS-11 — Dos tenants, resiliencia y beta repetible (CP-07/08/09/11)

**Objetivo:** comprobar dogfooding sin fugas y continuidad de operación.
**P0:** crear dos tenants **sintéticos** con dos owners distintos y datos canarios; no asumir que los tenants reales de /agente ya están conectados. **P1:** plan de aislamiento API, SDK, vault, backup, informes, métricas, eventos, scheduler y UI. **P2:** corregir únicamente filtraciones reproducibles. **P3:** run concurrente, IDOR, copia de evidencia entre tenants, revocación a mitad de run, caída worker, pérdida host, restore externo, alerta y rollback; reejecutar slice. **P4:** informe de fallos, RPO/RTO, SLA preliminar y coste.
**Archivos:** tests/security/integration y `reportes/VS-11-*`. **Gate:** ninguna fuga de tenant, recuperación y segunda ejecución repetible; revisión independiente. **Dependencias:** VS-10.

## VS-12 — Beta privada: release, operación y aceptación (CP-01…13)

**Objetivo:** habilitar solo beta interna en entorno privado, con permisos del founder.
**P0:** revisar CP-01…11, riesgos residuales y licencias; obtener autorizaciones de infraestructura y de deploy. **P1:** runbook de arranque, operación, incidentes, rotación, backup, on-call, límites de gasto, rollback. **P2:** preparar release reproducible, imagen por digest, configuración privada, smoke, probes, alertas, DNS/TLS privado; **no desplegar sin aprobación**. **P3:** ensayo canary, kill switch, restore, failover y aceptación del owner; gate fail-closed. **P4:** acta `GO_BETA_INTERNAL` o `NO_GO` con evidencias y excepciones permitidas.
**Archivos:** `docs/operations/**`, release manifests/workflows y `reportes/VS-12-*`. **Gate:** revisión independiente + aceptación founder; `customer_production` sigue deshabilitado. **Dependencias:** VS-11.

## VS-13 — Preparación del primer cliente, sin activarlo (CP-12/13)

**Objetivo:** que la beta pueda convertirse después en servicio contractual sin reingeniería mayor.
**P0:** inventario de privacidad, datos, licencias de reglas/feeds, DPA, ROE, disclosure, SLA y soporte. **P1:** separar entornos, credenciales, tenants, política de retención, límites de servicio, precio/coste y roles; no prometer SOC/EDR/DAST si no están validados. **P2:** plantillas de onboarding, consentimiento, revocación, informe, offboarding, borrado, incidentes y facturación; sin datos reales. **P3:** simulacro de alta/baja de cliente ficticio, backup, export y revocación; revisión legal/seguridad. **P4:** paquete de GO/NO-GO comercial y backlog P2.
**Archivos:** `docs/operacion-actual/campanas-vertical-slice-beta/reportes/VS-13-*` y `docs/operations/**`. **Gate:** revisión independiente y aprobación contractual explícita; ningún cliente real conectado automáticamente. **Dependencias:** VS-12.
