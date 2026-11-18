# VS-06C — Patchset

**Sin delta de código.** La campaña es una consulta de evidencia y su registro documental.

## Archivos tocados

| Archivo | Cambio |
|---|---|
| `reportes/VS-06C-REPORT.md` | Nuevo: recibo, alcance y límites |
| `reportes/VS-06C-EVIDENCE.md` | Nuevo: runs, campos y reproducción |
| `reportes/VS-06C-PATCHSET.md` | Nuevo: este archivo |
| `reportes/VS-06C-ROLLBACK.md` | Nuevo: borrado documental |
| `reportes/BITACORA-VIVA.md` | Entrada de campaña y fila de cola |
| `reportes/VS-06B-REPORT.md` | Puntero al recibo de CI |

## Por qué no hay cambio de workflow

Tres tentaciones, las tres descartadas:

| Tentación | Motivo del descarte |
|---|---|
| Añadir `workflow_dispatch` para relanzar a mano | El recibo ya existe por `push`/`pull_request`; un disparador manual solo añade superficie |
| Añadir `--ignore-vuln` para «estabilizar» el verde | Silenciaría hallazgos reales; el verde debe costar |
| Ampliar a escaneo diario programado | Consumo y decisiones de infraestructura que no se pidieron; el hueco declarado es otro |

## Riesgo de esta campaña

Ninguno sobre producto: no se modificó código, workflow, configuración ni datos. El único riesgo es de
**interpretación**, y por eso el informe insiste en que un run verde no es atestación de cadena de
suministro.
