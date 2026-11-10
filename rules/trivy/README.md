# Perfil opcional Trivy

Se inspecciona configuración Dockerfile offline con las comprobaciones embebidas del binario fijado. No se arranca ninguna imagen, no se aplica IaC ni se consulta una DB de advisories. El análisis de vulnerabilidades de imagen permanece not_tested. La fixture contrasta USER root con USER10001 para DS002; otros checks pueden seguir señalando problemas. No se anuncia que el control sea seguro de forma global.
