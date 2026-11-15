# 02 — Cuentas, proveedores y servicios: cuándo necesitas cada uno
## Grupo 0 — Reutilizar antes de comprar
| Servicio | Para qué | ¿Cuenta nueva? | Acción founder | Acción agente | Cuándo |
|---|---|---|---|---|---|
| GitHub | repo, PR, CI, permisos, releases | ya disponible | revisar 2FA, colaboradores, permisos, protección main | auditar Actions, secretos referenciados y ramas | ahora |
| Doppler u otro secret manager | claves de tenants, tokens, rotación | reutilizable | confirmar workspace y quién administra | proponer nombres, scopes, rotation plan | antes de staging |
| Grafana Cloud / OTel | métricas, logs y alertas | opcional si ya existe | elegir destino y presupuesto | probar exportación sin PII | antes de operación continua |
| Neon/Postgres | DB si SQLite no satisface despliegue multi-tenant | no obligatorio para demo | aprobar migración si se justifica | evaluar datos, RLS, migraciones y rollback | después de baseline |
| Fly.io u otra VM Linux | API privada y workers | posible reutilizar | elegir región UE, coste y owner | comparar compatibilidad OCI/volúmenes | después de laboratorio |
| Cloudflare/DNS | dominio y TLS, acceso privado | reutilizable | aprobar subdominio y política | preparar DNS/TLS sin publicar | staging |
| Sentry/alertas | errores y notificaciones | opcional | designar receptor | integrar alertas y redacción | staging |
| Google Workspace/IdP | identidad humana y MFA | reutilizable | decidir SSO y operadores | validar claims/scopes y revocación | piloto |

## Grupo 1 — Herramientas sin cuenta comercial necesaria para prueba local
| Herramienta | Uso | Verificación del agente |
|---|---|---|
| Gitleaks | secretos en repos autorizados | binario versionado, caso canario, output redactado |
| OSV-Scanner | CVEs en dependencias | DB actualizada, fixture vulnerable, red controlada para updates |
| Semgrep CE | SAST | versión y licencia de reglas, fixture positivo/negativo |
| Trivy | imágenes/IaC | versión, DB/feeds, fixture y tasa de falsos positivos |
| Syft | SBOM complementario | licencia, versión y validación del formato |
| pip-audit | dependencias Python | ejecución real y estado FAIL/BLOCKED correcto |
| OWASP ZAP/Schemathesis | pruebas web/API | solo staging propio con alcance escrito |
| pytest/Hypothesis | unit/property tests | reproducibilidad y cobertura de errores |

**Advertencia:** OSS no implica reglas comerciales gratuitas ni derecho automático a redistribuir datos de vulnerabilidades. El agente registra licencia de cada componente y feed.

## Grupo 2 — Opcionales posteriores
- OpenAI/Gemini/otros LLM: no necesarios para que funcionen scanners deterministas; solo para razonamiento/reportes agénticos. Conectar uno, con cuota y contrato de datos, si aporta valor.
- Almacenamiento S3-compatible: para evidencia y backups productivos, no para demo efímera.
- SIEM/Wazuh/OpenSearch: solo si ingestión y escala lo justifican; no bloquear piloto pequeño por ellos.
- Kubernetes/Kafka: no son prerrequisitos del primer cliente.
- Servicio de firma/contratos: puede ser proceso documental controlado al principio.

## Ficha de selección que prepara el agente
Para cada candidato: URL oficial, plan/precio y fecha de consulta, región y residencia de datos, DPA, controles MFA, API/CLI, exportación/backup, coste fijo/variable, limitaciones, lock-in, alternativa autohospedada, permisos mínimos, reversibilidad. No inventar precios: marcarlos `PENDIENTE DE COTIZACIÓN` hasta verificación.

## Decisiones mínimas del founder
F01: ¿reutilizamos Doppler? F02: ¿VM dedicada o Fly para el primer laboratorio persistente? F03: ¿almacenamiento de evidencia y backup? F04: ¿primer canal de alertas? El resto se decide por gate.
