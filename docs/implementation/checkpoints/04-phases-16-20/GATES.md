# Gates y aceptación

D3P4–D4P2 se mantienen PARTIAL. Las pruebas demuestran mecanismos concretos; no acreditan servicio equivalente a una plataforma líder ni cumplimiento universal.

- D3P4: cifrado auténtico, integridad, scope, corrupción, claves antiguas y retención probados. Falta checkpoint externo firmado independiente, restore completo de volumen/DB y automatización segura de reconciliación de purga interrumpida.
- D3P5: contexto desconocido no recibe score inventado; excepciones caducan; agentes no aprueban; decisiones tienen hash/fuente. Feeds externos no implementados: KEV/EPSS/CVSS unknown. Se requiere revisión de la política por otra persona.
- D3P6: informe trazable con estado/cobertura; se amplía la vertical Docker sintética con evidencia, una excepción revisada y un scan benigno. No hay aprobación humana real de negocio ni PDF ni interfaz completa.
- D4P1: CI instala el SDK real, verifica propagación y captura OTLP; valida Collector real y recepción. No se despliega ni se evalúa backend productivo. Muestreo explícito ALWAYS_ON solo para piloto, cola finita; pérdidas observables.
- D4P2: series acotadas y métricas autenticadas; configuración real validada con promtool. La alerta de5%5min es hipótesis de piloto, no SLO aceptado. No hay presupuesto de error contractual, burn-rate multiventana ni medición distribuida.

G1/G2/G3 no se declaran cerrados: revisión externa y garantías operativas siguen pendientes. ReleaseGates no cambia su valor por defecto. No se ejecutan herramientas sobre activos de clientes.
