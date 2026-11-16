# Campañas VS-00 a VS-06 — Baseline, contratos y seguridad

**Cada campaña usa P0→P4 del índice. No implementar código si el delta no está demostrado.** Referencias CP: [matriz](../02-MATRIZ-CIERRE-PRODUCCION.md).

## VS-00 — Auditoría diferencial final y trazabilidad (CP-01)

**Objetivo:** reconciliar código actual, ramas, 42 fases, CY-R, AD y C/B/D y obtener backlog de *deltas*, no de features duplicadas.
**Inspeccionar:** `README.md`, `docs/release/status.json`, `docs/ESTADO-VIGENTE.md`, `docs/auditoria-runtime/**`, `docs/adversarial/**`, `docs/operacion-actual/**`, `agntia_ciberseguridad/**`, `adversarial_lab/**`, `typescript/**`, `.github/workflows/**`.
**P0:** SHA y árbol, `git branch -a`, diffs relevantes, CI y reportes por SHA; mapa de importaciones/ownership y rutas API. **P1:** matriz capacidad→símbolo→test→informe→CP→estado. **P2:** corregir solo referencias obsoletas y duplicados documentales, nunca reescribir historial. **P3:** validar links, rutas, ausencia de secretos y consistencia de status. **P4:** reportar decisiones de arquitectura, gaps y rutas verificadas.
**Archivos:** actualizar índice y matrices; crear `reportes/VS-00-*`. **Gate:** cada capacidad y cada bloqueo tiene evidencia y responsable; ningún «no implementado» basado solo en plan antiguo. **Rollback:** revertir solo cambios documentales. **Dependencia:** ninguna.

## VS-01 — Contrato del slice y amenaza (CP-01/10/11)

**Objetivo:** congelar flujo `authorize→request→approve→queue→scan→findings→report→retest`, roles, ownership y versión.
**Inspeccionar:** `agntia_ciberseguridad/auth.py`, `app.py`, `agents/`, `jobs.py`, `storage.py`, `typescript/`, `docs/09-contrato-con-agente.md`; comprobar paths reales.
**P0:** listar endpoints, principales, grants, errores y payloads actuales. **P1:** diseñar esquemas `AuditScopeV1`, `AuditRunRequestV1`, `AuditRunStatusV1`, `FindingV1`, `EvidenceRefV1`, `ApprovalRefV1`, `RetestRequestV1`, `AuditEventV1` con tenantId, actorId, assetId, correlationId, idempotencyKey, schemaVersion y hashes; definir compatibilidad backward. **P2:** solo añadir contratos faltantes y validadores en sus owners. **P3:** contract tests Python↔TS, rechazos por scope expirado y tenant cruzado. **P4:** ADR de fronteras kernel/middleware/lab, semántica de estados y errores.
**Archivos candidatos:** `agntia_ciberseguridad/contracts.py` o contratos reales, `typescript/src/**`, `docs/09-contrato-con-agente.md`, tests contract. **Gate:** contrato versionado y revisión de seguridad; no ejecutar acciones con parámetros solo propuestos por LLM. **Rollback:** versión previa conservada. **Dependencia:** VS-00.

## VS-02 — Runner OCI, herramientas y feeds (CP-02/03)

**Objetivo:** pasar de adaptadores/fixtures a ejecución real controlada en entorno propio, manteniendo el laboratorio independiente.
**Inspeccionar:** `adversarial_lab/src/agntia_adversarial/execution/{oci,broker}.py`, `tools/`, `providers/`, `agntia_ciberseguridad/adapters/`, `tests/docker/`, `scripts/prepare_scanner_images.py`, `.github/workflows/scanner-contracts.yml`.
**P0:** listar herramientas realmente instaladas, OCI disponible, versión/digest, feeds, licencia, política de red y binarios BLOCKED. **P1:** seleccionar mínimo Gitleaks/OSV/Semgrep/Trivy para el slice; Syft/pip-audit según release; ZAP/Schemathesis/PyRIT/garak opcionales si no hay caso autorizado. **P2:** wiring por adapters existentes, imágenes por digest, `network=none` en ejecución, mounts RO, non-root, `cap-drop=ALL`, CPU/RAM/pids/timeouts/output cap y allowlist de comandos. **P3:** positivos/negativos, scanner ausente, feed viejo, timeout, salida corrupta, fuga de red, symlink y cancelación; registrar coverage explícita. **P4:** SBOM, licencia, receta reproducible y benchmark coste/duración.
**Archivos candidatos:** OCI, adapters, `tests/docker/**`, workflows, manifiestos de imágenes. **Gate:** al menos una auditoría real del activo sintético con receipts, ningún resultado «limpio» si el scanner falla. **Rollback:** deshabilitar runners, preservar evidencias. **Dependencias:** VS-01, host OCI elegido por founder.

## VS-03 — Gestor de secretos, identidad y autorización (CP-04/07)

**Objetivo:** credenciales de entorno sin filtración y acceso tenant/actor por capability real.
**Inspeccionar:** `agntia_ciberseguridad/{auth,config,app}.py`, `agents/routes.py`, `adversarial_lab/src/agntia_adversarial/{config,policy}/`, `typescript/**`, CI.
**P0:** identificar cada secreto referenciado y cada ruta mutadora; no leer valores. **P1:** matriz `SECRET_REF→env→consumer→scope→TTL→rotation` y matriz `route→principal→tenant→capability→approval`. **P2:** conectar referencias a Doppler/alternativa aprobada, rotación/revocación, desactivar fallback inseguro; token por entorno y tenant, no credencial global para agentes. **P3:** token ausente, duplicado, expirado, revocado, tenant distinto, actor agent en endpoint humano, replay y fuga en logs. **P4:** runbook de rotación y acceso de emergencia.
**Archivos:** auth/config/agents y tests; template `.env.example` sin valores, nunca `.env` real. **Gate:** cero secreto en repo/log; denegación cruzada demostrada; revisión independiente. **Rollback:** revocar credenciales nuevas y restaurar configuración segura. **Dependencia:** VS-01, founder habilita gestor.

## VS-04 — Evidencias, claves, backup y restore (CP-06)

**Objetivo:** custodia real recuperable ante pérdida de host, sin mezclar tenants.
**Inspeccionar:** `agntia_ciberseguridad/evidence/**`, `storage.py`, `adversarial_lab/src/agntia_adversarial/evidence/{vault,keys,paths}.py`, `store/backup.py`, `docs/operations/**`.
**P0:** comparar vault middleware/lab, cifrado, AAD, clave maestra host, retención y backup; inventariar datos excluidos. **P1:** diseñar key custody/KMS o envelope, versión de claves, aislamiento, restore, RPO/RTO medibles, borrado y legal hold. **P2:** adaptador de almacenamiento externo versionado y cifrado, manifest hashes, key references, restore a host limpio sin copiar claves en reportes. **P3:** blob manipulado, paths traversal/symlinks, ciphertext tenant B, clave rotada, backup corrupto, pérdida de host, retención/hold; medir RPO/RTO. **P4:** procedimiento de recuperación, costes y ownership.
**Archivos:** vault/keys/backup existentes, adapters storage, tests security/integration, runbook. **Gate:** restore completo a host nuevo, sin fuga cross-tenant; revisión independiente. **Rollback:** restaurar versión de clave/backup sin perder trazabilidad. **Dependencia:** VS-03, founder elige storage/KMS.

## VS-05 — Jobs, leases, cancelación, idempotencia (CP-08)

**Objetivo:** una orden de auditoría no duplica efectos, sobrevive fallos y se detiene al revocar.
**Inspeccionar:** `agntia_ciberseguridad/{jobs,storage}.py`, workers/outbox reales, `adversarial_lab/src/agntia_adversarial/planning/leases.py`, `execution/broker.py`, `store/**`.
**P0:** mapa de transacciones, lease/fencing, ACK, retries, DLQ, kill switch y límites de stdout. **P1:** estados tipados y transiciones, cancelación en vuelo, idempotencia tenant-scoped, límites por tenant y presupuesto. **P2:** patch mínimo para SIGTERM/kill del proceso OCI, reconciliación de job huérfano, dedupe de recibos y backoff; no añadir Kafka por defecto. **P3:** 2 procesos concurrentes, lease caducado, crash antes/después commit, ACK perdido, doble submit, revocación durante scan, kill switch y timeout. **P4:** runbook de incidentes y recuperación.
**Archivos:** workers/jobs/broker/leases reales, tests concurrency y failure injection. **Gate:** ninguna doble ejecución efectiva, estados recuperables, cancelación probada. **Rollback:** detener colas y recuperar jobs pendientes sin pérdida de ledger. **Dependencias:** VS-02/03/04.

## VS-06 — Revisión de seguridad, CI y release fail-closed (CP-05/07)

**Objetivo:** gate de beta basado en evidencia, no solo tests sintéticos.
**Inspeccionar:** `adversarial_lab/scripts/releasecheck.py`, `release/**`, `scripts/release_status.py`, `docs/release/**`, `.github/workflows/**`, `typescript/build-runtime.mjs`.
**P0:** auditar exit codes y comprobar audit BLOCKED, firma Ed25519 local vs atestación externa, SBOM y provenance. **P1:** política `beta_internal` vs `customer_production`, prohibir bypass silencioso y registrar excepciones no críticas. **P2:** pip-audit real, SBOM y hashes, provenance firmada según mecanismo elegido, CI con matrices Python/Node, scanner real opt-in y policy. **P3:** dependency vulnerable, SBOM manipulado, firma inválida, escáner bloqueado, secretos en logs, branch sin aprobación; verificar exit !=0. **P4:** paquete de revisión independiente y GO/NO-GO firmado.
**Archivos:** release scripts/workflows, reportes y tests; NO cambiar `status.json` sin comandos y evidencia. **Gate:** beta falla cerrado ante cualquier P0; producción de clientes sigue NO-GO. **Rollback:** volver a gate más restrictivo. **Dependencias:** VS-02…05.
