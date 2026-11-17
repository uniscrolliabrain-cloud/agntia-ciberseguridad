# VS-06C — Primer run real del CI de dependencias

**Base:** `7fdb14e`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
**Estado:** `PARTIAL` alto: el hueco concreto («el workflow nunca se ha ejecutado») queda cerrado con un
recibo de GitHub Actions. La atestación externa y el gate `--production` siguen abiertos **por diseño**.

## Qué se buscaba

VS-06B dejó `pip-audit` local en 0 vulnerabilidades y añadió `.github/workflows/dependency-audit.yml`,
pero con una advertencia honesta: **no había ningún run real**. Un workflow sin ejecutar es una
intención, no un control.

## Evidencia obtenida

Consultado vía API de GitHub sobre `uniscrolliabrain-cloud/agntia-ciberseguridad`:

| Run | Evento | Head | Conclusión | Inicio (UTC) | Fin (UTC) |
|---|---|---|---|---|---|
| `44084229258` | `push` | `7fdb14e` | `success` | 2026-11-17T12:33:18Z | — |
| `44084241625` | `pull_request` | `7fdb14e` | `success` | 2026-11-17T12:33:23Z | 12:34:00Z |

El workflow acumula **6 runs** (`total_count: 6`), todos sobre esta rama. Los dos citados son los que
corresponden al head actual, uno por cada disparador (`on: [push, pull_request]`).

## Qué implica un `success`

El job `audit` crea un entorno aislado, instala `pip-audit==2.10.1` y ejecuta **dos** auditorías:

```bash
.audit-venv/bin/python -m pip_audit --local --progress-spinner off
.audit-venv/bin/python -m pip_audit . --progress-spinner off
```

`pip-audit` devuelve código distinto de cero cuando encuentra una vulnerabilidad conocida, así que un
run verde significa: **con las versiones fijadas, en Python 3.12, el 2026-11-17, el conjunto de
dependencias declarado no tenía avisos abiertos**. Es la misma conclusión que se obtuvo en local, ahora
sostenida por un ejecutor distinto del portátil.

## Lo que un run verde NO significa

- **No es atestación de cadena de suministro.** No hay SLSA, no hay firma de artefactos, no hay
  procedencia verificable del índice de paquetes.
- **No cubre las imágenes de escáneres.** `gitleaks`, `semgrep`, `trivy` y `osv-scanner` van por digest
  en su propio workflow (`scanner-contracts.yml`); este job audita dependencias de Python.
- **No dice nada sobre vulnerabilidades no publicadas** ni sobre el día siguiente: la foto caduca.
- **No sustituye a `releasecheck.py --production`**, que sigue devolviendo **exit 1** de forma cerrada y
  no se relajó para que este informe quedara bonito.

## Nota sobre el orden de los hechos

El run existía ya cuando se abrió esta campaña: los `push` de VS-05A, VS-07B y VS-07C dispararon el
workflow porque `dependency-audit.yml` estaba fusionado en la rama desde VS-06B. No se ha reejecutado
nada a mano ni se ha tocado el YAML; **la campaña documenta el recibo, no lo fabrica**.

## Gate

`PARTIAL` alto. Se cierra el punto «falta run de CI» de VS-06B. Siguen abiertos, con motivo:

- Atestación externa y `--production` fail-closed: requieren decisión de release del founder.
- Un run sobre `main` **después** de fusionar #14–#17: hoy el CI verde es de la rama, no de `main`.

**Seguimiento:** [VS-06B-REPORT.md](VS-06B-REPORT.md) para el fix de trazas y los pins;
[VS-06-REPORT.md](VS-06-REPORT.md) para el diagnóstico original.
