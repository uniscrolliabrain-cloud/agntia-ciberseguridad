# VS-03 — Evidencia

**Base:** `6677899`. **Fecha:** 2026-11-16.

| Comprobación | Comando | Resultado |
|---|---|---|
| Referencias de secreto | `grep -n "_env\|EnvRef" agntia_ciberseguridad/config.py` | 6 tipos de referencia; ninguno con valor |
| Lectura de valores | `grep -rn "getenv\|environ" agntia_ciberseguridad` | Solo `os.getenv(<ref>)` en auth, vault, recovery, ingest, telemetría, agentes |
| Validadores de separación | `config.py:127–135` | Emergencia, delegación y métricas no pueden compartir referencia con principales |
| Autenticación | `auth.py:30–80` | Revocado/expirado/deshabilitado → 403; comparación en tiempo constante; un único match |
| Rutas mutadoras | `grep -rhoE "@(app\|router)\.(post\|put\|patch\|delete)\("` | 57, todas `POST` |
| Tests negativos | ver tabla en el reporte | Tenancy, expiración, revocación, replay y token de un solo uso |

## No ejecutado

- `python -m unittest` no se reejecutó en este turno: el workspace perdió `.venv` tras la
  restauración. Los resultados citados son de la última ejecución verificada (197 OK, 8 skipped).
- No se accedió a ningún gestor de secretos ni a valores de entorno reales.
- No se inspeccionó `.env` (inexistente y excluido por política).

## Reproducir cuando haya entorno

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m unittest tests.security.test_api_foundation tests.integration.test_jobs tests.security.test_agent_gateway
```
