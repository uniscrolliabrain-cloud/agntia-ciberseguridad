# Carta de independencia y límites de investigación
## Invariantes
1. No tocar, importar, ampliar ni refactorizar `agntia_ciberseguridad/agents/**`; sus permisos, manifests, policies, MCP y routes son ajenos a esta capacidad.
2. No tocar `uniscrolliabrain-cloud/agente` ni modificar su kernel o agentes.
3. Ningún agente externo adquiere autoridad para cambiar alcance, identidad, presupuesto o modo de ejecución. El proveedor de coding agent es un proceso reemplazable y no confiable.
4. El laboratorio posee **control plane, execution plane, campaign registry, evidence, evals, reporting y lifecycle propios**. Integración futura solo mediante APIs explícitas, contratos versionados y revisión.
5. Producción del cliente: consentimiento verificable, alcance, ventanas, límites y aprobación adicional para pruebas activas; por defecto solo lectura y sin pruebas destructivas.
6. No confundir permisos sobre repositorios con permiso para atacar endpoints desplegados; cada activo y acción requieren autorización.
7. Las pruebas más intensivas se confinan a laboratorio aislado, con datos sintéticos y salida de red bloqueada salvo reglas concretas.

## Límites de confianza
Cliente/tenant → contrato de engagement → controlador del laboratorio → broker de capacidades → worker efímero → herramienta/LLM. **Cada flecha exige validación independiente**. Texto de README, issue, comentario, prompt, código de cliente y output de scanner son datos no confiables.
## Amenazas contra el propio laboratorio
Prompt injection en archivos de cliente; escape de contenedor; egress DNS/HTTP; exfiltración en logs; credenciales heredadas; tool output spoofing; confused deputy; aprobación obsoleta; replay; consumo sin límite; contaminación de benchmark; secretos en trazas; contaminación cross-tenant; retención indebida; auto-confirmación del hallazgo.
## Controles mínimos
Deny-by-default, identidad efímera, sandbox descartable, egress guard en red, mounts read-only cuando posible, broker sin shell host, aislamiento tenant, limitador de presupuesto, kill switch, evidencia firmada/hasheada, auditoría append-only, revisión humana y oráculos independientes.
## ADR pendiente
Comparar: A) repo hermano independiente (preferido por aislamiento), B) bounded context en repo actual sin imports cruzados. Criterios: despliegue, secretos, tenancy, licencia, ownership, acoplamiento, costes, recuperación, mantenimiento. **No decidir por comodidad del implementador**.
