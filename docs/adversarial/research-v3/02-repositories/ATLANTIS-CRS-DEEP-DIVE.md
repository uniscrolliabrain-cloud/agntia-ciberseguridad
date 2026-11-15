# Atlantis CRS — descomposición de módulos y riesgos de adopción
**Fuente primaria inspeccionada:** `Team-Atlanta/aixcc-afc-atlantis`, tree raíz `8a2b41329515dcdbd201a106cd4f25a7569c1969`, `example-crs-webservice/README.md`, `example-crs-architecture/README.md`, `example-crs-webservice/build.py`. **No se ha ejecutado** el sistema ni leído el código completo de todos los módulos.

## Descomposición real según el README de implementación
| Módulo | Responsabilidad declarada | Transferencia |
|---|---|---|
| `crs_webserver` | API CRS, tareas del framework de competición | interfaz de entrada y contratos |
| `cp_manager` | construcción y gestión de contenedores de challenge projects | build farm y aislamiento |
| `crs-java` | detección Java centrada en sinkpoints con ensemble fuzzing | análisis semántico + fuzzing |
| `crs-multilang` | detección multilenguaje con LLM | planificación de hipótesis por lenguaje |
| `crs-p3` | serving HF de alto rendimiento, entrenamiento LoRA | coste/infra; NO requisito para V1 |
| `crs-patch` | generación de parches Crete con LLM tracing | propuesta + trazabilidad |
| `crs-sarif` | análisis SARIF, generación, validación y reachability | normalización y reachability |
| `crs-userspace` | CRS microservicios C/C++ con workflow Kafka | tareas distribuidas y eventos |
| `litellm` | gateway LLM OpenAI-compatible | abstracción de modelos, no autorización |

## Hallazgo arquitectónico
Atlantis no es un único 'agente hacker': separa gestión de proyectos, detectores por lenguaje, fuzzing, análisis SARIF, generación de parches, modelos y servicio. Es una evidencia concreta de por qué un simple loop de Codex con prompts no replica un CRS de competición. Para Agntia, la prioridad debe ser **motor de experimentos + oráculos + adaptadores especializados**, con coding agents intercambiables.

## Infraestructura observada
`example-crs-architecture` describe un ejemplo de AKS/Terraform/Kubernetes, con node pools, Tailscale del certamen, credenciales de framework y registry. No es despliegue multi-tenant comercial listo para usar. **No copiar** su configuración de identidad, red ni secretos a un SaaS de clientes. `build.py` invoca comandos de build con `os.system` y usa credenciales de entorno para construcción; el laboratorio propio no debe ejecutar scripts de terceros en el host ni interpolar entradas no confiables en shell.

## Qué falta inspeccionar antes de usar código
1. Inventario recursivo **por subtree** de cada módulo; el tree global se truncó.
2. Licencia de cada componente, submódulo y artefacto, dependencias transitivas, imágenes y datasets.
3. Diagramas de eventos/colas, coordinación de jobs, cancelación, errores y rollback.
4. Trazas de una tarea real: source→candidate→reproduction→patch→retest, con hashes.
5. Tests, CI, resultados reproducidos y costes.
6. Seguridad del executor, secretos, egress y aislamiento; diferencia entre sandbox de competición y servicio comercial.
7. Viabilidad de extraer patrones vs copiar servicios enteros.

## Decisión provisional
**STUDY** en profundidad, **NO WRAP** inmediato. Considerar PoC aislada de módulos específicos solo después de revisión de licencias y seguridad. Nunca integrar con `agntia_ciberseguridad/agents/**`.
