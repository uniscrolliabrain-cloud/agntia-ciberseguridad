# VS-08 — Evidencia

**Base:** `6390b7e`.

| Comprobación | Comando | Resultado |
|---|---|---|
| Rutas de auditoría | `grep -n "@app\\.\\(get\\|post\\)" agntia_ciberseguridad/app.py` | preview, audits, jobs, cancel, findings, historial, integridad |
| Rutas de evidencia/grants | mismo grep filtrado | assets, grants, approve, revoke, snapshots |
| SDK | `sed -n '17,70p' typescript/src/client.ts` | 9 métodos; sin submit, cancel, evidencia ni retest |
| Retest | búsqueda en rutas | sin endpoint |

No se accedió al repositorio `/agente` en ningún momento.
