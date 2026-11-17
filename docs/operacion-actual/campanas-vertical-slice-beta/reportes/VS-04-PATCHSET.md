# VS-04 — Patchset

**Base:** `9b889ab`.

## Cambios

| Archivo | Tipo |
|---|---|
| `reportes/VS-04-REPORT.md` | add |
| `reportes/VS-04-EVIDENCE.md` | add |
| `reportes/VS-04-PATCHSET.md` | add |
| `reportes/VS-04-ROLLBACK.md` | add |
| `reportes/BITACORA-VIVA.md` | modify |

## Código

Ninguno. Implementar backup externo exige elegir proveedor y gestionar credenciales; hacerlo con
disco local habría repetido el laboratorio y simulado una recuperación que no existe.

## Deltas propuestos

1. `key_version` en metadatos de evidencia (middleware).
2. Interfaz de almacén externo con prefijo por tenant y hash obligatorio.
3. Manifiesto de backup y restore verificado, con RPO/RTO medidos.
