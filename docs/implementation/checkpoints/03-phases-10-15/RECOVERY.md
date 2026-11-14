# Interrupción y recuperación

El2026-11-10 el ejecutor dejó de estar disponible durante la publicación. Último comando observado antes del corte: unittest terminó con72 casos descubiertos,66 aprobados y6 Docker omitidos; validadores documentales pasaron. El commit local no pudo comprobarse y no se atribuye a un SHA remoto.

El conector GitHub siguió operativo. El bloque se reconstruyó y preservó mediante API a partir de las implementaciones de este turno, el baseline remoto f61a36e823a185c8cfde9278a8689e6bb9877883 y las fuentes fijadas. Se añadieron pruebas de recuperación, historial y API. La validación de esa versión publicada es la CI asociada a su nuevo SHA, con conteos propios: no se hereda el PASS local anterior como prueba de bytes que no pudieron recuperarse del checkout.

No se han borrado ni sustituido archivos de un executor recuperado. Antes de retomar allí, comparar commits/árboles, conservar cambios ajenos y alinear una rama nueva con la publicada. La rama remota preserva código, fuentes vendorizadas y evidencia aunque el workspace no vuelva.
