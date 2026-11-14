# D6P6 — Reservas económicas y servicios comerciales

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 6. Prioridad M0; rol Coste/plataforma.

## Objetivo
Hacer efectivos los caps técnicos y no comprar servicios por precio aparente o trial automático.

## Artefactos previstos
- `agntia_ciberseguridad/billing/reservations.py`
- `agntia_ciberseguridad/billing/rates.py`
- `tests/integration/test_budget_concurrency.py`

## Contrato
Compromisos fijos+consumo+reservas+impuestos/FX no superan cap; contratación humana aparte.

## Dependencias
D3P1

## Tareas originales
- D6P6T1: Trasladar config/plans.json a ledger de céntimosEUR con compromisos, reservas, gasto y margen. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P6T2: Confirmar unidad por tenant/workspace, costes excluidos y asignación de infraestructura compartida. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P6T3: Versionar tarifas, impuestos, FX, mínimos y anualidades con origen/fecha y revisión. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P6T4: Reservar peor caso acotado antes del trabajo y reconciliar uso real/cancelación/proveedor tardío. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P6T5: Aplicar avisos y degradación de tareas opcionales sin desactivar autorización, aislamiento o audit. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P6T6: Probar concurrencia, crash, reversión de reserva, cuota deAPI y factura distinta a estimación. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P6T7: Revisar SaaS/MSSP/DPA y excluir VirusTotalPublic comercial; no comprar ni activar billing sin autorización. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D6P6-TEST-1: Dos llamadas concurrentes no consumen el mismo saldo ni elevan el cap al agotar cuota.
- D6P6-TEST-2: Tarifa/proveedor sin hard limit fiable queda bloqueado o usa margen explícito revisado.

Rollback: Deshabilitar nuevas llamadas pagadas y preservar reservas/conciliación; no activar upgrades.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
