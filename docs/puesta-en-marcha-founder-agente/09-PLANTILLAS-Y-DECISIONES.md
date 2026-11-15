# 09 — Plantillas operativas y registro de decisiones
## Ficha de servicio externo
```md
Servicio:
Objetivo:
Necesidad actual (sí/no):
Cuenta existente/nueva:
URL oficial y fecha de consulta:
Región y DPA:
Plan/precio verificado:
Owner de facturación:
Roles/scopes:
Secret ref (NUNCA valor):
Integración (archivo/ruta):
Prueba de conectividad:
Límite mensual:
Fallback/rollback:
Estado: TODO / READY / BLOCKED / NOT_VERIFIED
```

## Ficha de variable
```md
Nombre literal o referencia de esquema:
Archivo que la consume:
Requerida/condicional:
Entorno: local/staging/prod
Secret manager path:
Formato/validación (sin ejemplo real):
Rotación:
Owner:
Prueba fail-closed:
```

## Ficha de entorno
```md
Host/proveedor:
Región:
SO/runtime:
SHA/imagen digest:
CPU/RAM/disco:
Red/egress:
Usuarios y MFA:
Secret refs:
Persistencia/backup:
Restore verificado:
Alertas/kill switch:
Coste mensual observado:
Aprobó:
```

## Registro de decisiones
| ID | Decisión | Estado | Owner | Evidencia |
|---|---|---|---|---|
| F01 | GitHub permisos | PENDIENTE | Founder | |
| F02 | Gestor de secretos | PENDIENTE | Founder | |
| F03 | Host Linux | PENDIENTE | Founder | |
| F04 | Evidencia/backup | PENDIENTE | Founder | |
| F05 | Alertas | PENDIENTE | Founder | |
| F06 | Roles/IdP | PENDIENTE | Founder | |
| F07 | Licencia | PENDIENTE | Founder | |
| F08 | Oferta y contratos | PENDIENTE | Founder | |
| F09 | Autorización /agente | PENDIENTE | Founder | |
| F10 | Piloto interno | PENDIENTE | Founder | |

## Registro de ejecución
| Fecha | Acción | Actor | Rama/SHA | Resultado | Evidencia | Próximo paso |
|---|---|---|---|---|---|---|
| | | | | | | |

## Criterios para detenerse
Cualquier secreto expuesto, error cross-tenant, falta de autorización de activo, scanner fuera de alcance, gasto no aprobado, pérdida de evidencia o rollback no probado: detener, documentar, notificar al founder y esperar autorización.
