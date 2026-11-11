# Checkpoint8 — fases36–40

Rama `feat/cyber-phases-36-40`, apilada sobre `feat/cyber-phases-31-35`. Baseline remoto231db083db6d647ea1ff672e5f600ce49afc4c56, árbol b65ecd173feb3e055706fd69b87d0689fbab2bed idéntico al checkout local. No se modifica `/agente`, main, producción ni servicios de clientes. El bloque entrega implementación incremental; sus cinco gates completos siguen PARTIAL por los límites detallados. Siguiente bloque41–42 para empaquetado y aceptación, conservando los pendientes anteriores.

## D6P6 · Presupuesto

La migración8 añade cuentas mensuales y reservas monetarias a las anteriores reservas de intentos, que siguen con amount_cents=0. Las operaciones de scanners actuales continúan offline y no adquieren por ello un precio de hosting ni permiso para consumir un proveedor. Los caps Lite3000, L7000 y XL30000 céntimos se contrastan con config/plans.json. La unidad es tenant/workspace por mes natural UTC; impuestos, FX, mínimos y márgenes entran en las tarifas del servidor. No es una tarifa comercial ni un sistema de facturación fiscal.

BudgetPolicy declara plan, compromiso fijo, margen y referencia revisada de asignación compartida. Debe incluir mínimos, anualidades de caja y costes comunes pertinentes: la biblioteca no descubre una factura omitida. Rate conserva versión, fuente, revisión comercial, vencimiento, moneda, decimal string y límites. El cálculo redondea hacia arriba después de impuestos/FX, sin floats. Una tarifa sin hard limit verificado ni margen explícito revisado no admite reservas. Un margen es una hipótesis revisada, no un límite contractual del proveedor.

Ledger reserva peor caso bajo BEGIN IMMEDIATE, con principal humano budget.manage, tenant y clave estable. Replay idéntico conserva reserva; distinto payload/rate/binding da409. start conserva fondos; cancel libera solo antes de empezar; uncertain conserva fondos como reconciliation_required. Un crash después de start no libera dinero automáticamente. Settle admite factura tardía incluso después de liberar una reserva, contabiliza el pasivo en su periodo original, conserva referencia/hash y congela nuevas reservas si supera previsión/cap. No oculta gasto para aparentar cumplimiento del límite. Cambiar configuración del periodo bloquea nuevas operaciones hasta conciliación fuera del flujo actual; no hay endpoint de upgrade o reset del saldo.

La API expone lectura y operaciones nominadas de reserva/estado/conciliación. Son registros locales, sin llamada pagada, contratación, transferencia ni auto-upgrade. Las tools de modelos no incluyen mutaciones de presupuesto. No hay integración con factura real de hosting/proveedor, hard limits productivos ni alertas externas. El suelo de autorización/aislamiento/auditoría no se rebaja cuando el saldo se agota. config/plans.json conserva DESIGN_ONLY_NOT_ENFORCED para la oferta e infraestructura globales: el ledger acotado no convierte todo ese diseño en enforcement de gasto externo.

## D7P1 · TypeScript/Hono y eventos

typescript/src contiene DTOs/validadores de activos, páginas, jobs, presupuestos y delegaciones; el cliente añade lecturas nominadas de findings/política/reportes y preflight estático. Identidad y tenant se fijan al construir el cliente en servidor. No se acepta un path/URL genérico, un método de herramienta o credenciales del navegador. Se limita tamaño de respuesta, timeout, redirects, JSON, estado y pertenencia del tenant donde está presente en el contrato. Errores remotos no reenvían texto/trace del proveedor; se normalizan, y no hay retries automáticos que consuman dos veces una delegación.

La validación TypeScript estricta requiere tsc de la dependencia fijada; el transpiler offline nativo de Node solo verifica ejecución y no se presenta como typecheck. Las pruebas distinguen esa limitación local del job CI. Hono aporta rutas de lectura cerradas y depende de un resolver que autentique sesión y seleccione credencial/tenant en servidor: el SDK no inventa la identidad de AgntiaPro. Un URL aprobado exige también controles de DNS/egress de la red; no es una frontera SSRF universal para configuración administrada arbitraria.

Las tres tools agénticas requieren objeto vacío y reciben recurso/delegación de código del host. El backend conserva manifest, TTL, política vigente, revocación y consumo de un uso. No se usa un owner oculto para saltar agent_gateway_required. El patchset de integración es [propuesto](../../../integration/PATCHSET-AGENTE.md), no se ha aplicado ni se han cotejado las interfaces reales del repo madre.

El outbox se crea en la misma transacción de auditoría para estados seleccionados de jobs y presupuesto. Los envelopes contienen referencias, fecha, tipo, correlación y hash, sin documentos ni tokens. Poll es scoped y acotado; ACK valida id/hash/tenant/capacidad, se persiste y admite repetición. SyntheticConsumer muestra deduplicación durable y efecto local en la misma transacción antes de ACK. La entrega es at-least-once. No hay bus remoto, entrega push, scheduler alternativo ni exactly-once HTTP. Un cursor no se debe avanzar más allá de un evento no procesado. El catálogo actual no emite cada evento de todos los dominios.

## D7P2 · Interfaz humana

La consola existente se amplía con activos, presupuesto y propuestas. Enseña incertidumbre, cobertura y frescura sin verde global. Cada acción consulta de nuevo el backend. El detalle de propuesta muestra acción, destino local, impacto, hash, revisión, caducidad, motivo y fuentes; una casilla de lectura habilita el botón, pero solo el backend decide autorización. Otro humano debe aprobar y un409 exige refrescar. El viewer puede leer pero no revisar. El origen de software y los servicios del cliente no se modifican por aprobar interpretación de un finding.

Los documentos se descargan como vistas redactadas con control de acceso nuevo. Encontrar un ID no permite leer otro tenant. El DOM se construye con textContent y CSP; no hay scripts de terceros ni almacenamiento persistente de tokens. Cambiar organización o cerrar sesión borra vistas y memoria, con generaciones para respuestas tardías. Hay móvil/escritorio, foco y labels; falta auditoría WCAG formal, pruebas completas de usabilidad y BFF/login final de AgntiaPro. El token manual en memoria es una solución de piloto, no el UX final para clientes.

## D7P3 · E2E

Se enlazan grant/snapshot, job durable con resultado normalizado sintético, finding, custodia/revisión de documento, propuesta, aprobación, reporte y evento. Se prueba rechazo de viewer, conflicto ante aprobación repetida/concurrente, credencial revocada, tenant ajeno y ausencia de datos previos al cambiarlo. Otro recorrido combina aplicabilidad insufficient_information con presupuesto exhausted, sin garantía global.

Este E2E no invoca herramientas reales: los contratos Docker existentes sí ejecutan herramientas offline y retests de fixtures. Se preserva esa diferencia y no se narra una sola demo productiva con conectores que no existen. Evaluaciones de gateway existentes cubren ataques y tareas legítimas en alcance acotado; no demuestran seguridad universal de un modelo. No se activan los tracks M1 pendientes para completar una tabla. No se ha grabado vídeo de extremo a extremo con herramientas reales en este bloque.

## D7P4 · Hardening y recuperación

Pruebas de entradas desconocidas, identidad inyectada, números no finitos y semilla20261111, límites de permisos, replay de eventos y fallos de auditoría complementan la batería anterior. El ledger se revierte si falla su auditoría; no queda saldo fantasma ni evento de éxito. La migración7→8 conserva gobernanza/historia/auditoría.

Backup de laboratorio quiesced usa SQLite backup y ciphertext referenciado, configuración cifrada y clave externa independiente. El bundle AES-GCM autentica contenido; restore verifica hashes, paths permitidos, SQLite y cadena de auditoría en destino nuevo. Corrupción, otra clave o destino existente se rechazan. La restauración crea RESTORE_BLOCKED: API, servicios autenticados, ingestión y readiness quedan cerrados hasta conciliación. No se publican claves ni se eliminan restricciones posteriores al backup por asumir que el histórico es actual.

El bundle excluye árboles de snapshots y candidatos. Es recuperación parcial verificable de datos/custodia de laboratorio, no un backup productivo completo. Exige detener escritores externos y resolver jobs/efectos inciertos. Quedan restauración integral con snapshots, claves/rotaciones reales, privacidad actual, RTO/RPO, fallos de infraestructura combinados y revisión independiente. La licencia del código propio sigue pendiente, así como revisión legal y SBOM/vulnerabilidades transitivas completos.

La medición local ejecutó100 consultas ASGI de workspace por plan, tras10 warmups, sin TCP/TLS/scanners y con SDK ausente localmente. Cero errores; p50/p95, CPU, RSS y disco reales están en evidence/performance-local.json. No son capacidades de auditoría por plan ni coste mensual medido. El inventario de dependencias es metadata de distribuciones directas; vulnerabilidades NOT_EXECUTED y licencia PENDING, no un sello limpio.

## Ejecución y límites de la evidencia

Baseline:168 descubiertas,156 correctas,12 skips. Primera suite con el bloque:187 descubiertas,174 correctas,13 skips;8 Docker,4 SDK local y1 socket loopback denegado. Node offline:7 casos,5 correctos y2 skips (Hono sin instalar y contrato HTTP no lanzado). Esos conteos no se suman como pruebas distintas cuando el wrapper Python invoca la misma suite Node. El primer comando del wrapper baseline omitió su flag --output y terminó en usage; la suite baseline sí se ejecutó después. La primera instalación npm fue denegada por red/sandbox y una autorización quedó interrumpida con el reinicio del entorno: no se declara instalación local ni tsc/Hono correctos por ello.

La CI se configura para instalar paquetes fijados, typecheck real, contrato Node↔FastAPI, browser de revisión/descarga y contratos Docker/observabilidad. El estado remoto se añadirá con SHA/jobs cuando termine; hasta entonces es NOT_VERIFIED para los nuevos checks. No extrapolar el PASS de la PR anterior al código nuevo. El informe y evidence/ distinguirán el SHA probado de commits documentales posteriores.

No hay compras, envío de correo/notificaciones, despliegue, merge a main ni cambios en `/agente`. Los servicios de pago, egress externo y uso de clientes siguen sin habilitar. El siguiente bloque no borra los pendientes de gates anteriores.

## Cierre de dependencias y verificación remota

La primera implementación `416705d7c712a64dff6e8a485dc3b169aa143774` pasó los cinco workflows. El cierre consultó la [release oficial Hono4.13.18](https://github.com/honojs/hono/releases/tag/v4.13.18), publicada el11-11-2026; se fijó esa versión en lugar del pin inicial4.11.4. CI `5f6960d170e72426b2f022b5bc3122a7bdfd2a9b` compiló tsc estricto y pasó Node/Hono, la batería Python y `npm audit --omit=dev --audit-level=high --json`, sin vulnerabilidades notificadas para las dependencias runtime de npm en esa consulta. No cubre las dependencias Python, feeds futuros ni revisión de código/licencia.

El lockfile se recuperó del resultado real de npm en CI, con integrities de Hono4.13.18 y TypeScript5.9.3; no se inventaron checksums. La última revisión cambia a npm ci y normaliza errores de validación del SDK. Su SHA probado y resultados definitivos se registrarán en evidence/ci.json. La compilación offline local sigue sin sustituir tsc ni el contrato HTTP.

## Resultado final verificado

Código final probado: `7e271ae3dd16ed88891990b1a82cdb866ec081f0`. Cinco workflows de push terminados en success. Python3.11/3.12:187 casos descubiertos,179 pasan en el núcleo y8 Docker se ejecutan en su job separado con8 correctos; total187 casos Python distintos, cero fallos. No se suman las dos versiones de Python ni las repeticiones de demo/recovery. El wrapper contractual Python ejecuta también Node contra FastAPI real en loopback.

Node descubre7 casos: en ejecución standalone pasan6 y omite el caso que requiere servidor Python; dentro del wrapper con servidor real y Hono instalado ese caso también se ejecuta. No se cuentan esas dos ejecuciones como14 casos distintos. tsc estricto y npm ci con lock e integrities verificados pasan; npm audit runtime devuelve0 avisos en esta consulta. Esto no declara que el código esté libre de vulnerabilidades ni cubre toda la cadena Python/transitiva.

Chromium real verifica escritorio/móvil, rechazo de viewer, aprobación por otro humano, descarga de vista, cambio positivo de tenant, limpieza ante logout, presupuesto agotado visible, cero errores JS y sin overflow. Capturas sintéticas de la revisión previa5f6960 fueron descargadas e inspeccionadas visualmente; las capturas de la revisión final, hashes y artifactID están en evidence/ci.json. Collector OTLP/Prometheus y los contratos reales offline de scanners también pasan.

Las evidencias guardan URLs de runs/jobs y diferencian este SHA de commits posteriores exclusivamente documentales. Los cinco gates completos conservan PARTIAL: sin proveedor pagado conectado, wiring real de AgntiaPro, aceptación independiente, UX final, recuperación productiva integral ni demostración universal de seguridad/cumplimiento. PR#8 queda abierta en draft y apilada; main y despliegue permanecen sin cambios. Siguiente bloque:41–42.
