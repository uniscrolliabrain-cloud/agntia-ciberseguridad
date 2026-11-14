# D7P3 — E2E de dos tenants y recorridos de referencia

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 7. Prioridad M0; rol QA/E2E.

## Objetivo
Demostrar el middleware real en su alcance, sin sumar capacidades M1 no ejecutadas.

## Artefactos previstos
- `tests/e2e/`
- `scripts/demo_synthetic.py`
- `docs/implementation/E2E-RESULTS.md`

## Contrato
Fixtures deterministas, versiones/digests y evidencias enlazadas; cada escenario reporta PASS/FAIL/BLOCKED.

## Dependencias
D3P6, D4P6, D5P5, D5P6, D6P2, D6P6, D7P1

## Tareas originales
- D7P3T1: Ejecutar AppSec snapshot→tools reales→findings→revisión→reporte con fixture vulnerable y benigno. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P3T2: Ejecutar agent→gateway→policy→egress→denegación y una tarea legítima completa. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P3T3: Comprobar export de evidencia, trazas, métricas y logs sin canarios ni acceso cruzado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P3T4: Ensayar replay concurrente, revocación, grant caducado y manifest cambiado durante trabajo. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P3T5: Verificar cumplimiento insufficient_information y presupuesto agotado sin aparentar cobertura completa. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P3T6: Ejecutar escenarios M1 solo si sus gates pasaron y marcar el resto explícitamente diferido. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P3T7: Grabar demo y reporte reproducible con comandos/SHAs; no narrar acciones que no constan en backend. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D7P3-TEST-1: Dos tenants, canarios y grants cruzados no contaminan reportes/artefactos/eventos.
- D7P3-TEST-2: Una tarea legítima se completa y una salida adversarial se bloquea aun con modelo hostil.

Rollback: Revocar fixtures, detener admisión y conservar evidencia sanitizada; no usar datos de clientes para salvar el gate.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
