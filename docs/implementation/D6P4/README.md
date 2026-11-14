# D6P4 — Incidentes y contención propuesta

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 6. Prioridad M1; rol Respuesta a incidentes.

## Objetivo
Convertir señales en casos con alcance, evidencia y recuperación gobernada.

## Artefactos previstos
- `agntia_ciberseguridad/incidents.py`
- `playbooks/lab/`
- `tests/e2e/test_incident_workflow.py`

## Contrato
Caso con tenant/activo, severidad/confianza, cronología, dueño, evidencia y acciones diferenciadas de notificación legal.

## Dependencias
D3P6, D5P6

## Tareas originales
- D6P4T1: Definir estados detected/triaged/contained/recovering/resolved y responsables según horario real. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P4T2: Correlacionar eventos/findings y preservar evidencia antes de cualquier propuesta de limpieza. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P4T3: Crear playbooks solo de laboratorio y propuestas para revocar grants o aislar un recurso específico. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P4T4: Ligar aprobación a diff/objetivo/riesgo/coste y separar contención de declaración regulatoria. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P4T5: Implementar estados inciertos y conciliación con el proveedor antes de reintentar. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P4T6: Ensayar alerta duplicada, falso positivo, fallo parcial y recuperación con roles distintos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P4T7: Entregar runbook/escalado y cobertura real, sin prometer MDR humano24/7 o respuesta global. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D6P4-TEST-1: Alerta falsa no dispara revocación masiva o borrado automático.
- D6P4-TEST-2: Contención aprobada de laboratorio conserva rollback y no afecta otro tenant.

Rollback: Detener playbook, recuperar estado anterior permitido y conservar cronología de efectos/errores.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
