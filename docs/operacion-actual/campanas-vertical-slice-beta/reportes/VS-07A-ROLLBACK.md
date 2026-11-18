# VS-07A — Rollback

Ambos archivos son nuevos y no los importa código de producción, así que el rollback es eliminarlos.

1. `git rm scripts/alert_sink.py tests/integration/test_alert_delivery.py`
2. Reejecutar `python -m unittest discover -s tests` → vuelve a 199 tests (205 − 6).
3. No hay datos, esquema, migración ni configuración que revertir.

## Efecto

- Desaparece la única prueba de entrega y acuse de alertas; VS-07 vuelve a `BLOCKED` en ese punto.
- Ningún endpoint de la API, ninguna regla de `alerts.yaml` ni el colector cambian: el rollback no
  afecta a la operación.
- Si el receptor ya se usó para un simulacro, sus ficheros JSONL de acuses quedan como evidencia y no
  se borran con este rollback.
