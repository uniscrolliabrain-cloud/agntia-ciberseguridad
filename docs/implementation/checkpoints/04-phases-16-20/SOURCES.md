# Fuentes y licencias

Se integran bibliotecas/APIs; no se copia código upstream. Referencias verificables y versiones fijadas:

- OpenTelemetry Python SDK/exporter1.38.0, Apache-2.0: https://github.com/open-telemetry/opentelemetry-python/tree/v1.38.0 — Provider privado, propagador W3C, OTLP HTTP y SpanProcessor. Su funcionamiento se valida en CI con el SDK real, no con stub local.
- Collector Contrib0.138.0, Apache-2.0: https://github.com/open-telemetry/opentelemetry-collector-contrib/releases/tag/v0.138.0 — transform/privacy y pipeline acotado. Digest exacto en infra/observability/images.json y evidencia de CI.
- Prometheus3.7.2, Apache-2.0: https://github.com/prometheus/prometheus/releases/tag/v3.7.2 — promtool valida reglas/configuración en imagen real.
- cryptography>=46,<51, Apache-2.0 o BSD-3-Clause: https://github.com/pyca/cryptography — AESGCM, autenticación de ciphertext/AAD; conservar avisos según distribución.
- prometheus-client0.23.1, Apache-2.0/BSD según componentes: https://github.com/prometheus/client_python/tree/v0.23.1 — parser solo en pruebas de formato. Ver LICENSE/NOTICE del paquete concreto antes de distribuir.

El formato W3C no es prueba de identidad. El cifrado no acredita cumplimiento RGPD ni base jurídica. Las herramientas/scanners mantienen sus licencias ya registradas en checkpoints anteriores. No se compra ni activa servicio comercial.
