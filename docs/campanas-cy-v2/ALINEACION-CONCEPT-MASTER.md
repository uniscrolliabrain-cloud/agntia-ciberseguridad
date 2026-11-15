# Alineación con el Concept Master

**Fecha:** 2026-11-15. **Marco superior:** [CONCEPT-MASTER.md](CONCEPT-MASTER.md).
**Estado del repo:** demo sintética; cubre el sustrato técnico, no la visión completa.

Este documento corrige la lectura anterior. El programa CY-V2 y la arquitectura de E/S describen
un **middleware de auditoría con evidencia**; el Concept Master describe un **motor inmunitario
empresarial que protege, repara, reconstruye y evoluciona**. Lo primero es una parte de lo segundo,
no su equivalente.

## 1. Veredicto de cobertura

| Dominio del Concept Master | Cobertura real hoy | Dónde vive | Qué falta |
|---|---|---|---|
| 1. Infraestructura y cloud | Baja | `adapters/trivy`, config de targets | Conectores AWS/Azure/GCP, K8s, CSPM real (CY-V2-10/11) |
| 2. Software y DevSecOps | Media-alta | 4 escáneres, SBOM, reglas | Cobertura por lenguaje, DAST, remediación (CY-V2-04/29–31) |
| 3. IA y agentes | Media | Gateway, policy, evaluación scripted | RAG/memoria, MCP adversarial, inventario de agentes (CY-V2-22–26) |
| 4. Detección, intel y respuesta | Baja | Outbox, gobernanza de incidentes | Feeds, normalización, SIEM, casos, hunting (CY-V2-15–21) |
| 5. Identidad y confianza cero | Media | Principales, grants, roles, revocación | IdP, entitlement graph, escaladas (CY-V2-02/11) |
| 6. Resiliencia y recuperación | Baja-media | Vault, backup/restore lab | Continuidad por proceso, RTO/RPO, simulacros (CY-V2-33) |
| 7. Antifraude y comunicaciones | Baja | `governance/fraud.py` | Ingesta de correo, deepfake, verificación fuera de banda (CY-V2-27/28) |
| 8. Gobernanza y cumplimiento | Media | Legal, privacidad, evidencias | NIS2, CRA, AI Act, paquetes auditables (CY-V2-41) |
| 9. Gemelo digital | **Ausente** | Grafo v1 previsto (CY-V2-12–14) | Procesos, servicios críticos, proveedores, simulación |
| 10. Actualización y regeneración | Baja | Propuestas de remediación | Parche en sandbox, regresión, despliegue, flota multi-cliente |

**Conclusión:** el repo cubre aproximadamente **5 de 10 dominios**, y de ellos solo dos con
profundidad. El concepto de “sistema inmunitario” exige una capa que hoy no existe.

## 2. Los cuatro huecos que cambian el producto

### 2.1 Gemelo digital de negocio (no solo de activos)

El grafo de las campañas 12–14 relaciona activos, identidades y findings. El Concept Master pide
además **procesos empresariales y servicios críticos**: facturación, atención, pagos, logística,
autenticación, proveedores. Sin ellos no se puede responder «si falla X, ¿qué deja de funcionar?».

### 2.2 Antivisiones

No hay ningún motor de escenarios negativos. Es un concepto propio y diferenciador: biblioteca de
antivisiones, propagación de fallos por el grafo, servicios mínimos, protocolos y simulacros.

### 2.3 Flota multi-cliente

El caso «vulnerabilidad crítica en 40 empresas» no está cubierto: hoy cada tenant es un silo y no
existe detección agregada, priorización por flota ni despliegue masivo controlado con verificación.

### 2.4 Evolución y certificación

El producto debe mejorar sus propios adaptadores, reglas y procedimientos, y producir evidencia
periódica verificable (backups restaurados, continuidad ensayada, permisos auditados). Hoy hay
evidencia por job, no un **expediente de resiliencia** reutilizable por clientes, auditores o
aseguradores.

## 3. Qué campañas del programa 42 siguen siendo válidas

Todas, pero cambian de rango: pasan de «el producto» a «el sustrato del producto». En concreto:

- G0 (01–08) sigue siendo obligatorio: sin identidad, sandbox, jobs, evidencia y contrato padre no
  hay nada.
- G1 (09–14) construye el grafo de activos; **es la base, no el gemelo digital completo**.
- G2 (15–21) aporta la capa de detección; sin ella no hay inmunidad.
- G3 (22–28) cubre seguridad agéntica y fraude; es el dominio más diferencial de AgntiaPro.
- G4 (29–35) es el corazón de «protección ejecutable»: propuesta, parche, verificación, rollback.
- G5 (36–42) entrega la experiencia y la aceptación; debe incorporar el discurso de resiliencia.

## 4. Campañas que faltan (propuesta 43–48)

| # | Campaña | Resultado | Depende de |
|---|---|---|---|
| 43 | **Gemelo digital de procesos y dependencias** | Grafo de servicios críticos, proveedores y procesos; consultas de impacto | 12–14, 33 |
| 44 | **Motor de antivisiones** | Biblioteca de escenarios, propagación de fallos, servicios mínimos, simulacros | 43 |
| 45 | **Flota multi-tenant** | Detección agregada, priorización por flota y parcheo masivo con verificación | 29–31, 43 |
| 46 | **Continuidad y reconstrucción** | RTO/RPO por proceso, restore ensayado, modo degradado, runbooks | 06, 33, 43 |
| 47 | **Evidencia de resiliencia y certificación** | Paquetes auditables, mapeo RGPD/NIS2/AI Act/CRA, madurez | 37, 41, 46 |
| 48 | **Resiliencia meso/macro e interfaz aseguradora** | Protocolos sectoriales, simulacros colectivos, indicadores para socios | 44, 47 |

Estas seis campañas no sustituyen a las 42: las completan. Sin ellas el producto es un buen
middleware; con ellas es el sistema que describes.

## 5. Cambios de encuadre obligatorios

1. **Nombre y discurso:** «motor inmunitario digital y de evolución», no «escáner con informes».
2. **Métrica principal:** tiempo hasta protección y recuperación verificada, no número de findings.
3. **Ciclo:** Observar → Auditar → Comprender → Anticipar → Planificar → Proteger → Actualizar →
   Reconstruir → Endurecer → Validar → Desplegar → Aprender debe aparecer en API, eventos y UI.
4. **Alcance:** las exclusiones actuales (gobierno, hospitales, infraestructuras críticas) pasan a
   ser **fases posteriores**, no límites permanentes del producto.
5. **E/S:** los siete planos siguen siendo válidos como sustrato, pero faltan tres planos:
   **P8 gemelo digital**, **P9 simulación/antivisión** y **P10 flota y evolución**.
6. **Roles:** Pedro investiga, Laia comunica, Marcos opera. El middleware no crea identidades
   paralelas; cada efecto conserva actor, autorización, contexto y evidencia.
7. **Tres escalas:** micro (empresa) es el piloto; meso (ecosistema) y macro (sociedad) son
   evolución, con protocolos y simulacros, no promesas de seguridad absoluta.

## 6. Qué no cambia

- La regla «LLM propone, runtime dispone».
- La separación de funciones y la aprobación humana.
- La evidencia minimizada, cifrada y trazable.
- El aislamiento multi-tenant y el deny-by-default.
- El contrato con `/agente`: capacidades tipadas, receipts y eventos; nada de shell libre.

## 7. Próximo paso recomendado

Antes de ejecutar CY-V2-02, decidir entre:

- **A)** Terminar el sustrato G0–G5 y añadir 43–48 después. Más lento hasta ver el producto completo.
- **B)** Insertar 43 (gemelo digital) y 44 (antivisiones) en paralelo a G1, porque son el
  diferenciador y condicionan el modelo de datos.
- **C)** Reordenar el programa para que 43–48 sean G6 y declarar el piloto como «inmunidad
  empresarial», no como «auditoría».

La opción B es la que menos retrabajo genera: el gemelo digital cambia el esquema de activos y
conviene construirlo antes de congelar CY-V2-12.

## 8. Estado de esta reconciliación

Documento de alineación, no implementación. No se han modificado campañas existentes ni
`docs/release/status.json`. La decisión de reordenar el programa corresponde al founder.
