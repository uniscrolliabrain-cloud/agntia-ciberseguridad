# Decisiones preliminares de arquitectura y sourcing
## Regla de separación
El laboratorio puede vivir en **nuevo repo hermano** `agntia-adversarial-lab` (nombre provisional) con su propia API, despliegue y permisos; la decisión exige ADR. No importar `agntia_ciberseguridad/agents/**` ni usar su gateway. La comunicación futura es vía eventos o API de evidencias con contrato firmado, solo si hay necesidad demostrada.

## Componentes
| Componente | Estrategia provisional | Razón |
|---|---|---|
| Engagement/scope/revocation | BUILD | responsabilidad legal y de seguridad, debe ser nuestra |
| Sandbox isolation/broker | BUILD sobre primitivas auditadas | confianza crítica y separación |
| Coding agent adapters | BUILD wrappers | agnosticismo y diferencias de proveedores |
| Hypothesis ledger / experiment engine | BUILD | núcleo diferenciador |
| Oráculos/evaluation | BUILD + usar tests OSS | no confiar en autorreporte LLM |
| Fuzzers y SAST | WRAP | herramientas maduras existentes |
| API stateful testing | WRAP Schemathesis | fases y oráculos ya desarrollados |
| Web DAST | WRAP ZAP en lab | automation plans y ecosistema |
| AI security | WRAP PyRIT + garak | objetivos distintos y complementarios |
| Fuzzing pipeline | STUDY OSS-Fuzz | su infraestructura no es instalable trivialmente |
| CRS AIxCC | STUDY Atlantis | aprender arquitectura y validar licencias |
| Agent patterns CAI | STUDY ONLY | archivado y licencia mixta |
| Fuzzilli | STUDY | demasiado específico para integrar por defecto |
| General shell on customer host | REJECT | rompe scope y modelo de confianza |
| Autonomous publication | REJECT | privacidad, divulgación responsable |

## Interfaces mínimas futuras
Lab engagement API; experiment spec; provider capability registry; sandbox lease; tool invocation receipt; evidence bundle; finding/retest record; report export. Todo versionado y fail-closed. **Sin contratos ejecutables todavía:** primero PoC y threat model.
## Alternativas a investigar
Docker rootless/gVisor/Kata/Firecracker: elegir por threat model y coste, no por moda. SQLite/Postgres/object storage: seleccionar según single-host vs multi-tenant distribuido; no heredar DB del repo existente por defecto. Queue y scheduler: reutilizar conceptos de leases/idempotency, no código de jobs sin decisión ADR. S3-compatible para evidencias: cifrado, tenant isolation y retención.
## Dependencias y licencias
Revisión por release y archivo, NOTICE, AGPL/GPL, licencias de modelos y datasets, export controls, límites de pentesting, redistribución de payloads. La licencia de la raíz de un repo no garantiza licencia de todos sus artefactos.
