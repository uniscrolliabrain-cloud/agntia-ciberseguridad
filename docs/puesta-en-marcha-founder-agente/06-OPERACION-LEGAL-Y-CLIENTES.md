# 06 — Operación, clientes y obligaciones
## Antes de un cliente real
1. Definir oferta Lite/L/XL en términos verificables: activos, cadencia, técnicas, tiempos de entrega, exclusiones y dependencia de proveedores. No prometer SOC 24/7 si no existe equipo 24/7.
2. Elegir licencia del código propio y revisar licencias de herramientas, reglas y feeds para uso comercial.
3. Definir contrato de servicio, autorización escrita de auditoría (Rules of Engagement), activos/hosts/IP/repos autorizados, técnicas permitidas, ventanas, carga máxima, exclusiones, contacto de emergencia y revocación.
4. Evaluar RGPD: responsable/encargado, DPA cuando proceda, subencargados, residencia, conservación, derechos, incidentes y transferencia internacional. Asesoramiento legal especializado antes de compromisos.
5. Designar operador, suplente, canal privado de incidentes y escalado. Simular corte de emergencia.
6. Definir custodio de evidencias, acceso por rol, cifrado, retention schedule, exportación y borrado controlado.
7. Asegurar continuidad: backup, restore completo, pérdida de claves, recuperación de cola/jobs, reconciliación de efectos y RTO/RPO medidos.
8. Definir facturación/coste y soporte: límites de runs, almacenamiento, tokens, falsos positivos, intervención humana, costes de reanálisis y política de sobreconsumo.

## Matriz RACI resumida
| Actividad | Founder | Agente | Auditor/operador |
|---|---|---|---|
| Contratar servicio, aceptar términos | A/R | prepara comparativa | C |
| Crear credenciales y accesos | A/R | configura referencias sin valores | C |
| Instalar y probar entorno sintético | A | R | C |
| Autorizar activos de cliente | A/R | valida alcance técnico | C |
| Ejecutar auditoría autorizada | A (política) | R (SOP) | supervisa |
| Aceptar riesgo residual/producción | A/R | informa | C |
| Gestionar incidente | A | aporta evidencias | R operativo |
A=accountable, R=responsible, C=consulted; si no hay operador, el founder asume formalmente y debe documentarlo.

## Artefactos de cliente obligatorios
Ficha de tenant y activos; autorización firmada; ROE; registro de bases jurídicas y DPA si aplica; catálogo de servicios; plan de retención; contactos; presupuesto y límites; incident response; informe de cobertura con exclusiones; aprobación de remedios y cierre.

## Gates de lanzamiento
G0 laboratorio sintético reproducible. G1 entorno privado y credenciales separadas. G2 seguridad independiente y backups/restores. G3 identidad/integración /agente. G4 legal/operadores/canales. G5 piloto interno y aceptación founder. G6 cliente real de bajo impacto. Ningún gate se cierra con documento sin prueba.
