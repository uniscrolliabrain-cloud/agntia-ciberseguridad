# 03 — Secretos, variables, archivos privados y permisos
## Principios
El founder crea/autoriza credenciales en consola del proveedor; el agente prepara documentación, validadores y referencias. Nunca pegar tokens en chat, GitHub, PR, logs, prompts o reportes. Separar local/staging/producción y tenantA/tenantB. Un secreto se entrega por referencia a un workload, no como valor al LLM.

## Variables observadas en documentación del middleware
| Variable/referencia | Función | Fuente | Preparación |
|---|---|---|---|
| `AGNTIA_CYBER_CONFIG_FILE` | ruta de JSON de configuración | docs/config | archivo fuera del repo |
| `AGNTIA_RUNTIME_IMAGE` | ID inmutable de imagen construida | RUNBOOK Compose | solo imagen verificada |
| `AGNTIA_SERVER_CONFIG` | ruta JSON externo para Compose | RUNBOOK | fuera del checkout |
| `AGNTIA_SECRET_ENV_FILE` | ruta de env externo privado | RUNBOOK | permisos restrictivos |
| `principals[].token_env` | nombre de env por principal | RUNBOOK/config | credencial por principal |
| `evidence_policies[].key_refs` | nombres de claves de evidencia | RUNBOOK/config | claves AES-256 base64 gestionadas |
| `event_sources[].key_env` | credencial por fuente de evento | config | separación por fuente |
| `metrics_token_env` | token métricas si configurado | config | separado de API |
| `delegation_key_env` | firma delegación si se usa | config | rotación y scope |
| `emergency_token_env` | emergencia si se habilita | config | break-glass auditado |

**Importante:** las seis últimas son claves de esquema/referencias configurables, no nombres literales de variables. Confirmar schema actual en código antes de crear ninguna.

## Plantilla sin secretos (NO es configuración lista para arrancar)
```text
AGNTIA_CYBER_CONFIG_FILE=/ruta/privada/server.json
AGNTIA_RUNTIME_IMAGE=<image-id-verificado>
AGNTIA_SERVER_CONFIG=/ruta/privada/server.json
AGNTIA_SECRET_ENV_FILE=/ruta/privada/secrets.env
```
No ejecutar con placeholders; no introducir secrets en `.env.example`.

## Preparación por agente
1. Inspeccionar `agntia_ciberseguridad/config.py`, `infra/compose.yaml` y ejemplos vigentes; generar **inventario exacto** de settings requeridos, defaults y validadores.
2. Crear `config.template.json` con identificadores ficticios, referencias de env y explicaciones; sin claves.
3. Comprobar que sin env requerido el proceso falla cerrado, que tokens duplicados/ausentes se rechazan y que no hay owner por defecto.
4. Crear prueba de redacción de logs y `git secrets`/Gitleaks en CI.
5. Documentar rotación y recuperación: tokens de principal, claves AES y claves antiguas aún necesarias para descifrar evidencia histórica.
6. Probar lectura de secret manager desde runtime con identidad limitada; registrar solo presencia/ausencia, nunca valores.

## Matriz de permisos
Founder: admin de cuentas, compras, aprobación de acceso y revocación. Agente ejecutor: repo write en rama y entorno sintético, sin acceso a billing ni claves productivas. Runtime API: leer sus propias refs, no administrar secretos. Worker scanner: token scoped a activo/tenant, caducidad corta, sin credencial global. Operador: observabilidad y stop, no lectura irrestricta de evidencias. Auditor independiente: lectura de evidencia redactada y SHA, sin modificar pruebas.

## Rotación
Registrar fecha, custodio, secret ref, versión, consumidores, plazo de transición, verificación de decrypt/restore y revocación. Rotar no significa borrar claves antiguas mientras exista ciphertext dependiente; migrar/re-cifrar y verificar antes de retirar.
