# D3P1 — Jobs, idempotencia y estados fiables

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 3. Prioridad M0; rol Backend/jobs.

## Objetivo
Admitir trabajo asíncrono sin duplicar scans, findings o cargos al repetir una petición.

## Artefactos previstos
- `agntia_ciberseguridad/jobs/api.py`
- `agntia_ciberseguridad/idempotency.py`
- `tests/integration/test_job_replay.py`

## Contrato
POST audits responde202 con job_id; misma key/payload devuelve el mismo recibo y otra carga da409.

## Dependencias
D1P6

## Tareas originales
- D3P1T1: Definir estados pending/running/partial/completed/failed/cancelled/blocked/reconciliation_required y sus transiciones. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P1T2: Persistir comando canónico, actor, grant, snapshot, perfil y presupuesto antes del enqueue. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P1T3: Implementar unicidad transaccional de key/payload por tenant/operación y replay de resultados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P1T4: Crear endpoints de consulta/cancelación con scope sin aceptar tenant/actor como autoridad del body. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P1T5: Distinguir cancelación solicitada, cancelación efectiva y efecto externo ya iniciado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P1T6: Probar replay concurrente, body cambiado, cancelación y recuperación de API tras crash. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P1T7: Exportar estado y warnings sin filtrar datos de otro tenant ni resultados internos crudos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D3P1-TEST-1: Dos peticiones simultáneas iguales conservan un job y una reserva de coste.
- D3P1-TEST-2: Una respuesta202 nunca aparece en UI como auditoría completada.

Rollback: Bloquear admisión, drenar trabajos propios y conservar estados; no borrar claves para permitir duplicados.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
