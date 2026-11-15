> **ACTUALIZACIÓN 2026-11-15 — LEE ESTO ANTES DEL TEXTO**
> Base medida: `main@dd18f2a` + AD-01 `c57251c` · 196 tests Python OK (8 skips) · SDK 6/1 · 84 rutas `/v1` · esquema 8 · demo sintética, `production_enabled=false` · 2 PASS / 40 PARTIAL · sin PR ni revisión independiente.
> **Vigente aquí:** Las decisiones abiertas y la falta de integración con `/agente` siguen siendo ciertas.
> **Corregido/obsoleto:** «No hay motor AppSec/AI firewall, API runtime, scanners instalados» es falso a 2026-11-15: hay API de 84 rutas, 196 tests, cuatro adaptadores offline y SDK; nada de ello es producción.
> Mapa de ramas, contradicciones y pendientes: [ESTADO-VIGENTE.md](ESTADO-VIGENTE.md)

---

> **ACTUALIZACIÓN 2026-11-14 — LECTURA OBLIGATORIA**
> Este documento es histórico. Las ramas de implementación y recuperación ya se integraron en `main` (PR #10 y #11); las afirmaciones de ramas apiladas, código no integrado o baseline anterior deben contrastarse con HEAD. Estado: demo sintética **no producción**; reruns CI de Python/SDK, Docker scanner y navegador exitosos en el head de implementación, no equivalen a aceptación de clientes. Estado de gates en `docs/release/status.json`: 2 PASS / 40 PARTIAL. Fuente de verdad complementaria: `docs/auditoria-runtime/AUDITORIA-FUNCIONAL-2026-11-14.md` y `docs/auditoria-runtime/PROGRAMA-DIFERENCIAL-12-CAMPANAS.md`. Freebuff debe auditar el delta real y no repetir capacidades existentes. **Se preserva el contenido original completo a continuación.**

---

# 12 · Estado inicial y relevo

Fecha: 2026-11-10. Ruta local: `/workspace/agntia-ciberseguridad`. Proyecto separado de Agntia Gestoría y Agntia-video; no se han modificado esos repos ni `/agente` en esta tarea.

## Hecho en esta entrega

- Recogida técnica de requisitos del propietario y límites Lite/L/XL.
- Investigación selectiva de papers2024–2026, noticias recientes, marcos y fuentes oficiales europeas.
- Contraste de metadatos de31 repos públicos; ocho heads registrados como referencias, no versiones de instalación aprobadas.
- Identificación/resolución de redirecciones de Presidio y NeMo Guardrails; licencias desconocidas/no inequívocas señaladas.
- Arquitectura propuesta, controles agénticos propios por validar, catálogo OSS, matriz de cumplimiento, presupuestos y contratación.
- Benchmark de compañías representativas con diferencias frente a nuestro alcance y costes.
- Contrato propuesto al repo madre, roadmap incremental, casos/reportes, instrucciones para futuras IAs y validación documental.

## No hecho

No hay motor AppSec/AI firewall, API runtime, scanners instalados, integraciones con clientes o agentes, evidencia de protección activa, servicio cloud, compras ni certificación jurídica. Los programas iniciales validan documentos/configuración, no la ciberseguridad de un software. No se han replicado benchmarks ni auditado todas las dependencias estudiadas.

La siguiente IA debe verificar estado Git/SHA, leer fuentes/ADR y completar C1/C2 con fixtures locales. El gateway se prueba con acciones sintéticas y sin secretos; después se verifica cobertura y coste real antes de piloto. Conectar `/agente` requiere interfaces reales y autorización para escribir allí.

## Decisiones abiertas sin bloquear esta fundación

Unidad final de los planes (por cliente, workspace o despliegue), perfiles iniciales, legislación/sectores de clientes, contratos de herramientas, proveedor IA/región, motor de políticas, almacenamiento de producción y licencia del código propio. Los documentos adoptan hipótesis explícitas, no decisiones jurídicas definitivas. No pedir al propietario una batería de preguntas antes de tener un diseño revisable; priorizar una aclaración cuando realmente condicione una implementación.

## Pruebas y validación

Ejecutar `python scripts/validate_foundation.py` para enlaces relativos, JSON, metadatos y sumas presupuestarias. Registrar la salida en el informe de entrega. No convertir ese PASS en suite de seguridad aprobada. La futura CI documental usa Python3.12 y permisos read-only. Faltan íntegramente los tests de runtime/aislamiento/sandbox/modelo que describe el roadmap.

## Publicación

El usuario indicó que crearía el repositorio vacío en GitHub. Se prepara Git local sin credenciales ni contenido de otros proyectos. No hay autorización para comprar servicios o publicar datos de clientes. Verificar remoto y estado antes de subir; no sobreescribir trabajo que el propietario u otra IA haya añadido. La rama/commit publicado, si existe, se comunica con su resultado real.


## Resultado de publicación y validación de esta sesión

La consulta del remoto esperado `uniscrolliabrain-cloud/agntia-ciberseguridad` devolvió404 al conector. Eso no distingue repo todavía no creado, privado o no autorizado para esta conexión. Se conserva un commit Git local; no se afirma push a GitHub ni se crea el remoto en lugar del propietario.

Se ejecutó el validador documental con resultado PASS para enlaces, JSON, metadatos y presupuestos. No se ejecutó ninguna auditoría de seguridad, scanner o suite de benchmark. El estado detallado se conserva en docs/research/validation.json.


## Actualización posterior: repositorio remoto y campaña

El propietario confirmó el remoto `uniscrolliabrain-cloud/agntia-ciberseguridad` y pidió publicar toda la documentación. La nueva consulta confirmó repo vacío con permisos de escritura; se inicializó en main con commit766a08f457f0fa2a502c2a7da0f739499dc70efa. El404 anterior queda como antecedente y ya no describe la accesibilidad actual.

La entrega incorpora la campaña de siete días en docs/campaigns/2026-11-10-seven-days, con42 fases,294 tareas y84 gates planificados. El SHA final de publicación se consulta en GitHub/main, sin inventar un hash autorreferente en el documento. Solo se publica documentación/configuración/validadores, no un runtime protector.
