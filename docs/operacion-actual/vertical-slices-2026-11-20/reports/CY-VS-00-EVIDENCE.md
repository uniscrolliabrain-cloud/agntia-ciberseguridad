# CY-VS-00 — Evidencia

**Fecha:** 2026-11-20
**Base SHA:** `eaf7da0d60a5adc7302c977cdabdfd3900c922be`
**Rama:** `feat/cyber-vertical-slices-installable-20261120`

## Comandos ejecutados y salida

### 1. Estado de git y ramas

```
$ git status
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean

$ git rev-parse HEAD
eaf7da0d60a5adc7302c977cdabdfd3900c922be

$ git branch -a
* feat/cyber-vertical-slices-installable-20261120
  main
  remotes/origin/HEAD -> origin/main
  remotes/origin/docs/auditoria-y-plan-operativo-cyber-20261115
  remotes/origin/docs/cy-v2-connection-requirements
  remotes/origin/docs/cyber-bitacora-viva
  remotes/origin/docs/cyber-vertical-slices-handoff-20261120
  remotes/origin/docs/factory-recovery-v1-20261114
  remotes/origin/docs/hyperupdate-audit-20261115
  remotes/origin/docs/puesta-en-marcha-founder-operaciones-20261115
  remotes/origin/docs/roadmap-integracion-agente-20261115
  remotes/origin/feat/advlab-campaigns-C01-C18
  remotes/origin/feat/cognition-v2-sdk-ack
  remotes/origin/feat/cy-v2-01-baseline
  remotes/origin/feat/cyber-audit-2026-11-18
  remotes/origin/feat/cyber-autodoc-AD-01
  remotes/origin/feat/cyber-d1-foundation
  remotes/origin/feat/cyber-phases-06-10
  remotes/origin/feat/cyber-phases-10-15
  remotes/origin/feat/cyber-phases-16-20
  remotes/origin/feat/cyber-phases-21-25
  remotes/origin/feat/cyber-phases-26-30
  remotes/origin/feat/cyber-phases-31-35
  remotes/origin/feat/cyber-phases-36-40
  remotes/origin/feat/cyber-phases-41-42
  remotes/origin/feat/cyber-vs-00-baseline
  remotes/origin/feat/cyber-vs-01-contracts
  remotes/origin/feat/cyber-vs-01a-finding-contract
  remotes/origin/integration/advlab-hardening-20261115
  remotes/origin/work/advlab-B-vault-broker-release
  remotes/origin/work/advlab-D-operations
```

### 2. Validación de foundation

```
$ python scripts/validate_foundation.py
{"status": "PASS", "scope": "documentation, repository metadata and planned budget consistency only", "markdown_files": 327, "repository_metadata_records": 31, "security_scans_executed": 0, "words": 200654}
```

### 3. Ejecución de tests Python

```
$ python3 -m unittest discover tests/ -v
...
Ran 88 tests in 3.926s
FAILED (errors=44, skipped=8)
```

Desglose:
- 36 tests pass
- 8 tests skip (intencionales)
- 44 errors por `ModuleNotFoundError: No module named 'pydantic'` / `fastapi` (dependencias no instaladas en este entorno)

### 4. Análisis de ramas (merge-base y diff)

Las 26 ramas disjoint no comparten ancestro común con `main`, por lo que `git merge-base` retorna NONE y no se puede computar `git diff main...branch` automáticamente. Cada una requiere revisión manual.

Las 2 ramas con ancestro común:
- `origin/docs/cyber-vertical-slices-handoff-20261120`: merge-base = `eaf7da0` (main), 4 commits ahead, archivos: 4 docs de handoff
- `origin/feat/cyber-audit-2026-11-18`: merge-base = `eaf7da0` (main), 0 commits ahead/behind (mismo SHA)

## Archivos del repositorio (inventario)

Directorio `agntia_ciberseguridad/` (43 archivos .py + data/ + web/):
app.py, auth.py, config.py, contracts.py, errors.py, features.py, networking_policy.py, observability_routes.py, observability_schema.py, offline_database.py, releasecheck.py, reports.py, reviews.py, risk.py, safety.py, sbom.py, sbom_validation.py, scanning.py, service.py, snapshots.py, storage.py, util.py, workspace.py, cli.py

Subdirectorios: adapters/ (6 files), agents/ (10 files), billing/ (4 files), evidence/ (5 files), governance/ (8 files), jobs/ (6 files), runners/ (3 files), telemetry/ (8 files), web/ (3 files), data/cyclonedx/ (4 files)

## Conclusiones de evidencia

- El código fuente existe y está estructurado, pero no se pudo ejecutar la suite completa por dependencias faltantes.
- El SDK TypeScript no se pudo probar (no hay node/npm).
- 26 ramas tienen historia disjoint y requieren revisión manual.
- No se modificó ninguna rama existente.
- No se creó ningún archivo de código en esta campaña (solo documentación de reporte).