# Escenarios de aceptación · Fases 6–10

Se conserva distinción entre implementación, test de contrato, runtime real y aprobación de release. No hay revisión independiente realizada. Ningún PASS aquí equivale a autorización para auditar clientes.

| Escenario | Estado técnico | Evidencia y alcance |
|---|---|---|
| D1P6-TEST-1 | PASS | Catálogo de10 fronteras con caso benigno/adversarial y owner; `test_every_boundary_has_benign_adversarial_cases_and_owner` |
| D1P6-TEST-2 | PARTIAL | Gate de release rechaza flags de revisión/sandbox/worker incompletos; probe confirma socket ausente en scanner. Falta el revisor independiente exigido por la campaña |
| D2P1-TEST-1 | PASS | Snapshot local real con hook ejecutable no invocado, symlinks/hardlinks/FIFO rechazados y marcador host intacto; tenant ajeno404 |
| D2P1-TEST-2 | PASS para perfil local | Límites de bytes/entradas; no se extraen archives; LFS/submódulos etiquetados como no adquiridos y cobertura parcial. No incluye adquisición Git remota o imagen |
| D2P2-TEST-1 | PASS en CI | Contenedor real UID65532, root/input read-only, no socket, sin secreto/proxy de host, red denegada, no-new-privileges y capacidades eliminadas |
| D2P2-TEST-2 | PASS en CI | Timeout, salida excesiva y límite de procesos controlados; cleanup exacto verificado; regresión local de pipes también pasa |
| D2P3-TEST-1 | PASS en CI | Gitleaks8.30.1 real detecta canario pese a comentario/config/ignore del repo; export minimizado y repr sin valor del canario. Control benigno sin findings |
| D2P3-TEST-2 | PASS | Versión desconocida, JSON inválido, traversal, exitcode contradictorio o error no devuelven scan limpio |
| D2P4-TEST-1 | PASS en CI | OSV2.7.1 real y offline: paquete ficticio1.0.0 afectado,2.0.0 control; ningún paquete instalado ni consulta remota durante scan |
| D2P4-TEST-2 | PASS | Caché borrada no devuelve no_findings; metadata caducada devuelve stale; ecosistema ausente partial; hash alterado falla antes de uso |

CI Docker: [run42854842519](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/actions/runs/42854842519), SHA `29395da5671e6b063b54895f791de75d38d0792b`, cuatro casos aprobados sin skips. `evidence/ci.json` conserva versiones, hashes de release, image IDs, policy_hash y extractos de logs. La suite general omite esos cuatro casos cuando no hay opt-in y los cuenta como skipped.

No se agregan ejecuciones repetidas en Python3.11/3.12 como si fueran casos nuevos. Los tests de scanner incluyen varias invocaciones real/control/fallo; se reporta el número de casos unittest, no un número inventado de auditorías.
