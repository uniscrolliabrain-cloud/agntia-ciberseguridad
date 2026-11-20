# 04 · Matriz de gates, evidencia y riesgos

**Fecha:** 2026-11-20. **Estado:** simulación; ninguna celda de esta matriz es un PASS.

## 1. Gates

| Gate | Pregunta que responde | Evidencia mínima | Falla si |
|---|---|---|---|
| **G1 · Identidad y aislamiento** | ¿Cada lectura pertenece al tenant autenticado? | Pruebas cruzadas entre dos tenants, rechazos y auditoría | Hay una lectura cruzada o una identidad derivada del cliente |
| **G2 · Configuración y secretos** | ¿La instalación es reproducible y falla cerrada? | Digest, procedencia, arranque sin referencia, revisión de logs | Se usa un valor por defecto inseguro o se filtra un secreto |
| **G3 · Evidencia y resiliencia** | ¿Se puede reproducir y recuperar? | Comandos, exit codes, lease recuperado, job sin estado falso | Falta evidencia o un fallo deja estado inconsistente |
| **G4 · Reversibilidad** | ¿Se puede volver atrás dentro del tiempo declarado? | Ensayo de rollback cronometrado y estado posterior | El host no vuelve a su comportamiento previo |
| **G5 · Operación** | ¿Hay señales, alertas y on-call? | Métricas, alerta disparada, runbook y responsable | Una alerta definida nunca se probó |
| **G6 · Revisión independiente** | ¿Lo revisó alguien que no lo escribió? | Informe firmado con hallazgos y límites | El revisor es el autor o no hay informe |

## 2. Matriz campaña × gate

`S` = simulado en este paquete; `—` = no aplica; `P` = pendiente de ejecución real.

| Campaña | G1 | G2 | G3 | G4 | G5 | G6 |
|---|---|---|---|---|---|---|
| IP-00 Inventario | S | S | S | — | — | P |
| IP-01 Artefacto | — | S | S | S | — | P |
| IP-02 Laboratorio | S | S | S | S | — | P |
| IP-03 Staging del host | S | S | S | S | P | P |
| IP-04 Tenant piloto | S | P | S | S | P | P |
| IP-05 Canaria | S | — | S | S | S | P |
| IP-06 Olas generales | S | — | S | S | S | P |
| IP-07 Agentes | S | — | S | S | — | P |
| IP-08 Sombra | S | — | S | S | S | P |
| IP-09 Revocación | S | S | S | S | S | P |
| IP-10 Cierre | S | S | S | S | S | P |

Ninguna `S` equivale a PASS: significa que la campaña tiene guion, evidencia esperada y criterio
de aborto. La columna G6 es `P` en todas porque la revisión independiente sigue pendiente.

## 3. Evidencia esperada por campaña

| Campaña | Artefactos | Estado hoy |
|---|---|---|
| IP-00 | `IP-00/inventario.json`, `IP-00/brechas.md` | No existen |
| IP-01 | `IP-01/verificacion.txt`, `IP-01/mismatch.txt` | No existen |
| IP-02 | `IP-02/instalacion.log`, `IP-02/aislamiento.txt` | No existen |
| IP-03 | `IP-03/contrato-vivo.txt`, `IP-03/rollback.txt` | No existen |
| IP-04 | `IP-04/inscripcion.json`, `IP-04/delegacion.txt` | No existen |
| IP-05 | `IP-05/olas.json`, `IP-05/telemetria.txt` | No existen |
| IP-06 | `IP-06/olas.json`, `IP-06/incidentes.md` | No existen |
| IP-07 | `IP-07/delegaciones.txt`, `IP-07/rechazos.txt` | No existen |
| IP-08 | `IP-08/sombra.json`, `IP-08/divergencias.md` | No existen |
| IP-09 | `IP-09/killswitch.txt`, `IP-09/desinstalacion.txt` | No existen |
| IP-10 | `IP-10/revision.md`, `IP-10/limites.md` | No existen |

Los nombres fijan el contrato de evidencia. Un artefacto ausente es `NOT_VERIFIED`, no "sin
hallazgos".

## 4. Riesgos

| # | Riesgo | Impacto | Probabilidad | Mitigación | Disparador |
|---|---|---|---|---|---|
| R1 | Lectura cruzada entre tenants | Crítico | Baja con tests; alta si se improvisa | Pruebas de dos tenants en cada ola; tenant del servidor | Cualquier rechazo inexplicado |
| R2 | Secreto en logs o plan | Crítico | Media | Referencias, revisión de logs, sin valores en el plan | Cualquier valor en claro |
| R3 | Artefacto no reproducible | Alto | Media | Digest fijo, `provenance:check`, `npm ci --ignore-scripts` | Digest distinto |
| R4 | Rollback no probado | Alto | Alta | Ensayo en A y B; cronómetro; host previo | Rollback > 15 min |
| R5 | Deriva de política | Alto | Media | Versión aprobada por tenant; alerta; aborto | Versión aplicada ≠ aprobada |
| R6 | Presupuesto agotado a mitad de ola | Medio | Media | Reserva previa y cuota por tenant | Reserva rechazada |
| R7 | Agente con credenciales de owner | Crítico | Baja | Principal `agent`, delegación de un uso, pruebas negativas | Token con principal distinto |
| R8 | Falsa sensación de seguridad por documentar | Alto | Media | Estados `SIMULADO` y `NOT_VERIFIED`; sin PASS | Alguien cita el plan como protección |
| R9 | Dependencia de `agente` sin acuerdo | Alto | Alta | Contrato explícito; bloqueo hasta autorización | Instalación sin revisión del padre |
| R10 | Coste o licencia no resueltos | Medio | Media | No publicar ni cobrar; revisar licencia antes de distribuir | Uso comercial del paquete |

## 5. Qué falsaría esta propuesta

Si al ejecutar aparece cualquiera de estas observaciones, el plan debe revisarse, no maquillarse:

1. Una lectura devuelve datos de otro tenant.
2. El host arranca con una referencia de secreto ausente.
3. El mismo estado produce planes distintos para la misma política.
4. Un rollback deja el host sin el comportamiento previo.
5. Una alerta de aislamiento no llega a nadie.
6. Un agente reutiliza una delegación consumida.
7. El paquete abre red al importarse.
8. La revisión independiente encuentra un hallazgo crítico abierto.

## 6. Decisiones que se piden al owner

| # | Decisión | Opciones | Recomendación |
|---|---|---|---|
| D1 | Autorizar anillo B en staging del host | sí / no / más adelante | Sí, con ventana y rollback ensayado |
| D2 | Designar tenant piloto del anillo C | un tenant / ninguno | Uno, con consentimiento y DPA |
| D3 | Fijar umbral de divergencia para IP-08 | 0 / acordado por campaña | 0 no explicadas |
| D4 | Autorizar escritura en `agente` para PS-P1…PS-P6 | sí / no | No en este programa; PR separado del equipo del padre |
| D5 | Aceptar que el techo es N2 | sí / no | Sí; N3 exige otra revisión |

Sin D1 y D2, el programa se queda en anillo A. Sin D4, `agente` sigue siendo especificación.

## 7. Registro de estado

| Elemento | Estado |
|---|---|
| Campañas IP-00…IP-10 | `SIMULADA` |
| Fases F0…F10 | `PROPUESTA — NO APLICADA` |
| Instalación en host | `NO EJECUTADA` |
| Propagación a tenants | `NO EJECUTADA` |
| Revisión independiente | `PENDIENTE` |
| Enforcement (N3) | `FUERA DE ALCANCE` |
| Respuesta automática (N4) | `FUERA DE ALCANCE` |
| Escritura en `agente` | `NO REALIZADA` |

Este registro es la verdad del paquete. Cualquier resumen que lo contradiga —incluido un README
posterior— debe corregirse contra esta tabla.
