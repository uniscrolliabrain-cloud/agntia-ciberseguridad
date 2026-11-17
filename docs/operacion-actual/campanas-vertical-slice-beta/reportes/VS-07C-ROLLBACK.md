# VS-07C — Rollback

1. `git rm docs/operacion-actual/campanas-vertical-slice-beta/RUNBOOK-ALERTAS.md`
2. Eliminar el enlace desde la bitácora y desde `VS-07C-REPORT.md` si se retira también el informe.
3. `python scripts/validate_foundation.py` → vuelve a 292 Markdown (293 − 1) y sigue en PASS.

## Efecto

- El procedimiento deja de existir; VS-07 vuelve a tener alertas sin runbook (P4 abierto).
- Nada operativo cambia: no hay reglas, métricas, endpoints ni datos afectados.
- Los acuses JSONL de simulacros anteriores son evidencia y no se borran con este rollback.
