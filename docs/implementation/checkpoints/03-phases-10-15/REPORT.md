# Informe03 · Fase10 revisada y fases11–15

Fecha:2026-11-10. Repositorio uniscrolliabrain-cloud/agntia-ciberseguridad. Rama feat/cyber-phases-10-15; [PR#3](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/pull/3), apilada sobre PR#2. Este corte retoma el pendiente SBOM de la fase10 y entrega las cinco fases nuevas11–15. No duplica una fase para inflar el progreso.

## Capacidades entregadas

| Fase | ID | Resultado observable | Límite de cierre |
|---|---|---|---|
|10 revisada|D2P4|Validación oficial CycloneDX1.5 sin red, importación observada acotada, recursos incluidos en wheel|Solo CycloneDX1.5; importación sin verificar verdad/licencias, componentes anidados no desplegados; feed/otros ecosistemas pendientes|
|11|D2P5|Semgrep CE1.185.0, reglas locales propias para Python/JS/TS, parser minimizado y contratos reales|Bundle pequeño, sin Registry/Pro/interarchivo ni cobertura completa de lenguaje|
|12 opcional|D2P6|Trivy0.76.2 offline para Dockerfile, binario/checks embebidos fijados, parser y control real de USER|Vulnerabilidades de imagen, DB de advisories y otros perfiles IaC siguen not_tested|
|13|D3P1|Jobs durables,202, replay/409, consulta/cancelación con scope y una reserva local de intentos por job|Solo importe0; no ledger financiero ni pagos/cargos a proveedores|
|14|D3P2|Claim atómico, heartbeat, fencing, presupuestos de intentos, backoff, reconciliación operativa y ejecución real de fixture|SQLite de un nodo; no garantía exactly-once de proceso, despliegue o muerte del host completo|
|15|D3P3|Observaciones append-only, identidad estable, correlación separada, historial/paginación y ausencia que no implica arreglo|Revisión/excepciones humanas e inventario de despliegue/imagen completos van en fases posteriores|

**Implementación y pruebas entregadas; cierre global PARTIAL.** No se han cerrado la revisión independiente de D1P6 ni otros gates de release. Las herramientas se ejecutaron en CI sobre fixtures ficticias, no sobre clientes. La API devuelve jobs bloqueados por defecto; admitir un202 nunca habilita por sí solo un worker.

## Pruebas ejecutadas y trazabilidad

Versión validada: commit92cada0863e8f05a85aa78a8e6868970f5cfd354. [CI del núcleo](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/actions/runs/42861337075): Python3.11 y3.12, en cada job79 casos descubiertos,72 aprobados,0 fallidos y7 Docker omitidos explícitamente. No se cuentan las repeticiones entre versiones como casos nuevos.

[CI Docker](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/actions/runs/42861322183): **7 ejecutados,7 aprobados,0 fallidos,0 omitidos**, con Gitleaks, OSV, Semgrep y Trivy reales. Juntos son79 casos distintos cubiertos, no79 auditorías de clientes. Se comprobaron también construcción del wheel e inclusión de los tres esquemas CycloneDX y su licencia.

La evidencia sanitizada está en evidence/ci.json: SHA, run/job IDs, versiones, hashes de release, image IDs, policy_hash, digest upstream Semgrep, extractos de resultados y hashes de esquemas incluidos en distribución. Fuentes y decisiones están en SOURCES.md y DECISIONS.md. Los fallos previos se preservan en evidence/failed-*.json; no se ocultan bajo el último PASS.

El ejecutor local quedó no disponible durante un commit. Último resultado local observado:72 descubiertas,66 aprobadas,6 Docker omitidas. No pudo verificarse ese commit local. Se reconstruyó/preservó el bloque por el conector GitHub y se revalidó la versión publicada en CI con sus propios conteos, incluyendo nuevas regresiones. Ver RECOVERY.md. El PASS remoto no se atribuye a un árbol local que ya no era accesible.

## Contratos y flujo de jobs

POST /v1/tenants/{tenant}/audits admite un contrato cerrado: asset_id, grant_id, snapshot_id, snapshot_hash, expected_grant_revision, tool, perfil estático, hasta tres intentos y máximo de coste0. Idempotency-Key es obligatorio. Tenant, actor, rol, hash de autorización, política y credenciales se obtienen del servidor, no del body.

Antes de guardar se revalidan token/principal, autorización de activo, ventana/revisión del grant, snapshot registrado y política del tool administrada por servidor. Bajo BEGIN IMMEDIATE se comprueba de nuevo el grant y la unicidad tenant/operación/key. Mismo actor/key/payload conserva job; una propuesta distinta con esa key devuelve409. Una reserva local se crea en la misma transacción; no se crea otra en replay/retry. No se aceptan importes positivos ni se afirman reservas monetarias de servicios externos. La reserva de intentos es conservadora: puede retener el máximo autorizado hasta el cierre.

Estados: pending, running, partial, completed, failed, cancelled, blocked y reconciliation_required. GET jobs/{id} devuelve estado seguro sin comandos, tokens, authorization_stamp ni payload crudo. POST jobs/{id}/cancel exige revisión; pending se cancela efectivamente y libera su reserva. Running registra solicitud; cancelar una tarea no demuestra limpieza y puede exigir conciliación.

La migración3 añade jobs, claves de replay, reservas, resultados, proyección de findings y observaciones, con FKs compuestas por tenant y triggers append-only. Las migraciones anteriores siguen presentes, con backups previos y rollback. Resultado y observaciones se confirman atómicamente; una excepción entre ambas escrituras revierte todo.

## Worker, fallos y recuperación

Claim y límites de concurrencia son transaccionales. Default: dos slots globales, uno por tenant y uno por herramienta; los trabajos de conciliación siguen ocupando capacidad para no lanzar efectos inciertos en paralelo. Un nombre de worker no concede permisos: se reconstruye el principal original y se compara el sello de autorización, incluyendo cambios de credencial/rol/scope, con los valores actuales del servidor.

El worker comprueba grant, snapshot y política al reclamar, antes de ejecutar y durante esperas. El resultado solo se confirma si siguen vigentes owner de lease, fencing token y caducidad, identidad/grant y estado de cancelación. Un worker antiguo no puede sobrescribir la confirmación del nuevo. Errores definitivos no reintentan; timeout/disponibilidad solo reintentan con cleanup conocido, presupuesto restante y backoff con jitter acotado.

Una lease vencida pasa a reconciliation_required y no se relanza automáticamente. Se conserva el nombre exacto del contenedor antes de ejecutar. Worker.reconcile exige capacidad jobs.reconcile de un principal autorizado y limpieza real de ese nombre mediante el launcher; no acepta un booleano del LLM. Después incrementa fencing y solo permite reintentar si siguen activos principal/grant y presupuesto. No existe un endpoint Docker/cleanup arbitrario.

Las pruebas inyectan expiry tras claim, resultado antes de ACK, excepción entre resultado/observaciones, revocación antes del efecto, pérdida de cleanup, reintentos agotados y worker antiguo. Se demuestra una única confirmación persistida y una sola identidad de reserva; no se promete ejecución física exactly-once frente a todas las caídas. Un operador debe verificar el worker anterior al reconciliar un proceso externo incierto.

## Findings, custodia e incertidumbre

Cada observación liga tenant, activo, snapshot, job, herramienta/versión, policy_hash, regla/advisory, ubicación, componente, severidad y confianza separadas, con CVE/CWE cuando la fuente los identifica. Estado inicial suspected; exposición y reachability desconocidas permanecen unknown. Ni un comentario ni un campo de salida cambia revisión humana o declara explotación.

La identidad de proyección no incluye el ID del snapshot ni un secreto: incluye tenant, activo, tool, política, regla, ubicación y componente. Así se conserva historial entre snapshots comparables, mientras cambiar regla/bundle separa la observación. Una relación advisory/componente puede correlacionar tools sin fusionar o eliminar sus fuentes originales. Se prueban también homónimos entre tenants y cambios de política.

Se conservan first_seen/last_seen, contador, referencia a último job/snapshot y observaciones append-only. Si un finding simplemente no aparece en un scan, incluso un scan parcial o un error, no se marca arreglado. Los estados de revisión, excepción y cierre verificado requieren políticas/acciones humanas posteriores; aquí no hay endpoint para fabricarlos.

GET /v1/tenants/{tenant}/findings y GET findings/{id}/history aplican scopes y paginación limitada. El cursor del historial es opaco y solo puede referir a una observación del mismo tenant/finding; no exporta secuencias globales ni resultados de otras empresas.

## Herramientas y SBOM

Semgrep CE usa el digest upstream67518c174185a2043fdbed16c70631b79209499b3671178e7194379b48295a0d, versión1.185.0, métricas/version checks desactivados y reglas locales. Se ignoran suppressions y .semgrepignore del repositorio. Positivos y controles en Python/JavaScript/TypeScript pasaron en Docker. No se ejecuta código analizado ni se descarga un registry de reglas.

Trivy0.76.2 se descarga con SHA256bc0fc726e017b8927a62b2d3531d7a84ee01769daf5c99ed866dced54089fdbf. Se inspecciona Dockerfile, sin arrancar workloads ni descargar DB/check updates. Usa checks embebidos del binario fijado; el contenedor sigue sin red. La fixture verifica DS-0002 contra USER root y su control USER10001. Otros checks pueden seguir señalando problemas; el control no se anuncia seguro globalmente.

CycloneDX1.5 se valida con los esquemas oficiales del commitc320fc0f0b46873864927d9d5684eea7ba439728, incluidos SPDX/JSF y licencia Apache2.0. El registro de referencias rehúsa descargas externas. Importación limitada a2MiB/10000 componentes, con datos no verificados y omisiones explícitas. Un documento válido estructuralmente no prueba licencias, componentes instalados ni verdad del proveedor.

## Límites operativos, coste y continuación

El núcleo sigue siendo un piloto de un nodo SQLite. No hay despliegue Windows validado de snapshots, cifrado/retención/backup de producción, scheduler empresarial duplicado, integración con /agente ni revisión independiente completada. No se activó servicio de pago, facturación, transferencia o cambio de clientes. El middleware registra/explica resultados; no certifica seguridad o cumplimiento legal.

CI consume recursos: no se ha medido coste mensual por cliente ni se declaran cumplidos los techos30/70/300EUR mediante una prueba pequeña. El ledger financiero completo sigue en D6P6. El bloque Docker tardó13.022s en el run de evidencia y el núcleo aproximadamente2–3s por versión; son fixtures, no p95 de producción.

Reversión: detener admisiones/workers, preservar SQLite, resultados, observaciones y reservas. No borrar keys para forzar replay ni resetear leases inciertas. Conciliar solo el contenedor identificado y con permisos. Migraciones aditivas, sin downgrade destructivo automático. Si reaparece el ejecutor local, comparar SHA/árbol con la rama preservada y conservar cambios ajenos.

Siguiente bloque16–20: custodia/redacción de evidencia, priorización/revisión, reportes y vertical AppSec, OpenTelemetry y métricas. Los gates de release permanecen cerrados hasta verificar lo pendiente; una CI verde de fixtures no los aprueba por sí sola.
