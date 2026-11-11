# Checkpoint07 — fases31–35

Cierre:2026-11-11; investigación normativa observada2026-11-10. [PR#7](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/pull/7), rama feat/cyber-phases-31-35, apilada sobre PR#6. Baseline remoto ef862fe771ed28dc5c41c6688e208f623b00c9fd; árbol c76895b3d1b865a38a18893a39139b3de5695b6e contrastado con local antes de editar.143 tests iniciales,132 correctos y11 skips locales. El entorno anunciado unavailable volvió a estar operativo; no se perdió el checkout ni se reinició el proyecto.

|Fase|Entrega funcional|Gate completo|
|---|---|---|
|31 / D6P1|Inventario por sistema/finalidad/rol, catálogo normativo versionado, candidatos de aplicabilidad por seis regímenes y controles ligados a evidencia|PARTIAL: revisión jurídica competente y cobertura sectorial/nacional completa pendientes|
|32 / D6P2|Solicitudes revisadas de restricción/levantamiento, export de metadatos y purga sujeta a retención; propagación a derivados; expedientes de brecha|PARTIAL: SAR completo, borrado de backups y operación de restauración pendientes|
|33 / D6P3|Normalización offline de dominios/Unicode, señales falibles y verificación humana por canal previamente registrado|PARTIAL: correo/reputación/SPF/DKIM/DMARC autenticados, voz/deepfake y conectores pendientes|
|34 / D6P4|Incidentes versionados, deduplicación, cronología, contención revisada solo de laboratorio y conciliación de resultado incierto|PARTIAL: proveedores externos y respuesta productiva/24×7 pendientes|
|35 / D6P5|Dos reglas de fixtures, diff redactado, candidato privado, origen inmutable, aprobación y retests en sandbox|PARTIAL: rama/PR de cliente, fixes generales, merge/deploy y validación funcional productiva no habilitados|

## Capacidades para el cliente

El servicio prepara un expediente trazable en lugar de emitir un sello legal. Identifica inventarios declarados, preguntas sin respuesta, fuentes/fechas y controles con evidencia pendiente/presente/revisada. Una guía que contradice un hito normativo deja source_conflict y no activa automatización de fechas. Nombre comercial, tamaño aparente o nombre de un agente no determinan un rol jurídico. AI Act, RGPD, CRA, NIS2, DORA y ENS permanecen separados.

Los proveedores, regiones, DPA, transferencias y retención se registran como referencias declaradas. Un ICT provider no se equipara automáticamente a una entidad financiera DORA. La aplicabilidad puede quedar insufficient_information. Toda salida conserva compliance_verdict=not_provided; la revisión humana es una actuación autenticada con referencia de competencia, no una comprobación de titulación jurídica ni certificación.

La consulta de fuentes oficiales detectó la modificación de AI Act de2026. El catálogo incorpora la consolidación y el acto modificativo, con artículos y hitos diferenciados; no usa sin revisión el calendario original2024. Ver [SOURCES.md](SOURCES.md). Es un snapshot curado de metadatos, no una descarga íntegra ni un monitor legislativo automático. NIS2 en España queda nacionalmente not_verified, sin afirmar una transposición que no se haya verificado.

## Privacidad y brechas

Las solicitudes se ligan a IDs y revisiones de evidencia del tenant, base/finalidad referenciadas y otra revisión humana. Una restricción se comprueba antes de devolver originales o vistas; se propaga a hechos tipados e informes, incluso accediendo al artefacto de un informe por la API de evidencias. El linaje forma parte de la autenticación del artefacto derivado. Informes antiguos registrados sin linaje verificable quedan bloqueados para reconciliación, sin borrar su ciphertext.

Levantar una restricción exige propuesta y revisión nuevas. El hash del overlay impide que una aprobación antigua borre una restricción posterior. La exportación es de metadatos minimizados y declara no ser un SAR completo. Purga solo procede si expiró retención y no hay legal hold; conserva historia/tombstones y acaba awaiting_backup_reconciliation. No afirma haber borrado backups o todos los datos de una persona. No hay limpieza automática de todas las bases, snapshots o sistemas del cliente.

Una alerta técnica no inicia por sí sola un plazo de brecha. Se separan detección, constancia, datos personales, confirmación, rol y riesgo. Solo con hechos revisados y fuentes vigentes se prepara condicionalmente el reloj pertinente del responsable; el deber del encargado y la comunicación a afectados se presentan aparte. No se envía ninguna notificación ni se reutiliza ese reloj para otros regímenes. Datos de brecha/solicitudes tienen acceso adicional por rol o asignación; los viewers no leen esos expedientes.

## Antifraude e incidentes

Se analizan sender/reply/link por dominio normalizado sin navegar al enlace y sin conservar el buzón completo. Unicode, desajustes o un supuesto cambio de destino de pago son señales, no veredictos. Un authentication-results aportado por el mensaje sigue sin verificarse. No se consulta reputación, ni se declara que una voz sea falsa. El enlace/teléfono del propio mensaje no crea un canal confiable: se exige un directorio configurado antes en servidor y justificante revisado por humano distinto. No se paga, envía correo o bloquea un trabajador.

Los incidentes relacionan fuentes existentes del mismo activo/tenant, evidencias, dueño y cronología; un replay con la misma clave/contenido conserva el caso y una colisión devuelve409. Una alerta falsa puede cerrarse con revisión/evidencia sin revocaciones. Las transiciones diferencian triage, contención, recuperación y resolución de las decisiones regulatorias.

La única contención ejecutable del bloque es revocar una autorización de trabajo interna en lab_mode tras aprobar su hash/revisión exactos. No aísla hosts ni toca proveedores. Si se pierde el ACK después de revocar, el estado queda reconciliation_required; se comprueban grant y auditoría/correlación antes de reconocer el resultado, sin repetir a ciegas. Rollback significa emitir otra autorización con aprobación nueva, nunca resucitar la anterior.

## Remediación

Se soportan dos plantillas originales no productivas: retirar una canary sintética aislada y sustituir el eval de una función de fixture exacta. No son codemods generales. Solo actúan sobre canary.txt o fixture_eval.py, con finding/snapshot/política/ruta coherentes y recursos de laboratorio registrados por servidor.

El humano revisa diff redactado y hashes antes/después. Se construye un directorio privado, no una rama Git ni una PR de cliente. El origen no se modifica. Otro fichero, cambio de origen, finding distinto o candidato alterado bloquea la operación. Los retests usan las imágenes/reglas fijadas y el sandbox existente; no se ejecuta el código del repositorio. Default ReleaseGates sigue cerrado. Un resultado limpio del candidato se denomina retest_passed_fixture: no cambia el finding original a verified_fixed, ni activa merge/deploy.

## Verificación y continuidad

Las evidencias separan baseline, primera ejecución, CI y revisión final. La batería local final descubre168 tests,156 correctos y12 skips(8 Docker no solicitados y4 SDK no disponible localmente). Se añaden25 tests frente al baseline. La CI instala SDK real y ejecuta Docker aparte. El nuevo test Docker cubre ambos fixes con detección original real, aprobación, candidato, retest real y comprobación de origen intacto; no se cuentan dos iteraciones como dos tests independientes.

Los resultados remotos, SHA/jobs, capturas y comandos quedan en evidence/. Los gates completos permanecen PARTIAL por los pendientes indicados; revisión independiente y uso de clientes no se habilitan por un resultado verde. No se modifica `/agente`, se compra, se despliega ni se fusiona main.

Siguiente bloque36–40: reservas económicas, SDK TS/Hono, interfaz, E2E y hardening. Quedan41–42 para empaquetado/aceptación. Leer sus IDs exactos y preservar todos los límites antes de continuar.

## Cierre de CI verificado — 11 de noviembre de 2026

Commit de código probado: `4f74b8e7e34755a63b1f42a106f961351a61513e`. Los cinco workflows de push terminaron en success. La matriz Python 3.11/3.12 ejecuta el núcleo; Python 3.12 descubre168 pruebas, pasa160 y omite8 Docker. El job Docker separado pasa esas8: total168 pruebas distintas, cero fallos, sin sumar dos veces la matriz. El SDK de observabilidad se ejecutó en CI.

El retest gobernado real ejecutó Gitleaks y Semgrep sobre los dos candidatos sintéticos y comprobó origen intacto; sigue sin equivaler a reparación de clientes. Chromium real comprobó1440×1000 y390×844, sin overflow ni errores JS y con rechazo cross-tenant/logout. El collector OTLP y Prometheus sintéticos pasaron sus contratos; wheel/schemas y catálogo legal empaquetado también se verificaron. IDs, URLs y resultados están en [evidence/ci.json](evidence/ci.json). Estos resultados pertenecen al SHA indicado; los commits posteriores de documentación no cambian código.

Sigue pendiente inventariar artefactos históricos huérfanos sin fila de informe para resolver su procedencia antes de producción. No se afirma descubrimiento completo de datos personales.
