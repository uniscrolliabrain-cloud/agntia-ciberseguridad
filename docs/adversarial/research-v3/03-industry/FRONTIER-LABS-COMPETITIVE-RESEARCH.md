# Laboratorios y empresas líderes — análisis comparativo
## Criterios
Separar **publicación reproducible** (papers, repos, benchmarks) de **afirmación comercial** (marketing, rankings sin condiciones públicas). No inferir secretos industriales.

| Referencia | Fortaleza pública | Qué estudiar | Riesgo de imitación superficial |
|---|---|---|---|
| DARPA AIxCC / Team Atlanta | CRS competitivo y repo Atlantis | integración discovery/patch/oracles | copiar infra de competición como SaaS |
| XBOW | pentesting autónomo como producto | verificación de hallazgos, scoping, triage, workflow | atribuir arquitectura interna no publicada |
| Theori | investigación ofensiva y AIxCC | investigación profunda, expertos, metodología | equiparar talento humano a LLM |
| Trail of Bits | investigación y herramientas de análisis | revisiones de código, supply chain, fuzzing | depender de scanners como único método |
| Google Project Zero / Big Sleep | investigación de vulnerabilidades | selección de hipótesis, análisis de código, confirmación | confundir anuncios con replicabilidad |
| Microsoft AI Red Team | PyRIT, framework abierto | targets, evaluadores, ataques multi-turn | IA red team no es seguridad universal |
| NVIDIA | garak | probes, detectors, cobertura y calibración | confundir probes con explotación confirmada |
| Google OSS-Fuzz | fuzzing continuo | CI, corpus, dedupe, retest | coste e infraestructura masiva |
| UC Berkeley | CyberGym / E2E | benchmarks, oráculos, baselines | overfit a dataset conocido |
| OWASP | ZAP y estándares | workflows reproducibles, guías | herramientas no sustituyen criterio humano |

## Tres modelos operativos a comparar
**Modelo A — investigación profunda episódica:** equipo humano experto, pocos objetivos de alto valor, máxima calidad de hipótesis y revisión. Ventaja: creatividad y contexto; límite: escala.
**Modelo B — pipeline automatizado de gran volumen:** fuzzers/scanners, triage, reproducibilidad, CI. Ventaja: cobertura y repetición; límite: lógica empresarial y amenazas emergentes.
**Modelo C — sistema híbrido autónomo:** investigadores LLM proponen, herramientas especializadas ejecutan, oráculos verifican, humanos deciden acciones de riesgo. **Hipótesis de Agntia**: combinar A+B+C con aislamiento y evaluación. No hay evidencia de que esta combinación supere comercialmente a los líderes hasta medirla.

## Diferenciación pretendida
No 'hacker ilimitado'. Sí: **investigación continua basada en cambios, reproducibilidad, independencia de proveedor, data twin, control de autorización, recuperación y evidencia auditada**. Diferenciar entre pruebas de código, staging y producción, con resultados etiquetados.
## Due diligence pendiente
Recoger whitepapers de XBOW, Theori, Trail of Bits, Project Zero, casos públicos y divulgaciones; verificar fechas, benchmarks, falsos positivos, scope y participación humana. Las empresas no publican todos sus detalles; marcar UNKNOWN sin rellenar con conjeturas.
