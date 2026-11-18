# VS-07B — Patchset

Respecto a `acccf0d`: un archivo nuevo de pruebas, un módulo de pruebas auxiliar ya existente sin
cambios y **tres ediciones pequeñas** en producción/observabilidad.

## `agntia_ciberseguridad/telemetry/metrics.py`

```python
ADMISSION_REASONS=('quota','scope','identity','validation','other')
...
self.admissions={}                                  # en __init__
def admission(self,reason):
    reason=reason if reason in ADMISSION_REASONS else 'other'
    with self.lock:self.admissions[reason]=self.admissions.get(reason,0)+1
...
# export()
lines+=['# HELP agntia_job_admission_rejections_total Refused job admissions, never a security score.',
        '# TYPE agntia_job_admission_rejections_total counter']
for reason,value in sorted(self.admissions.items()):
    lines.append(f'agntia_job_admission_rejections_total{{reason="{reason}"}} {value}')
```

Etiquetas cerradas: motivo y nada más. Ni tenant, ni actor, ni job, ni ruta.

## `agntia_ciberseguridad/jobs/store.py`

```python
if state=='pending' and used+body.max_attempts>grant['max_requests']:
    # Refusals are not tenant-labelled: the counter only exposes the bounded reason.
    self.service.telemetry.metrics.admission('quota')
    reject('quota','Presupuesto local de intentos agotado',429)
```

El contador se incrementa antes de lanzar el rechazo, así que registra el 429 aunque la transacción
no llegue a confirmar. No se toca la condición ni el código de error.

## `infra/observability/alerts.yaml`

```yaml
- alert: AgntiaAttemptBudgetExhausted
  expr: increase(agntia_job_admission_rejections_total{reason="quota"}[15m]) > 0
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: Attempt budget exhausted; admissions are refused and no new scan runs
```

Sexta regla del grupo `agntia-pilot-hypotheses`. Severidad `warning` porque no hay impacto en
activos: hay denegación de servicio propia y un humano debe decidir si amplía presupuesto.

## `tests/integration/test_p3_drills.py` (~120 líneas)

Reutiliza el fixture de `tests/security/test_ingestion` y el receptor de `scripts/alert_sink.py`.
Contiene:

- `rule(name)` / `declare(text)`: leen nombre, expresión y severidad del YAML para que el simulacro
  use la regla declarada y no una inventada en la prueba.
- `Drill.page(...)`: firma, entrega, exige 202 y comprueba `acknowledged: true` / `contained: false`.
- Tres simulacros descritos en el informe.

## `tests/integration/test_alert_delivery.py`

Único cambio: el número esperado de reglas entregables pasa de 5 a 6.

## Decisiones

| Alternativa | Por qué se descartó |
|---|---|
| Regla de backup sobre una métrica inexistente | Sería una alarma que nunca puede dispararse: peor que el hueco declarado. |
| Etiquetar el rechazo con tenant o job | Cardinalidad y datos de cliente en métricas; el motivo basta para paginar. |
| Contar el rechazo dentro de la transacción con `after_commit` | La transacción se revierte en el rechazo y el contador se perdería. |
| Simulacros como script aparte | Las pruebas ya son el mecanismo de evidencia del programa; un script duplicaría el fixture. |
| Bajar `max_requests` de la autorización en la prueba | `proposal_hash` cubre los campos de la autorización y la manipulación se rechaza correctamente; se usan 20 admisiones reales. |
