# ADTC collector — Ciberseguridad

Collector conceptual: schemaVersion,eventId,eventType,tenantId,actorId,taskId,correlationId,causationId,traceId,spanId,idempotencyKey,source,evidenceRefs,resourceRefs,classification. Ingesta multi-repo bajo ACL y minimización; sin DMs, secretos, documentos o contenido sensible por defecto. Eventos nativos padre no verificados; diseñar bridge versionado. Dedupe, DLQ, backpressure, replay seguro, retención y consentimiento. Observación no bloquea SOP sin policy/mandato. Dos tenants sintéticos para gates.
