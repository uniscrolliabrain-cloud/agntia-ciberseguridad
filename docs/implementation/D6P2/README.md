# D6P2 — Privacidad, retención y brechas de datos

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 6. Prioridad M0; rol Privacidad/seguridad.

## Objetivo
Comprobar protección de datos del propio middleware y preparar incidentes sin notificar automáticamente.

## Artefactos previstos
- `agntia_ciberseguridad/privacy/retention.py`
- `agntia_ciberseguridad/privacy/breach_case.py`
- `tests/security/test_privacy_lifecycle.py`

## Contrato
Datos minimizados/scoped, DPA y proveedores registrados; reloj de constancia y evaluación humana diferenciada.

## Dependencias
D3P4, D6P1

## Tareas originales
- D6P2T1: Inventariar datos, finalidades, bases, subencargados, regiones, transferencias y retenciones del servicio. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P2T2: Implementar vistas minimizadas y acceso por necesidad con registro de lectura/descarga. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P2T3: Diseñar export/borrado/restricción y legal hold con autorización y reconciliación de backups. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P2T4: Crear expediente de brecha con detección, constancia, afectados, riesgo y responsable de decisión. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P2T5: Distinguir deber del encargado al responsable y eventual notificación/comunicación por régimen aplicable. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P2T6: Probar retención, restauración, claves y centinelas en prompts/export/proveedores. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P2T7: Actualizar documentación de privacidad del piloto y registrar pendientes jurídicos antes de usar datos reales. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D6P2-TEST-1: Borrado o export deA no incluye evidencia deB ni destruye legal hold vigente.
- D6P2-TEST-2: Una alerta técnica sin datos personales no dispara automáticamente notificaciónRGPD.

Rollback: Suspender export o purga, preservar evidencias bajo acceso limitado y escalar al responsable.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
