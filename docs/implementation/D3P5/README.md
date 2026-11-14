# D3P5 — Priorización, excepciones y revisión humana

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 3. Prioridad M0; rol Analista de seguridad.

## Objetivo
Producir prioridades comprensibles que no dependan de la narración del LLM.

## Artefactos previstos
- `agntia_ciberseguridad/risk.py`
- `agntia_ciberseguridad/exceptions.py`
- `tests/unit/test_risk_policy.py`

## Contrato
Riesgo combina severidad, evidencia, exposición/datos y contexto; unknown no equivale a low.

## Dependencias
D3P3

## Tareas originales
- D3P5T1: Especificar fórmula/reglas de prioridad versionadas y campos con fuente o unknown. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P5T2: Introducir KEV/EPSS/CVSS opcionales con fecha/licencia y sin adjudicar explotación al cliente. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P5T3: Definir revisión de falsos positivos con motivo, evidencia, responsable, caducidad y ámbito. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P5T4: Separar accepted_risk, suppressed, remediated y verified_fixed con autorización de cada transición. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P5T5: Permitir al modelo redactar explicación citada sin modificar puntajes o estados autoritativos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P5T6: Probar ordenación con datos faltantes, excepciones, cambios de política y evidencia contradictoria. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P5T7: Entregar backlog por dueño/plazo con cobertura visible y riesgos no evaluables. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D3P5-TEST-1: Advisory conocido sin evidencia de exposición no se convierte en explotación confirmada.
- D3P5-TEST-2: Excepción caducada reaparece y el LLM no puede aceptar riesgo sin principal autorizado.

Rollback: Volver a política anterior, conservar decisiones versionadas y recalcular proyecciones sin alterar observaciones.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
