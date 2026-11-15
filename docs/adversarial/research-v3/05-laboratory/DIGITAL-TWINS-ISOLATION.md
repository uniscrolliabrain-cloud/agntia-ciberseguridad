# Sandboxes, digital twins y datos sintéticos
## Problema real
Un clon de repositorio **no** reproduce automáticamente IAM, tráfico, colas, secretos, estado, cargas, redes, proveedores, DNS o comportamiento humano. Una copia de DB con nombres falsos tampoco es necesariamente anónima ni fiel.

## Modelo de fidelidad por capas
- **L0 Código:** commit, dependencias, build reproducible, tests.
- **L1 Servicios:** procesos, endpoints, contratos y versiones.
- **L2 Datos:** schemas, cardinalidades, relaciones, distribuciones, constraints, outliers y datos sintéticos.
- **L3 Identidad:** usuarios ficticios, roles, scopes, sesiones, credenciales falsas, políticas.
- **L4 Infraestructura:** colas, caches, DNS, red, contenedores, servicios externos simulados.
- **L5 Comportamiento:** paridad de tests con entorno permitido, latencia, concurrencia y carga.
- **L6 Fallos:** cortes, pérdida de datos, reintentos, degradación, backups y restore.
Cada ejecución declara **fidelity coverage**, componentes ausentes y mocks. No afirmar 'réplica exacta' sin validación.

## Estrategia de datos sintéticos
Generar por esquema y constraints; preservar integridad referencial, nulos, distribuciones y correlaciones relevantes; evitar muestreo de registros identificables. Medir divergencia y reidentificación; secretos siempre ficticios. Datos reales solo bajo contrato, proceso segregado y política de minimización; preferir nunca introducirlos en el laboratorio adversarial.

## Aislamiento de ejecución
Comparar Docker rootless+seccomp+AppArmor, gVisor, Kata y microVM Firecracker. No prometer aislamiento fuerte por `--network none` solamente: se necesita control del host, credenciales, volúmenes, sockets, syscalls, kernel, quotas y egress. Los agentes de código son **código no confiable**. No montar socket Docker, directorio HOME, SSH, credenciales de nube ni tokens GitHub en su worker.
**Control plane:** servicio con acceso a metadatos y autorizaciones, sin ejecución de código de cliente.
**Execution plane:** VM/worker descartable, snapshot de entrada, recursos limitados, red denegada, filesystem temporal, observabilidad externa.
**Evidence plane:** importador que valida hashes, tipo y tamaño, escanea/redacta artefactos antes de almacenarlos; los artefactos no son instrucciones.

## Pruebas de aislamiento previas a cualquier PoC
Intento de salida HTTP/DNS; mount escape; symlink traversal; acceso a host secrets; escritura fuera de workspace; consumo infinito CPU/memoria/disco; proceso huérfano; kill switch; worker crash; artefacto malicioso; contaminación entre tenants; destrucción y limpieza de discos/volúmenes. Ejecutar exclusivamente en infraestructura controlada.

## Modos de operación
**OFFLINE_REPO:** análisis local estático, sin red. **LAB_CLONE:** pruebas activas en réplica sintética. **CUSTOMER_STAGING:** pruebas delimitadas con autorización y red privada controlada. **CUSTOMER_PRODUCTION:** perfil restringido y aprobado expresamente, por defecto pasivo; pruebas destructivas excluidas salvo proceso extraordinario de autorización y continuidad.
