# Checkpoint 04 — fases16–20

Fecha: 2026-11-10. Repositorio: agntia-ciberseguridad. PR [#4](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/pull/4), apilada sobre PR#3. No se modifica `/agente`, no se despliega producción y no se fusiona main. Baseline remoto: `4bc761c199a7868bbf93e30c44e1d0eb5f721aea`;196 archivos contrastados por hash antes de editar. Baseline local:79 tests,72 correctos,7 Docker omitidos. El snapshot local restaurado conserva su historial propio; los commits remotos por API son la referencia de publicación.

## Resultado para el usuario

El middleware conserva originales y vistas redactadas como evidencias cifradas separadas; limita quién puede leer originales; permite a un analista proponer una decisión y a otro principal humano aprobarla; construye informes ejecutivos/técnicos sin presentar ausencia de hallazgos como garantía. API, admisión, worker, scanner, custodia y reportes producen trazas con un esquema cerrado. Hay métricas acotadas y un endpoint de operaciones por tenant. Ningún componente otorga permisos por el nombre de un agente.

| Fase | Entrega funcional | Estado del gate completo |
|---|---|---|
|16 / D3P4|AES-256-GCM, checksum, redacción falible, retención/hold, accesos auditados, pruebas de corrupción y rotación|PARTIAL: anclaje externo, KMS y operación forense pendientes|
|17 / D3P5|Reglas triage-v1, excepciones con caducidad, dos actores, revisiones optimistas, retest para verified_fixed|PARTIAL: feeds KEV/EPSS/CVSS y validación independiente pendientes|
|18 / D3P6|Snapshots de informes JSON/HTML/CSV cifrados, cobertura/fallos visibles, vertical Docker con revisión y control benigno|PARTIAL: PDF, UX y revisión independiente pendientes|
|19 / D4P1|SDK1.38.0, trazas W3C internas, raíces públicas nuevas, enlaces de reportes, cola de export limitada, Collector real|PARTIAL: retención/backend productivo, política de muestreo piloto y hardening operativo pendientes|
|20 / D4P2|Prometheus autenticado con credencial distinta, histogramas/counters de cardinalidad fija, alertas iniciales y medición|PARTIAL: SLO/burn-rate operativo, dashboards y carga con concurrencia de producción pendientes|

Los gates anteriores no se convierten en PASS por añadir estas capacidades. La ejecución sobre clientes permanece desactivada por defecto. Ver [GATES.md](GATES.md), [RISKS.md](RISKS.md) y [evidencia](evidence/README.md).

## Custodia y decisiones

La política se configura en servidor por tenant: referencias de claves, custodio, referencia de base jurídica y días de retención. Referenciar una base jurídica no verifica por sí mismo su validez. No se aceptan rutas o claves desde el agente. Los archivos cifrados usan nonce aleatorio y AAD que vincula tenant, ID, variante y hashes; SQLite no almacena claves ni el contenido completo del informe. Los metadatos, jobs y otros registros existentes todavía requieren cifrado del volumen y backups externos.

Los PDF se ponen en cuarentena y su vista es un marcador; no se ejecuta un parser PDF ni se promete desinfección. La redacción de texto/JSON detecta patrones concretos, no todos los secretos. El original exige capability y principal configurado como humano, motivo y auditoría; una vista redactada también requiere scope. La configuración `kind=human` es una declaración del operador y conserva el valor histórico por compatibilidad: no sustituye SSO/MFA, autenticación interactiva ni prueba de presencia humana.

Una propuesta requiere revisión de las evidencias, revisión esperada del hallazgo y hash; otro reviewer humano aprueba antes de caducar. El proponente y el autor del último scan no pueden aprobar. Las decisiones se conservan append-only. Accepted risk, suppressed y false positive caducan; su vista efectiva vuelve a suspected sin borrar la decisión histórica. Un hallazgo remediado solo pasa a verified_fixed tras un nuevo snapshot y retest completo de la misma herramienta/política, posterior a la remediación, sin la misma regla/ruta y con hashes comprobados. Esa verificación queda limitada a lo observado.

## Informes y telemetría

Los informes fijan fuentes, scope, grants, herramientas, versiones, hashes, cobertura y resultados; fallos, exclusiones o datos antiguos aparecen como incompletos. El hash de fuente evita duplicar un export idéntico. JSON, HTML escapado sin enlaces activos y CSV con protección de fórmulas están disponibles; PDF no se soporta. Todo informe nace `not_reviewed`; aprobar un hallazgo no certifica el informe.

El contexto externo de tracing no cambia tenant/rol ni elige la raíz de una petición pública. La propagación interna procede del job persistido. Solo se exportan atributos cerrados; no cuerpos, tokens, prompts, SQL ni rutas. El exportador solo permite loopback4318, desactiva proxies/redirects y usa cola/batches acotados con contadores de pérdida. Collector/Prometheus se fijan por digest tras probar las imágenes reales. El Collector actual usa debug básico para laboratorio; no es un backend persistente contratado.

La medición local de200 peticiones secuenciales, con diez de calentamiento, no usa TCP/TLS ni scanners ni SDK local. Se conserva p50/p95, errores, RSS/CPU de proceso y series, con limitaciones. No equivale a SLA, capacidad multiusuario o resultado de producción.

## Verificación ejecutada

SHA de código validado: `fcc7e66b18ef1c62f923ea229ced4cc261dcb67b`. CI Python3.11/3.12:103 descubiertos,96 correctos y7 Docker omitidos por matriz; job Docker separado:7/7 correctos. Por tanto103 tests distintos correctos entre ambos jobs, sin contar versiones/duplicados como tests nuevos. Los4 tests SDK omitidos localmente sí se ejecutaron en CI. Collector/Prometheus reales, promtool y recepción OTLP:PASS. Validadores de documentación/campaña, export de schemas y distribución:PASS en CI. El wheel local quedó bloqueado por red al descargar build dependencies, documentado por separado.

Medición local:200 solicitudes,0 errores, p50=1.248ms, p95=1.575ms, pico RSS47332KiB y18 series; secuencial ASGI sin SDK, sin red/TLS/scanners. Ver JSON para valores sin redondear.

## Verificación y continuidad

La evidencia distingue pruebas locales, SDK ejecutado en CI, herramientas Docker y Collector/Prometheus reales. Un fallo inicial de CI detectó enlaces de reportes asociados al span de DB: se corrigió moviendo el enlace fuera de ese contexto; se conserva el fallo. No se alteró el test para aceptar el comportamiento incorrecto.

Siguiente bloque21–25: logging estructurado, dashboards, eventos, resiliencia y registro de agentes. Debe conservar aislamiento, límites y gates pendientes, y seguir sin conectar `/agente` sin autorización específica. Ver [OPERATIONS.md](OPERATIONS.md) y el estado machine-readable de campaña.
