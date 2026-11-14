# D6P1 — Aplicabilidad legal y controles de cumplimiento

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 6. Prioridad M0; rol Privacidad/cumplimiento.

## Objetivo
Producir evaluaciones con fuentes/rol/fecha y datos faltantes, no certificados automáticos.

## Artefactos previstos
- `agntia_ciberseguridad/compliance/applicability.py`
- `controls/catalog.json`
- `tests/unit/test_applicability.py`

## Contrato
Cada obligación tiene jurisdicción, rol, finalidad, versión, aplicabilidad revisada y evidencia; el LLM solo propone.

## Dependencias
D1P6

## Tareas originales
- D6P1T1: Modelar proveedor/deployerIA, responsable/encargadoRGPD, fabricanteCRA y sector sin inferirlos del nombre del cliente. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P1T2: Crear inventario de sistemas/modelos/datos/proveedores y preguntas mínimas de aplicabilidad. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P1T3: Versionar fuentes oficiales y fechas; cotejar cambios AI Act y textos que quedaron inaccesibles en investigación. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P1T4: Mapear controles técnicos a requisitos con owner y estados evidencia pendiente/presente/no revisada/revisada. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P1T5: Separar AI Act, RGPD, CRA, NIS2, DORA y ENS y no reutilizar plazos automáticamente entre regímenes. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P1T6: Probar casos aplicable/no aplicable/datos faltantes y cambios de versión con revisión humana. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D6P1T7: Entregar expediente de preparación con limitaciones y canal de revisión competente, sin sello de conformidad. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D6P1-TEST-1: Cliente sin finalidad/rol suficiente queda insufficient_information, no compliant.
- D6P1-TEST-2: Una fecha de guía contradice fuente normativa y bloquea automatización del plazo.

Rollback: Despublicar valoración y conservar fuente/versión previa y motivo; no borrar decisiones históricas.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
