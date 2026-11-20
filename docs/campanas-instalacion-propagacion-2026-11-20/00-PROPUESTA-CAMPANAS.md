# 00 · Propuesta de campañas para instalar y propagar ciberseguridad

**Fecha:** 2026-11-20. **Programa:** CY-IP. **Estado:** propuesta simulada, no ejecutada.
**Base de partida:** `docs/release/status.json` con `production_enabled=false`, 2 fases PASS y
40 PARTIAL; paquete `@agntia/ciberseguridad@0.1.0-alpha.3`; auditoría de los dos repositorios
del 2026-11-18.

## 1. Problema

El middleware existe como demo sintética con API, SDK, adaptadores offline y contratos de agente,
pero **no hay un camino escrito para instalarlo en el host ni para propagarlo a tenants**. Sin ese
camino, cualquier instalación real improvisaría orden, permisos, cuotas y rollback. Esta propuesta
fija ese camino antes de tocar código o infraestructura.

La distinción central del programa:

- **Instalar** es dejar el paquete y su configuración disponibles y verificables en un host.
- **Habilitar** es permitir que un tenant use una capacidad concreta.
- **Propagar** es repetir la habilitación por olas, con evidencia y posibilidad de volver atrás.

Instalar no habilita. Habilitar no propaga. Propagar no autoriza enforcement.

## 2. Principios

1. **Fail-closed en configuración.** Una referencia ausente, un tenant no inscrito o una versión
   de política desconocida detienen la ola; no se degrada el aislamiento para continuar.
2. **Una capacidad por ola.** No se propaga "ciberseguridad" en abstracto: se propaga
   `findings.read`, luego `jobs.read`, luego sombra de política. Cada una tiene su gate.
3. **Un anillo por vez.** A → B → C → D. El anillo D nunca empieza con tenants que no pasaron C.
4. **Reversibilidad antes que velocidad.** Cada ola declara su rollback y su tiempo máximo de
   reversión antes de empezar.
5. **Identidad del servidor.** Tenant, activo y credencial se derivan del principal autenticado;
   nunca de un modelo, de una cabecera del navegador ni de un campo del plan.
6. **Evidencia minimizada.** Se archiva lo necesario para reproducir la decisión (SHA, versión,
   configuración sin secretos, resultados), no contenido de clientes.
7. **Sin PASS por documentación.** Un plan validado no ejecuta pruebas; un gate futuro no protege.
8. **Parada humana.** Cualquier anomalía de aislamiento detiene el programa, no solo la ola.

## 3. Superficies de instalación

| Superficie | Qué se instala | Quién escribe | Verificación |
|---|---|---|---|
| Paquete servidor | `@agntia/ciberseguridad` (workspace o artefacto) | Equipo del hijo | Digest, `provenance:check`, tests |
| Host `agente` | Resolver de sesión, cliente servidor, rutas BFF | Equipo del padre | Contrato vivo en loopback |
| Configuración | Referencias a entorno y secretos, allowlist de origen | Operación | Validación fail-closed al arrancar |
| Tenants | Inscripción, consentimiento, cuotas, presupuesto | Operación + owner | Estado por tenant y auditoría |
| Agentes | Manifiesto, aprobación, delegación de un uso | Humano autorizado | Consumo único y TTL |
| Observabilidad | Métricas, alertas, paneles de deriva | Operación | Alertas disparadas en simulacro |
| Evidencia | Informes, hashes, resultados de gates | Responsable de campaña | Paquete reproducible |

`agente` aparece como superficie de destino, no como código modificado en este repositorio.

## 4. Campañas

Cada tarjeta declara objetivo, anillo, precondición dura, fases de código implicadas, qué simula,
gate de salida y rollback. Las fases F0–F10 se detallan en
[03-FASES-CODIGO-PROPUESTAS.md](03-FASES-CODIGO-PROPUESTAS.md).

### IP-00 · Congelar inventario de instalación

| Campo | Valor |
|---|---|
| Objetivo | Inventariar versiones, rutas, flags, migraciones y secretos referenciados antes de instalar |
| Anillo | A |
| Precondición | Acceso de lectura al host y a este repo; sin credenciales reales |
| Fases | F0 |
| Simulación | Se recorre el inventario y se compara con `docs/release/status.json`; se anotan brechas |
| Gate de salida | G1: inventario completo, sin valores secretos, con SHA de partida |
| Rollback | No aplica: solo lectura |
| Evidencia | `IP-00/inventario.json`, `IP-00/brechas.md` |

### IP-01 · Contrato de instalación y artefacto verificable

| Campo | Valor |
|---|---|
| Objetivo | Fijar qué artefacto se instala, cómo se verifica y qué falla cierra la instalación |
| Anillo | A |
| Precondición | IP-00 cerrada; `npm ci --ignore-scripts` reproducible |
| Fases | F1, F2 |
| Simulación | Se calcula el digest del pack y se compara con `PROVENANCE.json`; se fuerza un mismatch |
| Gate de salida | G2: digest, procedencia y tests del artefacto reproducibles; mismatch aborta |
| Rollback | Descartar el artefacto; no hay estado que revertir |
| Evidencia | `IP-01/verificacion.txt`, `IP-01/mismatch.txt` |

### IP-02 · Instalación en laboratorio

| Campo | Valor |
|---|---|
| Objetivo | Instalar el paquete y arrancar el host sintético en anillo A sin enforcement |
| Anillo | A |
| Precondición | IP-01 cerrada; tenant sintético; sin datos de clientes |
| Fases | F3, F4 |
| Simulación | Secuencia de instalación, arranque, lectura gobernada y parada limpia |
| Gate de salida | G1 y G3: aislamiento entre dos tenants sintéticos y evidencia de cada paso |
| Rollback | `rollout halt` local y retirada del paquete; estado sintético desechable |
| Evidencia | `IP-02/instalacion.log`, `IP-02/aislamiento.txt` |

### IP-03 · Instalación en staging del host

| Campo | Valor |
|---|---|
| Objetivo | Repetir la instalación en una copia no productiva de `agente`, con enforcement apagado |
| Anillo | B |
| Precondición | IP-02 cerrada; autorización escrita del host; revisión del patchset del padre |
| Fases | F2, F5, F6 |
| Simulación | Resolver de sesión, cliente servidor, rutas BFF y contrato vivo; sin tráfico real |
| Gate de salida | G1, G2 y G4: sesión, tenant del servidor, secretos por referencia, rollback < 15 min |
| Rollback | Revertir el despliegue del host y apagar la flag; el paquete no escribe datos del host |
| Evidencia | `IP-03/contrato-vivo.txt`, `IP-03/rollback.txt` |

### IP-04 · Inscripción del tenant piloto

| Campo | Valor |
|---|---|
| Objetivo | Inscribir un tenant designado con consentimiento, cuotas y lectura gobernada |
| Anillo | C |
| Precondición | IP-03 cerrada; DPA y base jurídica; tenant y activos declarados por el owner |
| Fases | F4, F5, F7 |
| Simulación | Alta, consentimiento, primera lectura con delegación de un uso y su consumo |
| Gate de salida | G1 y G3: lectura solo del tenant inscrito, delegación consumida una vez |
| Rollback | Revocar delegación, apagar flag del tenant, conservar auditoría |
| Evidencia | `IP-04/inscripcion.json`, `IP-04/delegacion.txt` |

### IP-05 · Propagación canaria

| Campo | Valor |
|---|---|
| Objetivo | Pasar de 1 tenant a una fracción pequeña (5 %) y luego 25 %, con cuotas |
| Anillo | C |
| Precondición | IP-04 con ventana de observación sin anomalías de aislamiento |
| Fases | F5, F7, F8 |
| Simulación | Olas 5 % → 25 %, con presupuesto, límite de peticiones y aborto por deriva |
| Gate de salida | G3 y G5: sin cruces de tenant, sin agotar presupuesto, telemetría completa |
| Rollback | Volver a la ola anterior; ningún tenant sale del anillo C sin decisión explícita |
| Evidencia | `IP-05/olas.json`, `IP-05/telemetria.txt` |

### IP-06 · Propagación general por olas

| Campo | Valor |
|---|---|
| Objetivo | Extender la lectura gobernada a los tenants habilitados, en olas del 25 % |
| Anillo | D |
| Precondición | IP-05 cerrada; capacidad de soporte y on-call; cupo por tenant |
| Fases | F5, F7, F8 |
| Simulación | Cuatro olas, cada una con criterio de aborto y ventana de observación |
| Gate de salida | G1, G3, G5: aislamiento sostenido, cuotas respetadas, soporte informado |
| Rollback | Deshabilitar por ola y por tenant; el estado de inscripción se conserva |
| Evidencia | `IP-06/olas.json`, `IP-06/incidentes.md` |

### IP-07 · Propagación a agentes

| Campo | Valor |
|---|---|
| Objetivo | Permitir que agentes del host lean a través de delegaciones de un uso |
| Anillo | C–D |
| Precondición | IP-04/IP-05 cerradas; manifiesto y aprobación humana vigentes |
| Fases | F6, F7 |
| Simulación | Alta de agente, aprobación, emisión, consumo y rechazo del segundo uso |
| Gate de salida | G1 y G3: sin credenciales de owner, sin reutilización, TTL máximo 5 min |
| Rollback | Revocar delegación y manifiesto; el agente vuelve a `agent_gateway_required` |
| Evidencia | `IP-07/delegaciones.txt`, `IP-07/rechazos.txt` |

### IP-08 · Sombra de políticas (N2)

| Campo | Valor |
|---|---|
| Objetivo | Calcular decisiones de política y registrarlas sin aplicarlas, para medir falsos positivos |
| Anillo | C |
| Precondición | IP-04 cerrada; revisión independiente de la política; ningún enforcement |
| Fases | F4, F9 |
| Simulación | Se compara decisión calculada con acción permitida; se cuentan divergencias |
| Gate de salida | G6: política revisada, divergencias explicadas, cero bloqueos reales |
| Rollback | Apagar la sombra; no hay efecto sobre acciones |
| Evidencia | `IP-08/sombra.json`, `IP-08/divergencias.md` |

### IP-09 · Revocación y desinstalación

| Campo | Valor |
|---|---|
| Objetivo | Probar que se puede retirar la capacidad y el paquete sin dejar estado huérfano |
| Anillo | A–D |
| Precondición | Al menos una ola de IP-05 aplicada en simulacro |
| Fases | F9 |
| Simulación | Kill switch, revocación por tenant, retirada del host y verificación de auditoría |
| Gate de salida | G4: reversión completa dentro del tiempo declarado; auditoría íntegra |
| Rollback | No aplica: la campaña es el rollback |
| Evidencia | `IP-09/killswitch.txt`, `IP-09/desinstalacion.txt` |

### IP-10 · Verificación independiente y cierre

| Campo | Valor |
|---|---|
| Objetivo | Revisar el conjunto con un revisor que no escribió el código ni el plan |
| Anillo | A–D |
| Precondición | IP-00 a IP-09 simuladas y documentadas; evidencia archivada |
| Fases | F10 |
| Simulación | Recorrido de la matriz de gates y listado de lo que sigue `NOT_VERIFIED` |
| Gate de salida | G6: informe firmado; cualquier fallo vuelve a la campaña de origen |
| Rollback | No aplica |
| Evidencia | `IP-10/revision.md`, `IP-10/limites.md` |

## 5. Dependencias

```
IP-00 → IP-01 → IP-02 → IP-03 → IP-04 → IP-05 → IP-06
                                   ↘ IP-07
                                   ↘ IP-08
IP-02..IP-06 → IP-09
IP-00..IP-09 → IP-10
```

Paralelismo permitido solo con ownership disjunto: IP-07 e IP-08 pueden correr juntas sobre
tenants distintos, nunca sobre el mismo tenant en la misma ventana.

## 6. Calendario simulado

| Semana | Campañas | Hito |
|---|---|---|
| W0 | IP-00, IP-01 | Inventario y artefacto verificable |
| W1 | IP-02 | Instalación en laboratorio con dos tenants sintéticos |
| W2 | IP-03 | Staging del host con rollback medido |
| W3 | IP-04 | Primer tenant piloto en lectura gobernada |
| W4 | IP-05 | Canaria 5 % → 25 % |
| W5 | IP-06, IP-07 | Olas generales y agentes |
| W6 | IP-08, IP-09, IP-10 | Sombra, revocación y revisión independiente |

El calendario es una hipótesis de planificación, no un compromiso: cada campaña puede detenerse
sin arrastrar a las siguientes.

## 7. Precondiciones heredadas de la auditoría del 2026-11-18

| Origen | Qué bloquea | Campañas afectadas |
|---|---|---|
| I-02 · configuración y secretos por referencia | Sin secret manager real, la instalación no es reproducible | IP-03, IP-06 |
| I-04 · superficie de delegaciones | Sin emisión/revocación gobernada no hay agentes | IP-07 |
| I-07 · artefacto determinista | Sin digest reproducible no hay verificación | IP-01 |
| I-09 · `tenant_id` en proyección | Sin tenant en la lectura no se puede auditar el aislamiento | IP-04, IP-05 |
| I-10 · `Job.state` | Sin estados cerrados la telemetría miente | IP-05, IP-06 |
| PS-P1…PS-P6 (padre) | Sin configuración, PDP, ruta y relay no hay instalación en `agente` | IP-03, IP-07 |

Ninguna de estas brechas se cierra por escribir este documento.

## 8. Fuera de alcance

- Contención automática, respuesta a incidentes o acciones sobre producción (N4).
- Phishing, pruebas destructivas o escaneo de infraestructura de terceros.
- Compra de planes, activación de cobros o auto-upgrades.
- Publicación del paquete en npm o distribución comercial.
- Cualquier escritura en `agente` sin autorización expresa y revisión de su equipo.

## 9. Criterio de éxito

El programa se considera **listo para ejecución real** —no ejecutado— cuando: las 11 campañas
tienen gate, evidencia esperada y rollback; las fases F0–F10 tienen contrato e invariantes; la
matriz de [04](04-MATRIZ-GATES-Y-EVIDENCIA.md) no tiene celdas vacías; y un revisor independiente
puede recorrer el plan sin preguntar qué falta. Ese es el techo de este documento.
