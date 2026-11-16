# VS-00 — Patchset

**Base SHA:** `2da922ff8ae33bfb0824ae2a6dcec3f3b00e1c93`

## Cambios

| Archivo | Tipo | Motivo |
|---|---|---|
| `typescript/src/client.ts` | modify | `CyberError` usaba parameter properties, rechazadas por el modo strip-only de Node; se reescribe con campos explícitos y el mismo comportamiento |
| `docs/operacion-actual/campanas-vertical-slice-beta/reportes/VS-00-*.md` | add | Reporte, evidencia, patchset, rollback y matriz de capacidades |

## Diff conceptual del código

```ts
// antes
export class CyberError extends Error {
  constructor(public readonly kind: ErrorKind, public readonly status: number, …) { … }
}

// después
export class CyberError extends Error {
  readonly kind: ErrorKind; readonly status: number; readonly retryable: boolean;
  readonly correlationId: string | null;
  constructor(kind: ErrorKind, status: number, retryable = false, correlationId: string | null = null) {
    super(`Cyber middleware: ${kind}`);
    this.name = 'CyberError';
    this.kind = kind; this.status = status;
    this.retryable = retryable; this.correlationId = correlationId;
  }
}
```

Sin cambios de firma pública, de validación ni de códigos de error. `dist/` no está versionado y se
regenera con `npm run build`.

## Lo que no se tocó

- `agntia_ciberseguridad/**`, `app.py`, `agents/**`, `jobs/**`, `evidence/**`, `/agente`.
- `docs/release/status.json`.
- Contratos Pydantic: cualquier alta de campos queda para VS-01 tras el mapa de huecos.
