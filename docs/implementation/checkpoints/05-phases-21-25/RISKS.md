# Riesgos residuales

- No se ha realizado revisión independiente ni piloto de clientes; gates de release permanecen cerrados.
- El registro/delegación solo gobierna `/delegations/use`. Principales con bearer y roles heredados aún pueden usar otras rutas autorizadas; no hay garantía global contra bypass. El gateway debe cerrar esos caminos antes de habilitar clientes.
- kind=human es una declaración de configuración heredada, no SSO/MFA o prueba de presencia humana.
- HMAC de fuente/delegación exige secreto de alta entropía y canal TLS privado. No hay KMS/JWKS, prueba de hardware ni identidad de proveedor implementados. La clave de delegación es compartida del servicio; rotarla invalida tokens activos.
- Hash de manifest/artefacto declarado no demuestra procedencia, firma upstream ni revisión de código. El esquema cerrado evita ejecución, no audita el artefacto.
- Fuente comprometida con clave válida puede mentir dentro de su scope y cuota. Se conserva como unverified_observation; no se confía para aprobar/pagar/remediar.
- No hay conectores reales Wazuh/Falco/cloud/archivo; únicamente webhook sintético validado. No hay XDR/EDR.
- Retención de logs cubre registros operativos. Hold se aplica a existentes; política continua y base jurídica específicas pendientes. Eventos, audit, grants y backups no tienen eliminación legal integral automática.
- Cuotas de payload no acotan disco/WAL/índices/audit. Audit obligatorio puede crecer: requiere volumen cifrado, cuotas reales y backup/restore del operador. Cuando falla audit/DB obligatoria, se deniega mutación.
- Logs opcionales pueden perderse por cuota/error; se cuentan drops. Métricas en memoria se reinician; no son ledger de auditoría. No hay backend de logs productivo.
- Console muestra ventanas de veinte filas, no inventario completo; datos stale por regla24h inicial. Collector sin monitor se muestra not_monitored.
- Token en memoria no protege frente a malware del equipo o XSS en otras extensiones; la UI usa CSP y no HTML dinámico, pero no es un análisis completo de navegador/IdP.
- Carga ASGI sintética, sin scanners ni TLS/red: no demuestra SLA, concurrencia real entre procesos o coste mensual.
