# 03 — Decisiones del founder, cuentas, costes y secretos
**Regla:** el agente prepara alternativas y validaciones; el founder elige proveedor, acepta riesgos, autoriza gasto, crea cuentas y concede permisos. Ninguna cuenta/clave se crea por suposición. No compartir secretos en chat ni Git.

## Checklist de 8 decisiones
| ID | Decisión humana | Opción mínima recomendada | Evidencia de cierre |
|---|---|---|---|
| F01 | Permisos GitHub Freebuff/Codex | lectura + ramas/PR; sin merge ni deploy autónomo | captura o revisión de roles, branch protection |
| F02 | Host Linux de laboratorio | VM efímera separada de producción; OCI rootless si viable | proveedor, región, presupuesto, SSH/MFA, runtime |
| F03 | Primer agente real | uno con interfaz CLI/API soportada | contrato, límites, política de datos y coste |
| F04 | Secret manager | reutilizar Doppler u otro ya administrado | scopes, rotación, recuperación y auditoría |
| F05 | Vault/backup | storage privado con versionado + cifrado por tenant | política retención, restore test |
| F06 | Modelo de aislamiento | OCI endurecido probado o microVM para mayor riesgo | threat model y tests negativos aprobados |
| F07 | Alertas y kill switch | responsable + canal ya usado, on-call realista | simulacro de cancelación y recepción |
| F08 | Piloto | solo activos propios y consentimiento escrito | ROE/engagement, DPA si aplica, responsable y ventanas |

## Qué no contratar de entrada
No Kubernetes, Kafka, SIEM comercial, EDR propio, varias APIs LLM, ni plataforma de firma si un proceso controlado basta. Comprar solo cuando un gate tenga necesidad y coste medido. No dar por hecho que una herramienta open source es gratuita en operación o permite revender todas sus reglas/datasets.

## Infraestructura mínima
- VM Linux separada con snapshots, discos cifrados, MFA y acceso SSH restringido.
- Runtime OCI actualizado; imagen por digest, sin red, sin privilegios, sin montaje Docker socket, read-only y límites.
- Secret manager con identidad por workload y acceso de mínimo privilegio.
- Object store cifrado y backups independientes, pruebas de restore.
- Logs redactados, alertas, timeouts, presupuesto y corte de emergencia.
- Solo cuando se despliegue API: DNS/TLS y control de acceso privado.

## Variables existentes vs propuestas
### Middleware existente / referencias de configuración
`AGNTIA_CYBER_CONFIG_FILE`, `AGNTIA_RUNTIME_IMAGE`, `AGNTIA_SERVER_CONFIG`, `AGNTIA_SECRET_ENV_FILE`; referencias configurables `principals[].token_env`, `evidence_policies[].key_refs`, `event_sources[].key_env`, `metrics_token_env`, `delegation_key_env`, `emergency_token_env`. Validar contra el código y config vigentes antes de usar; los últimos no son nombres literales de env.
### Laboratorio declaradas
`ADVLAB_DATA_DIR`, `ADVLAB_ALLOW_NETWORK`, `ADVLAB_ALLOW_SUBPROCESS_PROVIDERS`, `ADVLAB_MAX_EVIDENCE_BYTES`, `ADVLAB_BUDGET_CENTS`, `ADVLAB_MAX_RUNS_PER_DAY`. Mantener red y proveedores subprocess desactivados hasta aprobación y enforcement verificado.
### Futuras — NO IMPLEMENTADAS por declararlas aquí
`ADVLAB_PROVIDER_CREDENTIAL_REF`, `ADVLAB_EVIDENCE_KMS_KEY_REF`, `ADVLAB_OBJECT_STORE_CREDENTIAL_REF`, `ADVLAB_DATABASE_CREDENTIAL_REF`, `ADVLAB_ALERT_WEBHOOK_REF`, `ADVLAB_SIGNING_KEY_REF`. Los nombres son propuestas; el agente debe definir schema/validación antes de usarlos.

## Presupuesto y aprobaciones
Registrar por proveedor: coste fijo, coste variable por run, almacenamiento, egress, logs, recuperación, reservas, límites y alarma. Definir `monthly_cap`, `run_cap`, `daily_cap` por tenant. Una reserva local no limita la factura externa: usar también controles del proveedor y alertas. Todo gasto o conexión con datos reales requiere aprobación explícita.
