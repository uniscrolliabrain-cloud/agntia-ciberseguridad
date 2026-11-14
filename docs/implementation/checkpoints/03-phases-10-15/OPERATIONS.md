# Operación del prototipo

Instalar el paquete con Python>=3.11. La CI verifica3.11/3.12, dependencias y wheel con recursos. Configuración y tokens solo del servidor. Jobs requiere tool_policy_hashes por herramienta, obtenidos de la instalación administrativa de imágenes; el body de un agente no los configura.

Rutas: POST /v1/tenants/{tenant}/audits con Idempotency-Key; GET jobs/{id}; POST jobs/{id}/cancel con expected_revision; GET findings; GET findings/{id}/history con limit1..100 y after opaco. Las rutas heredan Bearer/capacidades/tenant. No hay proxy Docker, shell o método libre.

create_app expone app.state.jobs para el componente backend y aplica ReleaseGates cerrado por defecto. Una admisión válida puede quedar blocked con release_gate_blocked, nunca ejecutarse a escondidas. No activar esos flags copiando las fixtures: antes debe existir evidencia de revisión, sandbox e identidad del worker.

JobStore, StaticScanner y Worker permiten una iteración run_once del worker dedicado. El runner usa imágenes verificadas, nombres persistidos y datos de caché administrados. No crear un segundo scheduler empresarial: la programación e integración organizacional pertenecen al repo madre y aún no se han conectado.

Ante lease vencida o cleanup desconocido: conservar el job/reserva en reconciliation_required. Detener/verificar el worker anterior. Worker.reconcile exige principal con jobs.reconcile, revisión actual y cleanup real del nombre persistido. No limpiar un nombre suministrado por texto del agente. No borrar una idempotency key para forzar otra ejecución.

Las únicas ejecuciones completas autorizadas por esta entrega son fixtures sintéticas de CI. Reproducir allí: instalar dev, preparar imágenes fijadas, construir probe y usar AGNTIA_RUN_DOCKER_TESTS=1 con los dos módulos tests.docker. El prototipo no requiere ni ofrece proveedores de pago.

El executor del chat quedó unavailable. La fuente vigente está en PR#3, no en un checkout local confirmado. Para continuar en otra máquina, usar esa rama y verificar su SHA antes de editar. No resetear un workspace que reaparezca con cambios del propietario.
