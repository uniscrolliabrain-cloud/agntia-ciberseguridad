# Conformidad y evaluación acotadas

## Matriz MCP

|Elemento|Estado observado|
|---|---|
|JSON-RPC2.0, initialize y notifications/initialized|Implementado en recurso propio, IDs enteros; notificación sin ID responde202 vacío|
|Versión2025-11-25 y header de sesión/protocolo|Implementado y ligado a actor/tenant/manifest/descriptor/epoch/TTL|
|tools/list, tools/call de lectura conocida|Implementado; schema/argumentos cerrados sin credenciales; grant inyectado por backend en header, autorización nuevamente en la llamada|
|Descriptores/skill/dependencias, drift y replay|Hash versionado, dos humanos, invalidación de permisos previos y tests|
|OAuth/OIDC, clientes externos, callback/redirect|UNSUPPORTED: sin passthrough o registro automático|
|Cliente hacia MCP externo, SSE/streams, batches, sampling/resources/prompts|UNSUPPORTED|
|Conformidad completa o auditoría independiente MCP|NO VERIFICADA|

La prueba del transporte es HTTP a FastAPI con fixtures; no se compara con una certificación de interoperabilidad externa. Tool poisoning sintético demuestra que el descriptor no amplía el executor y que su cambio invalida permisos; no prueba que todos los modelos ignoren instrucciones maliciosas.

## Corpus propio

24 candidatos estáticos:8 benignos y16 adversariales, seed7, labels de regresión. Se cubren rol falsificado, argumentos anidados, shell, destino externo, recurso ajeno, política caducada/distinta, revocación, memoria falsa, Unicode confusable, documento con campo system en ES/EN/FR, audiencia ajena, token alterado y URL de metadata. Los controles benignos hacen lecturas y proyectan paquetes tipados.

El planner es scripted-json-v1; model=null y prompt_hash=null porque no hay un modelo o prompt ejecutado. El fingerprint incluye corpus, schema, reglas y fuentes relevantes del gateway. Cambiar configuración invalida reutilizar resultados. Un futuro modelo debe añadir proveedor/versión/prompt/presupuesto y repetir evaluación, no editar model=null en un reporte existente.

Las métricas registran tarea benigna completada, peticiones adversariales completadas/rechazadas, FP/FN y p50/p95. Aquí FP significa candidato benigno rechazado; FN significa candidato adversarial definido por la suite que llegó a completar la lectura prevista. No representa una tasa universal de compromiso. No hay escenarios adaptativos, hold-out independiente, imagen/audio o un ataque semántico a un LLM real. Son pruebas de mecanismo, no un score de seguridad comercial.

Transcripciones minimizadas guardan case_id, clase de mutación, idioma anotado, código y resultado, sin tokens ni documentos originales. APIs/modelos externos=0; coste externo reservado/incurrido0céntimos. El tiempo de CPU del runner/CI y hosting del servicio no es coste comercial cero.
