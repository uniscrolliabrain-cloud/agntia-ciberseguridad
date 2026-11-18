# VS-03 — Patchset

**Base:** `6677899`.

## Cambios

| Archivo | Tipo | Motivo |
|---|---|---|
| `reportes/VS-03-REPORT.md` | add | Inventario de referencias, matriz de autorización, huecos y gate |
| `reportes/VS-03-EVIDENCE.md` | add | Comandos y límites de la evidencia |
| `reportes/VS-03-PATCHSET.md` | add | Este documento |
| `reportes/VS-03-ROLLBACK.md` | add | Reversión |
| `reportes/BITACORA-VIVA.md` | modify | Entrada VS-03 |

## Código

**Ninguno.** No se añade un `SecretStore` porque ya existe el patrón correcto: configuración de
referencias + lectura en el punto de uso. Crear otra capa sin gestor habría duplicado el diseño y
dado falsa sensación de revocación.

## Deltas propuestos para la siguiente pasada

1. Test de no fuga: serializar errores/telemetría con un valor de entorno canario y comprobar que no
   aparece.
2. Adaptador de gestor cuando el founder elija proveedor; interfaz mínima `get/rotate/revoke` con
   tenant y versión.
3. TTL por token además de `expires_at` por principal.
