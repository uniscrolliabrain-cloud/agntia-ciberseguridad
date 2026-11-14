# D7P4 — Hardening, rendimiento y recuperación

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 7. Prioridad M0; rol Revisor/SRE.

## Objetivo
Verificar fronteras y recuperación reales, no únicamente casos felices de aplicación.

## Artefactos previstos
- `tests/security/`
- `tests/performance/`
- `scripts/backup_restore_lab.py`
- `docs/implementation/RECOVERY-RESULTS.md`

## Contrato
Informe independiente de defectos críticos, capacidad medida y backups restaurados con claves.

## Dependencias
D7P3

## Tareas originales
- D7P4T1: Revisar bypass de auth, SSRF, rutas/archivos, injection en logs/reportes y límites de parser. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P4T2: Hacer pruebas de propiedades/fuzz acotadas sobre contratos, normalización y política con semillas guardadas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P4T3: Simular fallo de worker, DB, collector, DNS/proveedor y clave revocada durante operación. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P4T4: Ejecutar backup consistente de datos/evidencia/config y restaurar en entorno sintético separado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P4T5: Medir latencia/carga/CPU/RAM/disco y coste por los perfiles prometidos, con recursos y duración registrados. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P4T6: Revisar dependencias/licencias/SBOM del propio middleware y tratar findings propios igual que los del cliente. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D7P4T7: Bloquear release ante fuga tenant, ejecución no autorizada, secreto, pérdida de auditoría o gasto sin control. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D7P4-TEST-1: Pérdida de proceso/collector/DB temporal se recupera sin permitir acciones indebidas ni duplicar efectos.
- D7P4-TEST-2: Restauración reproduce scopes/evidencia y no requiere secretos publicados en Git.

Rollback: Congelar release, activar flagoff y restaurar copia verificada; no rebajar criterios para cumplir el calendario.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
