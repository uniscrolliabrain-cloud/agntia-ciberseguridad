# VS-06B — Patchset

Diferencias exactas respecto a `1946f8c`.

```diff
--- a/agntia_ciberseguridad/telemetry/tracing.py
+++ b/agntia_ciberseguridad/telemetry/tracing.py
-TRACEPARENT=re.compile(r'^00-[a-f0-9]{32}-[a-f0-9]{16}-0[01]$')
+TRACEPARENT=re.compile(r'^00-[a-f0-9]{32}-[a-f0-9]{16}-[0-9a-f]{2}$')
+def trusted_parent(parent):
+    """A stored parent is continued only when well formed, non-zero and sampled."""
+    if not parent or not TRACEPARENT.fullmatch(parent):return False
+    version,trace_id,span_id,flags=parent.split('-')
+    return trace_id!='0'*32 and span_id!='0'*16 and bool(int(flags,16)&1)
@@ span()
-        elif parent and TRACEPARENT.fullmatch(parent) and parent.split('-')[1]!='0'*32 and parent.split('-')[2]!='0'*16:
+        elif trusted_parent(parent):
@@ link_internal()
-        if self.available and parent and TRACEPARENT.fullmatch(parent):
+        if self.available and trusted_parent(parent):

--- a/pyproject.toml
+++ b/pyproject.toml
-"opentelemetry-sdk==1.38.0", "opentelemetry-exporter-otlp-proto-http==1.38.0"
+"opentelemetry-sdk==1.45.2", "opentelemetry-exporter-otlp-proto-http==1.45.2"

--- a/tests/integration/test_telemetry.py
+++ b/tests/integration/test_telemetry.py
+    async def test_stored_parent_is_continued_only_when_well_formed_and_sampled(self):
+        # flags 01 y 03 se continúan; ids en cero, versión distinta, sin muestreo y no-hex se rechazan
```

Nuevo archivo: `.github/workflows/dependency-audit.yml` (job `audit`, `pip-audit==2.10.1`,
`--local` y `pip-audit .`).

## Riesgo del cambio

- **Superficie:** una expresión regular y una función de validación de 5 líneas; sin cambios de
  contrato HTTP, esquema ni base de datos.
- **Regresión posible:** padres con flags distintos de `00/01` que antes se rechazaban ahora se
  aceptan *solo* si tienen bit de muestreo; es la semántica de W3C trace-context.
- **Dependencia nueva:** ninguna; 1.45.2 sustituye a 1.38.0.
- **Compatibilidad:** `opentelemetry-api` 1.45.2 requiere Python ≥ 3.9; el proyecto soporta 3.11/3.12.
