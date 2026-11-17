# VS-07C — Runbook por alerta (P4 documental)

**Base:** `eca27cb`. **Rama:** `docs/cyber-bitacora-viva`. **PR:** #17.
**Estado:** `PARTIAL` documental: el procedimiento existe y es ejecutable en local; propietario,
guardia y canal siguen `BLOCKED`.

## Qué faltaba

VS-07 dejó P4 (runbook de incidentes) abierto y VS-07B confirmó que dos de tres averías ya pagan a
alguien. Pero una alerta sin procedimiento deja al que la recibe sin saber qué mirar ni qué no
concluir. El programa pedía explícitamente "umbrales con propietario y runbook"; el propietario no lo
puede poner una IA, el procedimiento sí.

## Qué se escribió

`docs/operacion-actual/campanas-vertical-slice-beta/RUNBOOK-ALERTAS.md`:

- Cinco reglas comunes, incluida la más importante: **un acuse no es contención** y **la ausencia de
  señal no es salud**.
- Una tabla por regla con significado operativo, comprobaciones concretas y **lo que no se puede
  concluir**. Esa última columna es la que evita el daño típico: leer un scan incompleto como
  "activo limpio" o un `up == 0` como "no hay incidentes".
- Procedimiento por severidad: cinco `warning` y un `info`; el cupo lo amplía el propietario de la
  autorización, no el operador de guardia.
- Dónde se lee cada cosa: `/metrics` con token de métricas, estados de job con `jobs.read`, SQLite en
  laboratorio.
- Huecos declarados: propietario y horario, canal con acuse humano, exportador de backup y ensayo con
  Prometheus/Alertmanager reales.

## Resultado medido

- Validador documental: **PASS**, 293 archivos Markdown, enlaces locales resueltos (incluye los
  enlaces del runbook a VS-07A y VS-07B).
- Sin cambios de código: la suite sigue en **215 tests OK (8 skipped)**.
- No se ejecutó Prometheus ni Alertmanager: el runbook no se ha ensayado contra un colector real.

## Lo que esto NO es

- **No es un turno de guardia.** No hay persona asignada, ni horario, ni escalado; eso requiere
  decisión y coste del founder.
- **No es una promesa de detección.** Las reglas siguen siendo hipótesis de piloto; ninguna alerta
  demuestra que un activo esté seguro.
- **No cubre backup.** El simulacro D2 de VS-07B sigue `BLOCKED`: sin métrica no hay alerta que este
  runbook pueda atender.
- **No se ha ensayado.** Un runbook sin ensayo es un borrador: el ensayo exige el colector real y una
  persona que lo recorra.

## Gate

`PARTIAL` documental: procedimiento listo para revisión humana; operación 24×7 sigue cerrada.

## Delta recomendado

1. Asignar propietario y ventana de guardia por alerta (founder).
2. Ensayar el runbook con Prometheus + Alertmanager en Docker y corregir lo que no funcione.
3. Exportador de backup y su regla; repetir el simulacro D2 hasta que pagina.
