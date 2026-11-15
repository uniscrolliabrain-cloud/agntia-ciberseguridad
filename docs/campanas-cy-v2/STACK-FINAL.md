# Stack y librerías del repo acabado

**Fecha:** 2026-11-15. **Marco superior:** [CONCEPT-MASTER.md](CONCEPT-MASTER.md).
**Base real:** `pyproject.toml`, `typescript/package.json` y código de `main` (`b2cea46`). **Regla:** no introducir una dependencia que no resuelva un problema medido;
cada capa tiene una elección y una alternativa descartada con motivo.

## 1. Principios

1. **Aburrido y maduro** antes que novedoso: FastAPI, PostgreSQL, S3, OTel.
2. **Licencias permisivas** (MIT/BSD/Apache-2.0); LGPL solo como proceso separado; AGPL fuera.
3. **Sin lock-in**: PostgreSQL estándar, S3 API, OTLP, JWT/OIDC.
4. **Pocas piezas**: un servicio, un worker, una base, un bucket. Nada de microservicios.
5. **Reproducible**: versiones fijadas, imágenes por digest, reglas por hash, SBOM propio.

## 2. Núcleo (se mantiene)

| Capa | Elección | Versión / nota |
|---|---|---|
| Lenguaje | Python | 3.12 recomendado; CI 3.11 y 3.12 |
| API | FastAPI | `>=0.115,<1` |
| Contratos | Pydantic v2 | `>=2.10,<3`, `extra="forbid"` |
| Servidor | Uvicorn | `>=0.30,<1`, un worker por proceso |
| Cripto | `cryptography` | AES-256-GCM, Ed25519, base64 estricto |
| Esquemas | `jsonschema` | validación de documentos exportados |
| CLI | `argparse` (stdlib) | sin Typer/Click: menos superficie |

No se cambia FastAPI ni Pydantic: reescribir el núcleo no aporta valor y rompe 190 tests.

## 3. Persistencia (cambio principal del estado final)

| Pieza | Ahora | Final | Motivo |
|---|---|---|---|
| Motor | SQLite (`sqlite3` stdlib) | **PostgreSQL 16+** | Concurrencia real, réplica, RLS, backup PITR |
| Driver | stdlib | **psycopg 3** | Async, tipos nativos, pool |
| Migraciones | SQL versionado propio | **Alembic** o SQL idempotente versionado | Trazabilidad y rollback |
| Acceso | SQL directo | SQL directo + helpers | Sin ORM: las consultas de seguridad se leen y auditan |
| Aislamiento | `tenant_id` en cada consulta | `tenant_id` + **RLS** opcional | Defensa en profundidad |
| Búsqueda | LIKE | `pg_trgm` + índices GIN | Búsqueda de findings sin Elasticsearch |
| Grafos | tablas | **CTE recursivas** + tablas de aristas | Neo4j se pospone hasta medir profundidad |

Descartado por ahora: SQLAlchemy ORM (oculta SQL crítico), Neo4j (otra base que operar),
Elasticsearch/OpenSearch (peso y coste para el piloto), Redis (PostgreSQL cubre locks y caché).

## 4. Jobs, colas y eventos

| Pieza | Elección | Nota |
|---|---|---|
| Cola | Tabla de jobs + `FOR UPDATE SKIP LOCKED` | Ya existen leases/fencing; no hace falta broker |
| Reintentos | Backoff exponencial con jitter y DLQ en tabla | Replay idempotente |
| Outbox | Tabla outbox + dispatcher | At-least-once, dedup por id+hash |
| Bus del padre | Adaptador HTTP/NATS **solo cuando se conozca** | No inventar Kafka antes de tener consumidor |
| Scheduler | Un único scheduler con lease | Sin segundo orquestador empresarial |

Descartado: Celery (worker + broker extra), Kafka (complejidad operativa), SQS (lock-in cloud).

## 5. Evidencia y custodia

| Pieza | Elección |
|---|---|
| Objetos | S3 API: MinIO en laboratorio, R2/S3 en producción (`boto3`) |
| Cifrado | Envelope: AES-256-GCM por objeto, clave por tenant, AAD con tenant+id |
| Claves | KMS cloud o **Vault Transit**; en laboratorio, variables del host |
| Integridad | SHA-256 + firma Ed25519 del manifiesto de evidencia |
| Retención | Política por tenant con hold legal y purga auditada |

Descartado: cifrar en SQLite (no escala), GPG (operación frágil), claves en la base.

## 6. Seguridad y policy

| Pieza | Elección | Estado |
|---|---|---|
| Policy engine | Propio, determinista y versionado | Ya existe; se mantiene |
| Alternativa | OPA/Rego | Solo si la expresividad se queda corta |
| Identidad | OIDC/JWT del padre validado con **PyJWT[crypto]** o `authlib` | Nuevo en CY-V2-02/38 |
| mTLS | Terminación en proxy (Caddy/Nginx) | No en la app |
| Tokens de agente | Delegación de un uso firmada (HMAC/Ed25519) | Ya existe |
| Sanitización | `nh3` para HTML, sin render de contenido externo | Reportes |
| XML | `defusedxml` | Si entra algún feed XML |

Descartado: Cedar (curva de aprendizaje sin necesidad), Keycloak propio (el padre ya tiene IdP),
Passport/Clerk (identidad duplicada), LLM como policy.

## 7. Escáneres y supply chain

| Herramienta | Uso | Licencia |
|---|---|---|
| Gitleaks | Secretos | MIT |
| OSV-Scanner | Dependencias | Apache-2.0 |
| Semgrep CE | SAST con reglas propias | LGPL-2.1 (proceso separado) |
| Trivy | Imágenes, IaC, SBOM | Apache-2.0 |
| Syft (opcional) | SBOM CycloneDX detallado | Apache-2.0 |
| Cosign/Sigstore (fase release) | Firma de artefactos | Apache-2.0 |

Regla: imagen por `sha256:<64>`, reglas y feeds con fecha y hash; escáner ausente = `not_tested`,
nunca limpio.

## 8. Inteligencia y conectores

| Fuente | Cliente | Nota |
|---|---|---|
| NVD/CVE | `httpx` + caché PostgreSQL | API key opcional, rate limit |
| CISA KEV | JSON oficial | Diario |
| EPSS | API FIRST | Diario, guardar fecha |
| OSV | API/DB local | Ya integrado |
| MITRE ATT&CK | STIX/JSON | Versionado |
| AWS | `boto3` (extra `cloud-aws`) | Read-only, roles scoped |
| Azure | `azure-identity` + `azure-mgmt-*` | Read-only |
| GCP | `google-cloud-asset` | Read-only |
| SIEM/EDR | Adaptadores HTTP read-only | Wazuh/Defender primero |

Los SDK cloud van en **extras opcionales** para que el núcleo siga instalándose sin ellos.

## 9. SDK TypeScript

| Pieza | Elección |
|---|---|
| Lenguaje | TypeScript 5.9, `strict`, ESM |
| Framework host | Hono 4.13 |
| HTTP | `fetch` nativo, sin axios |
| Validación | Validadores propios + **tipos generados** desde JSON Schema de Pydantic |
| Tests | `node:test` (ya), sin Jest/Vitest |
| Paquete | privado, tarball `npm pack`, semver |

Se evita Zod en runtime: duplicaría los contratos de Pydantic. El JSON Schema es la fuente única.

## 10. Observabilidad

| Pieza | Elección |
|---|---|
| Trazas | OpenTelemetry SDK + OTLP/HTTP (ya instalado) |
| Métricas | `prometheus-client` (ya) |
| Logs | `logging` stdlib con formatter JSON propio |
| Backend | Grafana + Loki + Tempo self-host, o el del cliente |
| Correlación | `correlationId`/`causationId` en API, jobs y eventos |

Descartado: Datadog/Sentry (coste y salida de datos), `structlog` (dependencia innecesaria).

## 11. Informes

| Formato | Librería |
|---|---|
| JSON | Pydantic |
| HTML | Jinja2 con autoescape |
| SARIF 2.1.0 | Emisor propio validado contra schema |
| PDF | WeasyPrint (BSD) cuando HTML esté estable |
| Firma | Ed25519 sobre el manifiesto del informe |

Cada claim cita finding, snapshot y evidencia; el informe incluye `notTested` y frescura de feeds.

## 12. Calidad y CI

| Pieza | Elección |
|---|---|
| Tests | `unittest` (190 actuales) + **Hypothesis** para parsers |
| Contratos API | **Schemathesis** sobre OpenAPI |
| Integración | **testcontainers** para PostgreSQL |
| Carga | Locust o k6 en campaña de rendimiento |
| Lint/format | Ruff |
| Tipos | mypy en modo estricto progresivo |
| Seguridad CI | CodeQL, dependency review, OSV, Trivy de la imagen |
| SBOM | CycloneDX del propio middleware |

`pytest` no se introduce: migrar 190 tests no aporta seguridad y sí riesgo.

## 13. Empaquetado y despliegue

| Pieza | Elección |
|---|---|
| Dependencias | `uv` con lock reproducible; `pip` como fallback |
| Imagen | `python:3.12-slim` multi-stage, usuario no root, FS read-only |
| Local | Docker Compose (ya en `infra/`) |
| Producción | Contenedor + PostgreSQL gestionado + S3 + KMS; Kubernetes solo si el padre lo exige |
| Infra | Terraform cuando haya nube fija |
| Artefactos | wheel + tarball SDK + SBOM + firma |

Descartado: serverless (frío y límites), Kubernetes temprano (coste operativo), monorepo de 14
servicios.

## 14. Política de versiones y licencias

- Rangos en `pyproject.toml`, versiones exactas en el lock.
- Escáneres por digest; reglas y feeds por hash y fecha.
- Actualización mensual con canary y rollback; CVEs críticas en 72 h.
- Licencias permitidas: MIT, BSD-2/3, Apache-2.0, ISC, MPL-2.0.
- LGPL solo como binario separado (Semgrep). AGPL y SSPL prohibidas en el núcleo.
- Revisión legal de reglas, feeds y modelos antes de uso comercial.

## 15. Qué no se usará

LangChain/LlamaIndex, base vectorial, Kafka, Redis, Elasticsearch, Neo4j, GraphQL, gRPC,
microservicios, Kubernetes temprano, ORM pesado, Datadog/Sentry, Keycloak propio, Passport/Clerk,
cualquier SDK que exija enviar datos del cliente a un SaaS sin DPA.

## 16. Mapa de introducción por campaña

| Campaña | Introduce |
|---|---|
| 02 | PyJWT/authlib, RLS y matriz de auth |
| 05 | psycopg 3, Alembic, SKIP LOCKED |
| 06 | S3/boto3, KMS/Vault, firma Ed25519 |
| 09–11 | conectores cloud como extras |
| 12–14 | CTE recursivas, pg_trgm |
| 15–16 | clientes NVD/KEV/EPSS con caché |
| 17–19 | esquema de eventos y cases |
| 23–26 | harness de inyección y detección de comportamiento |
| 29–31 | parches en sandbox y re-scan |
| 36–37 | Jinja2, SARIF, PDF |
| 38–39 | manifiesto de capacidades y SDK generado |

## 17. Coste

Todo el stack base es OSS y corre en un VPS pequeño. Los únicos costes variables son PostgreSQL
gestionado, object storage, KMS y egress. Nada exige una suscripción para el piloto; las
alternativas gestionadas se eligen cuando el cliente lo pida, no por defecto.
