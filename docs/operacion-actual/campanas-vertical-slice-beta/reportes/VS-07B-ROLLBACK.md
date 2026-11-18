# VS-07B — Rollback

Cuatro cambios reversibles, sin esquema ni datos:

1. `git rm tests/integration/test_p3_drills.py`
2. Revertir en `tests/integration/test_alert_delivery.py` el número esperado de reglas de 6 a 5.
3. Quitar la regla `AgntiaAttemptBudgetExhausted` de `infra/observability/alerts.yaml`.
4. Revertir `metrics.admission`, la serie `agntia_job_admission_rejections_total` y la llamada en
   `JobStore._submit`.
5. `python -m unittest discover -s tests` → **212 tests** (215 − 3).

## Efecto

- El rechazo por presupuesto vuelve a ser silencioso: 429 sin señal, sin regla y sin página.
- El resto de simulacros no se ve afectado: el escáner caído depende de `agntia_scan_coverage_total`,
  que ya existía.
- Ningún dato, acuse o fichero de estado se borra: los JSONL del receptor son evidencia y quedan.
- La exposición Prometheus vuelve a su cardinalidad anterior; no hay migración que deshacer.

## Orden seguro

Si solo se revierte parte, mantener la regla y el contador **juntos**: dejar la regla sin la métrica
produce una alerta que nunca dispara, y dejar la métrica sin la regla produce una señal que nadie
consume. Los dos se retiran en el mismo commit.
