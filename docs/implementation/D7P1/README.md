# D7P1 — SDK TypeScript/Hono y contrato hacia /agente

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 7. Prioridad M0; rol Integración.

## Objetivo
Entregar herramientas de negocio y un consumidor simulado listo para wiring revisable.

## Artefactos previstos
- `typescript/src/client.ts`
- `typescript/src/hono.ts`
- `typescript/src/agent-tools.ts`
- `tests/contracts/test_python_ts.py`
- `docs/integration/PATCHSET-AGENTE.md`

## Contrato
Cliente servidor tipado con allowlist exacta; no tokens en navegador ni proxy shell/HTTP libre.

## Dependencias
D3P6, D5P6

## Tareas originales
- D7P1T1: Leer interfaces del repo madre solo cuando estén disponibles/autorizadas y documentar supuestos restantes. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P1T2: Crear DTOs y validadores runtime para assets/audits/jobs/findings/policy/reportes. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P1T3: Implementar timeouts, errores normalizados, paginación y headers servidor de correlación. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P1T4: Añadir router Hono de métodos/paths cerrados con principal/tenant derivados del servidor. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P1T5: Exponer catálogo de tools limitado y pruebas de que no incluye aprobación/privilegios/shell. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P1T6: Implementar outbox/event schemas/ACK y consumidor sintético con deduplicación durable. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P1T7: Entregar patchset propuesto para /agente; aplicarlo allí únicamente tras aprobación expresa. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D7P1-TEST-1: ClienteTS y API coinciden en errores, estados y validación de entradas desconocidas.
- D7P1-TEST-2: Tool agéntica no puede aprobar, elevar permisos, cambiar presupuesto o ejecutar comandos arbitrarios.

Rollback: Retirar SDK/route nueva conservando contratos anteriores; no modificar repo madre para forzar compatibilidad.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
