# Ownership de ficheros — programa AD

Regla: **un escritor por superficie y por iteración.** Si dos campañas necesitan el mismo fichero,
la segunda espera, rebasa y documenta el conflicto en su reporte. Ninguna campaña escribe fuera de
su fila sin ADR aprobado.

## 1. Superficies compartidas (serializadas)

| Superficie | Dueño | Regla |
|---|---|---|
| `agntia_ciberseguridad/storage.py` | AD-03 (migración 9) y AD-12 (posterior) | Una migración por campaña, nunca dos en paralelo; backup/restore y prueba de upgrade obligatorias |
| `agntia_ciberseguridad/app.py` | AD-11 | Solo registro de rutas read-only nuevas |
| `agntia_ciberseguridad/features.py` | AD-11 | Solo endpoints nominados; sin flags implícitos |
| `agntia_ciberseguridad/events/outbox.py` | AD-03 | Extender allowlist y proyección; prohibido segundo bus |
| `agntia_ciberseguridad/jobs/worker.py` | AD-03 y AD-05 | AD-03 lifecycle; AD-05 solo captura de entorno |
| `agntia_ciberseguridad/evidence/vault.py` | AD-04 | Reusar AES-GCM, 2 MiB, hold y retención |
| `agntia_ciberseguridad/agents/flows.py` | AD-10 | Solo interfaz tipada; sin egress nuevo |
| `scripts/export_schemas.py` | AD-02 y AD-11 | AD-02 contratos; AD-11 añade lectura |
| `typescript/src/client.ts` | AD-11 | Server-only, sin publish |
| `typescript/build-runtime.mjs` | AD-01 | Reparado; cambios requieren justificar compatibilidad Node ≥22 |
| `.github/workflows/*` | AD-14 | Pin de actions y permisos mínimos |

## 2. Superficies nuevas por campaña

| Campaña | Directorio/fichero nuevo | Estado |
|---|---|---|
| AD-01 | `docs/autodoc/BASELINE-AUDIT.md`, `FILE-OWNERSHIP.md`, `TRACEABILITY.md`, `tests/autodoc/test_baseline_inventory.py` | Creado |
| AD-02 | `agntia_ciberseguridad/autodoc/{contracts,claims}.py`, `tests/unit/test_autodoc_contracts.py` | Pendiente |
| AD-03 | `agntia_ciberseguridad/autodoc/capture.py`, `tests/integration/test_autodoc_capture.py` | Pendiente |
| AD-04 | `autodoc/{evidence_index,sealing}.py`, `tests/security/test_autodoc_evidence.py` | Pendiente |
| AD-05 | `autodoc/{environment,provenance}.py` | Pendiente |
| AD-06 | `benchmarks/cyber-evidence/**` | Pendiente |
| AD-07–AD-09 | evaluación, métricas y paquete de informe | Pendiente |
| AD-10 | `autodoc/{claim_checker,draft}.py` | Pendiente |
| AD-11 | `autodoc/routes.py`, `typescript/test/autodoc.test.mjs` | Pendiente |
| AD-12 | `autodoc/{publication,publication_schema}.py`, `docs/publications/REVIEW-POLICY.md` | Pendiente |
| AD-13 | `docs/publications/templates/**` | Pendiente |
| AD-14 | `scripts/autodoc_{validate,generate}.py`, `.github/workflows/autodoc.yml` | Pendiente |
| AD-15 | `scripts/autodoc_e2e.py`, `tests/e2e/test_autodoc_pipeline.py` | Pendiente |

## 3. Zonas prohibidas sin autorización explícita

- `/agente` (repo padre) y cualquier ruta fuera de este repositorio.
- `docs/release/status.json`: solo se modifica si la implementación real supera gates; nunca por
  progreso de campaña AD.
- Producción, publicación externa, datos de clientes y escaneo de terceros.
- Secretos: no se escriben en ficheros versionados ni en logs.
