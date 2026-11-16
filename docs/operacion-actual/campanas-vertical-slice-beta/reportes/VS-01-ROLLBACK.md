# VS-01 — Rollback

## Alcance

Esta campaña entrega **solo documentación**: reporte, mapa de contratos, evidencia y este rollback.
No hay cambios de código, esquema, migraciones ni configuración.

## Procedimiento

```bash
git revert <commit-de-VS-01>
```

o, si aún no se fusionó:

```bash
git branch -D feat/cyber-vs-01-contracts
```

## Efecto

Ninguno sobre el runtime. Los contratos y la persistencia quedan exactamente como en `main`
(`2da922f`). Si en el futuro se aplican los deltas recomendados (`AuditEventV1`,
`RetestRequestV1`, corrección de `causation_id`), su rollback exigirá migración propia y quedará
documentado en la campaña correspondiente.
