# @agntia/ciberseguridad

Server-only SDK for the synthetic pilot. Node24 is the verified CI target. No browser credential, generic proxy or agent approval tool. A trusted host resolver must authorize tenant/identity and issue single-use delegated reads. See [integration proposal](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/blob/feat/cyber-phases-41-42/docs/integration/PATCHSET-AGENTE.md) in the source repository; it has not been applied to `/agente`.

The package is private and UNLICENSED pending the owner's license decision. `npm pack` prepares a test artifact; it does not publish to npm or authorize commercial distribution.

Desde `0.1.0-alpha.2`, `client.ackOutbox(eventId, {consumer_id, content_hash})`
confirma una entrega del outbox existente. El consumidor debe persistir su efecto
local antes del ACK. El principal necesita `events.ack`; el método no se ofrece a
herramientas del modelo. No se reintenta automáticamente un POST incierto; el
backend puede reconciliar repitiendo explícitamente el mismo ID/consumer/hash.
