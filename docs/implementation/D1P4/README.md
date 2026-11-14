# D1P4 — Persistencia, migraciones y auditoría

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 1. Prioridad M0; rol Datos/evidencia.

## Objetivo
Crear estado durable con constraints de aislamiento, historia y recuperación antes de ejecutar trabajos.

## Artefactos previstos
- `agntia_ciberseguridad/storage.py`
- `agntia_ciberseguridad/migrations/`
- `agntia_ciberseguridad/audit.py`
- `tests/integration/test_migrations.py`

## Contrato
Persistencia inicial explícita; SQLite limitado a piloto de un nodo o PostgreSQL con mismas invariantes probadas.

## Dependencias
D1P2

## Tareas originales
- D1P4T1: Escoger backend piloto y documentar límites de concurrencia, topología y evolución futura a PostgreSQL. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P4T2: Crear tablas tenant-scoped con FKs compuestas, índices, revisiones e identidades externas e idempotentes. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P4T3: Implementar migraciones versionadas, backup previo, transacción y bloqueo para dos procesos inicializando a la vez. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P4T4: Añadir audit append-only con actor, política, correlación, hash y referencia de resultado minimizado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P4T5: Separar historial de findings/propuestas de vistas actuales y definir checkpoints externos para integridad reforzada. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P4T6: Ensayar fresh, upgrade, fallo intermedio, restauración y verificación de cadena con evidencia alterada. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D1P4T7: Medir contención y registrar limitaciones del almacenamiento sin anunciar soporte distribuido no probado. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D1P4-TEST-1: Una migración fallida revierte DDL y preserva objetos/auditoría previos.
- D1P4-TEST-2: Dos escrituras concurrentes con la misma identidad no crean dos objetos ni reservas.

Rollback: Recuperar copia consistente y conservar historial de migración; sin downgrade destructivo automático.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
