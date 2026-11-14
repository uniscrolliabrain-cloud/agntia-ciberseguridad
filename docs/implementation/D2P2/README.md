# D2P2 — Runner y sandbox de herramientas

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 2. Prioridad M0; rol Plataforma/sandbox.

## Objetivo
Ejecutar herramientas fijadas con límites y sin credenciales globales del host.

## Artefactos previstos
- `agntia_ciberseguridad/runners/base.py`
- `agntia_ciberseguridad/runners/container.py`
- `infra/scanners/`
- `tests/security/test_runner.py`

## Contrato
El adaptador escoge binario/perfil permitido; no recibe shell libre ni Docker socket en el worker.

## Dependencias
D1P6

## Tareas originales
- D2P2T1: Definir interfaz runner con argv cerrado, entorno permitido, entrada read-only y salida acotada. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P2T2: Fijar herramientas por versión/digest, procedencia y licencia; registrar reglas y DB como artefactos distintos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P2T3: Aplicar UID no privilegiado, FS temporal, límites CPU/RAM/pids/tiempo y no-new-privileges. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P2T4: Separar workers sin red y descarga controlada de bases; no pasar tokens de GitHub al scanner. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P2T5: Validar códigos de salida, stdout/stderr, cancelación y limpieza sin reutilizar workspaces entre tenants. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P2T6: Probar límites y accesos host/network en el runtime real, no solamente con mocks. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D2P2T7: Marcar BLOCKED si no hay sandbox suficiente; no usar ejecución host insegura como fallback. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D2P2-TEST-1: Un proceso que intenta red/archivo fuera de política no accede al host ni a secretos.
- D2P2-TEST-2: Timeout, fork excesivo o salida gigante produce fallo controlado y limpieza comprobada.

Rollback: Matar sandbox identificado, revocar su lease y conservar evidencia minimizada; no kill global de procesos.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
