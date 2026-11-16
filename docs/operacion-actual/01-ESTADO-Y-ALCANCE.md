# 01 — Estado técnico vigente y alcance real

**Fecha de reconciliación documental:** 2026-11-16. **Fuente:** GitIngest aportado, consultas directas a `main` y reportes fechados de 2026-11-15. **Sin nueva ejecución de tests.**

## Decisión principal

El repositorio contiene **dos paquetes independientes**: `agntia_ciberseguridad/` (middleware Python/FastAPI) y `adversarial_lab/` (laboratorio de evaluación adversarial). El SDK de `typescript/` es cliente server-only; **no** hay decisión vigente de reescribir todo a TypeScript. El laboratorio no debe importarse dentro del middleware por conveniencia ni saltarse las fronteras de autorización de `/agente`.

**Producto buscado:** auditorías defensivas autorizadas de activos y sistemas agénticos, evidencia verificable, findings, priorización, propuesta de remediación, aprobación humana, retest y operación gobernada; el servicio se integra con AgntiaPro mediante contratos versionados. No confundir con pentesting irrestricto, SOC/EDR completo ni explotación de clientes sin ROE.

## Inventario de capacidades y límites

| Superficie | Existe / evidencia documentada | Límite para producción |
|---|---|---|
| API y contratos | 84 rutas `/v1/tenants/{tenant}/…`, paquete Python, SDK TS, 8 migraciones SQLite; [estado medido anterior](../ESTADO-VIGENTE.md) | Son métricas de una ejecución previa, no medición nueva del HEAD; revisar autenticación y cross-tenant |
| Identidad y agentes | Auth, capacidades, gateway, políticas y manifiestos en código | Revisión independiente y prueba E2E con identidad real y revocación |
| Scanners del middleware | Adaptadores y fixtures para Gitleaks, OSV, Semgrep y Trivy | Ejecutar binarios/feeds reales en entorno autorizado; resultados y licencias verificados |
| Jobs y evidencias | Worker, outbox, vault y reportes implementados | Restauración externa, gestión de claves, resiliencia y pruebas de efectos |
| Laboratorio adversarial | 18 campañas implementadas en paquete separado, misiones sintéticas, broker, ledger, vault, OCI adapter | Herramientas externas y runtime OCI reales no verificados; no confundir mocks con proveedores |
| Hardening B | Validación de paths, HKDF por tenant, AAD, escrituras atómicas, broker con revocación/preflight y release fail-closed | Clave maestra en host, cancelación de procesos en vuelo y atestación externa pendientes |
| Operaciones D | Leases SQLite, fencing, idempotencia, backup/restore verificado con hashes y comprobaciones de tenant | Concurrencia multiproceso, custodia de backup externo y segregación real pendientes |
| Integración central | Contratos y SDK diseñados | No consta flujo E2E productivo firmado con `uniscrolliabrain-cloud/agente` |

## Evidencia y contradicciones temporales

- El [informe C01–C18](../adversarial/implementation-v1/execution/ADVLAB-EXECUTION-2026-11-15.md) registra **103 tests** en su ejecución.
- El [informe D](../adversarial/implementation-v1/execution/D-OPERATIONS-MULTITENANT-2026-11-15.md) registra **115 tests** tras hardening; es una ejecución posterior, no una cifra acumulable.
- [ESTADO-VIGENTE.md](../ESTADO-VIGENTE.md) registra **196 tests Python**, 8 skipped, y SDK **6 pass/1 skip** para el middleware sobre un SHA anterior. No se suman con los 115 del laboratorio.
- El informe adversarial antiguo afirma «rama no fusionada»; commits posteriores de GitHub incluyen `99255673b0ccfd47813eb8be74a2a19939e9b2a3` (integración adversarial B/D). El texto antiguo queda como registro histórico, no situación actual.
- [release/status.json](../release/status.json) declara `SYNTHETIC_DEMO_NOT_PRODUCTION`, `production_enabled=false`, `owner_acceptance=PENDING`, `independent_review=PENDING`; 2/42 fases PASS y 80/294 tareas PASS del programa original. **No cambiar esos estados solo por reorganizar documentación.**
- El [informe B](../adversarial/implementation-v1/execution/B-VAULT-BROKER-RELEASE-2026-11-15.md) registra `releasecheck.py --production` con exit 1 **esperado**, por audit de dependencias BLOCKED y firma sin atestación externa. Un gate de integridad con exit 0 no significa release elegible.

## Tres hitos, tres puertas distintas

1. **Laboratorio interno sintético operativo:** herramientas reales fijadas por versión, OCI aislado, secretos fuera del repo, backup/restore y observabilidad; sin sistemas de cliente.
2. **Piloto con activos propios:** autorización de alcance, escaneo autorizado, hallazgos/evidencias, informe y retest; integración supervisada con `/agente`.
3. **Primer cliente:** revisión independiente, custodia y restauración, privacidad y DPA, ROE firmado, segregación, soporte y aceptación del founder.

**Estado de publicación:** NO-GO cliente/producción. **Siguiente acción:** ejecutar la [matriz de cierre](02-MATRIZ-CIERRE-PRODUCCION.md) con evidencia por gate, sin reconstruir lo ya implementado.
