# D1P6 — Threat model y revisión de fronteras

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 1. Prioridad M0; rol Revisión de seguridad independiente.

## Objetivo
Fijar lo que debemos resistir y los casos de parada antes de instalar scanners o procesar repos hostiles.

## Artefactos previstos
- `docs/implementation/THREAT-MODEL.md`
- `docs/implementation/TRUST-BOUNDARIES.md`
- `tests/security/scenario_catalog.json`

## Contrato
Cada efecto tiene frontera, autoridad y escenario de fallo; scanner y LLM se consideran procesos no confiables.

## Dependencias
D1P3, D1P4, D1P5

## Tareas originales
- D1P6T1: Enumerar activos sensibles, adversarios, control del host, proveedor comprometido y amenazas fuera de alcance. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P6T2: Dibujar flujos de código, secretos, prompts, evidencias, telemetría y certificados de confianza. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P6T3: Asignar control/owner a aislamiento, egress, aprobaciones, supply chain, presupuestos y disponibilidad. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P6T4: Crear catálogo de escenarios críticos y separar seguridad frente a prompts de compromiso del servidor. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P6T5: Definir stop conditions para fuga tenant, ejecución arbitraria, secreto, pérdida de evidencia o gasto sin margen. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P6T6: Realizar revisión cruzada del día1 y documentar defectos, aceptación temporal y pruebas pendientes. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P6T7: Emitir gateG1: ninguna ruta de alto impacto habilitada si falta autenticación, scope o persistencia probados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D1P6-TEST-1: Cada frontera crítica tiene al menos un caso benigno y uno adversarial planificado.
- D1P6-TEST-2: El revisor identifica bypass del gateway o socket privilegiado y bloquea la habilitación.

Rollback: Volver a modo documental/admisión denegada hasta corregir fronteras; no ocultar exclusiones.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
