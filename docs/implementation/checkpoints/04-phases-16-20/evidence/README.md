# Evidencias del corte

`tests-local.json`: ejecución local real; skips explícitos. `load-local.json`:200 peticiones sintéticas secuenciales ASGI, sin SDK local, no SLA. `ci.json`: runs y jobs remotos, SHA y conclusión observada. `failed-run-01.json`: primer fallo de propagación de link al span correcto, corregido sin relajar test. `observability.json`: Collector/Prometheus reales y digests resueltos.

No se guardan tokens, originales ni logs completos con datos de clientes. Los fixtures son sintéticos. Duplicar matriz Python3.11/3.12 o push/PR no aumenta el número de tests distintos. Los tests Docker se omiten en runtime y se ejecutan separados en su job con imágenes fijadas.
