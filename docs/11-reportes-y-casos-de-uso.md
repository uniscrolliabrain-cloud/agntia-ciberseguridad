# 11 · Reportes y casos de uso del cliente

Todos los ejemplos de este documento son hipotéticos y sintéticos. No describen un incidente ni una auditoría ya ejecutados.

## Informe ejecutivo

Cliente/tenant, activos y entornos, periodo y snapshot, autorización, resumen de riesgos confirmados/sospechados, cambios frente al anterior, impacto de negocio, prioridades y decisiones humanas. Mostrar cobertura y huecos destacados, no un semáforo verde universal. Cada cifra apunta a findings/evidencias y al método de cálculo; las conclusiones IA se identifican como propuesta revisada o pendiente.

Ejemplo hipotético: «Se analizaron dos lockfiles y una imagen fixture; no se revisaron móviles ni cloud IAM. Hay una dependencia afectada por un advisory y un secreto canario redactado. La exposición de runtime es desconocida. Se propone actualizar en una rama y revisar la configuración». No afirmar explotación real por una coincidencia de versión.

## Informe técnico

Herramienta, versión/digest, reglas y fecha de DB, objetivo/commit, perfil, permisos, estado de ejecución, ubicación minimizada, CVE/CWE si existe, severidad/confianza, precondiciones, evidencia/canario, propuesta de remediación, riesgo de regresión y retest requerido. Anotar exclusiones, comandos reales seguros ejecutados y fallos, sin publicar secretos ni payloads peligrosos innecesarios.

Un finding puede cambiar o aceptarse temporalmente con motivo/owner/fecha. La desaparición del resultado de un scanner distinto no demuestra arreglo; comparar cobertura, versión y el control esperado. Los informes públicos se generan desde una vista redactada y se revisan antes de compartir.

## Expediente de cumplimiento

Entidad/rol/sistema/jurisdicción, fuente normativa y fecha, requisitos aplicables, control, evidencia, ausencia de datos, decisiones, responsable y caducidad. Incluir riesgo residual y revisión competente. No «certificado RGPD» ni «AI Act100%» por completar un checklist. Los plazos administrativos los confirma el responsable humano según régimen y fecha de constancia.

## Casos objetivo

1. **PR y supply chain:** cambio autorizado → snapshot sin ejecutar dependencias → scanners → finding → revisión → propuesta de PR → retest. Sin merge automático a producción.
2. **Agente y datos:** documento sintético hostil → tool intenta destino externo → política deniega → caso/evidencia → owner ve resultado. Una tarea legítima paralela termina, para comprobar utilidad.
3. **Cambio de MCP/skill:** manifiesto cambia → admisión caduca → revisión del nuevo scope → aceptación/denegación. No ejecutar la nueva herramienta para «aprobarla» con secretos reales.
4. **Phishing/estafa:** mensaje sospechoso autorizado → extracción aislada → señales y contexto → verificación por canal registrado → propuesta. No visitar URLs arbitrarias desde la red de administración ni acusar a una persona solo por un score.
5. **Incidente cloud:** evento existente → corroboración → preservar evidencia → contención propuesta → autorización → resultado y rollback. No revocar todas las credenciales automáticamente por una alerta no confirmada.
6. **Privacidad:** nuevo proveedor IA → revisión de datos/DPA/región → recomendación de minimización → aprobación del responsable. Un «EU endpoint» no prueba que no haya transferencias/subencargados fuera de la UE.
7. **Presupuesto:** reserva alcanza umbral → tareas opcionales diferidas → reporte de cobertura reducida → enforcement esencial sigue activo. No facturar un upgrade sin autorización.

## Frecuencia y honestidad operativa

Resumen diario solo de actividad persistida; semanal de riesgos/excepciones y dependencias desactualizadas; mensual de cobertura, métricas y presupuesto. Las urgencias siguen una política de severidad y disponibilidad real del servicio. El plan Lite on-demand no debe describirse como vigilancia24/7.

Para cada entregable mantener autor humano/técnico, generación, revisión, snapshot y retención. La cadencia pertenece a `/agente`; el middleware ofrece datos/reportes y eventos. No enviar correos/Slack ni notificaciones oficiales mediante herramientas sin una instrucción y autorización específica del usuario.
