# Riesgos residuales

- Revisión independiente pendiente y ReleaseGates cerrado. No hay datos reales de clientes, integración `/agente`, despliegue o certificación.
- PrincipalBinding.kind sigue siendo configuración del servidor. Declarar como human/service a un agente elude la clasificación: IdP/gateway de integración debe corregirlo antes de clientes. No se controla el host o llamadas directas a proveedores fuera del servicio.
- Contexto privado protege la aplicación de entradas no confiables, no de código Python privilegiado que un atacante ya consiga ejecutar dentro del proceso.
- Política y código deben ser inmutables durante una instancia. Tras cambiar fuentes se calcula hash nuevo y se reinicia con configuración aprobada. No copiar un hash antiguo de otro artefacto/plataforma sin contrastarlo.
- Egress no habilitado. Preflight DNS/IP no demuestra conexión TLS fijada contra rebinding, límites de una transferencia real, privacidad de un proveedor o restauración tras timeout.
- Hechos normalizados conservan clasificación confidential pero viven en SQLite; cifrado de volumen, backup, borrado legal y operación de retención integral siguen pendientes. Quarantine no es antivirus ni análisis PDF/imagen.
- Solo se extraen hechos de paquetes tipados; no es un extractor fiscal/legal ni un motor RAG. Modelos y memoria reales no están evaluados.
- MCP es un subconjunto backend propio. No OAuth/OIDC/client registration externo, token exchange, streams/SSE, sampling, resources/prompts, callback o servidor externo. Sesiones guardan historial con cuota, sin mantenimiento automático completo.
- Hashes de artefactos/skills declarados no prueban su procedencia o revisión upstream. Una admisión no autoriza ejecutar código de terceros.
- Dos secretos en el mismo entorno no equivalen a MFA. KMS, hardware/IdP, separación operativa y rotación productiva pendientes.
- Epoch invalida más permisos que el scope detenido, de forma conservadora. Resume exige nuevos grants y sesiones; no reactiva los anteriores.
- Un efecto local que adquiere la transacción antes del stop puede confirmar primero. Stop no mata procesos externos ni revierte una nota; no se habilitan esos efectos en este corte.
- Idempotencia/reserva0 solo cubre SQLite. No garantiza exactly-once HTTP, reconciliación bancaria, coste de cloud/LLM o compensación de efectos remotos.
- El corpus es pequeño, propio y estático;0 candidatos adversariales completados no demuestra protección universal. No hay modelo real ni evaluación adaptativa, multimodal o independiente.
- Cuotas de filas no acotan WAL/audit/backups/volumen. El operador necesita límites físicos, cifrado y restauración probada.
