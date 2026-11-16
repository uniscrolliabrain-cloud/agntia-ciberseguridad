# 03 — Cuentas, credenciales y decisiones del founder

**Propósito:** coordinar cuentas que el founder está abriendo sin almacenar claves en GitHub ni confundir servicios opcionales con bloqueantes. Complementa [inventario de proveedores](../puesta-en-marcha-founder-agente/02-CUENTAS-Y-SERVICIOS.md).

## Decisiones que desbloquean el primer laboratorio

| Orden | Servicio | Cuenta nueva | Founder decide/obtiene | Agente debe entregar | Gate |
|---|---|---|---|---|---|
| F01 | GitHub / Actions | Reutilizar | MFA, permisos, branch protection, límites de runners | Auditoría workflows y permisos de tokens | CP-01 |
| F02 | Doppler o gestor equivalente | Reutilizar si sirve | Proyecto y entornos `dev/staging/prod`, acceso mínimo | Matriz de variables, scopes, consumidores, rotación | CP-04 |
| F03 | VM Linux / Fly.io / entorno OCI | Decidir | Región UE, presupuesto, operador, red privada | Requisitos CPU/RAM/disco, Compose/OCI y smoke | CP-02 |
| F04 | Storage de evidencias y backup | Decidir | Bucket/volumen, región, retención y propietario | Cifrado, versionado, restore, lifecycle y costes | CP-06 |
| F05 | Custodia de claves/KMS | Decidir para producción | Proveedor, política de recuperación y roles | Diseño de claves, rotación y prueba de recuperación | CP-06 |
| F06 | Grafana/OTel + alertas | Reutilizar si existe | Destinatario, canal y presupuesto | Exportación redactada, panel, alerta y simulacro | CP-09 |
| F07 | Identidad de operadores | Reutilizar IdP | Roles, MFA, altas/bajas | Mapeo de claims, revocación, permisos por tenant | CP-07 |
| F08 | DNS/TLS/Cloudflare | Reutilizar | Subdominio y acceso privado | Configuración sin publicar servicios sin permiso | Staging |
| F09 | Revisión independiente | Elegir revisor | Aceptar alcance y presupuesto | Paquete de evidencias y remediaciones | CP-07/13 |
| F10 | ROE/DPA/privacidad | Founder + asesor | Aprobar límites, datos y contratos | Plantillas, matriz de retención, licencias | CP-12 |

## Herramientas OSS: no abrir cuentas comerciales por defecto

Gitleaks, OSV-Scanner, Semgrep CE, Trivy, Syft, pip-audit, Schemathesis, OWASP ZAP, pytest e Hypothesis pueden instalarse en los escenarios OSS pertinentes. El agente verifica licencias, reglas, feeds, versión y compatibilidad; «OSS» no concede automáticamente derecho a revender feeds o reglas de terceros.

**Proveedores de IA y herramientas opcionales:** Codex, Cline, FreeBuff, Antigravity, PyRIT/garak u otros conectores se activan solo tras validar interfaz real, coste, licencia, tratamiento de datos y necesidad. No son condición para ejecutar escáneres deterministas. No abrir cuentas SIEM/EDR/Kubernetes/Kafka por anticipado.

## Contrato de secretos (plantilla sin valores)

Para cada variable que pida el agente, registrar:

`SECRET_REF | proveedor | entorno | componente consumidor | capacidad mínima | expiración | rotación | responsable | estado`.

Ejemplo **solo de estructura**, no nombre de variable contractual: `<secret-ref> | gestor elegido | staging | worker | lectura de bucket limitado | 90d | procedimiento aprobado | founder | PENDING`.

**Prohibido:** pegar tokens en issues, Markdown, PR, chat, logs o reportes. Preferir referencias del gestor; no imprimir secretos en pruebas; rotar inmediatamente credenciales expuestas.

## Qué no debe hacer el agente sin autorización

No crear cuentas ni generar claves de producción por su cuenta; no subir secretos a GitHub; no desplegar públicamente; no ejecutar escaneos sobre clientes; no habilitar efectos activos ni integraciones con `/agente` sin aprobación. Preparar la solicitud precisa y esperar.
