# VS-07 — Observabilidad, alertas y límites económicos

**Base:** `45b5a7a`. **Estado:** `PARTIAL`; entrega real de alertas `BLOCKED`.
**Actualización 2026-11-17:** entrega y acuse demostrados contra receptor local firmado; ver
[VS-07A-REPORT.md](VS-07A-REPORT.md). Sigue faltando proveedor, guardia y runbook.
**Verificación:** mediciones sintéticas ejecutadas en este turno.

## P0 — Inventario real

- **Métricas:** `telemetry/metrics.py` con contadores por operación/estado, histograma de latencia
  (buckets 5 ms–10 s), jobs por herramienta y estado, cobertura de escaneo, señales de logs/eventos/
  delegaciones y contadores de descarte/fallo de exportación.
- **Vistas:** `telemetry/views.py` expone dashboard por tenant e investigación por job.
- **Logs:** captura con retención, hold y purga; tamaño acotado (236 bytes/registro medidos).
- **Reglas:** `infra/observability/alerts.yaml` define 5 alertas (API ausente, entrega de trazas
  incompleta, cobertura incompleta, scan antiguo, error budget del piloto).
- **Colector y dashboards:** `collector.yaml`, `prometheus.yaml`, `dashboards/`, con imagen fijada
  por digest.
- **CI:** workflow `observability.yml` ejecuta verificación, medición y carga.

## SLIs medidos (sintético, sin SLA)

| Métrica | Valor |
|---|---|
| p50 / p95 (200 req, secuencial) | 6,04 ms / 7,02 ms |
| p95 con concurrencia 10 (100 req) | 7,19 ms |
| Errores inesperados | 0 |
| Denegaciones cross-tenant esperadas | 20/20 |
| RSS pico | ~66 MB |
| Series de métricas | 18–20 |
| Logs descartados | **71 señales** (`('logs','dropped')`) |

El descarte es intencionado (pipeline acotado, la autenticación no depende de logs), pero significa
que la observabilidad **pierde señales** bajo carga; debe vigilarse con la alerta
`AgntiaTraceDeliveryIncomplete`, no ignorarse.

## Qué falla

- `scripts/verify_observability.py` **exit 1** en este workspace: intenta `docker pull` del colector
  y no hay Docker. En CI sí corre; aquí no se declara PASS.
- **No hay receptor real:** las reglas existen, pero no hay entrega, acuse ni escalado. El gate de la
  campaña (“la alarma llega y se relaciona con el run”) no se cumple.
- Sin prueba de simulacro (scanner caído, backup fallido, presupuesto excedido) contra receptor.

## Delta recomendado

1. Receptor falso local (HTTP con firma y dedupe) para probar entrega y acuse sin proveedor.
2. Simulacros P3 contra ese receptor, verificando correlación con job y tenant.
3. Presupuesto por tenant y rate limits ya existen en billing; falta alerta cuando se agota.
4. Umbrales con propietario y runbook (P4).

## Gate

`PARTIAL`: instrumentación y reglas verificadas; entrega real `BLOCKED` por receptor. No se marca
PASS de observabilidad operativa.

**Seguimiento:** entrega y acuse en [VS-07A-REPORT.md](VS-07A-REPORT.md); simulacros P3 en [VS-07B-REPORT.md](VS-07B-REPORT.md) (2 PASS, backup BLOCKED por falta de señal).
