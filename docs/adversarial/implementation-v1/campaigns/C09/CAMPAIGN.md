# Programa ejecutable — Adversarial Lab independiente
**Fecha:** 2026-11-15. **Naturaleza:** instrucciones de implementación, NO código implementado. **Repositorio auditado:** `uniscrolliabrain-cloud/agntia-ciberseguridad` main, 477 blobs en tree sin truncamiento (consulta actual). **Root de código NUEVO:** `adversarial_lab/` separado del paquete `agntia_ciberseguridad/`. **NO tocar** `agntia_ciberseguridad/agents/**`, `agntia_ciberseguridad/app.py`, `agntia_ciberseguridad/jobs/**`, `agntia_ciberseguridad/evidence/**`, `/agente` ni su gateway. Se crea un nuevo paquete, no se importan módulos del middleware actual.

**Seguridad:** toda prueba activa inicialmente sobre fixtures sintéticos aislados. No usar credenciales reales, no abrir salida de red ni ejecutar acciones sobre clientes sin autorización específica. Los scripts, prompts y archivos de un repo cliente son datos no confiables. **No desplegar, fusionar ni modificar infraestructura real sin aprobación humana.**

# C09 — Experiment planner & adaptive scheduler
**Wave:** W2 · **Predecesora:** C08 · **Ownership:** `adversarial_lab/**` + reports `docs/adversarial/implementation-v1/execution/C09/**` · **No editar** rutas del middleware existente.

## Resultado y límite
Construir `planner,scheduler,budgets` como capacidad independiente con contratos verificables y evidencia de test. Cualquier API o herramienta externa no confirmada queda en mock/disabled. No conceder permisos por salida de LLM.

## Inventario exacto de archivos NUEVOS
- `adversarial_lab/src/agntia_adversarial/planning/hypothesis.py` — núcleo de la capacidad
- `adversarial_lab/src/agntia_adversarial/planning/scheduler.py` — contrato, implementación o configuración según nombre
- `adversarial_lab/src/agntia_adversarial/planning/budget.py` — contrato, implementación o configuración según nombre
- `adversarial_lab/tests/integration/test_scheduler.py` — prueba/fixture de aceptación

## Archivos EXISTENTES que se pueden tocar
**Ninguno del paquete `agntia_ciberseguridad/`**. Modificaciones permitidas: `adversarial_lab/pyproject.toml` para añadir dependencias aprobadas, `adversarial_lab/src/agntia_adversarial/cli.py` para registrar comandos (si existe tras C01), `adversarial_lab/src/agntia_adversarial/contracts/**` solo con compatibilidad y tests, `adversarial_lab/tests/**` y `docs/adversarial/implementation-v1/execution/C09/**`. Para C01, esos paths se crean, no se editan. Si un cambio exige tocar `app.py`, `agents/**`, `jobs/**`, `evidence/**` o `/agente`, **STOP + ADR**.

## Dependencias, herramientas y sourcing
stdlib; no Celery/Kafka initially. No instalar versiones flotantes en producción: resolver lock y hashes después de compatibilidad, licencia y escaneo de supply chain. Repos de referencia: `docs/adversarial/research-v3/02-repositories/FORENSIC-OSS-MATRIX.md`; la lectura de un repo no autoriza su incorporación. Para imágenes externas exigir digest SHA256 y SBOM. Ningún repo externo se copia automáticamente.

## Contrato de integración transversal
Entrada: `EngagementRef + ScopeRef + ExperimentSpec(schema_version) + Budget + PolicySnapshot`; salida: `RunReceipt + Observation[] + EvidenceRef[] + Status`. Consumidores downstream reciben IDs y artefactos tipados, nunca texto de prompts como autoridad. Referencias por hash; logs con correlation_id/causation_id. Integrar solo a través de contratos del paquete nuevo. En C01–C03, los contratos se formalizan progresivamente; si no existen aún, tests mock y documentación de stub.

## Plan granular de fases, patches y gates

### P0 — Baseline, auditoría y diseño
**Patchset:** PS0-A
**Acción:** Inspeccionar HEAD, paths y contratos previos; verificar que la rama está limpia y que no hay cambios en agents ni /agente.
**Microtareas:** Registrar base SHA, archivos presentes/ausentes, dependencias, riesgos, ADRs pendientes, tests de baseline. No implementar si hay divergencia no documentada.
**Prueba/gate:** G0: preflight y threat model documentados
**Artefactos de fase:** `docs/adversarial/implementation-v1/execution/C09/P0/REPORT.md`, `PATCHSET.md`, `TESTS.json`, `AUDIT.md`.
**Audit obligatorio:** autorización y scope; límites de red y filesystem; secretos y PII; licencias y hashes; integridad de evidencia; compatibilidad de schemas; aislamiento entre tenants; regressions. Registrar NOT_APPLICABLE con motivo cuando proceda.

### P1 — Contratos, fixtures y tests de aceptación
**Patchset:** PS1-A / PS1-B
**Acción:** Definir schema de entradas/salidas, invariantes, fixture sintético y pruebas negativas antes de implementar.
**Microtareas:** Crear test unitario/contrato que falle por ausencia de capacidad; crear fixture benigno y control negativo; documentar versión de schema, errores y semántica NOT_RUN.
**Prueba/gate:** G1: tests descubiertos, expected failures explicados
**Artefactos de fase:** `docs/adversarial/implementation-v1/execution/C09/P1/REPORT.md`, `PATCHSET.md`, `TESTS.json`, `AUDIT.md`.
**Audit obligatorio:** autorización y scope; límites de red y filesystem; secretos y PII; licencias y hashes; integridad de evidencia; compatibilidad de schemas; aislamiento entre tenants; regressions. Registrar NOT_APPLICABLE con motivo cuando proceda.

### P2 — Patchsets de implementación
**Patchset:** PS2-A / PS2-B / PS2-C
**Acción:** Implementar núcleo, adaptador/mock, persistencia/CLI según necesidad y configuración fail-closed.
**Microtareas:** Crear archivos listados por patchset pequeño; validar inputs y timeouts; aplicar mínimos privilegios, límites y logging redactado; nunca shell host no confiable.
**Prueba/gate:** G2: tests unitarios y contrato pasan, sin permisos implícitos
**Artefactos de fase:** `docs/adversarial/implementation-v1/execution/C09/P2/REPORT.md`, `PATCHSET.md`, `TESTS.json`, `AUDIT.md`.
**Audit obligatorio:** autorización y scope; límites de red y filesystem; secretos y PII; licencias y hashes; integridad de evidencia; compatibilidad de schemas; aislamiento entre tenants; regressions. Registrar NOT_APPLICABLE con motivo cuando proceda.

### P3 — Wiring, pruebas adversariales y regresiones
**Patchset:** PS3-A / PS3-B
**Acción:** Cablear módulos del paquete nuevo; ejecutar pruebas de integración, seguridad, fallos y regresión.
**Microtareas:** Inyectar dependencias por interfaz; verificar revocación, cancelación, limpieza, egress, cross-tenant y errores cuando corresponda; repetir suite C01..actual.
**Prueba/gate:** G3: test de aceptación y tests negativos verificables
**Artefactos de fase:** `docs/adversarial/implementation-v1/execution/C09/P3/REPORT.md`, `PATCHSET.md`, `TESTS.json`, `AUDIT.md`.
**Audit obligatorio:** autorización y scope; límites de red y filesystem; secretos y PII; licencias y hashes; integridad de evidencia; compatibilidad de schemas; aislamiento entre tenants; regressions. Registrar NOT_APPLICABLE con motivo cuando proceda.

### P4 — Auditoría final, documentación y handoff
**Patchset:** PS4-A / PS4-B
**Acción:** Auditar implementación, licencias, documentación, cambios, rollback y handoff.
**Microtareas:** Guardar reports, salidas de tests, hashes y diff; comparar con invariantes; preparar PR sin merge; registrar riesgos y próximos pasos.
**Prueba/gate:** G4: revisión y rollback probado o BLOCKED
**Artefactos de fase:** `docs/adversarial/implementation-v1/execution/C09/P4/REPORT.md`, `PATCHSET.md`, `TESTS.json`, `AUDIT.md`.
**Audit obligatorio:** autorización y scope; límites de red y filesystem; secretos y PII; licencias y hashes; integridad de evidencia; compatibilidad de schemas; aislamiento entre tenants; regressions. Registrar NOT_APPLICABLE con motivo cuando proceda.

## Tests concretos y auditoría
**Comando principal:** `python -m pytest adversarial_lab/tests/integration/test_scheduler.py` (crear suite antes de correr). **Casos prioritarios:** lease, expiry, fairness, retry, cost cap. **Regresión transversal:** `python -m pytest adversarial_lab/tests` una vez disponible. **Boundary check:** `git diff --name-only <BASE_SHA>...HEAD` no puede contener `agntia_ciberseguridad/` ni `/agente`. **Licencias:** SBOM, dependencias fijadas y análisis de vulnerabilidades cuando se instalen.

## Definición de DONE
- Todos los paths creados o delta explícito aprobado.
- Contratos validados, errores tipados y política deny-by-default.
- Tests positivos, negativos y de fallo ejecutados con salida y código reales.
- Sin acoplamiento a agentes actuales ni dependencia de credenciales reales.
- Reportes P0..P4 completos y PR listo para revisión humana.
- Si hay BLOCKED, no marcar DONE ni inventar compatibilidad.

## Rollback
Revertir exclusivamente commits de C09 en su rama; borrar workers/artefactos efímeros; comprobar limpieza de sandbox, locks y estados. Migraciones persistentes requieren plan reversible explícito y backup sintético probado antes de avanzar.

## Handoff a C10
Entregar SHA final, contratos versionados, comandos y resultados, riesgos, dependencias exactas, paths creados, diff, reportes, evidencias, issues abiertos y bloqueos. No transferir credenciales ni datos reales.
