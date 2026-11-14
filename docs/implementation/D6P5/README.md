# D6P5 — Remediación revisable y retest

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 6. Prioridad M1; rol AppSec/remediación.

## Objetivo
Producir correcciones en ramas o workspaces aislados con revisión, no aplicar cambios ciegos.

## Artefactos previstos
- `agntia_ciberseguridad/remediation/proposals.py`
- `agntia_ciberseguridad/remediation/retest.py`
- `tests/e2e/test_fix_proposal.py`

## Contrato
Propuesta ligada al commit/finding, diff, tests esperados, riesgo y rollback; ejecución separada de merge/deploy.

## Dependencias
D3P6, D5P2

## Tareas originales
- D6P5T1: Seleccionar pocos fixes deterministas de fixtures y permitir explicaciónIA solo como propuesta. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P5T2: Crear diff/rama de laboratorio con origen inmutable, licencia y validación de rutas permitidas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P5T3: Restringir cambios a ficheros previstos y detectar modificación de workflows, permisos o secretos no autorizada. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P5T4: Capturar aprobación de contenido exacto y mantener merge/deploy como operaciones distintas no habilitadas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P5T5: Ejecutar retest y regresión en sandbox con política explícita antes de declarar arreglado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P5T6: Probar rebase/conflicto, replay, prueba fallida y rollback sin pérdida de trabajo. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P5T7: Publicar PR propuesta en remoto solo con instrucción/alcance concretos; ningún envío externo derivado de un prompt hostil. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D6P5-TEST-1: Origen cambió tras aprobación y la propuesta queda stale/conflict en lugar de pisarlo.
- D6P5-TEST-2: Finding ausente por scanner fallido no se marca verified_fixed.

Rollback: Cerrar o descartar únicamente rama/workspace propio; nunca resetear cambios del cliente.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
