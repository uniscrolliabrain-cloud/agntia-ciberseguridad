# VS-07A — Evidencia

**Base:** `1946f8c` · entorno `.venv` Python 3.12 · sin Docker.

## Pruebas de entrega

```
$ .venv/bin/python -m unittest tests.integration.test_alert_delivery -v
test_concurrent_duplicate_deliveries_produce_one_acknowledgement ... ok
test_every_declared_rule_can_be_delivered_and_correlated_to_its_job ... ok
test_malformed_alert_fields_are_rejected_not_stored ... ok
test_sender_free_text_never_reaches_the_receipt_or_the_state_file ... ok
test_signed_alert_is_acknowledged_linked_to_its_job_and_deduplicated ... ok
test_unsigned_tampered_oversized_and_unknown_paths_are_refused ... ok
Ran 6 tests in 3.154s
OK
```

## Acuse observado

```json
{"receipt": {"acknowledged": true, "alertname": "AgntiaScanSignalAbsentOrOld", "contained": false,
 "deduplicated": false, "job_id": "aaaaaaaa…", "receipt_id": "<32 hex>", "severity": "info",
 "status": "firing", "tenant": "tenantA",
 "traceparent": "00-1111…-2222…-03"}}
```

Segundo envío idéntico: mismo `receipt_id`, `deduplicated: true`, sin línea adicional en el fichero
de estado.

## Reglas entregadas

Extraídas de `infra/observability/alerts.yaml` en tiempo de prueba (`re.findall` sobre `- alert:`),
5 reglas: `AgntiaApiSignalAbsent`, `AgntiaTraceDeliveryIncomplete`,
`AgntiaDeclaredScanCoverageIncomplete`, `AgntiaScanSignalAbsentOrOld`,
`AgntiaApiPilotErrorBudgetFastBurn`. La prueba falla si el YAML y el receptor divergen en número.

## Suite completa

```
Ran 205 tests in 27.002s
OK (skipped=8)
```

## Límites

- Receptor en `127.0.0.1` iniciado en el propio proceso de prueba; no hay proveedor externo.
- No se ejecutó `scripts/verify_observability.py` (requiere `docker pull` del colector).
- No hay firma con clave gestionada: el secreto es un fixture de 16+ caracteres, no un secreto real.
