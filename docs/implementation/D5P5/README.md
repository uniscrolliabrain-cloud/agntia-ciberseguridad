# D5P5 — Evaluaciones adversariales con utilidad

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 5. Prioridad M0; rol Evaluación IA.

## Objetivo
Comprobar resistencia y tareas útiles en laboratorio con protocolos reproducibles.

## Artefactos previstos
- `evals/agent_security/`
- `evals/benign_tasks/`
- `scripts/run_agent_eval.py`
- `docs/implementation/AI-EVAL-RESULTS.md`

## Contrato
Suite/modelo/prompt/policy/versión y semillas fijados; datos sintéticos, costo reservado y resultados no heredados del paper.

## Dependencias
D5P2, D5P3, D5P4

## Tareas originales
- D5P5T1: Seleccionar subconjunto AgentDojo/licencias y casos propios compatibles con recursos y scope. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P5T2: Separar benign/dev/test/adaptativo y definir resultados permitidos y adversariales por tarea. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P5T3: Añadir casos de memoria/RAG, idioma, datos multimodales si aplican e instrucciones legítimas de terceros. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P5T4: Medir bloqueo, rechazo/ignorancia, tarea completada, FP/FN, escalados, p50/p95 y coste con denominadores. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P5T5: Ejecutar primero simulaciones deterministas sin API y después modelo autorizado bajo presupuesto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P5T6: Revisar errores manualmente y conservar transcripciones minimizadas/canarios, no secretos reales. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P5T7: Emitir gateG5 con límites: no replicación total, no seguridad universal y ningún paper convertido en métrica propia. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D5P5-TEST-1: Una suite sin ataques exitosos pero sin tareas benignas completas no se declara excelente defensa.
- D5P5-TEST-2: Cambio de modelo/prompt/policy invalida resultados previos para esa configuración.

Rollback: Volver a configuración anterior y bloquear casos de alto impacto; no ajustar el informe ocultando fallos.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
