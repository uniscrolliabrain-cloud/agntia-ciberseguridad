# D7P2 — Interfaz operativa y experiencia humana

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 7. Prioridad M1; rol Frontend/UX.

## Objetivo
Permitir revisar evidencia, cobertura y propuestas desde móvil/escritorio sin ocultar incertidumbre.

## Artefactos previstos
- `web/`
- `tests/browser/`
- `docs/implementation/UX-ACCEPTANCE.md`

## Contrato
UI propia de piloto o vistas integrables; AgntiaPro final requiere wiring separado, no se finge existente.

## Dependencias
D7P1

## Tareas originales
- D7P2T1: Diseñar bandeja de riesgos, activos, cobertura, jobs, policy, evidencias, presupuesto y propuestas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P2T2: Mostrar fuentes/periodo/estado y distinguir findings confirmados, sospechados, aceptados y no probados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P2T3: Crear diff/aprobación humana clara con destino, impacto, hash y caducidad. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P2T4: Añadir navegación finding→evidencia→trace con revalidación de acceso y datos minimizados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P2T5: Adaptar controles a móvil, teclado/accesibilidad y estados vacíos/error sin contenido activo externo. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P2T6: Probar login, cambio de tenant, descarga, edición concurrente, revisión y permisos en navegador. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P2T7: Entregar componentes/contratos a AgntiaPro sin introducir detalles del ERP o herramientas como decisiones innecesarias del cliente. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D7P2-TEST-1: Usuario cambia de tenant y no conserva datos/caché del anterior.
- D7P2-TEST-2: Vista parcial/stale o presupuesto agotado no muestra un indicador global seguro/verde.

Rollback: Desactivar vistas defectuosas y usar reportes/JSON scoped; mantener API privada.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
