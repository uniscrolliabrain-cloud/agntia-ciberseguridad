# D4P2 — Métricas, SLIs y presupuesto de error

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 4. Prioridad M0; rol SRE/observabilidad.

## Objetivo
Medir disponibilidad, latencia, cobertura y salud del pipeline con denominadores explícitos.

## Artefactos previstos
- `agntia_ciberseguridad/telemetry/metrics.py`
- `infra/observability/prometheus.yaml`
- `infra/observability/alerts.yaml`
- `tests/integration/test_metrics.py`

## Contrato
Métricas técnicas agregadas; métricas de cliente scoped en API, sin tenant/user/URL ilimitados como labels.

## Dependencias
D4P1

## Tareas originales
- D4P2T1: Definir SLIs de API, policy, queue lag, duración de scans, frescura, dropped events y tareas útiles. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P2T2: Fijar conjuntos pequeños de labels y mapear dimensiones de tenant a consultas autorizadas fuera de Prometheus. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P2T3: Exponer métricas con autenticación/red privada, buckets de histograma y contadores de resultados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P2T4: Crear alertas sobre ausencia de señales, backlog, lease expiry, presupuesto y dependencia caducada. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P2T5: Definir objetivos piloto como hipótesis y burn-rate/error budget con ventanas y denominadores. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P2T6: Generar carga sintética acotada y medir p50/p95, errores, recursos y cardinalidad real. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P2T7: Documentar umbrales medidos frente a objetivos; no convertir un load test local en SLA contractual. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D4P2-TEST-1: Cienmil valores distintos de un atributo externo no crean cienmil series.
- D4P2-TEST-2: Error/partial de scanner aumenta cobertura incompleta y no mejora artificialmente tasa de seguridad.

Rollback: Retirar reglas/labels defectuosos y preservar series/agregados anteriores; no inventar datos faltantes.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
