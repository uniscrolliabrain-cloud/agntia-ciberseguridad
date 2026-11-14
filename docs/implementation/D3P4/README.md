# D3P4 — Custodia, redacción y cadena de evidencia

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 3. Prioridad M0; rol Privacidad/evidencia.

## Objetivo
Guardar artefactos verificables y minimizados sin convertir reportes en otra fuga de información.

## Artefactos previstos
- `agntia_ciberseguridad/evidence/vault.py`
- `agntia_ciberseguridad/evidence/redaction.py`
- `tests/security/test_evidence_isolation.py`

## Contrato
Original cifrado y referencia; vista redactada revisable; políticas de acceso y retención por artefacto.

## Dependencias
D1P6

## Tareas originales
- D3P4T1: Definir custodio, clasificación, base/retención, legal hold y quién puede consultar cada evidencia. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P4T2: Implementar almacenamiento cifrado con checksum, tamaño, MIME y rutas seguras, sin claves en DB. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P4T3: Separar original, extracto redactado y resumen; marcar redacción automática como falible. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P4T4: Crear exportadores con escape HTML/CSV/PDF y protección de contenido activo e instrucciones incrustadas. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P4T5: Encadenar eventos de acceso/cambio y diseñar checkpoint firmado externo al proceso principal. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P4T6: Probar cross-tenant, sentinelas, corruptos, extensión falsa, retención y restauración con claves. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D3P4T7: Registrar límites forenses y de anonimización: hash/redacción no son certificación de verdad ni privacidad absoluta. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D3P4-TEST-1: Canarios secretos ausentes de logs/export/eventos y un tenant no descarga evidencia ajena.
- D3P4-TEST-2: Clave perdida/alteración de fichero produce error de integridad, no original falso o vacío.

Rollback: Parar exportaciones, preservar custodia y restaurar claves/copia probada; no destruir originales para ocultar filtración.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
