# D2P4 — OSV, inventario de dependencias y SBOM

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 2. Prioridad M0; rol AppSec supply chain.

## Objetivo
Relacionar componentes y advisories con evidencia y frescura, sin afirmar explotación por versión.

## Artefactos previstos
- `agntia_ciberseguridad/adapters/osv.py`
- `agntia_ciberseguridad/sbom.py`
- `fixtures/dependencies/`
- `tests/contracts/test_osv.py`

## Contrato
Componente identificado por ecosistema/purl/versión/hash; advisory con fuente/fecha y cobertura de lockfile.

## Dependencias
D2P1, D2P2

## Tareas originales
- D2P4T1: Elegir release OSV-Scanner, modo offline/online permitido y fuentes/cache con límites. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P4T2: Modelar componentes, purl, licencias observadas y relaciones directas/transitivas con valor unknown permitido. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P4T3: Generar o importar SBOM CycloneDX/SPDX con esquema y tamaño validados; fijar herramienta productora. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P4T4: Asociar advisory, versión afectada, fix disponible y fecha de datos sin inventar reachability. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P4T5: Probar fixtures de lockfiles, rango ambiguo, ecosistema ausente y paquetes sin versión exacta. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P4T6: Ejecutar scanner real y validar reproducibilidad y comportamiento offline/cache obsoleta. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P4T7: Exportar diferencias entre snapshots y distinguir paquete corregido de componente simplemente no analizado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D2P4-TEST-1: Un lockfile vulnerable y otro benigno producen resultados esperados sin instalar paquetes del cliente.
- D2P4-TEST-2: DB sin red/caducada o ecosistema no soportado produce partial/stale, no safe.

Rollback: Retener SBOM y anterior snapshot de DB; deshabilitar la interpretación incompatible sin borrar findings.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
