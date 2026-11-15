# Requisitos de conexión, entrada/salida y trasvase a `/agente`

**Fecha:** 2026-11-15. **Base:** `feat/cy-v2-01-baseline` (`84c8499`). **Estado:** lista de lo que
falta aportar; nada de esto está conectado todavía.

Este documento responde a una pregunta concreta: **qué necesito del founder para conectar todas
las dependencias del repo, abrir la punta por la que entra y sale la datos, e instalarlo en el
repo padre**. Cada requisito lleva ID para poder marcarlo. La columna «quién» distingue lo que solo
puede aportar el founder de lo que implemento yo una vez exista.

Referencias: [contrato con /agente](../09-contrato-con-agente.md),
[patchset propuesto](../integration/PATCHSET-AGENTE.md),
[plantilla de configuración](../integration/server-config.example.json).

## 0. Regla de secretos

Ningún token, clave o contraseña se pega en el chat, en un issue, en un commit ni en este
documento. Se inyectan como variables de entorno del proceso o en el gestor de secretos del host.
Todo lo que sigue son **nombres de referencia y formatos**, no valores.

## 1. Identidad y tenants (lo que hay que decidir)

| ID | Necesito | Detalle | Quién |
|---|---|---|---|
| A1 | IDs de tenant | Uno por empresa/workspace; minúsculas, sin PII (p. ej. `tenant-a`). Deben coincidir con el repo padre | Founder |
| A2 | Mapa organización → tenant | Cómo traduce `/agente` su organización/sesión al `tenant_id` del middleware | Founder + yo |
| A3 | Actor IDs | Identificador estable por humano y por agente (Pedro/Laia incluidos), sin email ni nombre real | Founder |
| A4 | Rol por actor | `viewer`, `analyst`, `operator`, `reviewer`, `owner`. `reviewer`/`owner` aprueban grants y evidencias; un LLM nunca | Founder |
| A5 | Quién es la autoridad de consentimiento | Actor `owner`/`reviewer` que firma cada consentimiento de auditoría | Founder |
| A6 | Frontera agente/humano | Confirmar que los agentes usan `kind: "agent"` y solo `agents.read` + delegación de un uso | Founder |
| A7 | Política de bloqueo | Si un principal se deshabilita o caduca, qué debe pasar en el host (hoy: 403 fail-closed) | Founder |

## 2. Secretos y claves (nombres exactos)

Cada principal referencia una variable de entorno; el valor lo genera el founder y **no** se
escribe en el JSON de configuración.

| ID | Variable (ejemplo de nombre) | Formato | Para qué | Quién |
|---|---|---|---|---|
| B1 | `AGNTIA_CYBER_TOKEN_OWNER_<TENANT>` | 24–512 caracteres ASCII imprimibles | Token Bearer del owner | Founder |
| B2 | `AGNTIA_CYBER_TOKEN_REVIEWER_<TENANT>` | idem | Aprobaciones y evidencias | Founder |
| B3 | `AGNTIA_CYBER_TOKEN_ANALYST_<TENANT>` | idem | Operación diaria | Founder |
| B4 | `AGNTIA_CYBER_TOKEN_AGENT_<TENANT>` | idem | Principal de agente (nunca rol owner/reviewer) | Founder |
| B5 | `AGNTIA_CYBER_EVIDENCE_KEY_<TENANT>` | base64 de **32 bytes** exactos | Cifrado AES-256-GCM de evidencias | Founder |
| B6 | `AGNTIA_CYBER_DELEGATION_KEY` | ≥32 bytes aleatorios (base64 o hex) | Firmar delegaciones de un solo uso | Founder |
| B7 | `AGNTIA_CYBER_EMERGENCY_TOKEN` | ≥32 bytes, **distinto de todos los anteriores** | Kill-switch de agentes | Founder |
| B8 | `AGNTIA_CYBER_METRICS_TOKEN` | ≥24 caracteres, separado | Scrape de métricas | Founder |
| B9 | `AGNTIA_CYBER_EVENT_KEY_<SOURCE>` | ≥24 caracteres, uno por fuente | Ingesta de eventos firmados | Founder |

Reglas que el servidor ya exige y conviene saber antes de generar nada: los tokens deben ser
únicos entre principales; las claves de evidencia no pueden repetirse entre tenants; la clave de
emergencia, la de delegación, la de métricas y las de fuentes deben ser **referencias distintas**
de cualquier token de principal.

## 3. Configuración del servidor (`server.json`)

Un único archivo JSON fuera del repo, referenciado por `AGNTIA_CYBER_CONFIG_FILE`. La plantilla
está en [server-config.example.json](../integration/server-config.example.json) y **no contiene
secretos**, solo nombres de variables.

| ID | Necesito | Detalle |
|---|---|---|
| C1 | Ruta del archivo en el host | Fuera del repo, permisos `600`, montada solo lectura en el contenedor |
| C2 | `data_dir` | Volumen persistente para SQLite, evidencias y backups (p. ej. `/state`) |
| C3 | Targets autorizados | Repos, directorios, imágenes o webs reales con red/puertos/prefijos permitidos |
| C4 | Consentimientos | Tenant, targets, perfiles (`static_read`/`passive_web`/`active_lab`), vigencia, autoridad y tope de coste |
| C5 | Políticas de evidencia | `key_refs`, base legal, custodio y retención por tenant |
| C6 | Presupuestos | `budget_policies` por tenant (Lite 30 €, L 70 €, XL 300 €) |
| C7 | Raíces de workspace | Rutas locales aprobadas para snapshots; sin comodines |
| C8 | Fuentes de eventos | `event_sources` por tenant y target, con límite por minuto |
| C9 | Canales de verificación | `callback_directory` o `in_person` para fraude/BEC |
| C10 | Egress aprobado | `approved_egress_refs` solo a targets `web` ya declarados |

## 4. Dependencias de ejecución

| ID | Necesito | Detalle | Quién |
|---|---|---|---|
| D1 | Cuatro imágenes de escáner con digest inmutable | Gitleaks, OSV-Scanner, Semgrep CE, Trivy en formato `sha256:<64>`; el runner rechaza tags mutables | Founder / yo construyo |
| D2 | Acceso a Docker | El runner usa `/usr/bin/docker`; decidir socket, grupo o Docker rootless en el host | Founder |
| D3 | Feeds y bases | OSV DB y Trivy DB: salida a internet con allowlist, o caché offline con fecha de actualización | Founder |
| D4 | Reglas Semgrep | Las reglas propias viven en `rules/`; confirmar que se revisan y versionan antes de habilitar | Founder |
| D5 | Colector OTel | Si `telemetry_export=local_collector`: endpoint OTLP/HTTP, TLS y retención | Founder |
| D6 | Almacenamiento y backup | Volumen, ruta de backup, retención y destino cifrado; restore ensayado | Founder |
| D7 | Custodia de claves | Decidir si las claves de evidencia viven en variables del host o en un KMS/secret manager | Founder |
| D8 | Python y wheelhouse | Versión 3.11/3.12 y, si es air-gapped, ruedas preinstaladas | Founder / yo |

## 5. La punta de entrada (inbound)

Hoy el servicio escucha en `127.0.0.1:8012` con `agntia-ciberseguridad serve --config …` y expone
`/v1/tenants/{tenant}/…` con `Authorization: Bearer`. No hay BFF, OIDC ni mTLS implementados: eso
es host.

| ID | Necesito | Detalle |
|---|---|---|
| E1 | Hostname privado y TLS | DNS interno + certificado; el middleware no debe quedar en Internet |
| E2 | Decisión de autenticación del host | OIDC/sesión/mTLS del BFF de AgntiaPro; el cliente del navegador nunca recibe el token interno |
| E3 | Red permitida | Qué subredes pueden llamar al puerto; allowlist explícita |
| E4 | Orígenes aprobados del SDK | Valores para `approvedOrigins` (solo HTTPS o loopback de laboratorio) |
| E5 | Límite de cuerpo | 64 KiB por defecto; confirmar si el host necesita otro valor |
| E6 | Rate limiting del borde | Hoy hay cuotas por tenant/plan; decidir límite de conexiones del proxy |
| E7 | Consola | Decidir si la consola piloto (`web/console`) se sirve tras el BFF o se retira |
| E8 | Correlation IDs | Confirmar que el host propaga `X-Correlation-ID` y no lo genera el modelo |

Flujo previsto: navegador/Laia → BFF de `/agente` (sesión y tenant) → SDK servidor
`@agntia/ciberseguridad` → middleware → job/worker → evento → proyección.

## 6. La punta de salida (outbound)

| ID | Necesito | Detalle |
|---|---|---|
| F1 | Consumidor del outbox | `consumer_id`, cursor inicial y quién ejecuta el ACK (`events.ack`) |
| F2 | Semántica de entrega | Confirmar at-least-once con deduplicación por `id` + `content_hash`; no exactly-once |
| F3 | Bus real del padre | Si `/agente` usa bus propio: tipo, endpoint, credenciales y mapeo de eventos `job.*`/`budget.*` |
| F4 | Destino de reportes | Descarga directa, almacenamiento del padre o ambos; formatos aceptados |
| F5 | Exportación de evidencia | Quién puede pedir originales, con qué aprobación y durante cuánto tiempo |
| F6 | Métricas y trazas | Scrape de `/metrics` con token separado; destino OTLP si se habilita |
| F7 | Datos que nunca salen | Confirmado: sin tokens, sin secretos crudos, sin muestras privadas, sin prompts completos |

## 7. Instalación en `uniscrolliabrain-cloud/agente`

| ID | Necesito | Detalle |
|---|---|---|
| G1 | Autorización de lectura del repo padre | Inventariar sesión, tenant, event bus, approval service, secret manager y BFF reales; sin esta lectura no hay wiring posible |
| G2 | Autorización de escritura separada | Un PR pequeño en `/agente` para montar el cliente, no un cambio amplio |
| G3 | Forma de consumo del paquete | Workspace local o tarball `npm pack`; el paquete es privado y no está publicado |
| G4 | Versión fijada | SHA/tag del middleware que el padre acepta; sin `latest` |
| G5 | Credencial de servicio del padre | Principal `kind: "service"` con tenant mínimo y rotación |
| G6 | Mapeo de aprobaciones | Cómo se traduce la aprobación humana del padre al `approval_id` del middleware |
| G7 | Contrato de herramientas | Confirmar `cyber_assets_read`, `cyber_findings_read`, `cyber_jobs_read` y la delegación de un uso |
| G8 | Entorno de destino | Staging del padre, nunca producción en esta fase; URL y red |
| G9 | Permiso para abrir PR | El conector GitHub actual devuelve 403 al crear pull requests |

## 8. Decisiones legales y operativas

| ID | Necesito | Detalle |
|---|---|---|
| H1 | Licencia del código propio | Hoy no hay licencia elegida; impide distribución |
| H2 | DPA y base legal | Aplicabilidad RGPD por rol, retención y derechos |
| H3 | Canal privado de seguridad | Dónde se reportan vulnerabilidades del propio middleware |
| H4 | Revisión independiente | Fecha y responsable; hoy `independent_review=PENDING` |
| H5 | Aceptación de piloto | Qué entorno cuenta como laboratorio y qué datos se permiten |
| H6 | Operadores humanos | Quién atiende incidentes y con qué escalado |

## 9. Lo que NO necesito

- Tokens, claves o contraseñas por chat: solo nombres de variables y despliegue en el host.
- Acceso a producción, clientes reales o redes de terceros.
- Compras, suscripciones o APIs de pago.
- Credenciales de modelos LLM: el middleware no llama a ningún modelo.
- Datos personales para el piloto sintético.

## 10. Qué falta en código antes de que esto sea plug-and-play

Para no confundir requisitos con software terminado:

1. No existe BFF/OIDC/mTLS propio; el host debe autenticar.
2. El adaptador del bus del padre no está escrito; hoy solo hay outbox por polling.
3. El paquete SDK es privado y se instala por tarball, no desde un registro.
4. La consola es piloto y usa token en memoria.
5. Los conectores cloud/SOC y el bundle semver de capacidades son campañas CY-V2-10/20/38.
6. Los escáneres reales requieren Docker y opt-in; en CI se ejecutan, en local no por defecto.

## 11. Orden mínimo para el trasvase

| Hito | Qué se necesita | Bloquea |
|---|---|---|
| M0 · Demo local | Nada del founder; ya reproducible con 190 tests | — |
| M1 · Laboratorio propio | A1–A4, B1–B5, C1–C2, D1–D3, E1/E3 | Datos reales |
| M2 · Staging del padre | G1–G5, E2/E4, F1/F2 | Integración |
| M3 · Piloto aceptado | H1–H6, revisión independiente, restore ensayado | Clientes |

Con M1 marcado puedo completar la configuración y ejecutar la primera auditoría real sobre un
repo autorizado. Con M2, el trasvase de eventos y reportes hacia `/agente`.
