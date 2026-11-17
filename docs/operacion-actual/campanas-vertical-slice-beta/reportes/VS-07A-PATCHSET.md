# VS-07A — Patchset

Archivos nuevos respecto a `1946f8c`; ningún archivo existente de producción se modificó.

## `scripts/alert_sink.py` (~130 líneas)

```python
MAX_BODY=65536
SIGNATURE=re.compile(r'^sha256=[a-f0-9]{64}$')
ALERT=re.compile(r'^Agntia[A-Za-z]{3,60}$')
JOB=re.compile(r'^[a-f0-9]{32}$')
TENANT=re.compile(r'^tenant[A-Za-z0-9_-]{0,40}$')
TRACEPARENT=re.compile(r'^00-[a-f0-9]{32}-[a-f0-9]{16}-[0-9a-f]{2}$')

def traceparent_is_usable(value): ...      # versión 00, ids no nulos, bit de muestreo
class Rejected(Exception): ...             # 400 con código, nunca con el cuerpo recibido
class AlertSink:
    def signature(self,body): ...          # 'sha256=' + HMAC-SHA256
    def verify(self,body,signature): ...   # hmac.compare_digest
    def parse(self,body): ...              # proyección de 6 campos; descarta el resto
    def accept(self,body): ...             # dedupe por huella + acuse + JSONL opcional
    def server(self,host,port): ...        # POST /alerts: 202 / 400 / 401 / 404 / 413
def main(): ...                            # secreto desde --secret-env, no desde argv
```

## `tests/integration/test_alert_delivery.py` (~75 líneas)

Seis pruebas: acuse con dedupe, firma/tamaño/ruta, campos malformados, no fuga de texto libre,
correspondencia con `alerts.yaml` y concurrencia.

## Decisiones de diseño

| Alternativa | Por qué se descartó |
|---|---|
| Receptor dentro de `agntia_ciberseguridad/` | No es código de producto; sería superficie de ataque sin necesidad. Queda como script, como `verify_observability.py`. |
| Alertmanager real | Requiere contenedor y no aporta acuse verificable sin proveedor. |
| Firma en `Authorization` | Se confundiría con credencial de API; cabecera propia y explícita. |
| Guardar el cuerpo completo | Metería texto libre del emisor (posible secreto) en disco. Solo se guarda la proyección. |
| Secreto por `--secret` | Visible en `ps`; se lee del entorno. |
