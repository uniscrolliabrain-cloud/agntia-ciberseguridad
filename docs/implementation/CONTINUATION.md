# Continuidad de implementación

**Estado vigente:** [checkpoint31–35](checkpoints/07-phases-31-35/REPORT.md), rama feat/cyber-phases-31-35, PR#7 apilada sobre PR#6. Expedientes legales/privacidad/antifraude/incidentes y candidatos de fixes sintéticos implementados. Gates completos PARTIAL. Siguiente36–40; después41–42. No habilitar clientes, merge/deploy o `/agente`. Antes de restaurar copias hay que reconciliar restricciones actuales.

## Registro histórico después del primer checkpoint

Estado machine-readable: `docs/campaigns/2026-11-10-seven-days/campaign.json`. D1P1 y D1P2 PASS; D1P3–D1P5 PARTIAL. Otras37 fases NOT_STARTED. Se han preparado el modelo de amenazas y fronteras de D1P6; no se atribuye ejecución de esa revisión.

La autorización del propietario sigue siendo desarrollar las42 fases en este repo con reportes. No hace falta renovar permiso para pruebas sintéticas, fixes, ramas o PR. No hay autorización para modificar `/agente`, clientes reales, compras, despliegue o merge de implementación.

Antes de anunciar G1 completo:

1. Cerrar la trazabilidad de identidad para los futuros jobs y evidencias, con referencias de credencial y sin almacenar secretos. La autorización se revalida en cada admisión/ejecución, no solo en API. Los tests actuales demuestran ese mecanismo en servicio/preflight, no en un worker.
2. Completar estado de operaciones externas, idempotencia y separación historial/vista actual al crear jobs/evidencias. No transformar el límite máximo de un grant en una reserva económica ficticia. Los componentes posteriores pueden prepararse como código no habilitado; sus gates siguen pendientes.
3. Adquirir snapshots inmutables sin ejecutar código, con límite de archivos, bytes, symlinks/archivos especiales y cambio concurrente. D1P5 actual congela configuración; D2P1 deberá congelar contenido. Explicar ese reparto de alcance sin ocultar el pendiente del checklist original.
4. Revisar D1P6 de forma independiente del implementador, incluidos riesgos de bypass y socket privilegiado. El documento actual es auto-revisión, no aprobación externa. Conservar defectos y pruebas de regresión.
5. Disponer de un ejecutor Docker válido para las fases de sandbox y herramientas. El socket local de esta sesión está denegado. Se puede diseñar CI aislada con fixtures, imágenes fijadas y permisos mínimos; no se puede heredar un PASS de la CI Python como PASS Docker.

No cambiar nombres/IDs de la campaña ni marcar todo PASS para desbloquear el DAG. Si se reorganizan tareas que hacen referencia a futuros componentes, documentar la decisión y conservar sus criterios de aceptación en la fase responsable.

Orden posterior: D1P6, D2P1/D2P2 y adaptadores; D3jobs/evidencias/reportes; D4observabilidad; D5gateway agéntico; D6privacidad/legal/presupuesto; D7SDK/UI/E2E/operación. Seguir dependencias del JSON. Los tracks independientes pueden prepararse, pero no habilitar ejecuciones de impacto a través de gates pendientes.

El ZIP de main es anterior al runtime y no se ha regenerado. No usarlo como instalador del servicio. La implementación vigente está en PR#4 apilada; las referencias anteriores son históricas. Revisar SHA remoto antes de continuar y conservar cambios ajenos.
