# VS-06 — Patchset

**Base:** `008aaeb`.

| Archivo | Tipo |
|---|---|
| `reportes/VS-06-*.md` | add |
| `reportes/BITACORA-VIVA.md` | modify |

Sin cambios de código, pins ni workflows: el intento de upgrade se revirtió al demostrar que rompe
la propagación de trazas, y añadir `pip-audit` a CI con CVE abiertos dejaría el pipeline en rojo
permanente. El gate ya falla cerrado en producción.
