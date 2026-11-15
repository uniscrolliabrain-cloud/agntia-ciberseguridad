# api-authz — control de autorización horizontal

**Propósito:** comprobar si un usuario autenticado puede leer o modificar recursos de otro usuario
en una API sintética, sin atacar sistemas reales.

**Precondiciones:** gemelo sintético levantado, datos ficticios, engagement activo, egress denegado.

**Hipótesis falsables:**
1. Un token de `user-001` no puede leer `order` de `user-002`.
2. Cambiar el `user_id` del path no devuelve datos ajenos.
3. Un rol `support` no puede ejecutar acciones de `admin`.

**Exclusiones:** no se prueba DoS, no se envían payloads destructivos, no se toca infraestructura real.
