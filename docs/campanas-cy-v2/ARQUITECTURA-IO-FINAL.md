# Arquitectura de entrada/salida del producto final

**Fecha:** 2026-11-15. **Alcance:** concepto final, no PMV. **Base:** visión R01–R10, roadmap L0–L8
y programa CY-V2. **Estado:** diseño; el código actual solo cubre una parte del plano P2–P5.

Este documento responde a una pregunta distinta de [REQUISITOS-CONEXION.md](REQUISITOS-CONEXION.md):
no «qué credenciales me das para el piloto», sino **qué entra y qué sale cuando el producto esté
terminado**, para que lo que construyamos ahora no haya que rehacerlo al conectar los 14 dominios.

## 1. Principio rector

El middleware no es un lago de datos ni un SOC. Es el **sistema de registro de exposición,
comportamiento de agentes y evidencia verificable** de AgntiaPro. Todo lo que entra es dato no
confiable; todo lo que sale es una conclusión con procedencia, cobertura y estado epistémico.

Tres invariantes gobiernan la E/S completa:

1. **Nada entra como instrucción.** Repos, logs, PDFs, issues, salidas de herramientas y documentos
   RAG son datos. Ningún contenido externo amplía permisos ni cambia política.
2. **Nada sale como veredicto sin evidencia.** Un finding, un informe y un evento citan snapshot,
   herramienta, versión, regla y fecha; la ausencia de hallazgos se publica como cobertura, no como
   seguridad.
3. **Ningún efecto sale sin aprobación vinculante.** Propuesta y ejecución son actos distintos,
   con hash, tenant, actor, objeto y TTL; el LLM nunca aprueba.

## 2. Los siete planos de E/S

| Plano | Qué transporta | Dirección | Autoridad final |
|---|---|---|---|
| **P1 Control** | Intenciones, aprobaciones, cambios de política, cancelaciones | Padre → middleware | Kernel/policy del padre |
| **P2 Observación de activos** | Snapshots de repos, imágenes, IaC, configuraciones cloud, identidades | Fuentes → middleware | Cliente autoriza el activo |
| **P3 Telemetría** | Eventos de auth, cloud audit, tool calls de agentes, SIEM/EDR, señales de fraude | Fuentes → middleware | Fuente + consentimiento |
| **P4 Inteligencia** | CVE/NVD, KEV, EPSS, OSV, ATT&CK, avisos de proveedor | Feeds → middleware | Feed con fecha y licencia |
| **P5 Evidencia** | Artefactos, hashes, extractos redactados, cadena de custodia | Middleware interno | Custodio designado |
| **P6 Acción** | Parches, contención, tickets, bloqueos de egress | Middleware → sistemas del cliente | Humano aprueba |
| **P7 Proyección** | Findings, casos, postura, informes, eventos, receipts | Middleware → padre/humanos | Middleware + kernel |

El error clásico que este diseño evita: mezclar P3 con P1. Un log que dice «ignora tus reglas» es
telemetría; una aprobación que dice «ejecuta» es control. Nunca comparten canal ni validación.

## 3. Entradas del producto final (por grupo de campañas)

### G1 · Activos y exposición

| Fuente | Qué entra | Entidad canónica | Cadencia | Confianza |
|---|---|---|---|---|
| Git/PRs (GitHub, GitLab, Azure DevOps) | Snapshot de código, rama, commit, autor | `Snapshot`, `Asset` | Por cambio y programada | T1: contenido no confiable |
| Registros de contenedores | Imagen, digest, SBOM, firma | `Asset(image)`, `Dependency` | Por push y diaria | T1 |
| IaC y configuración cloud | Terraform, CloudFormation, manifiestos K8s | `Asset`, `Configuration` | Por cambio | T1 |
| AWS/Azure/GCP read-only | Inventario, políticas, roles, buckets, redes | `Asset`, `Identity`, `Permission` | Diaria/semanal | T2: API autenticada, dato del cliente |
| IdP/SCIM | Humanos, service accounts, grupos, MFA | `Identity`, `Permission` | Diaria | T2 |
| CMDB/registro de activos | Ownership, criticidad, entorno | `Asset.owner`, `Asset.criticality` | Semanal | T2 |
| Manifiestos de agentes/MCP | Tools, skills, modelos, scopes, hashes | `AgentManifest`, `ToolManifest` | Por cambio | T1 |

### G2 · Inteligencia y detección

| Fuente | Qué entra | Entidad | Cadencia | Confianza |
|---|---|---|---|---|
| NVD/CVE, OSV | Vulnerabilidades y versiones afectadas | `IntelEntity(CVE)` | Diaria | T2 con fecha |
| CISA KEV, EPSS | Explotación conocida y probabilidad | `IntelSignal` | Diaria | T2 |
| MITRE ATT&CK | Técnicas y mapeo | `Detection.attack` | Por release | T2 |
| SIEM/EDR read-only (Wazuh, Defender, Sentinel) | Alertas, detecciones, entidades | `SecurityEvent`, `Signal` | Streaming/5 min | T2 |
| Gateway de LLM/agentes | Tool calls, prompts redactados, destinos, coste | `AgentEvent` | Streaming | T2 |
| Email gateway / ERP | Facturas, cambios de IBAN, remitentes, adjuntos | `FraudSignal` | Por evento | T2 |

### G3 · Seguridad de IA y fraude

- Corpus de evaluación propio y versionado (prompt injection directa/indirecta, poisoning de tool
  output, RAG, memoria) — **entra como fixture, nunca como ataque a terceros**.
- Metadatos de documentos RAG: fuente, sensibilidad, tenant, hash; no el contenido completo salvo
  consentimiento.
- Señales de voz/vídeo: metadatos y artefactos aportados por el cliente; el detector produce
  `suspected`, nunca `confirmed`.
- Verificación fuera de banda: referencia de directorio y método (`callback_directory`,
  `in_person`), no el número de teléfono en el prompt.

### G4/G5 · Respuesta y entrega

- Estado de ramas y CI del cliente (para verificar parches), tickets, runbooks y resultados de
  tabletop.
- Aprobaciones humanas del padre con identidad, objeto, hash y TTL.
- Telemetría de negocio: coste por tenant, uso, SLO, no datos personales.

### Lo que no entra nunca

Secretos crudos, credenciales de producción con permiso de escritura, código de clientes sin
autorización, datos personales innecesarios, muestras de terceros, resultados de escaneos no
autorizados, «resultados» que un LLM declara sin ejecución, ni contenido externo con instrucciones.

## 4. Modelo canónico (lo que se guarda y se transfiere)

| Entidad | Clave | Invariantes |
|---|---|---|
| `Tenant` | id opaco | Aísla todo; sin tenant no hay consulta |
| `Asset` | id estable + tipo | Ownership, criticidad, fuente y fecha |
| `Identity` / `Permission` | id + proveedor | Sin secretos; solo relaciones y scopes |
| `Grant` / `Consent` | id + tenant | Autoridad humana, vigencia, targets, revocable |
| `Snapshot` | hash + commit | Inmutable, sin ejecución de código |
| `Job` | id + idempotency key | Estados explícitos, lease/fencing, cancelable, replay-safe |
| `Finding` | huella regla+recurso+ubicación | Estado epistémico, revisión, historial |
| `ExposurePath` | nodos + aristas | Explicable, con confianza y evidencia por salto |
| `IntelEntity` / `IntelSignal` | CVE/purl/CPE | Freshness, licencia, versión |
| `Detection` | id + versión + hash | Regla firmada, ATT&CK, FP medidos |
| `Case` | id + tenant | Señales agrupadas, sospecha ≠ confirmación |
| `RemediationPlan` | hash del plan | Diff, impacto, precondiciones, rollback |
| `Approval` | id vinculante | Tenant+actor+objeto+hash+TTL |
| `Evidence` | hash + custodio | Cifrada, minimizada, retención y hold |
| `BudgetReservation` | tenant+mes | Céntimos, sobrecoste explícito |
| `Event` | id + secuencia | Append-only, versionado, at-least-once |
| `Receipt` | id + idempotency | Prueba de efecto, no promesa |
| `Report` | id + snapshot | Cada claim cita evidencia; incluye `notTested` |

Regla de identificadores: **opacos y estables**; nunca email, nombre de repo o IP como clave.
Regla temporal: todo en UTC, con `first_seen`, `last_seen`, `observed_at` y `valid_until`.

## 5. Salidas del producto final

### 5.1 Hacia el padre (`/agente`)

- `CapabilityManifest` semver: capacidades, schemas, efectos, scopes, aprobaciones, eventos,
  compensaciones y compatibilidad.
- `IntentEnvelope` de entrada y `EffectReceipt` de salida, con `correlationId`/`causationId`.
- Eventos de dominio versionados (`security.finding.changed`, `security.case.opened`,
  `security.remediation.verified`, …) entregados at-least-once con deduplicación por id+hash.
- Tarjetas y proyecciones para Pedro/Laia construidas **solo** desde eventos reales.

### 5.2 Hacia humanos

- Postura y cobertura: qué se probó, qué no, con qué fuentes y frescura; nunca semáforo verde por
  ausencia de datos.
- Informes ejecutivo, técnico y regulatorio con cadena causal y anexo de evidencia.
- Bandeja de aprobaciones con hash, diff, coste e impacto; historial de decisiones.
- Exportaciones: JSON/HTML primero; SARIF/PDF cuando exista pipeline validado.

### 5.3 Hacia sistemas del cliente (solo propuestas o efectos aprobados)

- PR en rama efímera con tests ejecutados; nunca push directo a la rama principal.
- Ticket/expediente con deduplicación e idempotencia.
- Contención propuesta (revocar token, aislar servicio, bloquear egress) con simulación previa y
  recibo; la ejecución real es una capacidad separada y aprobada.
- Aviso a SIEM/SOAR del cliente como evento, no como acción.

### 5.4 Hacia agentes

- Herramientas de lectura nominadas y acotadas por recurso.
- Delegaciones de un solo uso con TTL y consumo atómico.
- Ninguna herramienta de shell, HTTP libre, aprobación, compra o cambio de presupuesto.

## 6. Contrato que hay que congelar ahora (para no rehacerlo)

Aunque el producto completo llegue después, estos nueve puntos deben nacer estables:

1. Envelope de evento con `schemaVersion`, `id`, `tenant`, `sequence`, `correlationId`,
   `causationId`, `occurredAt`, `source`, `objectId`, `contentHash`.
2. Entrega at-least-once + dedup; nunca prometer exactly-once distribuido.
3. Estados de finding y de job cerrados y versionados.
4. Aprobación ligada a tenant/actor/objeto/hash/TTL, invalidable por cambio de contenido.
5. `EffectReceipt` con idempotency key, resultado y evidencia.
6. Errores con código seguro, `retryable`, `reconciliation_required` y `correlationId`; sin filtrar
   datos de otro tenant.
7. IDs opacos y paginación por cursor (`after`), no offsets.
8. Niveles de redacción (`public`, `internal`, `restricted`) y prohibición de secretos en eventos.
9. Manifiesto de capacidades con semver y política de compatibilidad.

## 7. Fronteras de confianza

- **T0** configuración del servidor y claves: solo host.
- **T1** contenido del cliente (código, documentos, issues): nunca instrucción, siempre validado.
- **T2** APIs autenticadas de terceros: dato verificado en origen, no en intención.
- **T3** salidas de modelos y agentes: propuestas no confiables.
- **T4** decisiones humanas: únicas que autorizan efectos sensibles.

Aislamiento: claves por tenant, consultas siempre filtradas por tenant del token, evidencias
cifradas con AAD, egress por allowlist, sin reutilizar credenciales entre tenants.

## 8. Escalado al estado final

| Hoy (demo) | Estado final | Qué no puede cambiar |
|---|---|---|
| SQLite + worker único | PostgreSQL + colas con leases/fencing | Estados, idempotencia y auditoría |
| Outbox por polling | Bus del padre o broker gestionado | Envelope y semántica at-least-once |
| Claves en variables | KMS/secret manager con rotación | Cifrado por tenant y AAD |
| Un nodo | Workers por perfil y tenant | Aislamiento y límites por job |
| Consola piloto | UI del padre (Laia/Pedro) | Autorización en servidor, no en UI |

## 9. Qué campañas producen cada plano

| Plano | Campañas |
|---|---|
| P1 Control | 02, 07, 25, 34, 38, 39 |
| P2 Activos | 09, 10, 11, 22 |
| P3 Telemetría | 17, 19, 20, 21, 26, 27 |
| P4 Inteligencia | 15, 16, 18 |
| P5 Evidencia | 06, 31, 37 |
| P6 Acción | 29, 30, 32, 33, 34, 35 |
| P7 Proyección | 12, 13, 14, 36, 37, 39 |

## 10. Decisiones del founder para el estado final

No son credenciales: son decisiones de producto que cambian el diseño de E/S.

1. Nube prioritaria (AWS, Azure o GCP) y si el piloto es multi-cloud.
2. IdP del cliente (Entra ID, Google Workspace, Okta) y modelo de federación.
3. Ecosistema SIEM/EDR a integrar primero y si es read-only.
4. Herramienta de ticketing/PR del cliente (GitHub, GitLab, Azure DevOps, Jira).
5. Formatos de informe exigidos por clientes (JSON/HTML/SARIF/PDF).
6. Residencia de datos y retención por tipo de evidencia.
7. KMS/secret manager y política de rotación.
8. Tenancy: pool compartido o silo por cliente.
9. SLO y ventana de recuperación aceptables.
10. Qué señales de fraude se aceptan sin datos personales.

## 11. Criterio de alineación con el máster

El producto estará alineado cuando pueda demostrar, con evidencia:

1. Un `IntentEnvelope` del padre se convierte en capability tipada, sin shell ni URL libre.
2. Un activo no autorizado no genera ningún job, aunque el prompt lo pida.
3. Un finding siempre cita snapshot, herramienta, versión y regla.
4. Un caso distingue `suspected` de `confirmed` y un deepfake nunca se declara certeza.
5. Una remediación se propone, aprueba, aplica en rama y se verifica con re-scan.
6. Un `verified_fixed` solo existe con evidencia posterior a la corrección.
7. Un evento se reproduce sin duplicar efectos.
8. Un tenant no puede leer ni inferir nada de otro.
9. Un informe declara `notTested` y frescura de feeds.
10. Laia puede explicar el estado usando solo eventos y receipts reales.
11. El coste por tenant es medible y el sobrecoste es explícito.
12. Todo lo anterior ocurre sin LLM en el camino crítico.

## 12. Fuera del máster

Gobierno, hospitales, infraestructuras críticas, fintech especializada, resiliencia social, EDR
propio, SOC humano 24/7, explotación ofensiva, campañas de phishing reales y certificaciones
automáticas. La continuidad incluida es la de la pyme cliente, no la de un Estado.

## 13. Relación con los otros 13 dominios

Ciberseguridad es el dominio 1/14. Su E/S debe ser **agnóstica del vertical**: el padre no debe
conocer findings ni scanners, solo `IntentEnvelope`, `CapabilityManifest`, `EffectReceipt` y
`DomainEvent`. Si un futuro dominio (finanzas, legal, clientes) necesita el mismo patrón, el
contrato ya estará probado aquí. Ese es el verdadero criterio de alineación con el máster.
