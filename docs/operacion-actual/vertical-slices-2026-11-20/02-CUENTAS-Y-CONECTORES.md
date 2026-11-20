# Frontera founder — cuentas, conectores, secretos y aceptación
**Regla:** el ejecutor prepara puertos, env schema, validación, stubs y pruebas con fake; el founder decide y configura cuentas. Nunca solicitar valores de secretos en chat ni commitearlos. No asumir que disponer de cuenta significa que una integración esté habilitada. Confirmar lo ya existente antes de pedir alta nueva.

| Servicio | ¿Cuenta nueva? | Qué aporta founder | Qué deja agente preparado | Gate sin cuenta |
|---|---|---|---|---|
| GitHub / GitHub App / Actions | normalmente reutilizar | instalación App, repo allowlist, permisos mínimos read contents/actions; write solo con aprobación | manifest de permisos, webhook firmado, PR proposal, fixtures y checks de rate-limit | `GITHUB_NOT_CONFIGURED` |
| Doppler | reutilizar si existe | proyecto/config por dev/staging/prod; service token de alcance mínimo en secret store/Actions, nunca aquí | refs y consumidores, schema, startup checks, rotación, test fake | `SECRET_BROKER_NOT_CONFIGURED` |
| Identidad AgntiaPro / Supabase | reutilizar | issuer/JWKS/audience, mapeo tenant y service-to-service aprobados | JWT validation, principal mapping, revocación, rechazo cross-tenant | `HOST_IDENTITY_NOT_CONFIGURED` |
| OCI / Fly.io / runner Linux | seleccionar entorno autorizado | región UE, límites, cuenta/proyecto, acceso privado, presupuesto | contenedor rootless, seccomp/caps, no-network, límites CPU/mem, health/readiness | `OCI_NOT_VERIFIED` |
| Escáneres OSS (OSV, Gitleaks, Semgrep CE, Trivy) | generalmente no | autorizar feeds/alcance y licencias si procede | instalador con versiones/digests fijados, adapters, fixtures y smoke | `SCANNER_UNAVAILABLE` |
| Evidence storage S3-compatible | elegir/reutilizar | bucket privado EU, credencial scoped, retención y política de borrado | storage port, encryption, signed refs, restore test fake, checksum | `EVIDENCE_STORAGE_NOT_CONFIGURED` |
| KMS/custodia de claves | elegir para prod | key id/ref, permisos de encrypt/decrypt, recovery owners | envelope crypto, rotación/revocación, negative tests | `KMS_NOT_CONFIGURED` |
| Grafana Cloud / OTLP | reutilizar | endpoint, credencial ingest, alert contact y límites | redaction, trace/span/event correlation, dashboards as code y alerta simulada | `OTEL_NOT_CONFIGURED` |
| DNS/TLS/Cloudflare | reutilizar | subdominio staging, acceso privado y certificados | config documentada, origin policy, no exposición pública por defecto | `PUBLIC_ENDPOINT_DISABLED` |
| Correo/avisos | reutilizar Resend/SMTP si autorizado | dominio verificado, sender y permiso de avisos | sink local, templates, retries, suppression, rate-limit | `NOTIFICATIONS_DISABLED` |
| Revisión independiente/ROE/DPA | no API | revisor, alcance firmado y aceptación founder | checklist legal/seguridad, audit trail, paquete evidencias | `PRODUCTION_NO_GO` |

## Configuración segura
- Usar nombres contractuales del código cuando existan; **no inventar variables obligatorias**. Para nuevas variables, documentar nombre, tipo, origen, consumidor, entorno, scopes, validación, rotación y fallback cerrado; generar `.env.example` sin valores.
- El estado de cada conector debe ser `DISABLED`, `MISSING_CONFIG`, `CONFIGURED_UNVERIFIED`, `VERIFIED_SANDBOX`, `VERIFIED_PRODUCTION` según evidencia. `CONFIGURED` nunca significa conexión comprobada.
- Configurar credenciales por referencias de Doppler o secret broker; evitar persistir tokens en Postgres/SQLite, artefactos, logs y reportes. No imprimir `doppler secrets download` ni valores.
- Para cada conector: test de schema, credencial ausente, scope insuficiente, 401/403/429/5xx, timeout, revocación, doble entrega, leak redaction, tenant incorrecto y recuperación.
- Aceptación: cada conector con `PROVIDER / PURPOSE / OWNER / TENANT_SCOPE / SECRET_REF_NAME / PERMISSIONS / CALLBACK / SANDBOX_URL / COST_LIMIT / TEST / EVIDENCE / STATUS`.
- Bloqueo del founder: una ficha accionable por dependencia, con URL de alta oficial **solo verificada**, scopes exactos y coste confirmado. Si no se dispone de URL o coste actualizado, dejar `PENDING_RESEARCH` en lugar de inventarlo.
- No habilitar escaneo activo de terceros, despliegue público, escritura en `agente` ni GO producción sin autorización separada.
