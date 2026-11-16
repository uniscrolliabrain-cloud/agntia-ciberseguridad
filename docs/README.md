> **ÍNDICE OPERATIVO ACTUAL — 2026-11-16**
> **Comenzar en [docs/operacion-actual/README.md](operacion-actual/README.md)**. Los documentos de esta carpeta son historia, investigación y especificaciones que pueden contener estados superados. [Matriz de cierre](operacion-actual/02-MATRIZ-CIERRE-PRODUCCION.md) · [Cuentas y secretos](operacion-actual/03-CUENTAS-SECRETOS-FOUNDER.md) · [Handoff](operacion-actual/04-HANDOFF-EJECUCION.md). El laboratorio adversarial fue integrado posteriormente en `main`; no utilizar avisos antiguos «no fusionado» como verdad actual. `docs/release/status.json` sigue indicando NO producción.

---

> **ACTUALIZACIÓN 2026-11-15 — LEE ESTO ANTES DEL TEXTO**
> Base medida: `main@dd18f2a` + AD-01 `c57251c` · 196 tests Python OK (8 skips) · SDK 6/1 · 84 rutas `/v1` · esquema 8 · demo sintética, `production_enabled=false` · 2 PASS / 40 PARTIAL · sin PR ni revisión independiente.
> **Vigente aquí:** El índice de documentos y la lectura de evidencia (hecho, proveedor, hipótesis, NO VERIFICADO) siguen válidos.
> **Corregido/obsoleto:** «Las tareas están NOT_STARTED» es incorrecto: hay 80 tareas PASS y 214 PARTIAL. Añadido el programa AD y este estado vigente.
> Mapa de ramas, contradicciones y pendientes: [ESTADO-VIGENTE.md](ESTADO-VIGENTE.md)

---

> **ACTUALIZACIÓN 2026-11-14 — ESTADO VIGENTE**
> PR #10 y #11 integraron las ramas en `main`. El repositorio dispone de demo sintética funcional, **no productiva**; las referencias a código solo proyectado o ramas no fusionadas son históricas. CI de Python 3.11/3.12, SDK, scanner Docker y navegador reejecutada en el head de implementación: SUCCESS; esto no valida seguridad independiente ni clientes reales. Fuente de verdad: `docs/release/status.json` (2 fases PASS, 40 PARTIAL), `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md` y `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`. Contrastar toda instrucción con `main` antes de actuar. **Se conserva íntegramente el documento original debajo.**

---

# Documentación técnica · Agntia Ciberseguridad

Edición inicial: 2026-11-10. Objetivo: construir middleware defensivo para el equipo de seguridad de AgntiaPro, con alto uso de OSS y presupuestos técnicos acotados. Todo lo que todavía es diseño se identifica como tal.

| Documento | Contenido |
|---|---|
| [01 · Visión y requisitos](01-vision-y-requisitos.md) | Petición del propietario traducida a capacidades y límites |
| [02 · Arquitectura y confianza](02-arquitectura-y-confianza.md) | Entidades, workers, datos, credenciales y enforcement |
| [03 · Seguridad agéntica](03-seguridad-agentica-y-conceptos-propios.md) | Amenazas y seis propuestas de ingeniería propias a validar |
| [04 · Herramientas OSS](04-herramientas-oss-y-adaptadores.md) |31 repos, selección inicial, licencias y adaptadores |
| [05 · Cumplimiento europeo](05-cumplimiento-europeo.md) | RGPD, AI Act, CRA y evaluación de aplicabilidad |
| [06 · Planes y servicios](06-planes-presupuesto-y-servicios.md) | Lite30€, L70€, XL300€, supuestos, reservas y términos |
| [07 · Papers y noticias](research/07-papers-y-noticias.md) | Investigación selectiva2024–2026, límites y decisiones |
| [08 · Compañías](research/08-companias-y-capacidades.md) | Referencias representativas y qué se puede adaptar |
| [09 · Contrato con /agente](09-contrato-con-agente.md) | API/capacidades, SDK, eventos y herramientas propuestas |
| [10 · Roadmap y aceptación](10-roadmap-operaciones-y-aceptacion.md) | Fases C0–C9, pruebas críticas y operación |
| [11 · Reportes y casos](11-reportes-y-casos-de-uso.md) | Ejecutivo/técnico/legal y recorridos hipotéticos |
| [12 · Estado y handoff](12-estado-inicial-y-handoff.md) | Qué se hizo, qué no y continuidad |
| [ADR0001](adr/0001-fundacion-documental.md) | Alcance inicial y decisiones de arquitectura |

Artefactos: [fuentes](research/sources.json), [metadatos de repos](research/repositories.json), [refs de investigación](research/source-refs.json), [planes](../config/plans.json) y [validación](research/validation.json).

## Lectura de la evidencia

- Fuente consultada: existe página/abstract/metadato que respalda el hecho acotado.
- Afirmación del proveedor: lo que declara en su material, sin prueba independiente nuestra.
- Hipótesis de diseño: decisión propuesta que necesita implementación/medición.
- NO VERIFICADO: instalación, benchmark, eficacia, factura final o interpretación que no se ha comprobado.

Fecha de guía no equivale a versión de ley consolidada. Un score de scanner no equivale a auditoría completa. Un repos con SPDX conocido no acredita licencia de modelos/feeds ni derecho de reventa del servicio. La primera implementación mantendrá estas distinciones en APIs/reportes, no solo en documentación.


## Campaña ejecutable de siete días

Leer [campaña y siete jornadas](campaigns/2026-11-10-seven-days/README.md):42 fases,294 microtareas,84 escenarios, dependencias, calidad de referencia, gates, contratos, evidencias y continuidad30/60/90. Las tareas están NOT_STARTED; validar el plan no ejecuta ninguna prueba de seguridad.
