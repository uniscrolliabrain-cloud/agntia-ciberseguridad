# Campañas de instalación y propagación — 2026-11-20

**Programa:** CY-IP (Cyber · Instalación y Propagación).
**Fecha del paquete:** 2026-11-20.
**Repositorio que se documenta:** `agntia-ciberseguridad` (hijo). El repositorio padre `agente` se cita como destino de instalación y **no se ha abierto, modificado ni ejecutado**.
**Estado global:** **SIMULACIÓN DOCUMENTAL — NO EJECUTADA**. No hay PASS, tenants reales, credenciales, despliegues ni cambios en `agente`. Única excepción: F0–F2 (manifiesto, verificación de artefacto y configuración fail-closed) existen como código probado desde el 2026-11-20; las campañas siguen sin ejecutarse.

Este paquete responde a una pregunta concreta: *si mañana se autorizara instalar este middleware
en el host y propagarlo a tenants, ¿qué campañas harían falta, en qué orden, con qué fases de
código y con qué evidencia?* La respuesta se escribe como simulación revisable, no como resultado.

## 1. Qué hay aquí y qué no

| Hay | No hay |
|---|---|
| Propuesta de 11 campañas CY-IP con dependencias, gates y rollback | Campañas ejecutadas |
| Simulaciones paso a paso de instalación en host y propagación a tenants | Instalación real en `/agente` ni en staging |
| Fases de código: F0–F2 implementadas y probadas; F3–F10 propuestas | Instalación en host, migraciones, parches en `agente` o campañas ejecutadas |
| Matriz de evidencia, riesgos y criterios de falsación | PASS, certificaciones, clientes o protección activa |

## 2. Reglas de la simulación

1. **Nada se declara ejecutado.** Todo estado es `SIMULADO` o `NOT_VERIFIED`; ninguno es `PASS`.
2. **Los comandos y salidas son expectativas.** Se escriben para que un revisor pueda ejecutarlos
   después y comparar; no son transcripciones de una sesión real.
3. **No se inventan hashes, IDs de job, tenants ni fechas de ejecución.** Los únicos números
   citados son los medidos: el 2026-11-18 (228 tests Python OK con 8 skips; SDK 12 casos, 10 pass
   y 2 skip; pack determinista con SHA256 `09c94d52…`; `provenance:check` verde) y el 2026-11-20
   (260 tests OK con 8 skips; el mismo pack verificado contra `PROVENANCE.json` con
   `scripts/verify_artifact.py`, y arranque fail-closed de la configuración de rollout). No cubren
   campañas ni código futuro.
4. **`agente` no se escribe.** Sus contratos aparecen como especificación para su equipo, igual
   que en [PATCHSETS-2026-11-18.md](../integration/PATCHSETS-2026-11-18.md).
5. **Un gate futuro no protege hoy.** La documentación no convierte `production_enabled=false`
   en una capacidad de enforcement.
6. **La licencia, el DPA, la revisión independiente y la autorización escrita del host siguen
   siendo precondiciones**, no consecuencias de este programa.

## 3. Anillos de propagación

| Anillo | Destino | Datos | Enforcement | Salida |
|---|---|---|---|---|
| **A · Laboratorio** | Tenant sintético del repo | Fixtures | Nunca | Contratos y planes deterministas |
| **B · Staging del host** | Copia no productiva de `agente` | Sintéticos o anonimizados | Apagado; solo lectura gobernada | Instalación reproducible y rollback probado |
| **C · Piloto** | 1 tenant designado por el owner | Reales acotados, con consentimiento | Lectura gobernada; escritura deshabilitada | Evidencia y aceptación del piloto |
| **D · General** | Resto de tenants habilitados | Reales | Solo capacidades ya aprobadas | Propagación por olas con cuotas y aborto |

La regla es **un anillo por vez y nunca saltar C**. Un tenant del anillo D sin paso previo por C
queda fuera de la propuesta.

## 4. Escalera de capacidades

| Nivel | Nombre | Qué permite | Quién lo aprueba |
|---|---|---|---|
| N0 | Sin integración | Nada | — |
| N1 | Lectura gobernada | Activos, findings y jobs del tenant, con delegación de un uso | Humano con `agents.delegate` |
| N2 | Sombra | El host calcula decisiones de política y las registra sin aplicarlas | Owner + revisión independiente |
| N3 | Enforcement limitado | Bloqueo de acciones concretas ya cubiertas por política y tests | Revisión independiente + aceptación escrita |
| N4 | Respuesta automática | Contención sin humano | **Fuera de esta propuesta** |

Este programa llega como máximo a **N2** en simulación. N3 y N4 se mencionan solo para marcar
el límite y evitar que un lector los deduzca del texto.

## 5. Documentos

| Documento | Contenido |
|---|---|
| [00 · Propuesta de campañas](00-PROPUESTA-CAMPANAS.md) | Objetivo, principios, superficies, 11 campañas, DAG, calendario y precondiciones |
| [01 · Simulación de instalación](01-SIMULACION-INSTALACION-HOST.md) | Preflight, verificación de artefacto, instalación, sombra y fallos inyectados |
| [02 · Simulación de propagación](02-SIMULACION-PROPAGACION-TENANTS.md) | Anillos, inscripción, olas, cuotas, incidentes simulados y revocación |
| [03 · Fases de código propuestas](03-FASES-CODIGO-PROPUESTAS.md) | F0–F10: archivos, contratos, invariantes, pruebas y rollback |
| [04 · Matriz de gates y evidencia](04-MATRIZ-GATES-Y-EVIDENCIA.md) | Gates G1–G6, matriz, riesgos, falsación y decisiones pedidas |

## 6. Resumen de campañas

| Campaña | Objetivo | Anillo | Estado |
|---|---|---|---|
| IP-00 | Congelar inventario de instalación y línea base | A | SIMULADA |
| IP-01 | Contrato de instalación y verificación de artefacto | A | SIMULADA |
| IP-02 | Instalación en laboratorio con datos sintéticos | A | SIMULADA |
| IP-03 | Instalación en staging del host, enforcement apagado | B | SIMULADA |
| IP-04 | Inscripción del primer tenant piloto en lectura gobernada | C | SIMULADA |
| IP-05 | Propagación canaria 5 % → 25 % con cuotas | C | SIMULADA |
| IP-06 | Propagación general por olas y presupuesto | D | SIMULADA |
| IP-07 | Propagación a agentes con delegaciones de un uso | C–D | SIMULADA |
| IP-08 | Sombra de políticas (N2) sin enforcement | C | SIMULADA |
| IP-09 | Revocación, desinstalación y kill switch | A–D | SIMULADA |
| IP-10 | Verificación independiente y cierre del programa | A–D | SIMULADA |

IP-01 ya cuenta con el manifiesto y el verificador implementados y probados en este árbol (F0/F1).
Eso adelanta trabajo de la campaña, no la ejecuta: no hay host, no hay tenant real y su estado
sigue siendo `SIMULADA`.

## 7. Qué haría falta para ejecutar de verdad

- Autorización escrita del owner para el host y para cada anillo.
- Revisión independiente de autenticación, aislamiento por tenant, cifrado y restore.
- Licencia del paquete y del modelo de distribución resueltas; hoy `private=true` y licencia pendiente.
- DPA y base jurídica por tenant antes de tocar datos reales.
- Secret manager real con rotación; los ejemplos de configuración son referencias, no valores.
- Ventana de operación con on-call, criterios de aborto y rollback ya ensayado en A y B.
- Evidencia archivada con SHA, versión de herramienta y resultados, incluidos error, skipped y
  `not_tested`. Un scan sin hallazgos no certifica nada.

Mientras cualquiera de esas condiciones falte, este paquete sigue siendo un plan: **no una
instalación, no una propagación y no una protección**.
