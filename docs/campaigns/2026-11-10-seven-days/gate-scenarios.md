# Matriz ejecutable de gates por fase

84 escenarios de aceptación planificados; **ninguno ejecutado por crear esta documentación**. Complementar con tests unitarios/contractuales apropiados, no inventar un número de tests pasados.

## D1P1 · Baseline, alcance y contrato de servicio

- D1P1-TEST-1 · Entorno sin Docker registra BLOCKED sin declarar pruebas runtime aprobadas. · Estado: NOT_EXECUTED.
- D1P1-TEST-2 · Checkout con cambios ajenos se conserva y la implementación no los sobrescribe. · Estado: NOT_EXECUTED.

## D1P2 · Paquete, configuración y contratos tipados

- D1P2-TEST-1 · Un campo desconocido de identidad o shell provoca422 antes de cualquier efecto. · Estado: NOT_EXECUTED.
- D1P2-TEST-2 · NaN, payload gigante o configuración insegura impiden arranque/admisión de manera explicable. · Estado: NOT_EXECUTED.

## D1P3 · Identidad, tenancy y capacidades

- D1P3-TEST-1 · PrincipalA consulta IDB y recibe404 sin metadatos, tamaño o export deB. · Estado: NOT_EXECUTED.
- D1P3-TEST-2 · Un token revocado entre petición y job no permite usar permisos antiguos. · Estado: NOT_EXECUTED.

## D1P4 · Persistencia, migraciones y auditoría

- D1P4-TEST-1 · Una migración fallida revierte DDL y preserva objetos/auditoría previos. · Estado: NOT_EXECUTED.
- D1P4-TEST-2 · Dos escrituras concurrentes con la misma identidad no crean dos objetos ni reservas. · Estado: NOT_EXECUTED.

## D1P5 · Inventario de activos y autorización de trabajo

- D1P5-TEST-1 · Una URL a metadata/link-local y un redirect fuera del grant se bloquean antes de conectar. · Estado: NOT_EXECUTED.
- D1P5-TEST-2 · Un grant caducado o revocado impide iniciar/reintentar una auditoría. · Estado: NOT_EXECUTED.

## D1P6 · Threat model y revisión de fronteras

- D1P6-TEST-1 · Cada frontera crítica tiene al menos un caso benigno y uno adversarial planificado. · Estado: NOT_EXECUTED.
- D1P6-TEST-2 · El revisor identifica bypass del gateway o socket privilegiado y bloquea la habilitación. · Estado: NOT_EXECUTED.

## D2P1 · Adquisición de snapshots sin ejecutar código

- D2P1-TEST-1 · Repo fixture con hooks, enlaces simbólicos y rutas escapadas no toca el host. · Estado: NOT_EXECUTED.
- D2P1-TEST-2 · Zip bomb, LFS/submódulo externo o fichero excesivo queda rechazado o explícitamente parcial. · Estado: NOT_EXECUTED.

## D2P2 · Runner y sandbox de herramientas

- D2P2-TEST-1 · Un proceso que intenta red/archivo fuera de política no accede al host ni a secretos. · Estado: NOT_EXECUTED.
- D2P2-TEST-2 · Timeout, fork excesivo o salida gigante produce fallo controlado y limpieza comprobada. · Estado: NOT_EXECUTED.

## D2P3 · Adaptador Gitleaks y protección de secretos

- D2P3-TEST-1 · Canario fixture genera finding, pero su valor no aparece en export/log/evento. · Estado: NOT_EXECUTED.
- D2P3-TEST-2 · Error de scanner, versión desconocida o JSON inválido no se convierte en scan limpio. · Estado: NOT_EXECUTED.

## D2P4 · OSV, inventario de dependencias y SBOM

- D2P4-TEST-1 · Un lockfile vulnerable y otro benigno producen resultados esperados sin instalar paquetes del cliente. · Estado: NOT_EXECUTED.
- D2P4-TEST-2 · DB sin red/caducada o ecosistema no soportado produce partial/stale, no safe. · Estado: NOT_EXECUTED.

## D2P5 · Semgrep CE y reglas propias revisadas

- D2P5-TEST-1 · Código fixture vulnerable se detecta y su variante corregida no mantiene el mismo finding confirmado. · Estado: NOT_EXECUTED.
- D2P5-TEST-2 · Comentario hostil contra el auditor no modifica reglas, scope ni resumen autoritativo. · Estado: NOT_EXECUTED.

## D2P6 · Trivy para imágenes e IaC del piloto

- D2P6-TEST-1 · Imagen de laboratorio afectada por advisory produce evidencia del componente realmente presente. · Estado: NOT_EXECUTED.
- D2P6-TEST-2 · No hay imagen/IaC o DB reciente y el reporte distingue not_tested/partial. · Estado: NOT_EXECUTED.

## D3P1 · Jobs, idempotencia y estados fiables

- D3P1-TEST-1 · Dos peticiones simultáneas iguales conservan un job y una reserva de coste. · Estado: NOT_EXECUTED.
- D3P1-TEST-2 · Una respuesta202 nunca aparece en UI como auditoría completada. · Estado: NOT_EXECUTED.

## D3P2 · Worker con leases, fencing y retries

- D3P2-TEST-1 · Un worker con lease vieja no confirma ni sobrescribe el resultado del nuevo. · Estado: NOT_EXECUTED.
- D3P2-TEST-2 · Actor/grant revocado antes de reclamar o antes de efecto externo bloquea trabajo. · Estado: NOT_EXECUTED.

## D3P3 · Normalización, deduplicación y contexto

- D3P3-TEST-1 · Dos herramientas que señalan lo mismo se relacionan sin borrar sus observaciones originales. · Estado: NOT_EXECUTED.
- D3P3-TEST-2 · Un finding desaparece por parser fallido y no se marca automáticamente arreglado. · Estado: NOT_EXECUTED.

## D3P4 · Custodia, redacción y cadena de evidencia

- D3P4-TEST-1 · Canarios secretos ausentes de logs/export/eventos y un tenant no descarga evidencia ajena. · Estado: NOT_EXECUTED.
- D3P4-TEST-2 · Clave perdida/alteración de fichero produce error de integridad, no original falso o vacío. · Estado: NOT_EXECUTED.

## D3P5 · Priorización, excepciones y revisión humana

- D3P5-TEST-1 · Advisory conocido sin evidencia de exposición no se convierte en explotación confirmada. · Estado: NOT_EXECUTED.
- D3P5-TEST-2 · Excepción caducada reaparece y el LLM no puede aceptar riesgo sin principal autorizado. · Estado: NOT_EXECUTED.

## D3P6 · Reportes y primera vertical AppSec

- D3P6-TEST-1 · Fixture vulnerable y benigno producen informes distintos con evidencia, sin secreto canario. · Estado: NOT_EXECUTED.
- D3P6-TEST-2 · Errores de scanner o cobertura ausente se muestran en resumen ejecutivo y técnico. · Estado: NOT_EXECUTED.

## D4P1 · OpenTelemetry y correlación extremo a extremo

- D4P1-TEST-1 · Una ejecución asíncrona conserva trazabilidad sin aceptar identidad del baggage externo. · Estado: NOT_EXECUTED.
- D4P1-TEST-2 · Un canario secreto no aparece en span, evento, excepción o export OTLP. · Estado: NOT_EXECUTED.

## D4P2 · Métricas, SLIs y presupuesto de error

- D4P2-TEST-1 · Cienmil valores distintos de un atributo externo no crean cienmil series. · Estado: NOT_EXECUTED.
- D4P2-TEST-2 · Error/partial de scanner aumenta cobertura incompleta y no mejora artificialmente tasa de seguridad. · Estado: NOT_EXECUTED.

## D4P3 · Logs estructurados y privacidad de telemetría

- D4P3-TEST-1 · Un mensaje hostil con saltos/HTML/ANSI no falsifica entradas ni ejecuta contenido en UI. · Estado: NOT_EXECUTED.
- D4P3-TEST-2 · Redacción y export impiden recuperar secretos centinela de cualquier salida autorizada. · Estado: NOT_EXECUTED.

## D4P4 · Dashboards y navegación de investigación

- D4P4-TEST-1 · ViewerA no obtiene series/eventos deB a través de dashboard o enlace de trace. · Estado: NOT_EXECUTED.
- D4P4-TEST-2 · Datos ausentes y collector caído se muestran como unknown/stale, no verde. · Estado: NOT_EXECUTED.

## D4P5 · Ingestión de eventos y conectores pasivos

- D4P5-TEST-1 · Evento repetido, adelantado o fuera de orden conserva historia sin duplicar incidente. · Estado: NOT_EXECUTED.
- D4P5-TEST-2 · Un payload que declara tenantB con credencialA se rechaza sin persistir contenidoB. · Estado: NOT_EXECUTED.

## D4P6 · Carga, retención y resiliencia de observabilidad

- D4P6-TEST-1 · Caída del backend de logs/traces no permite acción denegada ni bloquea por tiempo indefinido la API. · Estado: NOT_EXECUTED.
- D4P6-TEST-2 · Una ráfaga sintética respeta límites y registra pérdidas sin declarar observación completa. · Estado: NOT_EXECUTED.

## D5P1 · Registro de agentes, tools y capacidades delegadas

- D5P1-TEST-1 · Un agenteA delega y el hijo no recibe más herramientas/destinos que el padre. · Estado: NOT_EXECUTED.
- D5P1-TEST-2 · Un token de actor/tenant/audiencia distintos se rechaza antes de resolver secretos. · Estado: NOT_EXECUTED.

## D5P2 · Policy engine y control determinista de acciones

- D5P2-TEST-1 · Una salida maliciosa del modelo pide una tool/argumento no permitido y el executor la bloquea. · Estado: NOT_EXECUTED.
- D5P2-TEST-2 · Política caducada o motor caído no se resuelve ejecutando como owner. · Estado: NOT_EXECUTED.

## D5P3 · Flujos de datos, egress y cuarentena

- D5P3-TEST-1 · Lectura permitida de un documento privado seguida de envío a destino nuevo queda denegada. · Estado: NOT_EXECUTED.
- D5P3-TEST-2 · Una instrucción inyectada en log/repo/PDF no amplía tools ni permisos del plan. · Estado: NOT_EXECUTED.

## D5P4 · MCP, skills y cambios de supply chain

- D5P4-TEST-1 · Una descripción/schema de tool cambia y su autorización anterior deja de valer. · Estado: NOT_EXECUTED.
- D5P4-TEST-2 · Un MCP externo intenta reutilizar un token de otro recurso y no obtiene acceso. · Estado: NOT_EXECUTED.

## D5P5 · Evaluaciones adversariales con utilidad

- D5P5-TEST-1 · Una suite sin ataques exitosos pero sin tareas benignas completas no se declara excelente defensa. · Estado: NOT_EXECUTED.
- D5P5-TEST-2 · Cambio de modelo/prompt/policy invalida resultados previos para esa configuración. · Estado: NOT_EXECUTED.

## D5P6 · Revocación, kill switch y aprobación de efectos

- D5P6-TEST-1 · Agente revocado entre dos llamadas no ejecuta la segunda por caché o lease antiguo. · Estado: NOT_EXECUTED.
- D5P6-TEST-2 · Timeout tras efecto externo se reconcilia; el kill switch no promete deshacerlo mágicamente. · Estado: NOT_EXECUTED.

## D6P1 · Aplicabilidad legal y controles de cumplimiento

- D6P1-TEST-1 · Cliente sin finalidad/rol suficiente queda insufficient_information, no compliant. · Estado: NOT_EXECUTED.
- D6P1-TEST-2 · Una fecha de guía contradice fuente normativa y bloquea automatización del plazo. · Estado: NOT_EXECUTED.

## D6P2 · Privacidad, retención y brechas de datos

- D6P2-TEST-1 · Borrado o export deA no incluye evidencia deB ni destruye legal hold vigente. · Estado: NOT_EXECUTED.
- D6P2-TEST-2 · Una alerta técnica sin datos personales no dispara automáticamente notificaciónRGPD. · Estado: NOT_EXECUTED.

## D6P3 · Antifraude y verificación por contexto

- D6P3-TEST-1 · Mensaje con supuesto nuevoIBAN no convierte su propio enlace/teléfono en canal confiable. · Estado: NOT_EXECUTED.
- D6P3-TEST-2 · Dominio/voz sospechosos no producen veredicto definitivo ni bloqueo laboral automático. · Estado: NOT_EXECUTED.

## D6P4 · Incidentes y contención propuesta

- D6P4-TEST-1 · Alerta falsa no dispara revocación masiva o borrado automático. · Estado: NOT_EXECUTED.
- D6P4-TEST-2 · Contención aprobada de laboratorio conserva rollback y no afecta otro tenant. · Estado: NOT_EXECUTED.

## D6P5 · Remediación revisable y retest

- D6P5-TEST-1 · Origen cambió tras aprobación y la propuesta queda stale/conflict en lugar de pisarlo. · Estado: NOT_EXECUTED.
- D6P5-TEST-2 · Finding ausente por scanner fallido no se marca verified_fixed. · Estado: NOT_EXECUTED.

## D6P6 · Reservas económicas y servicios comerciales

- D6P6-TEST-1 · Dos llamadas concurrentes no consumen el mismo saldo ni elevan el cap al agotar cuota. · Estado: NOT_EXECUTED.
- D6P6-TEST-2 · Tarifa/proveedor sin hard limit fiable queda bloqueado o usa margen explícito revisado. · Estado: NOT_EXECUTED.

## D7P1 · SDK TypeScript/Hono y contrato hacia /agente

- D7P1-TEST-1 · ClienteTS y API coinciden en errores, estados y validación de entradas desconocidas. · Estado: NOT_EXECUTED.
- D7P1-TEST-2 · Tool agéntica no puede aprobar, elevar permisos, cambiar presupuesto o ejecutar comandos arbitrarios. · Estado: NOT_EXECUTED.

## D7P2 · Interfaz operativa y experiencia humana

- D7P2-TEST-1 · Usuario cambia de tenant y no conserva datos/caché del anterior. · Estado: NOT_EXECUTED.
- D7P2-TEST-2 · Vista parcial/stale o presupuesto agotado no muestra un indicador global seguro/verde. · Estado: NOT_EXECUTED.

## D7P3 · E2E de dos tenants y recorridos de referencia

- D7P3-TEST-1 · Dos tenants, canarios y grants cruzados no contaminan reportes/artefactos/eventos. · Estado: NOT_EXECUTED.
- D7P3-TEST-2 · Una tarea legítima se completa y una salida adversarial se bloquea aun con modelo hostil. · Estado: NOT_EXECUTED.

## D7P4 · Hardening, rendimiento y recuperación

- D7P4-TEST-1 · Pérdida de proceso/collector/DB temporal se recupera sin permitir acciones indebidas ni duplicar efectos. · Estado: NOT_EXECUTED.
- D7P4-TEST-2 · Restauración reproduce scopes/evidencia y no requiere secretos publicados en Git. · Estado: NOT_EXECUTED.

## D7P5 · Empaquetado, Windows/Linux y supply chain de release

- D7P5-TEST-1 · Instalación limpia en el entorno declarado ejecuta demo/tests del alcance o registra plataforma no verificada. · Estado: NOT_EXECUTED.
- D7P5-TEST-2 · Rollback conserva evidencia y no borra cambios del usuario ni contactos/proyectos ajenos. · Estado: NOT_EXECUTED.

## D7P6 · Aceptación, reporte al founder y próximos90días

- D7P6-TEST-1 · Cada claim de producto tiene evidencia enlazada o etiqueta not_verified/deferred. · Estado: NOT_EXECUTED.
- D7P6-TEST-2 · El owner puede reproducir el piloto y comprender qué no está protegido sin leer todo el código. · Estado: NOT_EXECUTED.
