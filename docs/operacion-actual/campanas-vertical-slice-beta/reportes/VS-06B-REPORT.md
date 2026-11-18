# VS-06B — Cierre del bloqueo de dependencias

**Base:** `1946f8c`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
**Estado:** bloqueo de **dependencias** resuelto; la **atestación externa** sigue `BLOCKED`.

## El defecto era nuestro, no del SDK

VS-06 concluyó que subir `opentelemetry-sdk` a 1.45.2 rompía la propagación de trazas y revirtió el
upgrade. Reproduje el fallo y lo aislé:

1. Con 1.45.2, `TraceContextTextMapPropagator().inject()` emite el byte de flags **`03`**
   (muestreo + bit de trace-id aleatorio), no `01`.
2. `telemetry/tracing.py` validaba el padre guardado con `^00-…-0[01]$`, así que **descartaba todo
   padre** generado por el propio servicio y el worker abría una traza nueva.
3. El test comparaba trace-ids y fallaba con dos valores distintos: no había pérdida de contexto
   del SDK, había un **filtro propio demasiado estrecho**.

`parent=None` estaba silenciosamente degradando la trazabilidad extremo a extremo **también con
1.38.0** si el flags byte no era `00`/`01`; el upgrade solo lo hizo visible.

## Corrección

| Antes | Después |
|---|---|
| `TRACEPARENT = ^00-[a-f0-9]{32}-[a-f0-9]{16}-0[01]$` | `^00-[a-f0-9]{32}-[a-f0-9]{16}-[0-9a-f]{2}$` |
| validación inline duplicada en `span()` y `link_internal()` | `trusted_parent()` único: versión `00`, ids no nulos, bit de muestreo activo |

Se mantiene el criterio restrictivo: un padre con ids en cero, sin bit de muestreo, con otra versión
o con flags no hexadecimales **sigue rechazándose**, y hay test para cada caso.

## Pins y auditoría

`pyproject.toml`: `opentelemetry-sdk==1.45.2`, `opentelemetry-exporter-otlp-proto-http==1.45.2`
(arrastra `opentelemetry-api==1.45.2`).

`pip-audit` sobre el entorno real:

| Momento | Resultado | Exit |
|---|---|---|
| Antes (1.38.0 + pip 24.0) | 14 vulnerabilidades (2 de OpenTelemetry + 12 de `pip`) | **1** |
| Después del upgrade de OTel, pip sin tocar | 12 vulnerabilidades, todas de `pip==24.0` | **1** |
| Después (OTel 1.45.2 + pip 26.3) | `No known vulnerabilities found` | **0** |
| `pip-audit .` (solo dependencias del proyecto) | `No known vulnerabilities found` | **0** |

Las 12 restantes eran la **versión de la herramienta** `pip` del entorno, no una dependencia de
runtime; se resuelven actualizando `pip` en el job, que es lo que hace cualquier instalación sana.

## Gate nuevo en CI

`.github/workflows/dependency-audit.yml` crea un venv aislado, instala el proyecto y
`pip-audit==2.10.1`, y ejecuta `--local` **y** `pip-audit .`. Ambos con exit != 0 bloquean el PR.
Esto cierra el hallazgo P1 de VS-06 ("nada impide fusionar una dependencia vulnerable").

## Lo que no cambia

- **Atestación externa:** el gate `--production` sigue fallando cerrado por diseño. No se relajó.
- **Alcance:** el audit cubre dependencias declaradas e instaladas, no CVEs del sistema operativo,
  del kernel ni de las imágenes de escáner (eso es VS-02, Trivy).
- **Sin PASS de release:** la beta sigue sin autorización; esto solo quita un bloqueo técnico.

## Verificación

- Suite completa: **205 tests OK (8 skipped)**, 27,0 s.
- `tests/integration/test_telemetry.py`: **10 OK**, incluido el test de propagación que fallaba y uno
  nuevo de flags/ids.
- `scripts/validate_foundation.py`: `PASS` (280 archivos Markdown).
- Bundle de release en `5c12bbd`: **PASS**, 39 wheels, smoke del artefacto instalado PASS,
  integridad PASS; `releasecheck.py --production` sigue en **1** (fail-closed).
- Comandos del workflow de auditoría simulados en venv limpio: ambos con exit **0**; con el pin
  anterior, el mismo auditor devuelve las 2 CVE y exit **1**.

**Seguimiento:** el «aún sin run de CI» queda cerrado por [VS-06C-REPORT.md](VS-06C-REPORT.md), con los runs `44084229258` y `44084241625` en `success` sobre `7fdb14e`. La atestación externa y el run en `main` siguen pendientes.
