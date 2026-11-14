# Fuentes, versiones y licencias

Consulta selectiva2026-11-10; no auditoría exhaustiva ni instalación de estos motores.

- MCP esquema2025-11-25: commit `c4c367f9f58296a7053f5c78a52fd02bfbb56a49`, archivo schema/2025-11-25/schema.ts, observado mediante API de commits por ruta. [Fuente fijada](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/c4c367f9f58296a7053f5c78a52fd02bfbb56a49/schema/2025-11-25/schema.ts). Se contrastaron JSON-RPC, initialize, initialized notification y tools. Se implementa un subconjunto del recurso propio; no conformidad completa.
- [OPA LICENSE](https://github.com/open-policy-agent/opa/blob/main/LICENSE): Apache-2.0, leído en esta sesión. No se instala, copia ni se ejecuta un benchmark de OPA. Rego y desacoplamiento de decisiones son una alternativa de diseño futura.
- [Cedar LICENSE](https://github.com/cedar-policy/cedar/blob/main/LICENSE): Apache-2.0, leído en esta sesión. No se instala/copía; su modelo de principal/acción/recurso informa la comparación, no acredita formalmente esta implementación.
- [AgentDojo LICENSE](https://github.com/ethz-spylab/agentdojo/blob/main/LICENSE): MIT, leído en esta sesión. No se descarga/ejecuta su suite ni se reutiliza un resultado publicado. El corpus propio es estático y sin modelo.
- CaMeL y demás papers: referencias en investigación inicial del repo. Se mantiene el principio de separar datos no confiables de control; no se declara implementar un sistema formal equivalente ni replicar sus resultados.

La implementación usa stdlib(Python hmac/hashlib/contextvars/sqlite3), Pydantic/FastAPI y custodia existentes. No se añaden credenciales comerciales o dependencias de proveedor. Los hashes de artefacto inventariados no sustituyen una revisión de licencias/procedencia.

