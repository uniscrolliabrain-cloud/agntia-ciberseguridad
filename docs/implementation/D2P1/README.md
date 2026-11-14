# D2P1 — Adquisición de snapshots sin ejecutar código

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 2. Prioridad M0; rol AppSec/ingestión.

## Objetivo
Obtener código y artefactos autorizados con procedencia sin convertir su importación en ejecución.

## Artefactos previstos
- `agntia_ciberseguridad/snapshots.py`
- `agntia_ciberseguridad/artifact_limits.py`
- `tests/security/test_ingestion.py`

## Contrato
Un snapshot contiene commit/hash, grant, límites y cadena de custodia; hooks/submodules/postinstall no se ejecutan.

## Dependencias
D1P6

## Tareas originales
- D2P1T1: Definir entradas Git/local/image/lockfile y permisos mínimos separados para su adquisición. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P1T2: Fijar commits/digests y verificar tamaño, número de ficheros, rutas canónicas y tipos antes de extraer. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P1T3: Deshabilitar hooks, recursion de submódulos, filtros y descargas LFS no aprobadas durante checkout. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P1T4: Controlar enlaces, traversal, archivos especiales, compresión y ficheros binarios; no seguir enlaces fuera del snapshot. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P1T5: Guardar inventario/hash/manifiesto del snapshot sin copiar secretos a logs o títulos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P1T6: Probar repos hostiles sintéticos y cancelación durante adquisición sin ejecución ni fuga fuera de scope. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P1T7: Registrar cobertura y exclusiones por fichero/lenguaje para que la auditoría no invente análisis completo. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D2P1-TEST-1: Repo fixture con hooks, enlaces simbólicos y rutas escapadas no toca el host.
- D2P1-TEST-2: Zip bomb, LFS/submódulo externo o fichero excesivo queda rechazado o explícitamente parcial.

Rollback: Eliminar solo workspaces temporales propios; preservar referencias y error, no archivos del cliente.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
