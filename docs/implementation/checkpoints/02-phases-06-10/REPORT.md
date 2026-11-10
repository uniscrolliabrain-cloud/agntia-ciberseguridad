# Informe02 · Fases 6–10

Fecha:2026-11-10. Repo `uniscrolliabrain-cloud/agntia-ciberseguridad`. Rama `feat/cyber-phases-06-10`. [PR#2](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/pull/2), apilada sobre la primera entrega. No merge a main, cambios en `/agente`, compras o despliegue.

## Resultado para el producto

Este bloque añade adquisición de código local con permisos y custodia, un launcher de herramientas con perfiles cerrados y dos adaptadores de análisis reales: Gitleaks para secretos y OSV para dependencias. Ya se han ejecutado esos binarios en Docker de CI contra datos ficticios. La API permite crear/consultar snapshots; no permite ejecutar scanners de clientes. `StaticScanner` es una frontera interna denegada por defecto hasta verificar gates de release.

**El código del bloque está entregado y probado en el alcance descrito; no se declaran cinco fases completamente cerradas.** D1P6 carece de revisión independiente; siguen pendientes modalidades de adquisición, validación completa SBOM y habilitación del worker de producción. Los estados globales permanecen PARTIAL para que no se salten dependencias. La columna técnica siguiente permite ver lo implementado sin confundirlo con autorización de despliegue.

| Fase | ID | Entregado y comprobado | Pendientes de cierre |
|---|---|---|---|
|6|D1P6|Modelo de amenazas ampliado,10 fronteras, casos benignos/adversariales y gate fail-closed|Revisión independiente; no sustituida por auto-revisión/CI|
|7|D2P1|Snapshot local POSIX, hashes/manifest, grants, límites, O_NOFOLLOW, tipos seguros, cancelación, auditoría y custodia DB|Git remoto/commit, imagen, Windows nativo y consistencia multiarchivo atómica unsupported; cobertura local declarada|
|8|D2P2|Runner Docker cerrado con UID, no red/socket/credenciales, read-only, cuotas, timeout/output, cancelación y cleanup; pruebas reales pasan|Validar despliegue propio, separar launcher/API y cerrar revisión de release|
|9|D2P3|Gitleaks8.30.1 fijado y ejecutado; parser minimizado, deduplicación, política no controlada por repo, errores seguros y canario real/control|Solo modo directorio/snapshot; habilitación cliente bloqueada por gates previos|
|10|D2P4|OSV2.7.1 real offline, caché por hash/fecha, advisories/componentes, SBOM observado y diferencias sin inventar resolución|Feed completo revisado, matriz de ecosistemas y validación oficial/importación amplia SBOM; sin reachability ni licencias inferidas|

## Código y contratos

`SnapshotStore.acquire` valida principal/empresa/grant, reabre la raíz sin seguir componentes simbólicos y copia archivos regulares con límites de entrada, fichero, bytes totales, profundidad y ruta. Rechaza hardlinks, symlinks y tipos especiales; compara stat antes/después de lectura y directorio; revalida autorización durante y al terminar. No invoca Git, hooks, filtros o gestores de paquetes. `.git` se excluye; punteros LFS y `.gitmodules` quedan explícitos como adquisición incompleta. Los binarios se etiquetan como tales, sin inventar análisis de lenguaje.

El manifiesto liga tenant, activo, grant/revisión, actor, correlación y hashes. La migración2 añade `snapshots` con FKs compuestas; upgrade desde versión1 conserva tenant/auditoría y crea backup. Un directorio huérfano no se publica. Una caída entre rename y commit sigue requiriendo conciliación de huérfanos no visibles; no hay transacción distribuida entre filesystem y SQLite.

Rutas nuevas: `POST /v1/tenants/{tenant}/snapshots` con el contrato cerrado `AuditPreview`, y `GET /v1/tenants/{tenant}/snapshots/{snapshot_id}`. La primera requiere grant vigente; la segunda comprueba pertenencia e integridad antes de devolver metadatos, sin ruta local absoluta. No hay endpoint shell, Docker, model/method o scanner libre.

`ContainerRunner` solo admite dos tools/versiones y image IDs/digests inmutables, construye argv fijo y usa entorno mínimo. Scanner UID65532, filesystem e input de lectura, tmpfs noexec, no red, sin caps, no-new-privileges, memoria/swap/CPU/pids/fd/tiempo y salida acotados. El launcher de confianza usa el daemon local, mientras el scanner nunca recibe su socket. El usuario/LLM no elige executable, flags, mount, cache URL ni entorno. Es un componente para un servicio worker separado, no una razón para exponer el daemon en la API.

Los parsers separan findings/no_findings/error y conservan incertidumbre; `scan_clean=false` evita presentar ausencia de findings como seguridad certificada. Gitleaks elimina valores y líneas de secreto. OSV conserva fuente/ID, versión observada, fixes reportados y fecha/hash de DB; explotación, reachability, severidad, licencias y relaciones ausentes permanecen unknown. Un componente no observado en el siguiente snapshot no se marca automáticamente corregido.

## Pruebas y evidencia real

- Última suite local registrada: **56 descubiertas,52 aprobadas,0 fallidas,4 omitidas**. Las cuatro omitidas son Docker porque el socket local sigue denegado. Log y SHA256 en `evidence/tests.json`/`tests.txt`.
- CI Python3.11 y3.12: en cada job,56 descubiertas,52 aprobadas y4 Docker omitidas. No se cuentan esas repeticiones como casos distintos.
- **CI Docker:4 ejecutadas,4 aprobadas,0 fallidas,0 omitidas**, con Gitleaks y OSV reales. [Run42854842519](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/actions/runs/42854842519), código `29395da5671e6b063b54895f791de75d38d0792b`. CI general [42854836657](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/actions/runs/42854836657).
- Esos bloques cubren56 casos distintos en total, con pruebas reales de lectura/SQLite/API/procesos y contenedores. No equivalen a56 auditorías de clientes ni a un benchmark de cobertura de vulnerabilidades.

Se ensayaron hooks y tipos hostiles, mutation/cancelación y límites; custodia/alteración/huérfanos; aislamiento entre tenants; timeout y overflow del launcher; red/archivo/secretos/proxy/socket/caps/UID/cuotas en contenedor; canario pese a suppressions; control benigno; advisory sintético/control, DB ausente/caducada y attestación alterada. Ver [GATES.md](GATES.md).

Se conserva el fallo del primer Docker run en `evidence/failed-docker-run-01.json`: herramientas pasaron y probes fallaron por permisos de la fixture. Después se corrigió un deadlock real de pipes al exceder salida: hay test de regresión local y el run Docker completo posterior pasó. El test ASGI usa un ticker acotado solo en pruebas para el problema de wakeups del sandbox local, sin modificar el código productivo para ocultarlo.

## Procedencia, recursos y coste

Release oficial Gitleaks8.30.1 Linux x64, SHA256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`, core/defaults MIT. OSV2.7.1 Linux amd64, SHA256 `fb7dab19a8bd9bbe5c3189f09d4b7ee1820c9553a23bac202648a56efd2f6ee8`, Apache2.0. Releases/licencias/docs fueron consultadas en sus tags; notices incluidos. No se usa la action comercial Gitleaks.

Imágenes scratch construidas desde esos binarios, versión comprobada dentro del contenedor, policy_hash e image IDs guardados en `evidence/ci.json`. La base Python del probe se resuelve a digest en su build y no es una imagen de producto. No se descargan feeds ni se validan credenciales reales durante el scan. La DB de integración contiene solo un advisory inventado para un paquete ficticio; no acredita cobertura de la base OSV completa.

Suite local aproximadamente1.4s y bloque Docker verde2.765s en el run registrado; contextos/mediciones precisas en evidencia. No hay p95 productivo, coste por tenant o cobertura global medida. CI/build/download/hosting consumen recursos aunque no se haya contratado ningún servicio. Los techos30/70/300EUR siguen sin ledger económico hasta su fase específica.

## Riesgos y continuación

Revisión independiente pendiente; no hay runner de clientes habilitado, jobs durables, lease/fencing/retry, almacenamiento de informes finales o monitorización continua. No hay soporte validado de snapshots Windows nativos, Git remoto/imágenes o importación SBOM general. Mantener explícita esa cobertura. Los datos de originales y SQLite requieren cifrado, retención y backups de despliegue, todavía no configurados aquí.

Reversión: deshabilitar launcher/herramientas y detener nuevas admisiones; conservar snapshots, DB, evidencias y auditoría. No borrar orígenes ni matar procesos globalmente. Cada contenedor de pruebas se identifica y limpia por nombre exacto. La migración es aditiva, no downgrade destructivo automático.

Siguiente bloque numerado11–15: D2P5 Semgrep, D2P6 Trivy opcional, D3P1 jobs/idempotencia, D3P2 worker/leases y D3P3 normalización. Su habilitación sigue condicionada por los gates de release documentados. Esta entrega no modifica el plan de42 IDs ni presenta pendientes como PASS.
