# Programa VS-CY — Vertical slice productivo + beta dogfooding

**Diseño documental 2026-11-16. Ejecutor del código: FreeBuff. Autor de las campañas: ChatGPT. Estado: PLANIFICADO / NO EJECUTADO.** Publicado como documentación; no autoriza despliegue ni acceso a terceros.

## Objetivo de aceptación

Un owner de AgntiaPro autoriza activos **propios** en un tenant de dogfooding; LAIA/Pedro solicita una auditoría por contrato versionado; el kernel valida capacidades y aprobación; el middleware recibe una orden idempotente; un worker aislado ejecuta Gitleaks/OSV/Semgrep/Trivy seleccionados; se producen evidencias cifradas, findings, informe ejecutivo y técnico; el owner aprueba una propuesta (no se autoaplica); se verifica con retest; observabilidad, backups, kill switch y auditoría permiten operación repetible. Un segundo tenant sintético prueba aislamiento. **Beta interna productiva ≠ servicio autorizado a clientes**.

## Fuente de verdad, no duplicar campañas

Leer antes: [estado](../01-ESTADO-Y-ALCANCE.md), [matriz CP](../02-MATRIZ-CIERRE-PRODUCCION.md), [handoff](../04-HANDOFF-EJECUCION.md), [CY-R01–R12](../../auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md), [C01–C18](../../adversarial/implementation-v1/execution/ADVLAB-EXECUTION-2026-11-15.md), [B](../../adversarial/implementation-v1/execution/B-VAULT-BROKER-RELEASE-2026-11-15.md), [D](../../adversarial/implementation-v1/execution/D-OPERATIONS-MULTITENANT-2026-11-15.md), [onboarding](../../puesta-en-marcha-founder-agente/07-PLAN-DE-TRABAJO-Y-CHECKLIST.md). `docs/release/status.json` conserva NO-GO y se actualiza solo por mecanismo de verificación, nunca por maquillaje documental.

## Waves y dependencias

| Wave | Campañas | Dependencia | Salida |
|---|---|---|---|
| W0 | VS-00, VS-01 | main actualizado | Baseline y contrato de producto congelados |
| W1 | VS-02, VS-03, VS-04 | W0 + decisiones founder | Runtime y escáneres verificables, secretos y persistencia |
| W2 | VS-05, VS-06, VS-07 | W1 | Aislamiento, resiliencia y release gates |
| W3 | VS-08, VS-09 | W2 + permiso explícito para /agente | Integración y experiencia end-to-end |
| W4 | VS-10, VS-11 | W3 + autorización de activos propios | Dogfooding real, telemetría y reportes |
| W5 | VS-12, VS-13 | W4 + revisión independiente | Beta GO/NO-GO y preparación comercial futura |

**No son 14 módulos nuevos:** cada campaña debe comenzar inventariando el código existente y limitarse al delta necesario. Las 42 fases originales, CY-R, AD y C/B/D se mapean como evidencia, no como listas de trabajo acumulables.

## Convenciones de ejecución FreeBuff

- Rama por campaña: `feat/cyber-vs-XX-<slug>` desde HEAD de main. PR sin merge automático; no escribir en /agente ni desplegar sin aprobación del owner.
- Protocolo por fase: P0 auditoría y baseline; P1 contratos y diseño diferencial; P2 patchset mínimo; P3 tests positivos, negativos y fallo; P4 documentación, reporte, rollback y revisión. **En campañas bloqueadas por cuentas, entregar mocks/contratos y registrar BLOCKED, no inventar integración.**
- Entregables por campaña: `docs/operacion-actual/campanas-vertical-slice-beta/reportes/VS-XX-{REPORT,EVIDENCE,PATCHSET,ROLLBACK}.md` y PR. En REPORT registrar SHA base/final, paths reales, diffs, comandos, exits, fixtures, CI, estado, riesgos, decisiones del founder, costes y próxima acción.
- Los paths propuestos son **candidatos derivados de la documentación**: FreeBuff debe comprobarlos con `git ls-files` y localizar símbolos reales antes de modificar. No crear módulos duplicados porque un nombre no coincida.
- Fail-closed, deny-by-default, idempotencia, fencing, auditoría append-only, scope allowlist, no salida de datos sensibles a LLM, ningún escaneo externo sin ROE, secretos solo en gestor y pruebas de dos tenants.
- Codex/revisor independiente verifica cambios críticos de auth, tenancy, vault, sandbox y release; no marcar PASS por autoevaluación de FreeBuff.

## Artefactos

[Campañas VS-00 a VS-06](01-CAMPANAS-BASE-Y-SEGURIDAD.md) · [Campañas VS-07 a VS-13](02-CAMPANAS-INTEGRACION-Y-DOGFOODING.md) · [Contratos, gates y handoff](03-CONTRATOS-GATES-HANDOFF.md).

## Condición de beta interna

Se exige un recorrido completo con un activo propio y autorización escrita; 2 tenants sin fugas; scanner real y fixture controlado; evidence chain cifrada y recuperable; propuesta aprobada y retest; fallos y reintentos visibles; release audit verificable; rollback y alertas; coste por run medido. Si un P0 falla: **NO-GO**. La beta puede ser privada con excepciones no críticas expresamente aprobadas y limitadas, nunca con bypass de aislamiento o autorización.
