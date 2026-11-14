# D5P6 — Revocación, kill switch y aprobación de efectos

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 5. Prioridad M0; rol Seguridad/operación.

## Objetivo
Parar nuevas acciones de un agente comprometido y distinguir efectos ya aceptados por terceros.

## Artefactos previstos
- `agntia_ciberseguridad/agents/revocation.py`
- `agntia_ciberseguridad/approvals.py`
- `tests/security/test_kill_switch.py`

## Contrato
Revocación efectiva en todos los gateways; propuesta/approval ligados a recurso, hash, caducidad y principal vigente.

## Dependencias
D5P1, D5P2

## Tareas originales
- D5P6T1: Implementar revocación por agente, tool, grant y tenant con versión comprobada en cada efecto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P6T2: Diseñar aprobación humana de diff/hash/objetivo/coste y evitar autoaprobación del agente proponente. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P6T3: Aplicar idempotencia y reservation antes de efectos y conservar estado reconciliation_required. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P6T4: Crear panel/CLI de emergencia con autenticación reforzada, alcance y motivo auditado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P6T5: Inventariar caminos fuera del gateway y bloquear la habilitación si permiten bypass. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P6T6: Probar revocación concurrente, caché antigua, replay de aprobación y efecto ya confirmado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D5P6T7: Documentar playbook de parada/recuperación con tiempos medidos y límites reales de cancelación. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D5P6-TEST-1: Agente revocado entre dos llamadas no ejecuta la segunda por caché o lease antiguo.
- D5P6-TEST-2: Timeout tras efecto externo se reconcilia; el kill switch no promete deshacerlo mágicamente.

Rollback: Mantener denegación y registrar efectos en vuelo para conciliación/rollback aprobado.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
