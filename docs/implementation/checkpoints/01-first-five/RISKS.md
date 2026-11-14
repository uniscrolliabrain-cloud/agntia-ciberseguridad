# Riesgos y pendientes del primer corte

- No es un sistema de auditoría completo ni protección activa. `security_scan_executed=false` es obligatorio en toda respuesta de preview.
- El consentimiento administrativo de la fixture prueba autorización técnica, no autenticidad de una firma o representación jurídica de un cliente.
- Rutas y DNS validados solo en preflight: no protegen lecturas futuras de repos mutables ni clientes HTTP que vuelvan a resolver. No existe ejecución de scanner en esta entrega.
- SQLite es un nodo, un worker de API. Contención acotada devuelve503. No se ha validado NFS, réplica o despliegue distribuido.
- Triggers/hashes no protegen contra un administrador que modifica todo el fichero y la configuración. Falta cifrado/anclaje externo de despliegue.
- No hay reservas agregadas, jobs, informes de cliente ni conector a `/agente`. Los contratos exportados de capacidades futuras son diseños tipados, no endpoints activos.
- No hay pruebas de contenedor, Windows o revisión independiente. CI de Python no convierte esas coberturas en PASS.
- La licencia del código propio sigue pendiente de decisión del propietario; no se copió código de los upstreams estudiados.
- Se mantienen las fuentes y límites legales del research. Ningún test técnico acredita conformidad AI Act/RGPD ni el equivalente a un SOC24/7.
