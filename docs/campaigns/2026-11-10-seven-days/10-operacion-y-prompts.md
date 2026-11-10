# 10 · Operación de la campaña e instrucciones a implementadores

Este documento no despliega agentes ni da autorización para escribir en `/agente` o producción. Define un protocolo de trabajo para humanos/IAs que reciban una tarea concreta.

## Antes de cada fase

Leer README/AGENTS, campaña, dependencias y estado Git. Confirmar SHA/entorno/grant, alcance M0/M1 y presupuesto. Abrir fase en rama propia sin resetear trabajo ajeno. Revisar fuentes y versiones de herramientas aplicables. Si falta una dependencia crítica, registrar BLOCKED y continuar solo trabajo independiente.

Roles funcionales: lead integra, backend/datos implementan core, AppSec integra herramientas, SRE observa/recupera, seguridad agéntica diseña políticas, privacidad evalúa datos, QA valida, reviewer cuestiona evidencia. Son responsabilidades que pueden compartir personas; no son contrataciones ni permisos de runtime.

La paralelización es opcional y requiere coordinación de ownership: auth/storage/contracts no se editan simultáneamente sin acuerdo. Cambios al contrato generan ADR y tests de consumidor. Una IA puede proponer restricciones pero no autorizarse ampliaciones. La aprobación del usuario no se solicita para tareas reversibles ya autorizadas, sí para nuevos efectos que lo requieran después de preparar un resultado revisable.

## WIP, ramas y commits

WIP pequeño: una fase por ejecutor, integración tras gate, cambios de contrato explícitos. Rama orientativa `feat/cyber-dNPn-slug`; commits con problema/resultado, pruebas ejecutadas y limitaciones. PRs pequeñas; no mezclar cambios de otros repos o instalar servicios ajenos. El usuario pidió publicar esta documentación en main; eso no aprueba automáticamente toda futura implementación o despliegue.

## Prompt de ejecución de fase

> Trabaja únicamente en la faseID asignada de campaign.json. Lee objetivo, contrato, archivos previstos, dependencias, microtareas, pruebas y rollback. Verifica el checkout y preserva cambios ajenos. Implementa un resultado real con límites y datos sintéticos. Ejecuta los tests apropiados; si falta runtime registra BLOCKED, sin fallback inseguro. No atribuyas resultados de papers o proveedores a este código. Entrega SHA/PR, comandos, conteos, evidencia sanitizada, defectos y siguiente paso. No avances dependientes si falla una frontera crítica. No toques /agente/producción, compres o envíes datos externos sin alcance autorizado.

## Prompt de revisión

> Revisa el resultado como un tercero que desconoce la conversación. Comprueba comportamiento e invariantes, no solo nombres de archivo. Busca scope/cross-tenant, secreto, ejecución de datos no confiables, bypass de policy, replay/timeout, coste, parserfail y claims exagerados. Reproduce los gates con fixtures cuando el entorno exista. Distingue tests simulados y reales. Si algo no se probó, marca NOT_VERIFIED o BLOCKED. El revisor no rellena PASS por intención ni por un resumen del implementador.

## Prompt de cierre diario

> Resume hechos persistidos del día: fases/tasks, SHAs, pruebas/comandos/entorno, gasto y duración medidos, cobertura, errores, decisiones y bloqueos. Usa estados definidos y referencias. Explica qué puede hacer ahora un cliente de laboratorio y qué no. No narres trabajo inexistente ni escondas M1 diferidos. Actualiza el backlog y deja handoff reproducible para el siguiente ejecutor.

## Estructura de evidencia futura

`evidence/DnPn/README.md`, TESTS.md, RISKS.md y DECISIONS.md con hashes/referencias. Logs originales fuera de Git; adjuntar solo versión minimizada. Campaign.json puede enlazar artefactos de CI/commit con revisión. No contener credenciales, dumps, rutas personales o datos de clientes.

## Cambios del plan

IDs son estables. Si una tarea se divide, añadir subtareas o un ADR con trazabilidad, no renumerar el historial para fingir continuidad. Una fase puede diferirse por coste/capacidad, pero el reporte del producto conserva la capacidad como ausente. No quitar un caso de gate para obtener verde; justificar modificación con amenaza/alcance y revisión.

## Al terminar

Entregar README de arranque real, demo sintética, SDK/contratos, scripts de pruebas, matriz de plataformas, SBOM/avisos, operación/rollback/restore y founder report. Etiquetar el nivel documental/demo/piloto/producción según evidencia. El deadline orienta prioridades; no sustituye un gate. Para instrucciones concretas usar las [plantillas](templates/phase-report.md) y el [reporte final](templates/founder-report.md).
