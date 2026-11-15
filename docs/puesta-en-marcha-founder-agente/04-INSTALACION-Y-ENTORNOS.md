# 04 — Instalación y entornos: del repositorio al servicio privado
## E0 — Reproducción local, sin datos reales
**Founder:** autoriza entorno propio y presupuesto cero o mínimo. **Agente:** clona SHA fijado y verifica Python >=3.11, venv, Node compatible, Docker Linux/OCI y scripts del repo; no instalar paquetes globales sin necesidad.

```bash
git clone https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad.git
cd agntia-ciberseguridad
git rev-parse HEAD
python3 -m venv .venv
. .venv/bin/activate
python -m pip --version
python -m unittest discover -s tests
bash scripts/verify_lab.sh
```
Los comandos son **puntos de partida**, revisar flags/dependencias con el RUNBOOK antes de ejecutarlos. No exponer API ni conectar proveedores reales. En Windows usar PowerShell y `scripts/verify_lab.ps1`.

## E1 — Bundle reproducible
Seguir `docs/operations/RUNBOOK.md`: obtener artifact del SHA correcto, verificar attestation con `gh attestation verify manifest.json --repo uniscrolliabrain-cloud/agntia-ciberseguridad` si corresponde, hashes y `scripts/release_bundle.py --verify`. Crear venv limpia e instalar wheelhouse con `--no-index --require-hashes` y lock específico de plataforma. SDK TS se distribuye como tarball, no como paquete npm publicado. El agente reporta diferencias entre docs y scripts actuales.

## E2 — Servidor privado de laboratorio
**Founder:** elegir host Linux y región, habilitar MFA/SSH limitado, aprobar gasto. **Agente:** construir imagen por digest revisado, definir config privada, persistencia cifrada, loopback, TLS privado si aplica, no Docker socket, no red arbitraria, límites CPU/RAM/pids, FS read-only y usuario no root. `infra/compose.yaml` es el punto de partida documentado.
```bash
docker compose -f infra/compose.yaml config --quiet
# SOLO tras revisar imagen/config/volúmenes/secret refs:
docker compose -f infra/compose.yaml up -d
```
No imprimir `docker compose config` sin `--quiet` si pudiera revelar secretos. No ejecutar up en producción sin aprobación.

## E3 — Staging autorizado
DNS/TLS, IdP/MFA, API privada, OTel, métricas, backups, restore, alertas, kill switch, tenantA/tenantB sintéticos, política de red y scopes. Ejecutar E2E con activos propios de prueba. Registrar tiempo/coste real.

## E4 — Piloto con cliente
Solo tras `docs/release/PILOT-ACCEPTANCE.md`: licencia, DPA cuando aplique, ROE firmado, operador, revisión independiente, límites, retención, soporte, reversión y aprobación humana. Comenzar con análisis de bajo impacto; no escaneo activo de terceros sin autorización explícita.

## Requisitos operativos no negociables
- Runtime y volúmenes separados de /agente y otros tenants; no compartir secrets.
- Config versionada sin valores; drift detection; snapshot/restore probado.
- Egress y objetivos allowlist, validación tras DNS y redirecciones.
- Retención de evidencias, cifrado, auditoría de accesos, eliminación conforme política.
- Runbook para caídas de scanner, feeds caducados, presupuesto agotado, revocación y respuesta a incidente.

## Criterio de aceptación por entorno
E0: tests y logs reproducibles. E1: bundle verificado. E2: API privada, seguridad básica y backups. E3: aislamiento, observabilidad, recuperación y dos tenants. E4: revisión independiente y contratos. Si falta evidencia, `BLOCKED` o `NOT_VERIFIED`.
