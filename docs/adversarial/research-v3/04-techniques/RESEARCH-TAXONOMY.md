# Taxonomía de investigación adversarial avanzada
**Alcance:** ingeniería defensiva en entornos propios/autorizados. Esto es catálogo de hipótesis y evaluaciones, no instrucciones para intrusión no autorizada.

| Dominio | Hipótesis investigables | Oráculo y evidencia | Control negativo |
|---|---|---|---|
| SAST/taint | fuente no confiable alcanza operación sensible | dataflow, prueba en fixture, stack trace | flujo sanitizado |
| Autorización | dos roles acceden a recursos ajenos | matriz rol×recurso×acción, respuesta y estado | owner legítimo |
| Lógica empresarial | transición de estado viola invariante | property test, ledger antes/después | transición válida |
| Concurrencia | TOCTOU, idempotencia o retry crea inconsistencia | invariantes DB/event log, replay | ejecución serial |
| API | schema y servidor divergen | contract test, stateful model, logs | endpoint conforme |
| Supply chain | artifact no corresponde a source/provenance | hash, SBOM, firma, CI attestation | build pinneado |
| Secret management | material sensible aparece en salida | canary sintético, DLP, log diff | valor no sensible |
| Cloud/IAM | permiso excede rol mínimo | simulación de policy, effective permissions | rol restringido |
| Containers | frontera de aislamiento insuficiente | egress test, mounts, capabilities | sandbox endurecido |
| AI/agents | instrucciones en datos inducen uso indebido de herramienta | policy decision + canary, trace | documento benigno |
| RAG/memory | contaminación cambia decisiones | benchmark before/after, trace | corpus limpio |
| MCP/tooling | descripción/herramienta excede permisos | deny decision y schema validation | descriptor firmado |
| Availability | fallo de dependencia produce cascada | SLO, RTO/RPO, traces, restore | failover exitoso |
| Data integrity | rollback/backup restaura estado incorrecto | checksums y constraints | backup íntegro |
| Multi-service | confianza rota entre identidades/eventos | correlation IDs, ABAC tests | servicio autorizado |

## Escalera metodológica
1. Formular hipótesis falsable y riesgo.
2. Identificar activo, permisos y límites.
3. Crear fixture vulnerable **sintético** y control corregido.
4. Elegir método: estático, property-based, fuzz, simulación o prueba de integración.
5. Ejecutar bajo broker y registrar versiones, seed, recursos y observaciones.
6. Aplicar oráculo determinista; separar CONFIRMED / DISPROVED / INCONCLUSIVE / NOT_RUN.
7. Minimizar caso y reproducir en sandbox nuevo.
8. Proponer fix, verificar seguridad y regresión.
9. Incorporar test de regresión y documentar límites de generalización.

## Técnica avanzada ≠ más agresividad
El nivel alto proviene de *oráculos correctos*, *corpus evolutivo*, *selección adaptativa*, *métodos diferenciales*, *análisis semántico*, *evaluación temporal*, *modelado de estados* y *verificación independiente*. Las pruebas destructivas sobre sistemas reales aumentan riesgo sin mejorar necesariamente la calidad científica.
