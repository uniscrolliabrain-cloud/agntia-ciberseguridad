# D1P2 — Paquete, configuración y contratos tipados

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 1. Prioridad M0; rol Backend/API.

## Objetivo
Crear un servicio mínimo instalable con configuración cerrada y contratos versionados.

## Artefactos previstos
- `pyproject.toml`
- `agntia_ciberseguridad/app.py`
- `agntia_ciberseguridad/config.py`
- `agntia_ciberseguridad/contracts.py`
- `tests/unit/test_contracts.py`

## Contrato
API /v1 privada, health liveness/readiness separados, errores seguros y DTOs extra=forbid con límites.

## Dependencias
D1P1

## Tareas originales
- D1P2T1: Crear paquete Python y CLI con factoría de aplicación, versión de API y configuración por entorno. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P2T2: Definir IDs opacos, fechas UTC, revisión optimista y cantidades monetarias en unidades enteras mínimas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P2T3: Modelar Tenant, Principal, Asset, Grant, Job, Finding, Evidence, Approval y BudgetReservation sin secretos embebidos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P2T4: Normalizar errores con code, correlation_id, retryable y reconciliation_required; ocultar excepciones internas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P2T5: Añadir límites de body, listas, strings, archivos y cabeceras; separar liveness de dependencia disponible. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P2T6: Instalar en entorno limpio, exportar JSON Schema y validar round-trip y compatibilidad de versión. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P2T7: Ejecutar casos de entrada inválida y guardar comandos/resultados reales, sin sustituirlos por ejemplos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D1P2-TEST-1: Un campo desconocido de identidad o shell provoca422 antes de cualquier efecto.
- D1P2-TEST-2: NaN, payload gigante o configuración insegura impiden arranque/admisión de manera explicable.

Rollback: Desactivar la aplicación nueva; mantener intacta la documentación y configuración previa.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
