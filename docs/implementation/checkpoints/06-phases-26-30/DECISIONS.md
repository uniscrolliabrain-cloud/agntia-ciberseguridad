# Decisiones y comparación de policy

|Alternativa|Ventaja relevante|Coste/frontera en este piloto|Decisión|
|---|---|---|---|
|OPA/Rego, Apache-2.0|Motor general con decisiones de policy separadas de aplicación y ecosistema de evaluación|Añade distribución/runtime o evaluación WASM, versionado y contrato de datos que igualmente deben validarse; no elimina la necesidad de enforcement|No instalado; considerar al crecer reglas/dominios|
|Cedar, Apache-2.0|Modelo explícito de principal/acción/recurso y autorización con schemas|Integración SDK/FFI/servicio adicional; no resuelve automáticamente identidad, egress, approvals o efectos distribuidos|No instalado; alternativa futura|
|Reglas Python cerradas propias|Pocas acciones, DTO estricto, auditoría y transacción local en el stack existente|Menor expresividad y requiere revisión propia; no se hereda garantía formal de otro motor|Elegido para este alcance, hash de reglas/código y tests de fail-closed|

No se ha ejecutado benchmark comparativo de OPA/Cedar ni se afirma superioridad de rendimiento/seguridad. Sus licencias se consultaron; no se copió código.

1. Cerrar el acceso directo en Authenticator, no depender únicamente de middleware HTTP. Contexto privado solo tras validar un grant; no contexto de tracing como autoridad.
2. Invalidar grants previos al upgrade sin eliminarlos. Cada cambio de control o descriptor invalida conservadoramente todos los tokens/sesiones del tenant mediante epoch.
3. Mantener acciones de lectura y propuesta local; no incorporar shell, action_post, correo, pagos, remediación o HTTP genérico.
4. Tratar la evidencia como datos no confiables, restringir extracción a un esquema pequeño y conservar taint/procedencia. No usar redacción como autorización de exportación.
5. Declassificación necesita dos humanos y hash/destino/TTL, pero todavía no habilita transporte. No resolver secretos donde no hay executor de proveedor validado.
6. Fijar MCP2025-11-25 y cumplir handshake en el subconjunto entregado; no afirmar conformidad global. Bearers propios no se pasan a servidores externos.
7. Hashear descripciones/instrucciones/dependencias; listar una descripción confiable de la tool built-in. Los descriptores de terceros no gobiernan al modelo ni se ejecutan.
8. Elegir una nota local con reserva monetaria0 como primer efecto aprobado. Su idempotencia transaccional no se extrapola a redes distribuidas.
9. Segundo secreto de emergencia separado; reconocer que no equivale a MFA. Detener nuevos efectos, sin afirmar reversión de uno ya confirmado.
10. Usar corpus propio y planner scriptado sin modelo/APIs. Medir utilidad junto a rechazo; registrar configuración exacta y no convertir el score en una promesa de defensa contra todos los LLM.

11. Mantener el grant fuera del schema de argumentos MCP: header X-Agntia-Grant inyectado por backend tras validar el plan, nunca un valor que deba generar/ver el modelo.
