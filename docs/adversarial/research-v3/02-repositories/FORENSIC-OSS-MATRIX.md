# Matriz forense de repositorios externos — inventario verificable
**Método:** GitHub API: metadatos del repositorio, default branch, licencia declarada y tree recursivo; lectura de README o arquitectura seleccionados. Fecha 2026-11-15. **No clone, instalación, SCA ni tests**. SHA es commit de tree, no necesariamente HEAD commit; no confundir.

| Proyecto | Tree SHA observado | Blobs | Licencia declarada | Riesgo / estado |
|---|---|---:|---|---|
| Team-Atlanta/aixcc-afc-atlantis | 8a2b41329515dcdbd201a106cd4f25a7569c1969 | >=34225 | GitHub NOASSERTION; README MIT | tree truncado; terceros incluidos |
| aliasrobotics/CAI | 6dc79257777f5f1c9500b4d2319935d34a47412e | 1537 | GitHub NOASSERTION | archivado; LICENSE y LICENSE-MIT |
| microsoft/PyRIT | c91ba04c127d56229f3559c8a6146506844bc45c | 4129 | MIT | terceros en LICENSES |
| NVIDIA/garak | 892779207cbc38f65a738ef9cbdfbc1e83aa0b55 | 888 | Apache-2.0 | probes/datasets con licencias específicas |
| google/oss-fuzz | d204ac8a3f7589ad2b7b11d90b886f772aadc484 | 7205 | Apache-2.0 | multitud de proyectos, imágenes y terceros |
| zaproxy/zaproxy | 17c25b45ad0f79631ae8d611a6fa647275aa131b | 2268 | Apache-2.0 | addons/versiones aparte |
| schemathesis/schemathesis | c0ab1b669d522aec41b6ed07dba8f78c8c745f42 | 2536 | MIT | motor con fuzzing/stateful |
| googleprojectzero/fuzzilli | a291c162e1636025787eab33ec3bde75914815d5 | 359 | Apache-2.0 | herramienta específica de JS engines |

## Análisis de arquitectura basado en documentos reales
**Atlantis:** README separa `example-crs-webservice` implementación, `example-crs-architecture` despliegue, `example-crs-appendix` herramientas. Árbol truncado impide auditoría exhaustiva; siguiente investigación debe obtener subtree por directorio, y rastrear licencias transitivas.
**CAI:** `docs/cai/architecture/overview.md` documenta 7 pilares, incluyendo tracing y human-in-the-loop. Ejemplos de patrones deterministas, paralelización y guardrails. Su licencia no debe simplificarse a MIT porque tiene archivos de licencia distintos y README con restricciones.
**PyRIT:** README confirma CLI scanner, GUI y framework; targets HTTP, WebSocket, Playwright y APIs de modelos; adaptador LiteLLM opcional. Reutilizar como herramienta **separada**, no como control plane. Revisar `pyrit/orchestrator`, `pyrit/score`, `pyrit/memory` y docker al fijar versión.
**garak:** README describe probes estáticos, dinámicos y adaptativos; `garak/probes`, `garak/detectors`, `garak/resources/red_team/evaluation.py`. Requiere configurar generadores, detectores y calibración; no equivale a evaluación de autorización empresarial.
**OSS-Fuzz:** `docs/oss-fuzz/architecture.md` confirma builder, fuzz targets, ClusterFuzz, reportes y verificación de fixes. Reusar patrón, no instalar infraestructura Google completa.
**ZAP:** árbol incluye `docker/integration_tests/configs/plans/` con planes de autenticación y automation; evidencia de configuración reproducible de DAST. Escanear solo lab o scope autorizado.
**Schemathesis:** `ARCHITECTURE.md` define fases probing, schema_analysis, auth_bootstrap, examples, coverage, fuzzing y stateful; separa transport, engine events y report handlers. Excelente patrón de **engine declarativo + adapters + eventos**, con cuidado de que auth_bootstrap puede crear identidades/cambiar estado.
**Fuzzilli:** `Docs/HowFuzzilliWorks.md` describe IR, mutación, lifting y ejecución persistente. Estudiar para generación de experimentos, no dependencia universal.

## Matriz de transferencia
| Proyecto | Decisión provisional | Qué extraer | Riesgo |
|---|---|---|---|
| Atlantis | STUDY + PoC selectiva | CRS task graph, patch validation, build pipelines | complejidad, tree truncado, licencias transitivas |
| CAI | STUDY ONLY | patterns, turns, tracing, HITL | archivo, licencia mixta |
| PyRIT | WRAP isolated | AI red teaming, scoring, traces | modelos y costes, permisos |
| garak | WRAP isolated | probes/detectors | falsos positivos, datasets |
| OSS-Fuzz | STUDY/WRAP | fuzz pipeline y corpus | infraestructura masiva |
| ZAP | WRAP lab | DAST automation plans | efectos en servicio y credenciales |
| Schemathesis | WRAP lab | API fuzz/stateful testing | creación de estado, auth |
| Fuzzilli | STUDY | IR y mutación | foco JS engines |

## Próxima auditoría de código externa antes de integración
Para cada repo seleccionado: commit SHA (no solo tree), release/tag, SPDX por archivo, SBOM, dependencia/transitivas, CVEs, secretos, test suite, uso de red, permisos de Docker, recursos, soporte comercial, pinning y mantenimiento. Ejecutar PoC en sandbox aislado, registrar logs y exit codes. No declarar 'aprobado para producción' por la licencia del README.
