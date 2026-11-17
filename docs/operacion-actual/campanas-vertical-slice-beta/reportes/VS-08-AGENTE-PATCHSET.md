# VS-08 — Patchset para /agente (propuesta, no aplicada)

**Estado:** propuesta. **Prohibido aplicar sin autorización explícita del owner.**

## Contrato propuesto

```ts
type AuditRequest = {
  schema_version: 1;
  asset_id: string;      // 32 hex
  grant_id: string;      // 32 hex
  snapshot_id: string;   // 32 hex
  tool: 'gitleaks'|'osv'|'semgrep'|'trivy';
  max_attempts: 1|2|3;
  maximum_cost_cents: 0;
};
```

- Idempotencia: cabecera `Idempotency-Key` de 8–100 caracteres; repetir con el mismo cuerpo devuelve
  `replayed: true`, nunca un segundo job.
- Tenant y actor se derivan del principal autenticado; el body no los acepta.
- Errores: 401 auth, 403 capability, 404 tenant ajeno, 409 conflicto de revisión, 424 gate de release,
  429 cupo, 502 contrato.
- Eventos: `{tenant_id, job_id, correlation_id, causation_id, type, at}`; `causation_id` debe venir
  de la petición, no copiarse de la correlación.

## Instalación

1. Dependencia server-only; nunca importar en cliente ni en el LLM.
2. Variables: `CYBER_BASE_URL`, `CYBER_TENANT_ID`, credencial por gestor (nunca en prompt).
3. Origen aprobado explícito; sin `https` no se permite salvo loopback de desarrollo.

## Rollback

Retirar el adaptador y volver al cliente anterior; no hay migración de datos. Los jobs ya creados
siguen consultables por API.
