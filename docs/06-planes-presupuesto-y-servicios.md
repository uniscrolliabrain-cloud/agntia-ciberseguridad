# 06 · Planes Lite/L/XL y servicios comerciales

Los30/70/300€ son techos solicitados por el propietario. Esta edición los interpreta como coste técnico mensual de un tenant/workspace piloto, no precio de venta ni presupuesto para clientes/volumen ilimitados. Confirmar esta unidad antes de una oferta. El coste de alojar el software del cliente, trabajo humano, puesta en marcha y asesoramiento jurídico se declaran aparte; no esconderlos dentro de una promesa de seguridad completa.

## Modelo de gasto propuesto

| Partida en EUR/mes | Lite | L | XL |
|---|---:|---:|---:|
| Cómputo de seguridad | 10 | 20 | 70 |
| Almacenamiento/backups | 2 | 3 | 12 |
| APIs IA | 5 | 7 | 45 |
| Servicios de pago opcionales | 0 | 30 | 100 |
| Reserva impuestos/FX/variaciones | 13 | 10 | 73 |
| **Máximo asignado** | **30** | **70** | **300** |

Estos importes son **asignaciones de diseño, no cotizaciones de VPS o garantías de capacidad**. El [JSON](../config/plans.json) lo declara y limita un piloto por número de activos/frecuencia. El consumo de varios tenants no se obtiene multiplicando descuentos supuestos ni reutilizando una licencia individual si el contrato MSSP no lo permite.

Lite: análisis por snapshot/cambio bajo cuota, sin SIEM pesado obligatorio, reportes y evaluación agéntica pequeña; reutilizar infraestructura/CI autorizada cuando exista, midiendo su coste. L: más frecuencia/activos y un servicio comercial opcional dentro de30€. XL: mayor capacidad, retención y evaluación, conectores seleccionados; tampoco un SOC humano24/7 o SIEM ilimitado.

El suelo de seguridad es idéntico: aislamiento, scope, protección de secretos, política determinista, evidencia y aprobaciones. No dar a Lite una versión insegura para abaratar. Cambian volumen, frecuencia y herramientas, no derechos básicos de protección de datos.

## Precios y términos consultados

| Servicio | Hecho observado2026-11-10 | Uso propuesto |
|---|---|---|
| [Cloudflare](https://www.cloudflare.com/en-gb/plans/) | Publicita Pro20USD/mes con facturación anual o25USD mensual; por dominio/servicio y add-ons aparte | Free como opción; Pro L/XL solo si factura final convertida/impuestos cabe. No incluye por ello todo AI Security empresarial |
| [Snyk](https://snyk.io/plans/) | Página actual presenta Team desde25USD/mes para equipos pequeños, límites por producto; Evo requiere Enterprise | Candidato opcional, no suponer antiguo mínimo5 ni comprar sin comprobar checkout/servicio para terceros |
| [Semgrep](https://semgrep.dev/pricing/) | Free con límites publicados y Teams desde30USD/contribuidor/mes en la página consultada | Base local CE/reglas revisadas; SaaS Free solo si uso comercial/multicliente y datos son admisibles |
| [VirusTotal public API](https://docs.virustotal.com/reference/getting-started) | Términos publicados prohíben uso en productos/servicios comerciales | Excluido de los tres planes salvo contrato comercial verificado; nunca subir muestras privadas automáticamente |
| Wiz/CrowdStrike/PaloAlto/Microsoft suites | Productos empresariales con contratos, consumo o licencias existentes | Referencias de diseño y conectores BYOL; no incluidos por defecto en30/70/300€ |

Importante: no se compró ningún servicio, no se comprobó un checkout con IVA y no hay tipo de cambio contractual fijado. Las tarifas publicadas no son precios EUR finales. Una anualidad pagada por adelantado no cumple un límite mensual de caja solo porque el proveedor muestre un equivalente mensual. Suscripciones y trials con auto-upgrade permanecen apagados.

## Control económico que habrá que implementar

Libro por tenant con compromiso fijo, consumo acumulado, reservas en vuelo, coste de cancelación, impuestos/FX y saldo. Reservar el peor caso acotado antes de encolar o llamar API. Concurrencia exige transacción/constraint, no sumar después. Reconciliar consumo reportado, discrepancias y facturas. Registrar política y versión de tarifa; no confiar solo en token count del LLM.

A80% avisar y diferir tareas opcionales; a95% solo trabajo previamente reservado/prioritario; al límite no admitir gasto nuevo. Son umbrales propuestos, no enforcement existente. Si el proveedor carece de hard limit o tiene cargos tardíos, reservar margen o excluirlo. Un tope de presupuesto del dashboard no es por sí solo un tope de factura.

La degradación mantiene las reglas de autorización y rutas críticas locales. Se reducen resúmenes LLM, frecuencia de scans secundarios y retención no obligatoria antes de quitar controles esenciales. Las tareas diferidas aparecen en reportes; no convertirlas en clean ni esconder huecos de cobertura.

Medir CPU/RAM/disco por scanner, tiempo, llamadas API, bases descargadas, tamaño de SBOM y eventos. No desplegar Wazuh/OpenSearch/Falco/31 herramientas juntas para Lite. Puede ser mejor integrar telemetría ya mantenida por el cliente. El precio de licencia cero no elimina actualizaciones, backups, operación o RAM.

## Gate de contratación

Para activar un pago: verificar precio/facturación/moneda, impuestos y conversión, límites y penalizaciones, uso comercial y MSSP, datos/región/retención, DPA/subencargados, presupuesto y autorización del propietario. Si no cabe, elegir OSS o reducir alcance; no superar el cap ni inventar que incluye la oferta empresarial más avanzada.
