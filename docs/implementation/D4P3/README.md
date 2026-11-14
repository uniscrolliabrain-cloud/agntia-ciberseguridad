# D4P3 — Logs estructurados y privacidad de telemetría

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 4. Prioridad M0; rol SRE/privacidad.

## Objetivo
Unificar logs seguros, búsquedas y política de retención sin coleccionar contenido innecesario.

## Artefactos previstos
- `agntia_ciberseguridad/telemetry/logging.py`
- `agntia_ciberseguridad/telemetry/retention.py`
- `tests/security/test_telemetry_redaction.py`

## Contrato
Log con timestamp, nivel, componente, IDs opacos y code; sin credenciales ni contenido de cliente por defecto.

## Dependencias
D3P4, D4P1

## Tareas originales
- D4P3T1: Definir schema de log y límites de longitud, codificación y campos permitidos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P3T2: Redactar cabeceras, excepciones y subprocess outputs antes de persistir o enviar a proveedores. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P3T3: Separar log operativo, audit de seguridad y evidencia original con controles/retenciones distintos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P3T4: Añadir parser seguro y protección de CRLF/log forging, ANSI y contenido activo. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P3T5: Implementar búsqueda tenant-scoped y vistas redactadas sin acceso directo a backend global. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P3T6: Ensayar borrado/retención/legal hold con datos sintéticos y errores de exportación. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P3T7: Revisar que traces, métricas, logs y artefactos usen la misma política de datos y no filtros contradictorios. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D4P3-TEST-1: Un mensaje hostil con saltos/HTML/ANSI no falsifica entradas ni ejecuta contenido en UI.
- D4P3-TEST-2: Redacción y export impiden recuperar secretos centinela de cualquier salida autorizada.

Rollback: Cortar ingestión/export peligrosa, preservar copia segura y tratar filtración según runbook.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
