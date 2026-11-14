# D3P6 — Reportes y primera vertical AppSec

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 3. Prioridad M0; rol Producto/reportes.

## Objetivo
Cerrar snapshot→scan→finding→revisión→reporte con datos sintéticos verificables.

## Artefactos previstos
- `agntia_ciberseguridad/reports.py`
- `templates/reports/`
- `tests/e2e/test_appsec_vertical.py`

## Contrato
Reporte JSON/HTML reproducible, snapshot/reglas/fecha, alcance y not_tested; PDF solo si se verifica seguro.

## Dependencias
D3P2, D3P3, D3P4, D3P5

## Tareas originales
- D3P6T1: Crear vistas ejecutiva/técnica con periodo, tenant, autorización y autores/generación/revisión. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P6T2: Incluir hallazgos, confianza, cobertura, fallos y versión de herramientas/bases en cada salida. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P6T3: Escapar contenido externo y limitar anexos; no incorporar enlaces activos o secretos a reportes públicos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P6T4: Construir filtros por activo/estado/dueño y snapshots versionados para comparación posterior. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P6T5: Ejecutar vertical real con herramientas fijadas sobre fixtures y revisión de una excepción. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P6T6: Comparar export repetido, datos alterados, fail/partial y acceso por viewer/analyst/reviewer. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P6T7: Emitir gateG3 con demo, conteos y limitaciones; no usar benchmarks externos como resultados propios. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D3P6-TEST-1: Fixture vulnerable y benigno producen informes distintos con evidencia, sin secreto canario.
- D3P6-TEST-2: Errores de scanner o cobertura ausente se muestran en resumen ejecutivo y técnico.

Rollback: Retirar export defectuoso y conservar JSON/evidencia; no declarar validado un PDF no comprobado.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
