# VS-05B — Rollback

Un solo archivo, sin datos ni esquema:

1. `git rm tests/integration/test_worker_multiprocess.py`
2. `python -m unittest discover -s tests` → **222 tests** (223 − 1).

## Efecto

- Desaparece la única prueba que ejerce `claim`/`complete` desde **dos procesos del sistema operativo**.
  El fencing sigue implementado y probado en un solo proceso por VS-05 y VS-05A; lo que se pierde es la
  evidencia multiproceso.
- No se toca producto, configuración ni base de datos: los jobs del fixture viven en directorios
  temporales que se destruyen al terminar cada test.
- Ningún acuse, libro de backup o evidencia de campañas anteriores se ve afectado.
