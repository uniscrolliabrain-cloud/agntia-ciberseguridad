# D4P4 — Dashboards y navegación de investigación

**SCAFFOLD ORIGINAL PRESERVADO / NOT_STARTED / NOT_EXECUTED.** [Manifest original](../../campaigns/2026-11-10-seven-days/campaign.json) · [Flow](../../factory/01-PIPELINE.md) · [ADTC](../../factory/03-TRACE-OBSERVABILITY.md). Día original: 4. Prioridad M1; rol Producto/SRE.

## Objetivo
Dar contexto operativo comparable al patrón de plataformas líderes sin exigir toda su infraestructura.

## Artefactos previstos
- `infra/observability/dashboards/`
- `agntia_ciberseguridad/telemetry/views.py`
- `docs/implementation/DASHBOARDS.md`

## Contrato
Vista de salud global solo operador; vistas de cliente scoped con freshness, coverage y relaciones, no score universal.

## Dependencias
D4P2, D4P3

## Tareas originales
- D4P4T1: Elegir mínimo local para Lite y stack Prometheus/Grafana opcional según recursos y revisión AGPL. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P4T2: Diseñar vistas API/policy/jobs/scanners, cobertura, datos stale, incidentes y presupuesto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P4T3: Enlazar dashboard→finding→evidencia→trace con acceso revalidado en cada salto. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P4T4: Configurar datasources read-only y credenciales por entorno; no exponer panel admin o consultas globales a clientes. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P4T5: Anotar ejecuciones reales y cambios de versión para explicar anomalías y regresiones. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P4T6: Validar desktop/móvil, accesibilidad, datos vacíos y relaciones entre errores y fuentes. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.
- D4P4T7: Entregar paneles versionados con capturas y consultas reproducibles, sin branding que simule productos adquiridos. **Aceptación:** Acción demostrada con artefacto/evidencia y gate de fase ejecutado; no marcar por texto generado.

## Gates originales no ejecutados
- D4P4-TEST-1: ViewerA no obtiene series/eventos deB a través de dashboard o enlace de trace.
- D4P4-TEST-2: Datos ausentes y collector caído se muestran como unknown/stale, no verde.

Rollback: Volver a vistas HTML/JSON mínimas y despublicar dashboards inseguros.

Después: Astra libre, reconciliación, patchsets y handoffs de fase. No hay scans ejecutados por esta preparación.
