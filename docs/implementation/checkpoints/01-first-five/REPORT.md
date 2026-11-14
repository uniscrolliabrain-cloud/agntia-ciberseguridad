# Informe 01 · Primeras cinco fases

Fecha: 2026-11-10. Rama: `feat/cyber-d1-foundation`. Repo: `uniscrolliabrain-cloud/agntia-ciberseguridad`.

## Resultado observable

Se han trabajado D1P1–D1P5 y construido un núcleo instalable de API privada: inventario por empresa, identidad/roles, aprobación por un revisor distinto, revocación, preflight de alcance y persistencia con auditoría. **No son42 fases terminadas, ni cinco fases íntegramente cerradas.** El registro conserva los pendientes de cada fase; se separa el código provisional probado del gate completo para habilitar capacidades posteriores.

| Fase | Estado del entregable | Qué está demostrado | Qué falta para cierre completo |
|---|---|---|---|
| D1P1 | PASS | Baseline y entorno, dos tenants ficticios, preservación de cambios ajenos y Docker denegado registrado | Sin bloqueos del baseline |
| D1P2 | PASS | Paquete/CLI, factoría, DTOs, errores, límites,13 esquemas e instalación limpia en Python3.11/3.12 por CI | Sin bloqueos de paquete; no implica habilitación de workers |
| D1P3 | PARTIAL | Autenticación, scopes, roles, separación de revisión, revocación y aislamiento API | Identidad federada/secret-manager de producción y aplicación a jobs/exportaciones todavía inexistentes |
| D1P4 | PARTIAL | Migraciones, backup/restore, rollback, dos procesos, unicidad, FKs, cadena y contención | Identidades/idempotencia de jobs/reservas e historial de findings; anclaje externo y cifrado de despliegue |
| D1P5 | PARTIAL | Referencias de activos, consentimiento configurado, grants, CIDR/DNS/rutas, límites y revalidación | Snapshot de contenido y aislamiento/egress durante un trabajo real en D2; custodia de consentimientos reales fuera del piloto |

El detalle de escenarios está en [GATES.md](GATES.md). El alcance ejercitado pasa sus pruebas; los pendientes anteriores impiden anunciar los gates completos como aprobados. La implementación posterior dependiente puede prepararse como código provisional, pero no activarse saltando estos requisitos.

## Pruebas realmente ejecutadas

- **29 ejecutadas, 29 aprobadas, 0 fallidas, 0 errores, 0 omitidas**, Python3.12.14, duración0.839s en el último run registrado.
- SQLite real: upgrade/fresh, rollback de DDL, backup/restore, triggers append-only, corrupción privilegiada detectada, concurrencia de procesos y unicidad de activos.
- API ejecutada mediante ASGI en proceso: auth, tenant ajeno404, viewer403, hashes/revisiones409, no autoaprobación, grant revocado/caducado, token rotado, datos secretos no reflejados, body/frames limitados.
- Red: resolución DNS inyectada, múltiples respuestas y bloqueos de metadata/redirect/ruta; **no conexión de red ni escáner**. Revocación durante DNS bloquea la previsualización.
- El primer runner de evidencias tuvo un error de imports; se conserva `failed-run-01-*`, se corrigió y se ejecutó otra vez. Antes se detectó/corrigió bloqueo WAL concurrente. No se ocultan esos fallos bajo un PASS documental.

Comandos reales:

```bash
python -m venv --system-site-packages .venv
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/run_foundation_tests.py --output docs/implementation/checkpoints/01-first-five/evidence
.venv/bin/python scripts/export_schemas.py
.venv/bin/agntia-ciberseguridad --version
.venv/bin/python scripts/benchmark_foundation.py
python scripts/validate_foundation.py
python scripts/validate_campaign.py
```

La venv local usa dependencias ya instaladas, por eso **no se declara instalación limpia verificada**. CI ya completó instalación limpia en Python3.11 y3.12:29 pruebas aprobadas por versión, exportación reproducible de schemas y CLI. [Run42841629212](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/actions/runs/42841629212), SHA de código `713da0ae4735a2c51f5e92a8ed070d4c13d0f0f6`. Evidencia sanitizada en `evidence/ci.json`. Son58 ejecuciones CI de los mismos29 casos, no58 casos distintos. El estado de este primer checkpoint es **dos fases cerradas y tres parciales**.

## Rendimiento medido y costes

Fixture SQLite de100 append, cuatro hilos: p50=0.743ms, p95=19.700ms, máximo=108.963ms, 0 errores; cadena válida de100 eventos. Datos completos en `evidence/contention.json`. No mide capacidad de escáner, multi-host ni producción. No se han comprado servicios ni consumido APIs de pago; coste futuro por cliente no medido. Los límites30/70/300EUR siguen siendo diseño, sin ledger agregado implementado.

## Bloqueos, riesgos y continuación

Docker/Compose están instalados pero el socket local da `permission_denied`. Cero pruebas Docker y cero escáneres ejecutados. No usar ejecución de host para simular aislamiento. La revisión independiente de D1P6 está NOT_VERIFIED; el threat model escrito por el implementador no la reemplaza. Se han preparado los documentos de esa frontera sin habilitarla.

Persisten: snapshots de repos, runner seguro, adaptadores Gitleaks/OSV/Semgrep, jobs/evidencia/reportes, observabilidad, gateway de agentes, controles legales, presupuesto, SDK/Hono/UI y E2E de las fases posteriores. **No se ha modificado `/agente`, desplegado, conectado clientes ni fusionado esta implementación a main.**

Código y reporte publicados en [PR#1](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/pull/1), rama `feat/cyber-d1-foundation`, para preservar el trabajo. El árbol de código publicado `ca64eb57941af10de2d5774238d446ca508fd0a2` coincide con el checkout local aunque sus commits tienen parent distinto por la publicación API inicial. La autorización de publicar documentación en main no se extrapola a fusionar código automáticamente. No se solicita ninguna confirmación rutinaria para continuar el desarrollo autorizado.

## Reversión

Detener el servicio y conservar datos/auditoría/backups. No ofrecer downgrade destructivo. La suite probó restaurar una copia consistente SQLite sintética; no se ha ensayado restauración cloud o Windows. Ver [QUICKSTART](../../QUICKSTART.md), [DECISIONS](../../DECISIONS.md), [THREAT-MODEL](../../THREAT-MODEL.md) y [SCOPE](../../SCOPE.md).
