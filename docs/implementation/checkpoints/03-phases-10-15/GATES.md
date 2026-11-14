# Matriz de aceptación del corte10–15

PASS técnico significa el escenario ejercitado en el alcance indicado, no la aprobación de producción. Evidencia base: commit92cada0863e8f05a85aa78a8e6868970f5cfd354, CI núcleo42861337075 y Docker42861322183.

| Escenario | Estado | Evidencia y límite |
|---|---|---|
|D2P4-TEST-1|PASS en fixture|OSV real vulnerable/control del corte anterior sigue pasando; validación/importación CycloneDX1.5 oficial añadida y wheel verificado|
|D2P4-TEST-2|PASS|DB ausente/caducada y ecosistema ausente conservan error/stale/partial; no se declara feed completo|
|D2P5-TEST-1|PASS en CI|Semgrep real detecta eval dinámico Python/JS/TS y deja de señalar variantes literal_eval/JSON.parse|
|D2P5-TEST-2|PASS en CI|nosemgrep y .semgrepignore hostiles no cambian el bundle administrado ni su detección|
|D2P6-TEST-1|DEFERRED|No se ha analizado una imagen afectada por advisory; solo Dockerfile está habilitado. No usar un fallo de configuración como prueba de paquete vulnerable|
|D2P6-TEST-2|PARTIAL|Perfil sin configuración reportada devuelve partial y image_vulnerabilities=not_tested; no se prueba una DB de imagen fresca porque no se usa|
|D3P1-TEST-1|PARTIAL|Dos submissions concurrentes conservan un job/una reserva local de intentos y coste0; ledger económico/importe positivo no está implementado|
|D3P1-TEST-2|PASS en API|202 devuelve admisión pending/blocked con audit_completed=false; estado/consulta/replay/cancelación probados. No se ha construido UI en este corte|
|D3P2-TEST-1|PASS|Lease vencida y fencing anterior no confirman; tras cleanup verificado una generación nueva completa sin segundo resultado persistido|
|D3P2-TEST-2|PARTIAL|Actor/política revocados bloquean claim y actor revocado antes del efecto evita scanner. Grant se revalida por la política existente; falta una prueba worker específica de cada momento de revocación de grant|
|D3P3-TEST-1|PARTIAL|Normalizador relaciona advisory/componente entre tools conservando IDs distintos; integración conserva observaciones. Falta correlación real de dos scanners de componentes/imágenes|
|D3P3-TEST-2|PASS|Ausencia/scan parcial no cambia suspected a arreglado; regla nueva conserva observaciones viejas. Errores de parser nunca se convierten en safe|

Otros checks: transacción resultado/observaciones revierte ante crash sintético; API tenant ajeno404/viewer403; sello de identidad no exportado; observaciones/resultados append-only; historial acotado con cursor opaco; Python3.11/3.12; distribución con esquemas offline.

La revisión independiente sigue NOT_VERIFIED. Las positivas de ReleaseGates en fixtures no son una aprobación jurídica/técnica de un cliente.
