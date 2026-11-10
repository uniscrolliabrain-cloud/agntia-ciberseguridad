# Fuentes y componentes

Se reutilizan FastAPI/Pydantic, SQLite y OpenTelemetry ya fijados en checkpoints anteriores. No se copian herramientas de terceros ni se instalan sensores.

- HMAC-SHA256: biblioteca estándar Python `hmac`, comparación constant-time `compare_digest`: https://docs.python.org/3/library/hmac.html . Su uso aquí exige secreto provisionado y audiencia/scope/TTL persistidos; no equivale a un sistema JWT/IdP externo.
- SQLite transacciones BEGIN IMMEDIATE e integridad: https://www.sqlite.org/lang_transaction.html . Un nodo y un worker; no prometer transacción distribuida.
- Playwright Python1.56.0 y Chromium de su distribución para CI de fixtures: https://github.com/microsoft/playwright-python/tree/v1.56.0 . Apache-2.0 del wrapper; navegadores conservan sus licencias propias. No se incorpora al runtime del middleware.
- Grafana: https://github.com/grafana/grafana/blob/main/LICENSE . AGPL-3.0; solo alternativa futura. Se entrega consola propia y no se copia/distribuye Grafana.
- Wazuh/Falco: catálogo y licencias de investigación existente; no instalados ni validados como sensores de cliente en este bloque. Evaluar privilegios, formato, scopes y términos antes de habilitar cada conector.

Las fuentes de investigación inicial no se convierten en eficacia medida de este software. Ninguna documentación acredita revisión jurídica o protección completa.
