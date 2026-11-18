# VS-03 — Rollback

## Alcance

Solo documentación. No hay cambios de código, configuración, variables de entorno ni credenciales.

## Procedimiento

```bash
git revert <commit-de-VS-03>
```

## Efecto

Ninguno sobre el runtime ni sobre el gestor de secretos, que no se tocó. Las referencias de
`config.py` y la autenticación quedan exactamente como en `6677899`.
