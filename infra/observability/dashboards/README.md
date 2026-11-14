# Consola mínima versionada

UI propia en `agntia_ciberseguridad/web/console.*`, entrada `/console`; datasource de negocio `/v1/tenants/{tenant}/dashboard`. No se instala Grafana ni se conecta un datasource global al navegador. Las rutas mantienen credencial solo en memoria, CSP restrictiva y autorización de cada salto. Desktop1440px y móvil390px se prueban en Chromium con fixtures y capturas de CI. La configuración Prometheus existente se mantiene para operadores, sin tenant labels.

El JSON declara unknown/not_tested/not_monitored; no deduce salud del Collector a partir de un flag. Presupuesto e incidentes se declaran not_evaluated. Las relaciones de job/evidencia requieren acceso nuevamente; se muestra que hay contexto de trace sin dar una URL a un backend global. UI no administra claves, manifests ni grants de clientes.

Grafana es opcional futuro, con revisión AGPL-3.0 y aislamiento del datasource antes de habilitarlo. No hay panel de administración o branding de terceros incorporado.
