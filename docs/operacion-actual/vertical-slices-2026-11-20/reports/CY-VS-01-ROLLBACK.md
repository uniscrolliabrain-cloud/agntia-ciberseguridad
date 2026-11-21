# CY-VS-01 — Rollback

**Fecha:** 2026-11-20
**Base SHA:** `eaf7da0d60a5adc7302c977cdabdfd3900c922be`
**Rama:** `feat/cyber-vertical-slices-installable-20261120`

## Cambios realizados en esta campaña

Solo se agregó un archivo de documentación (manifiesto de capacidades). No se modificó código fuente, no se cambió configuración, no se alteró base de datos ni esquemas.

| Archivo | Acción |
|---------|--------|
| `docs/implementation/schemas/cyber-capabilities.v1.json` | Creado |

## Procedimiento de rollback

```bash
# Volver a main
git switch main

# Eliminar la rama de trabajo (descarta todos los cambios de CY-VS-00 y CY-VS-01)
git branch -D feat/cyber-vertical-slices-installable-20261120
```

O, para conservar la rama pero descartar solo los cambios de CY-VS-01:

```bash
git switch feat/cyber-vertical-slices-installable-20261120
git rm docs/implementation/schemas/cyber-capabilities.v1.json
git commit -m "docs(cyber-vs): revert CY-VS-01 cyber-capabilities manifest"
```

## Migraciones de base de datos

Ninguna. No se tocó el esquema de SQLite.

## Compatibilidad

No aplica — no se modificó código existente. Toda la API, SDK y contratos permanecen sin cambios.

## Riesgos residuales

Ninguno de código. El gate de instalación (`npm pack`, artefacto reproducible) está bloqueado por falta de Node.js en este entorno, no por código.

## Siguiente campaña

CY-VS-02 — Identidad, tenancy y delegación.