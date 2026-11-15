# Cierre de ramas legacy — inventario y operación pendiente

Fecha: 2026-11-15. Estado: PR legacy #2–#9 cerradas; PR #12 fusionada; todas las ramas de abajo verificadas con `ahead_by=0` contra `main` después de integrar el plan CY-V2. **Las ramas NO han sido eliminadas remotamente** porque el conector GitHub disponible no expone delete-ref. No interpretar PR cerrada como rama borrada.

## Ramas aptas para limpieza (previa revalidación)

- `docs/factory-recovery-v1-20261114` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15
- `docs/roadmap-integracion-agente-20261115` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15
- `feat/cyber-d1-foundation` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15
- `feat/cyber-phases-06-10` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15
- `feat/cyber-phases-10-15` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15
- `feat/cyber-phases-16-20` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15
- `feat/cyber-phases-21-25` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15
- `feat/cyber-phases-26-30` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15
- `feat/cyber-phases-31-35` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15
- `feat/cyber-phases-36-40` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15
- `feat/cyber-phases-41-42` — sin commits exclusivos respecto a `main` en la comprobación del 2026-11-15

## Procedimiento seguro para el operador con permisos

1. Revalidar `git fetch --prune origin` y comparar `origin/main...origin/<rama>`; exigir cero commits ahead y comprobar que no exista PR abierta ni protección aplicable.
2. Eliminar únicamente la referencia remota validada, una por una, mediante interfaz GitHub o `git push origin --delete <rama>`; **no** usar force-push ni borrar `main`.
3. Registrar resultado y SHA de `main` en este documento o reporte; si cambia alguna rama, detenerse y revisar antes de borrar.
4. Conservar PRs, commits, informes y las 42 fases históricas como trazabilidad. Abrir nuevas ramas CY-V2 desde HEAD de `main`.

El plan de 42 campañas está en `docs/campanas-cy-v2/PROGRAMA-42-CAMPANAS-FREEBUFF.md`. Estado de producto: demo sintética, no producción.
