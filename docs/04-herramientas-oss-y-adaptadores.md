# 04 · Catálogo OSS y estrategia de integración

Se consultaron metadatos GitHub de31 repos el2026-11-10. [repositories.json](research/repositories.json) conserva canonical URL, licencia SPDX informada, rama y última actividad. [source-refs.json](research/source-refs.json) registra ocho heads observados. Ninguno se ha instalado, ejecutado o auditado en profundidad; metadata no demuestra ausencia de malware ni autorización comercial de todos sus componentes.

## Selección y alcance propuesto

| Repositorio | Función | Entrada/salida prevista | Decisión inicial y límites |
|---|---|---|---|
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Secretos | Snapshot Git → findings redactados | MVP; no validar credenciales llamando al proveedor |
| [OSV-Scanner](https://github.com/google/osv-scanner) | Dependencias | Lockfiles/SBOM → vulnerabilidades | MVP; confirmar alcance/fecha de DB |
| [Semgrep](https://github.com/semgrep/semgrep) | SAST | Código no ejecutado → JSON/SARIF | MVP CE con reglas propias/revisadas; motor LGPL-2.1, reglas/Pro tienen términos distintos |
| [Trivy](https://github.com/aquasecurity/trivy) | Imágenes/IaC/SCA | Artefacto → findings/SBOM | Elegir perfiles para no duplicar todo OSV/Grype |
| [Syft](https://github.com/anchore/syft) | SBOM | Imagen/directorio → CycloneDX/SPDX | Complemento si el caso exige su cobertura |
| [Grype](https://github.com/anchore/grype) | Vulnerabilidades | SBOM/imagen → findings | Alternativa/comparación a Trivy, no doble coste permanente |
| [Checkov](https://github.com/bridgecrewio/checkov) | Configuración IaC | Terraform/K8s/etc. → controles | Opcional por lenguaje; sin aplicar cambios |
| [ZAP](https://github.com/zaproxy/zaproxy) | Web/API | Staging autorizado → alertas | Pasivo primero; active scan es otro perfil aprobado |
| [Nuclei](https://github.com/projectdiscovery/nuclei) | Comprobaciones por plantilla | Activos autorizados → findings | Diferido: templates fijadas, revisión de efectos y límites; no templates arbitrarias del LLM |
| [Prowler](https://github.com/prowler-cloud/prowler) | Postura cloud | Cuenta scoped → controles | Concesiones read-only específicas; APIs también pueden costar |
| [Wazuh](https://github.com/wazuh/wazuh) | Host/FIM/eventos | Agentes/telemetría → alertas | Evaluación L/XL o infraestructura del cliente; SPDX NOASSERTION, revisar licencias por componente |
| [OpenSearch](https://github.com/opensearch-project/OpenSearch) | Búsqueda/eventos | Eventos → consultas | Diferido por RAM/disco/operación; no obligatorio Lite |
| [Falco](https://github.com/falcosecurity/falco) | Detección runtime | Kernel/syscalls → eventos | Linux con permisos y soporte adecuados; no worker genérico |
| [Tetragon](https://github.com/cilium/tetragon) | Observabilidad/enforcement eBPF | Runtime → eventos/políticas | Solo despliegues compatibles y revisión de privilegios |
| [CrowdSec](https://github.com/crowdsecurity/crowdsec) | Señales y bloqueos | Logs → decisiones | Motor MIT; feeds/licencias y bouncers separados; bloqueos en modo propuesta inicialmente |
| [Coraza](https://github.com/corazawaf/coraza) | WAF autoalojado | Tráfico autorizado → eventos | Requiere integración proxy y tuning; no sustituye mitigación DDoS de red |
| [OWASP CRS](https://github.com/coreruleset/coreruleset) | Reglas WAF | Request → detección | Versionar y medir falsos positivos |
| [OPA](https://github.com/open-policy-agent/opa) | Policy engine | Atributos autenticados → decisión | Candidato preferente a probar; enforcement externo al LLM |
| [Cedar](https://github.com/cedar-policy/cedar) | Autorización | Principal/acción/recurso → decisión | Alternativa a OPA; elegir, no duplicar motores sin necesidad |
| [OpenFGA](https://github.com/openfga/openfga) | Autorización relacional | Relaciones → scope | Reutilizar gateway madre si ya resuelve esto |
| [Presidio](https://github.com/data-privacy-stack/presidio) | Asistencia PII | Extracto → entidades/redacción | Repositorio trasladado; metadatos MIT. No anonimización garantizada |
| [garak](https://github.com/NVIDIA/garak) | Evaluación LLM | Modelo propio/lab → resultados | Probes seleccionados, coste acotado y casos benignos/adversariales sintéticos |
| [PyRIT](https://github.com/microsoft/PyRIT) | Evaluaciones IA | Fixtures → resultados | Laboratorio, sin campañas contra terceros |
| [promptfoo](https://github.com/promptfoo/promptfoo) | Evaluación/regresión | Casos/config → métricas | Verificar qué capacidades son OSS vs servicio comercial |
| [NeMo Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) | Rails programables | Mensajes/tools → señales/controles | No frontera única; modelos, telemetría y licencias aparte |
| [AgentDojo](https://github.com/ethz-spylab/agentdojo) | Benchmark | Tareas sintéticas → utilidad/seguridad | Evaluación, no un firewall de producción |
| [CaMeL](https://github.com/google-research/camel-prompt-injection) | Investigación data/control flows | Laboratorio → observaciones | Inspiración/experimento, no instalar como escudo universal |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | Transporte/contratos | Sesiones y tools | No concede seguridad por usar MCP; audiencia, scope y red se implementan |
| [OpenSSF Scorecard](https://github.com/ossf/scorecard) | Señales supply chain | Repo → prácticas | Score no prueba que el código sea seguro |
| [Dependency-Track](https://github.com/DependencyTrack/dependency-track) | Gestión SBOM | CycloneDX → inventario/riesgo | Opcional según volumen; no necesario para primer piloto |
| [DefectDojo](https://github.com/DefectDojo/django-DefectDojo) | Gestión findings | Scans → casos/deduplicación | Candidato integración futura; no duplicar un ticketing ya existente |

## Integración mínima recomendada

Primer pipeline: snapshot local autorizado → Gitleaks + OSV + Semgrep CE/reglas revisadas → normalización → evidencia redactada → finding/reporte → propuesta de PR. Añadir Trivy cuando haya imágenes o IaC. Empezar con cuatro adaptadores bien probados en vez de instalar31 herramientas en un único contenedor privilegiado.

Un adaptador declara versión, digest, licencia, perfiles, schema de entrada, permisos de red, timeout, RAM/CPU, códigos de salida y parser. Los códigos de salida de vulnerabilidad y de error no son iguales. Guardar stdout/stderr limitado y redactado; proteger el original con política. No descartar fallos de parser como «sin vulnerabilidades».

Las herramientas con base de vulnerabilidades necesitan caché/actualización y fallback declarado. Datos obsoletos provocan estado partial/stale; un corte de red no debe hacer aparecer una auditoría limpia. Evitar descargar reglas remotas variables en cada scan. El build de la herramienta y el snapshot de reglas deben quedar fijados por separado.

## Licencias y prestación comercial

La mayoría de metadatos informan Apache-2.0/MIT; Semgrep informa LGPL-2.1 y Wazuh NOASSERTION. Verificar LICENSE, avisos, dependencias, reglas/modelos/feeds e integración como servicio/MSSP antes de distribuir o revender. No llamar a todos «gratis sin condiciones». Hay licencias específicas de cloud, bases y conectores que no se deducen del SPDX de la raíz.

Presidio aparece trasladado a data-privacy-stack/presidio y NeMo a NVIDIA-NeMo/Guardrails; se resolvieron esas redirecciones en vez de registrar la respuesta301 como repo auditado. El software local, una suscripción SaaS gratuita y un servicio con derecho de reventa son tres cuestiones distintas.

No subir código, binarios, logs o URLs privadas a reputación pública por defecto. VirusTotal public API se excluye de la base comercial: sus términos publicados prohíben ese uso. Un proveedor de pago solo se añade tras aprobar coste, DPA, residencia, retención y derecho de integración.
