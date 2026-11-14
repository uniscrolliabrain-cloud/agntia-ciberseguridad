# D1P1 — Baseline, alcance y contrato de servicio

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 1. Prioridad M0; rol Lead implementador.

## Objetivo
Convertir la documentación en un baseline reproducible y evitar heredar aprobaciones o capacidades inexistentes.

## Artefactos previstos
- `docs/implementation/BASELINE.md`
- `docs/implementation/SCOPE.md`
- `scripts/verify_environment.py`

## Contrato
El baseline enumera SHA, herramientas realmente disponibles, activos sintéticos y alcance; ningún cliente real entra por defecto.

## Dependencias
ninguna

## Tareas originales
- D1P1T1: Anotar SHA remoto/local, árbol, ramas, estado Git y fecha de ejecución antes de instalar dependencias. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P1T2: Inventariar Python, Node, pnpm, Docker/Compose, SO, arquitectura, memoria y límites del ejecutor. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P1T3: Leer AGENTS, fuentes y ADR; abrir un registro de decisiones nuevas con autor y motivo. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P1T4: Definir dos tenants ficticios, responsables humanos y repos fixture fuera de cualquier dato real. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P1T5: Fijar alcance Lite piloto, exclusiones, horarios y significado de observación continua frente a tareas programadas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P1T6: Crear rama de implementación y plantilla de evidencias con estados PASS, FAIL, BLOCKED y NOT_VERIFIED. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P1T7: Comprobar que ningún documento o UI atribuya protección, certificación o equivalencia empresarial todavía no demostradas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D1P1-TEST-1: Entorno sin Docker registra BLOCKED sin declarar pruebas runtime aprobadas.
- D1P1-TEST-2: Checkout con cambios ajenos se conserva y la implementación no los sobrescribe.

Rollback: Conservar el baseline y revertir únicamente archivos propios; no resetear repos ajenos.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
