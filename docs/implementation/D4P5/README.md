# D4P5 — Ingestión de eventos y conectores pasivos

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 4. Prioridad M1; rol Detección/telemetría.

## Objetivo
Recibir señales de sistemas autorizados sin instalar agentes privilegiados de forma indiscriminada.

## Artefactos previstos
- `agntia_ciberseguridad/events/ingest.py`
- `agntia_ciberseguridad/events/normalize.py`
- `tests/contracts/test_event_ingest.py`

## Contrato
Fuente autenticada, schema versionado, reloj/procedencia, deduplicación y cuotas por tenant.

## Dependencias
D4P3, D3P3

## Tareas originales
- D4P5T1: Definir fuentes piloto webhook/archivo/OTel y mapeo de autenticación a tenant y entorno. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P5T2: Validar tamaño, timestamps, tipo, versión y firma/audiencia del productor. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P5T3: Crear normalización común con observación original referenciada y campos unknown. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P5T4: Implementar deduplicación, cursores y backpressure con contadores de rechazo/drops visibles. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P5T5: Proponer adaptadores Wazuh/Falco/cloud solo como perfiles específicos con licencia/privilegios revisados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P5T6: Probar replay, fuente comprometida sintética, reloj desviado y cola llena sin fuga o falsas confirmaciones. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P5T7: Reportar cobertura real de sensores: sin telemetría endpoint no se anuncia XDR/EDR completo. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D4P5-TEST-1: Evento repetido, adelantado o fuera de orden conserva historia sin duplicar incidente.
- D4P5-TEST-2: Un payload que declara tenantB con credencialA se rechaza sin persistir contenidoB.

Rollback: Revocar fuente y detener nueva ingestión; mantener watermark y artefactos previos.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
