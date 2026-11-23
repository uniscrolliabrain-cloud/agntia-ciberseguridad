# CY-VS-01 — Evidencia

**Fecha:** 2026-11-20
**Base SHA:** `eaf7da0d60a5adc7302c977cdabdfd3900c922be`
**HEAD SHA:** `52855ea...`
**Rama:** `feat/cyber-vertical-slices-installable-20261120`

## Comandos ejecutados

No se ejecutaron comandos de instalación (no hay `node`/`npm` en este entorno). Se verificó la estructura de archivos existentes.

## Archivos reutilizados (F0–F2, sin modificación)

| Archivo | Líneas | Propósito |
|---------|--------|-----------|
| `agntia_ciberseguridad/install.py` | ~230 | InstallManifest modelo, verify(), provenance_digest(), sha256_file() |
| `scripts/install_manifest.py` | ~85 | CLI build/check para manifiestos de instalación |
| `scripts/verify_artifact.py` | ~28 | CLI verify de artefacto contra manifiesto y provenance |
| `docs/implementation/schemas/InstallManifest.json` | ~75 | JSON Schema para InstallManifest |
| `typescript/PROVENANCE.json` | ~18 | Provenance de @agntia/ciberseguridad@0.1.0-alpha.3 |
| `typescript/package.json` | ~34 | Package SDK: name, version 0.1.0-alpha.3, exports, scripts |

## Nuevo archivo creado

| Archivo | Tamaño | Contenido |
|---------|--------|-----------|
| `docs/implementation/schemas/cyber-capabilities.v1.json` | ~335 líneas | Contrato de capacidades: 13 capacidades, sideEffects, scopes, risk, approvals, input/output, idempotency, timeouts, error codes, feature flags, fail-closed |

## Validación JSON

El archivo `cyber-capabilities.v1.json` se escribió mediante el editor en 3 operaciones. Cada operación fue exitosa, indicando que el archivo se creó correctamente. La validación programática con `json.load()` no se pudo ejecutar por limitaciones del entorno de terminal (comandos Python tardan >300s).

## BLOCKED_FOUNDER

**Acción:** Instalar Node.js >=22 y ejecutar en `typescript/`:
```
npm run build && npm run pack:deterministic
```
Verificar que dos ejecuciones producen el mismo SHA256 del tarball (artefacto reproducible).

**Por qué está bloqueado:** No hay `node`/`npm` disponibles en este entorno de ejecución. No es un bloqueo de código, es un bloqueo de entorno.

## Decisiones

- No se modificó ningún archivo existente.
- No se creó código de instalación nuevo (F0–F2 ya existen).
- `cyber-capabilities.v1.json` es un documento de contrato declarativo, no código ejecutable.
- `docs/release/status.json` se mantiene NO-GO.