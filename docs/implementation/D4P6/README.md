# D4P6 — Carga, retención y resiliencia de observabilidad

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 4. Prioridad M0; rol SRE/performance.

## Objetivo
Impedir que observar la seguridad agote recursos, presupuesto o disponibilidad del propio middleware.

## Artefactos previstos
- `tests/performance/telemetry_workload.py`
- `infra/observability/resource_limits.yaml`
- `docs/implementation/OBSERVABILITY-RESULTS.md`

## Contrato
Presupuestos separados de señal crítica/agregada y telemetría opcional; drops y cobertura siempre visibles.

## Dependencias
D4P2, D4P3

## Tareas originales
- D4P6T1: Fijar hipótesis de ingestión, almacenamiento, retención y cardinalidad por perfil Lite/L/XL. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P6T2: Configurar colas acotadas, batching, compresión y límites de disco/memoria del exporter. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P6T3: Separar evidencia requerida y auditoría de muestras de tracing que pueden descartarse. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P6T4: Ensayar collector/backend caído, disco cercano a cuota, latencia elevada y ráfaga de eventos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P6T5: Medir bytes/evento, p95, CPU/RAM, drops, lag y coste extrapolado con fórmulas explícitas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P6T6: Probar degradación segura con aviso al cliente y restauración sin duplicar ni ocultar huecos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P6T7: Emitir gateG4 con resultados por perfil; bajar alcance antes de superar presupuesto o quitar aislamiento. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D4P6-TEST-1: Caída del backend de logs/traces no permite acción denegada ni bloquea por tiempo indefinido la API.
- D4P6-TEST-2: Una ráfaga sintética respeta límites y registra pérdidas sin declarar observación completa.

Rollback: Reducir sampling/frecuencia opcional, restaurar límites seguros y preservar alertas esenciales.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
