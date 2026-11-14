# Decisiones del checkpoint

1. Integrar por rutas de negocio cerradas, sin endpoint de modelo/método o consola genérica. Mantener FastAPI, SQLite y contrato previo.
2. Usar AES-GCM de cryptography en vez de cifrado propio. Cada tenant referencia claves externas de32 bytes; primera activa y anteriores aprobadas para lectura. No implementar un supuesto KMS local.
3. Original y redacción son objetos cifrados distintos. Eliminar original antes de plazo no es una decisión automática del LLM. Hold requiere revisor humano y revisión esperada.
4. Mantener kind histórico human por compatibilidad, pero documentar que solo es configuración del servidor. La futura identidad de /agente deberá acreditar el principal; el payload no puede elegirlo.
5. Usar reglas deterministas triage-v1 con campos unknown en vez de simular feeds comerciales. No integrar LLM en puntajes o aprobación.
6. Guardar informes cifrados; SQLite conserva referencias/metadatos. Snapshot coherente de fuentes y hash de contenido, sin root de auditoría variable dentro del hash idempotente.
7. Rechazar traceparent/baggage público como autoridad y contexto. Mantener contexto W3C solo en persistencia interna. IDs de correlación no otorgan acceso.
8. Provider privado del SDK, sin autoinstrumentación que registre SQL o cuerpos. ALWAYS_ON explícito para laboratorio; backend de producción y sampling serán decisión operativa futura.
9. Métricas globales con secreto propio de operador. Consultas por tenant a través del endpoint autenticado, sin tenant como label. No dar visibilidad global a un owner de un cliente.
10. Resolver tags de imágenes en CI y fijar RepoDigests verificados. Conservar logs/resultados de intentos fallidos y no atribuir a local pruebas Docker/SDK ejecutadas remotamente.
