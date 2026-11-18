# VS-07A — Entrega y acuse de alertas contra receptor local firmado

**Base:** `1946f8c`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
**Estado:** entrega y acuse **demostrados en sintético**; escalado a persona sigue `BLOCKED`.

## Qué faltaba

VS-07 verificó instrumentación y reglas, pero declaró `BLOCKED` la entrega real: "las reglas
existen, pero no hay entrega, acuse ni escalado". Sin receptor, la frase "la alarma llega y se
relaciona con el run" era una hipótesis, no un hecho medido.

## Qué se construyó

`scripts/alert_sink.py` — receptor local **firmado** con `/alerts` como único punto de entrada:

| Propiedad | Implementación | Prueba |
|---|---|---|
| Autenticidad | HMAC-SHA256 del cuerpo en `X-Agntia-Signature: sha256=…`, comparación en tiempo constante | firma ausente, alterada o de otro cuerpo → **401** |
| Idempotencia | huella = SHA-256 de la proyección normalizada; segundo envío idéntico devuelve **el mismo `receipt_id`** con `deduplicated: true` | 8 envíos concurrentes → **1** acuse, **1** línea de estado |
| Proyección mínima | solo `alertname`, `status`, `severity`, `job_id`, `tenant`, `traceparent`; el texto libre del emisor **no se guarda ni se devuelve** | cuerpo con `summary`, `annotations` y `password` con canario → canario ausente del acuse y del fichero |
| Correlación | `job_id` obligatorio (32 hex) y `traceparent` opcional con la misma regla que el servicio | 5 reglas de `alerts.yaml` entregadas y correlacionadas |
| Acuse honesto | `acknowledged: true`, `contained: false` | acuse no implica contención ni cierre de incidente |
| Límites | cuerpo ≤ 64 KiB, validación de campos, 404 fuera de `/alerts` | 413 y 404 con exit distinto de 202 |
| Secreto | leído de `CYBER_ALERT_SINK_SECRET` (env), nunca de `argv` | no aparece en la línea de comandos del proceso |

`/alerts` no se registra en la API del producto: es una herramienta de verificación local, igual que
`verify_observability.py`.

## Resultado medido

- `tests/integration/test_alert_delivery.py`: **6 tests OK**.
- Suite completa: **205 tests OK (8 skipped)**.
- Las 5 reglas declaradas en `infra/observability/alerts.yaml` se entregan y quedan ligadas a su
  `job_id`, sin excepción.

## Lo que esto NO es

- **No es un proveedor de alertas.** No hay PagerDuty/Slack/email, ni turnos, ni escalado a persona.
- **No hay acuse humano.** `acknowledged` significa "el receptor recibió y registró", no "alguien lo
  leyó". El escalado y el runbook siguen abiertos (P4 de VS-07).
- **No cruza el firewall de la nube:** receptor en `127.0.0.1`, útil para pruebas y CI, no para
  operación 24×7.
- **No valida el colector real:** eso sigue dependiendo de `verify_observability.py` y Docker (CI).

## Gate

`PARTIAL` → **`PARTIAL` alto**: la entrega y el acuse están probados de punta a punta contra un
receptor real por HTTP; la operación con proveedor y con persona de guardia sigue `BLOCKED` por
decisión del founder (proveedor, coste y horario).

## Delta recomendado a continuación

1. Sustituir el receptor por el proveedor elegido conservando firma, dedupe y proyección mínima.
2. Simulacros P3 (scanner caído, backup fallido, presupuesto agotado) contra el receptor, con
   correlación a job y tenant.
3. Umbrales con propietario y runbook por alerta; hoy solo hay `summary`.
