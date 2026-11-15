# 01 — Inventario de capacidades y brechas de puesta en marcha
## Fuentes del repositorio consultadas
`README.md`, `docs/02-arquitectura-y-confianza.md`, `docs/09-contrato-con-agente.md`, `docs/operations/RUNBOOK.md`, `docs/release/PILOT-ACCEPTANCE.md`, `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`, `pyproject.toml`. La auditoría es documental y selectiva, no un test de producción.

## Qué hay y qué falta
| Superficie | Existencia respaldada | Brecha operativa |
|---|---|---|
| Core Python FastAPI | API /v1, configuración explícita, roles y tenants | identidad productiva, configuración validada, revisión independiente |
| SDK TS/Hono | paquete server-only empaquetable | consumidor real /agente, scopes, contrato, pruebas |
| Persistencia | SQLite, migraciones, ledger/outbox y leases declarados | política backup/restore completa, evaluación de Postgres para multi-tenant |
| Scanners | Gitleaks, OSV, Semgrep, Trivy en adaptadores offline | binarios/imágenes reales, versiones, reglas, feeds, licencias y pruebas de alcance |
| Evidencia | vault AES-GCM y reportes | custodia, rotación, retención, backup, restore, DPA |
| Operación | Compose privado, scripts verify_lab, CI y bundle | servidor elegido, alertas, responsable, runbooks probados |
| Producto | planes Lite/L/XL y UI piloto | precios/coste operativo, SLA, soporte, contratos, aceptación |
| Seguridad de agentes | gateway propuesto/implementado parcialmente | identidad delegada, approval binding y wiring real |
| Adversarial Lab | rama independiente | NO es requisito para iniciar checklist del middleware; mantener plan propio |

## No confundir
- 196 tests Python y 84 rutas aparecen en notas de estado del repo, **no son tests ejecutados en esta sesión**.
- `2 PASS / 40 PARTIAL` es estado de las fases, no porcentaje de endpoints funcionando.
- `docs/release/PILOT-ACCEPTANCE.md` aún bloquea clientes reales.
- `docs/operations/RUNBOOK.md` conserva párrafos históricos obsoletos; usar sus advertencias fechadas y contrastar comandos con HEAD.
- Los planes CY-R02…R12 de auditoría funcional existen y deben coordinarse con el agente que ya los ejecuta, sin duplicarlos.

## Inventario que el agente debe entregar primero
Tabla por servicio: ruta de código, dependencia externa, configuración, permisos, test real, coste, estado `READY/BLOCKED/NOT_VERIFIED`, responsable y acción mínima. Añadir un diagrama de flujo real de datos desde /agente hasta API, worker, evidence store y respuesta. Ninguna credencial en la tabla.
