# 11 · Continuidad30/60/90 y ámbitos adicionales

La ambición de plataforma se conserva sin fingir que una semana sustituye un programa de seguridad mantenido. Este backlog identifica capacidades y gates posteriores; no es un compromiso de horas, adquisición de servicios o producción automática en esas fechas.

## Próximos30días · Validar y estabilizar el piloto

Cerrar fallos del día7, contratos reales de herramientas, revocación y recovery. Medir uso de dos tenants sintéticos y después clientes piloto solo bajo acuerdo. Verificar límite económico, ruido, tiempo de triage, disponibilidad del operador y calidad de reportes. Acordar licencia propia y canal privado de seguridad, DPA/retención/transferencias, responsables y soporte.

Ampliar lenguajes de SAST y fixtures, comparar parsers/releases, verificar DBfreshness, mejorar retest y excepciones. Completar UI/SDK sin escribir en `/agente` hasta tener aprobación del patchset. Publicar cambios pequeños y mantenibles, nunca un estado ficticio «todo seguro».

## Próximos60días · Cobertura contextual

| Dominio | Capacidad propuesta | Gate adicional |
|---|---|---|
| Web/API | ZAPpasivo y active_lab autorizado; auth/BOLA/JWT/GraphQL según fixture | Scope, no efectos destructivos, cuentas de test y rate/coste probados |
| Nuclei | Plantillas revisadas por efecto y origen | Template pin, safe profile, ninguna plantilla libre del modelo |
| Cloud | Inventario/IAM/config mediante cuenta scoped | Permisos mínimos, paginación, readcost, ausencia de datos cross-account |
| Kubernetes | Configuración, admisión y runtime opcional | Clúster de laboratorio, privilegios evaluados, no aplicar cambios sin aprobación |
| Runtime | Conectores Wazuh/Falco/Tetragon según SO | Recursos/sensores realmente disponibles y procedimiento de retirada |
| SIEM | Ingestión de fuentes seleccionadas y reglas | Backpressure, orden/replay, cobertura y privacidad |
| Threat intelligence | KEV/advisories y feeds con licencia | Fuente/fecha, integridad, revisión y distinción de explotación real |
| Rules | Sigma/YARA/CRS según caso | Licencia, ejemplos benignos, falsos positivos y update/reversión |
| Supply chain IA | Inventario de modelos/pesos/tokenizers/adapters | No cargar serialización insegura para analizarla; hashes/procedencia/licencias |
| Correo/antifraude | Señales autorizadas y cambio de canal verificado | Accesos mínimos y ninguna acción financiera automática |
| Identidad | SSO/OIDC, delegación y offboarding | Audiencia, revocación, sesión cruzada y emergencia probadas |
| Datos | Descubrimiento/redacción con revisión | Muestreo minimizado, falsos negativos y retención controlados |

Estos dominios pueden aumentar coste, RAM y responsabilidad. No introducirlos en Lite por defecto ni aprovechar una demo gratis de proveedor como financiación permanente. BYOL exige derechos y scopes del cliente.

## Próximos90días · Madurez operativa

Medir disponibilidad/carga real, recuperación periódica, incidentes simulados y operación con cambios de modelo/proveedor. Revisar independencia de la política respecto del LLM y del almacenamiento compartido. Evaluar tests de penetración externos con alcance autorizado, auditoría de arquitectura y revisión jurídica competente.

Ampliar continuidad, alertas/escalado y soporte al horario realmente contratado. Solo entonces proponer SLO/SLA comerciales ajustados a hardware/plantilla. Explorar integración con fuentes empresariales ya contratadas por clientes sin insinuar que su licencia está incluida en nuestros planes.

## Límites estructurales que no desaparecen por un roadmap

Un middleware no observa hosts sin sensores, paquetes TLS sin integración ni agentes que salten el gateway. No evita DDoS volumétrico desde un VPS pequeño, no atribuye campañas globales con la misma visibilidad de Mandiant, ni certifica leyes o detecta todo deepfake. La plataforma debe exponer esos huecos como parte del producto.

## Actualización de investigación

Revisar papers/versiones y fuentes oficiales con fecha, no incorporar repos automáticamente. Si cambia un esquema/protocolo/ley/tarifa, abrir propuesta con efecto sobre compatibilidad y clientes. Mantener resultados reproducibles por configuración. Un benchmark mejor en un paper no justifica cambiar un control en producción sin medir seguridad, utilidad y costes propios.
