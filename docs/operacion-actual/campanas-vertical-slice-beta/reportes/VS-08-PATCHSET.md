# VS-08 — Patchset

**Base:** `6390b7e`.

| Archivo | Tipo | Motivo |
|---|---|---|
| `typescript/src/client.ts` | modify | `submitAudit` con `Idempotency-Key` en cabecera y `cancelJob` con revisión esperada |
| `typescript/test/client.test.mjs` | modify | Pruebas de ambos métodos y de sus rechazos |
| `reportes/VS-08-*.md` | add | Reporte, evidencia, propuesta y rollback |
| `reportes/BITACORA-VIVA.md` | modify | Entrada VS-08 |

`#request` acepta cabeceras extra; no se expone un cliente genérico. No se toca `/agente`, ni rutas,
ni contratos Pydantic.
