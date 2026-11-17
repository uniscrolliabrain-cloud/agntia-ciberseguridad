# VS-06B — Rollback

Si el upgrade o la validación nueva causan un problema en un entorno ya desplegado:

1. `git revert <sha-de-VS-06B>` — revierte pins, `trusted_parent()` y el workflow de auditoría a la
   vez; no hay migración de datos ni cambio de esquema que deshacer.
2. Reinstalar dependencias: `.venv/bin/pip install -e '.[dev]'` (vuelve a 1.38.0).
3. Reejecutar `python -m unittest tests.integration.test_telemetry` para confirmar 9 tests OK.

## Efecto de revertir

- Vuelven **2 CVE** de `opentelemetry-api==1.38.0` (CVE-2026-114603, CVE-2026-126360) y el job
  `Dependency audit` **fallará** a propósito: el rollback deja CI en rojo, que es el comportamiento
  fail-closed esperado.
- La trazabilidad vuelve al comportamiento anterior, en el que cualquier padre con flags `03` se
  descarta y el worker abre una traza nueva.

## Rollback parcial (solo la validación, manteniendo 1.45.2)

No recomendado: sin `trusted_parent()` la propagación extremo a extremo se pierde silenciosamente y
`test_persisted_trace_propagates_to_worker_and_report_link` falla. Si se aplica, debe registrarse
como regresión conocida en la bitácora antes de fusionar.
