# 05 — Seguridad, validación y aceptación
## Principios innegociables
LLM propone, runtime dispone; deny-by-default; fail-closed; idempotencia; evidencias inmutables o versionadas; multi-tenant; scopes y revocación; auditoría; supervisión humana. La autorización se valida en cada ejecución, no solo al planificar.

## Matriz de pruebas negativas obligatorias
| Familia | Caso seguro de laboratorio | Resultado exigido |
|---|---|---|
| Tenant | tenantA pide evidencia de tenantB | DENY, sin revelar existencia ni bytes |
| Paths | IDs con `../`, absolutos, separadores, Unicode y symlinks | REJECT antes de IO fuera de root |
| Crypto | intercambiar ciphertext entre tenants/IDs | fallo de autenticación; no plaintext |
| Claves | rotación, pérdida simulada, restore y revocación | recuperación documentada, logs sin secretos |
| OCI | leer ruta host no montada | imposible; sin acceso |
| OCI | conectar a red/DNS desde worker | DENY/timeout controlado |
| OCI | fork/CPU/memoria/timeout/cancelación | límites efectivos, cleanup |
| Broker | tool fuera de manifest, scope vencido | DENY con audit |
| Provider | credencial inválida o sin interfaz | BLOCKED, no fallback inseguro |
| Evidencia | salida enorme o binaria maliciosa | truncado/redacción/size cap sin fuga |
| Release | pip-audit ausente o vulnerable | NO-GO producción |
| Estado | crash tras efecto antes de ACK | reconciliación, no doble efecto |
| Logs | datos sensibles y tokens canario | redacción y control de acceso |
| RLS | operador y tenants A/B en backend real | cero cruces en query/export/search |
| Prompt injection | email/repositorio pide ampliar permisos | tool call rechazada, no escalado |
| Engagement | activo fuera de allowlist/ventana | denegado y alertado |

## Qué significa PASS
- Unit PASS: aserciones ejecutadas localmente con SHA/exit; no demuestra seguridad del host.
- Integration PASS: proveedor real o runtime aislado probado con versión, config y logs.
- Security PASS: controles negativos y review independiente sobre frontera pertinente.
- Pilot PASS: ROE autorizado, DPA aplicable, operaciones de bajo impacto y rollback probado.
- Production GO: aprobación founder, aceptación independiente y gates completos. Un test faltante es BLOCKED, no PASS.

## Release checklist
[ ] Dependencias fijadas y SBOM con procedencia
[ ] pip-audit/SCA ejecutado, vulnerabilidades triadas
[ ] Firmas verificadas y claves fuera del repo
[ ] OCI real con restricciones y pruebas negativas
[ ] Vault segregado y restauración
[ ] Scope y revocación verificados
[ ] Logs sin PII/secrets y alertas entregadas
[ ] RLS/tenancy verificados en backend real
[ ] PR revisado, branch protection y CI
[ ] Aceptación explícita del founder

## Piloto
Primero gemelo sintético; después activos propios en staging; finalmente primer cliente con autorización escrita por activo, técnicas permitidas, horarios, límites de carga, contacto de emergencia, retención, custodia, plan de notificación y aprobación de informe. Prohibidas pruebas destructivas o de terceros fuera de alcance.
