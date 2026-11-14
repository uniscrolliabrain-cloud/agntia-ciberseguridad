# D3P2 — Worker con leases, fencing y retries

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 3. Prioridad M0; rol Plataforma/jobs.

## Objetivo
Procesar trabajos de forma recuperable y revalidar permisos después de esperas o revocaciones.

## Artefactos previstos
- `agntia_ciberseguridad/jobs/worker.py`
- `agntia_ciberseguridad/jobs/leases.py`
- `tests/integration/test_worker_recovery.py`

## Contrato
Reclamo/heartbeat/ACK con owner y fencing; reintento solo dentro de política y presupuesto.

## Dependencias
D3P1, D2P2

## Tareas originales
- D3P2T1: Implementar reclamo atómico y límite de paralelismo por tenant, herramienta y capacidad global. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P2T2: Agregar heartbeat, lease expiry y fencing token comprobado al escribir resultados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P2T3: Reconstruir principal/grant/config vigentes antes de cada ejecución y efecto externo. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P2T4: Clasificar errores retryable, permanentes e inciertos; backoff/jitter, intentos y dead-letter visibles. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P2T5: Hacer cleanup idempotente y reconciliar reservas incluso si el proceso muere entre pasos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P2T6: Inyectar crash tras claim, tras scan y antes de ACK y comprobar recuperación sin pérdida o duplicado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P2T7: Registrar comandos/tiempos y límites reales de concurrencia del almacenamiento elegido. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D3P2-TEST-1: Un worker con lease vieja no confirma ni sobrescribe el resultado del nuevo.
- D3P2-TEST-2: Actor/grant revocado antes de reclamar o antes de efecto externo bloquea trabajo.

Rollback: Detener workers, esperar expiración controlada y recuperar con fencing; no ejecutar efectos inciertos dos veces.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
