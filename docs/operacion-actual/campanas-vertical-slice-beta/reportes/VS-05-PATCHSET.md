# VS-05 — Patchset

**Base:** `24bd252`.

| Archivo | Tipo | Motivo |
|---|---|---|
| `tests/integration/test_jobs.py` | modify | Cancelación en vuelo sin resultado persistido |
| `typescript/src/client.ts` | restore | Fix de `CyberError` de VS-00 para pasar el contract test |
| `reportes/VS-05-*.md` | add | Reporte, evidencia, patchset y rollback |
| `reportes/BITACORA-VIVA.md` | modify | Entrada VS-05 |

Sin cambios en `jobs/store.py`, `worker.py` ni esquema: el comportamiento era correcto y la campaña
pedía probarlo.
