# 09 · Calidad y comparación con actores líderes

La investigación previa identifica patrones públicos de Wiz, PaloAlto, CrowdStrike, SentinelOne, Microsoft, Google/Mandiant, Cloudflare, Snyk y Semgrep. Es una referencia representativa, no ranking independiente. No se han contratado ni evaluado todas sus ofertas.

## Qué significa «a la altura» en esta campaña

Mismo rigor exigible en nuestro scope: controles fuera del modelo, mínimo privilegio, historia/evidencia, recuperación, resultados reproducibles, políticas y coste transparentes. No significa equivalencia de sensores, datos de amenazas, personal, respuesta mundial, disponibilidad o certificación. La semana entrega un piloto candidato si los gates pasan; la madurez se desarrolla con uso, revisión y operación.

| Dominio/patrón | Entrega de la semana | Evidencia esperada | Diferencia pendiente |
|---|---|---|---|
| Inventario y contexto | Assets/snapshots/relaciones | Scope e identidad probados | Descubrimiento multinube/endpoint exhaustivo |
| AppSec | Gitleaks/OSV/Semgrep; TrivyM1 | Contratos reales/fixtures/retest | Más lenguajes, alcance semántico y escala |
| Supply chain | SBOM, reglas/digests/versiones | Procedencia y stale visibles | Firma/certificación de todo proveedor |
| CNAPP/IAM | Modelo de relaciones y propuesta | No inferir cloud no observado | Conectores, permisos y pruebas por nube |
| DSPM/DLP | Etiquetas/egress del scope | Canarios y composición bloqueada | Descubrimiento de todos los datos empresariales |
| AI-SPM | Registro agentes/tools/skills | Drift/admisión/revocación | Inventario de agentes fuera del gateway |
| Runtime agente | Política y salida controladas | Modelo hostil no autoriza efectos | Defensa universal/fuera del trust model |
| MCP security | Versión/audiencia/manifests | Contratos y bypass tests | Todas las implementaciones/proveedores |
| Observabilidad | OTel + métricas/logs correlacionados | p95, cobertura, drops, redacción | Plataforma global de alto volumen |
| SRE | Health, backlog, freshness y recovery | Fallos/restore probados | SLA contractual y personal24/7 |
| SIEM | IngestiónM1 y esquema común | Fuente/scope/replay | Lago de datos/retención ilimitados |
| XDR/EDR | Integraciones futuras | Sensores declarados realmente activos | EDR propio/cobertura completa de hosts |
| SOAR | Propuestas/playbooks de laboratorioM1 | Aprobación y rollback | Respuesta autónoma irreversible |
| Antifraude | Señales/contextoM1 | Verificación fuera de banda | Detección perfecta de deepfakes/estafas |
| GRC | Aplicabilidad/evidencia revisable | Fuentes/roles/datos faltantes | Certificación legal o auditoría externa |
| DevSecOps | SDK, CI, PRpropuestaM1 | Tests/diff/commit/retest | Merge/deploy en todo cliente |
| Privacidad | Minimización/retención/scopes | Borrado/hold/export probados | Garantía jurídica automática |
| Coste | Caps/reservas y degradación | Concurrencia/factura conciliable | Servicios empresariales ilimitados por30€ |

## Lista de calidad de release

No secreto canario en salidas; no acceso cruzado; toda acción sensible comprobada por servidor; replays sin duplicados; rechazo de scope/manifest cambiado; audit conservado; fallos de herramientas visibles; reporte cita evidencia y cobertura; snapshots/versiones conocidos; backup restaurado; costo medido; consumidor de referencia funciona; matriz de plataformas verificadas; contacto/responsabilidad humana definidos para el piloto.

«Cero» se limita a los casos ejecutados: no escribir «cero vulnerabilidades» o «100%seguro» porque esas pruebas pasaron. La cobertura cuenta activos/perfiles realmente analizados y no el número de herramientas listadas. Los datos ausentes muestran unknown.

## Observabilidad ampliada sin inflar Lite

Se consultaron siete repos adicionales: OpenTelemetry CollectorContrib/Python, Prometheus, Grafana, Loki, Tempo y Vector. Sus metadatos están en [observability-upstreams.json](observability-upstreams.json). Grafana/Loki/Tempo informan AGPL-3.0 y Vector MPL-2.0; revisar obligaciones, reglas/plugins y distribución antes de adoptarlos. Metadata no es auditoría del código.

Lite puede producir OTel/Prometheus y vistas mínimas con recursos acotados; no necesita desplegar todos esos backends a la vez. L/XL o infraestructura existente del cliente amplían dashboards/retención. Meter todo en un VPS y llamarlo «líder» empeora disponibilidad y costo. La decisión se basa en medidas del día4 y7.

## Condiciones de comparación comercial

Publicar funciones propias demostradas, versiones/alcance, límites, soporte y precio técnico real. No usar logos para sugerir integración contratada ni afirmar que una suite empresarial está incluida porque ofrece una API. Conectores BYOL requieren derechos y credenciales por cliente. Datos y conocimiento propietario de fabricantes no se copian.
