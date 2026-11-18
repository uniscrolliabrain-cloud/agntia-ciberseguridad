# @agntia/ciberseguridad

Server-only SDK for the synthetic pilot. Node24 is the verified CI target. No browser credential, generic proxy or agent approval tool. A trusted host resolver must authorize tenant/identity and issue single-use delegated reads. See [integration proposal](https://github.com/uniscrolliabrain-cloud/agntia-ciberseguridad/blob/feat/cyber-phases-41-42/docs/integration/PATCHSET-AGENTE.md) in the source repository; it has not been applied to `/agente`.

The package is private and UNLICENSED pending the owner's license decision. `npm pack` prepares a test artifact; it does not publish to npm or authorize commercial distribution.

## Artefacto reproducible

`npm run pack:deterministic` genera `.pack/agntia-ciberseguridad-<version>.tgz`
con cabeceras tar y gzip normalizadas: dos ejecuciones producen el mismo SHA256.
`PROVENANCE.json` fija el digest del contenido empaquetado (`dist`, `README.md`,
`package.json`) y viaja dentro del artefacto. Tras cambiar el SDK hay que ejecutar
`npm run provenance:write` y revisar el diff; el CI ejecuta `npm run provenance:check`.
El SHA del tarball crudo de `npm pack` no es estable y no se usa como identidad.

Desde `0.1.0-alpha.2`, `client.ackOutbox(eventId, {consumer_id, content_hash})`
confirma una entrega del outbox existente. El consumidor debe persistir su efecto
local antes del ACK. El principal necesita `events.ack`; el método no se ofrece a
herramientas del modelo. No se reintenta automáticamente un POST incierto; el
backend puede reconciliar repitiendo explícitamente el mismo ID/consumer/hash.

Desde `0.1.0-alpha.3` el SDK cubre el alta gobernada completa sin transporte
genérico: `createManifest`, `approveManifest`, `issueDelegation` y
`revokeDelegation`, además de `governedRead`. El manifiesto y la delegación los
emite un principal humano con `agents.manage`/`agents.delegate`; el token de un
uso se entrega al cliente del agente, que solo puede ejecutar lecturas nominadas.
La delegación caduca como máximo en cinco minutos y se consume en el primer uso.
Ninguno de estos métodos se expone como herramienta de modelo ni como ruta del
BFF Hono.
