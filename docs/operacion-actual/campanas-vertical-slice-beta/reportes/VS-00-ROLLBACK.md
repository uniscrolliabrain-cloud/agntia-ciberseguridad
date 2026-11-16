# VS-00 — Rollback

## Alcance del cambio

Un archivo de código TypeScript (`typescript/src/client.ts`) y cinco documentos. No hay migraciones
de base de datos, ni cambios de contrato, ni despliegues.

## Procedimiento

```bash
git revert <commit-de-VS-00>
# alternativa: git checkout <base-sha> -- typescript/src/client.ts
cd typescript && npm run build && npm test
.venv/bin/python -m unittest discover -s tests
```

## Efecto esperado del rollback

- Vuelve el fallo del contract test en Node ≥ 22 con strip-only: el cliente TS no se puede cargar en
  ese modo. No afecta a Python ni al laboratorio.
- Los informes VS-00 desaparecen; no hay pérdida de evidencia histórica porque no modifican reportes
  previos.

## Compatibilidad

`CyberError` conserva constructor, campos y errores. Un rollback no rompe a consumidores que ya
usen `kind`, `status`, `retryable` o `correlationId`.
