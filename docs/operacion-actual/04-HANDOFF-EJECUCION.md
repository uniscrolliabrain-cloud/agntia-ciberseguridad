# 04 — Handoff de ejecución diferencial para FreeBuff

## Misión

Cerrar las dependencias de [matriz CP-01…CP-14](02-MATRIZ-CIERRE-PRODUCCION.md) sin duplicar código existente, manteniendo `SYNTHETIC_DEMO_NOT_PRODUCTION` hasta superar gates reales. La primera tarea es **verificar**, no reimplementar.

## Preflight obligatorio

1. `git fetch --all --prune`; registrar HEAD de `main`, ramas relevantes y commits de integración. No asumir que el dump GitIngest refleja el HEAD del día.
2. Leer [centro operativo](README.md), [estado](01-ESTADO-Y-ALCANCE.md), [matriz](02-MATRIZ-CIERRE-PRODUCCION.md), `docs/release/status.json`, informes adversariales C/B/D y reportes de auditoría runtime.
3. Inspeccionar implementaciones reales: `agntia_ciberseguridad/{auth,agents,jobs,evidence,scanners}/` (ajustar rutas a árbol real), `adversarial_lab/src/agntia_adversarial/{domain,execution,evidence,planning,store,release}/`, `typescript/`, tests y `.github/workflows/`.
4. Emitir inventario por gate con paths, símbolos, SHA, tests existentes y **diferencia exacta** respecto a producción. No declarar un faltante solo por leer un roadmap antiguo.
5. Abrir rama de trabajo nueva; no modificar `main` directamente en campañas de código. Un agente por superficie de escritura; PR revisable y sin despliegue.

## Entregables de cada campaña

- `docs/operacion-actual/reports/CP-XX-REPORT.md`: alcance, diff, resultados, errores, decisiones y riesgos.
- `docs/operacion-actual/reports/CP-XX-EVIDENCE.md`: SHA, comandos, exit, logs redactados y pruebas negativas.
- `docs/operacion-actual/reports/CP-XX-ROLLBACK.md`: cambios, migraciones, compatibilidad y recuperación.
- Si se necesita decisión del founder, registrar `BLOCKED` y especificar **una acción concreta** (cuenta, scope, presupuesto, autorización o proveedor).

## Restricciones

- `/agente` es otro repositorio: contrato versionado y patchset propuesto, **sin escribirlo** sin autorización.
- Mantener aislamiento del laboratorio y middleware; prohibido importarlos cruzadamente sin ADR.
- Acciones de seguridad activas solo en gemelos sintéticos o activos propios expresamente autorizados.
- Ninguna prueba sobre terceros; ningún token real en artefactos; red denegada por defecto en sandbox.
- Los gates de release deben fallar cerrado si faltan auditoría, atestación, autorización o evidencia.
- No afirmar «producción» por pasar tests sintéticos; el founder decide el GO después de revisión independiente.

## Secuencia sugerida

CP-01 baseline → CP-02/03/04/05 entorno y proveedores → CP-06/07/08/09 custodia y seguridad → CP-10/11 piloto propio → CP-12/13 primer cliente. CP-14 solo por decisión de producto.

**Fin de cada ola:** reporte de cambios, tests heredados vs reejecutados, bloqueos, riesgos residuales y siguiente patchset; detenerse si hay incompatibilidad de contratos, secretos ausentes o cambios no autorizados.
