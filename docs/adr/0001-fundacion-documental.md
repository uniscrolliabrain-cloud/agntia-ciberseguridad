# ADR0001 · Fundación documental antes de ejecutar herramientas

Fecha: 2026-11-10. El propietario solicita un middleware defensivo independiente conectado en el futuro a `/agente`, investigación actual y un README/docs antes de implementar. Se crea un repositorio local sin tocar los proyectos previos.

Decisión: priorizar inventario, policy enforcement y evidencia; integrar OSS por adaptadores aislados y servicios opcionales. El runtime y avatares pertenecen al repo madre; el middleware no duplicará su scheduler ni su identidad. Python/FastAPI más SDK TS/Hono es una propuesta para facilitar herramientas existentes, pendiente de contrastar interfaces reales del repo madre sin modificarlo.

Se pospone ejecutar/instalar scanners, comprar SaaS, conectar agentes, desplegar, escanear clientes y otorgar certificaciones. Los documentos de arquitectura y presupuestos son especificaciones; los únicos programas iniciales validan documentación/configuración.

La licencia del código propio queda pendiente de elección del propietario; no confundir publicidad en GitHub con licencia libre de redistribución. No se copia código de terceros. Los repos estudiados conservan sus licencias y términos propios.
