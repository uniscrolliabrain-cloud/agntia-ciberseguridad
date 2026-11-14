# D5P1 — Registro de agentes, tools y capacidades delegadas

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 5. Prioridad M0; rol Seguridad agéntica.

## Objetivo
Inventariar quién puede hacer qué y ligar cada llamada a identidad, recurso y finalidad.

## Artefactos previstos
- `agntia_ciberseguridad/agents/registry.py`
- `agntia_ciberseguridad/agents/capabilities.py`
- `tests/security/test_delegation.py`

## Contrato
Manifest versionado y autorización corta con audiencia, scope, nonce, expiración y concesión padre.

## Dependencias
D1P6, D3P4

## Tareas originales
- D5P1T1: Modelar agente, tool/skill, versión/hash, proveedor, schema, permisos, datos y red aprobados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P1T2: Crear admisión/revisión de manifests y capacidades por principal, tarea y recurso. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P1T3: Firmar/verificar sobres canónicos con audiencia, expiración, nonce y política vinculada. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P1T4: Implementar delegación atenuada y prohibir expansión silenciosa de herramienta, destino o sensibilidad. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P1T5: Resolver credenciales solo en ejecutor y separarlas del prompt y resultado de tool. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P1T6: Probar token repetido, firma alterada, cambio de audiencia, revocación y carrera de delegación. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P1T7: Mostrar inventario real y herramientas no gobernadas; no llamar protegido a un agente que usa otro camino. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D5P1-TEST-1: Un agenteA delega y el hijo no recibe más herramientas/destinos que el padre.
- D5P1-TEST-2: Un token de actor/tenant/audiencia distintos se rechaza antes de resolver secretos.

Rollback: Revocar admisión de herramientas/capacidades; conservar inventario y evidencia de uso.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
