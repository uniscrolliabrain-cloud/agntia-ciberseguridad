# 07 — Plan de ejecución de la puesta en marcha
**Este plan es operacional y de onboarding, no una campaña de implementación del Adversarial Lab.** El agente que desarrolla Adversarial Lab continúa en su propia rama.

## Semana 1: preparar lo existente
| Orden | Tarea | Founder | Agente | Entregable/gate |
|---|---|---|---|---|
| 01 | Baseline y estado real | confirmar objetivo | comparar main, docs y código, reejecutar tests | matriz y logs |
| 02 | GitHub y permisos | revisar 2FA, Freebuff/Codex y main protection | auditar CI, tokens referenciados | roles verificados |
| 03 | Dependencias/OSS | aceptar licencias y presupuesto | instalar scanners en entorno sintético y probar | fixtures y outputs |
| 04 | Secret manager | decidir reutilizar Doppler | mapa de referencias y template | secretos fuera del repo |
| 05 | Host de laboratorio | elegir VM/servicio y región | requisitos, hardening y coste | ficha de infraestructura |
| 06 | Bundle y Compose | autorizar entorno propio | verify bundle, imagen y config privada | smoke sin clientes |
| 07 | Evidencias/backup | elegir almacenamiento | backup/restore sintético | restore report |

## Semana 2: operación y conexiones
| Orden | Tarea | Founder | Agente | Entregable/gate |
|---|---|---|---|---|
| 08 | Alertas | elegir receptor | OTel/alerta y simulacro | acuse de alerta |
| 09 | IAM y tenancy | aprobar roles | dos tenants sintéticos, revocación | pruebas negativas |
| 10 | SDK /agente | aprobar lectura y luego escritura por separado | contrato y patchset sin aplicar al padre | revisión de interfaces |
| 11 | Costes y límites | fijar tope mensual | estimar y medir coste por run | presupuesto/alerta |
| 12 | Seguridad y review | aceptar revisión externa | preparar threat model, SBOM, resultados | dictamen independiente |
| 13 | Legal y servicio | aprobar oferta, ROE, DPA y licencia | preparar plantillas | paquete comercial |
| 14 | Piloto interno | autorizar activos propios | ejecutar bajo supervisión y retest | informe/GO-NO-GO |

**Las semanas son bloques de trabajo, no plazos garantizados.** El primer cliente se habilita solo después de gates y revisión independiente.

## Checklist founder (copiar y marcar)
- [ ] F01 Permisos GitHub y MFA revisados
- [ ] F02 Secret manager elegido
- [ ] F03 Host/región/presupuesto aprobados
- [ ] F04 Almacenamiento y backup elegidos
- [ ] F05 Alertas y responsable designados
- [ ] F06 IdP/roles aprobados
- [ ] F07 Licencia y uso de OSS revisados
- [ ] F08 Oferta y límites comerciales definidos
- [ ] F09 ROE y autorización de activos preparada
- [ ] F10 DPA/privacidad/retención revisados
- [ ] F11 Revisión de seguridad independiente encargada
- [ ] F12 Autorización específica de /agente decidida
- [ ] F13 Piloto interno autorizado
- [ ] F14 Primer cliente: GO firmado, no automático

## Checklist agente
- [ ] A01 Inventario verificable con SHA
- [ ] A02 Tests reejecutados y gaps
- [ ] A03 Escáneres y feeds probados
- [ ] A04 Config template sin secretos
- [ ] A05 Bundle/release verificado
- [ ] A06 Lab privado y smoke
- [ ] A07 Restore completo probado
- [ ] A08 Alertas/kill switch probado
- [ ] A09 Cross-tenant y revocación
- [ ] A10 Integración propuesta y revisada
- [ ] A11 Presupuesto y costes medidos
- [ ] A12 Evidencias para auditor independiente
- [ ] A13 Informe de piloto interno

## Reglas de avance
Un `PASS` requiere SHA, comando, exit, log y actor; `BLOCKED` incluye dependencia exacta; `NOT_VERIFIED` no se presenta como éxito. No abrir cuentas ni generar keys antes de necesitarlas. No desplegar ni tocar main sin autorización.
