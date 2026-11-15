---
title: Agntia Adversarial Lab
emoji: 🧪
colorFrom: indigo
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Agntia Adversarial Lab — Space

MVP sintético del laboratorio adversarial. Corre un ciclo completo sobre gemelos en proceso y muestra
el informe con los hashes de evidencia.

## Crear el Space

1. En Hugging Face, **New Space → Docker → Blank** (CPU basic, gratis).
2. Sube estos tres archivos a la raíz del Space: `Dockerfile`, `app.py`, `README.md`.
3. El build clona el repo público e instala `adversarial_lab`; no necesita secretos.

## Límites

- Solo datos sintéticos; no hay clientes, modelos externos ni claves.
- El resultado es `PARTIAL` porque Semgrep/OSV/Syft/Schemathesis/ZAP/PyRIT/garak están `BLOCKED`.
- La evidencia vive en `/tmp` del contenedor y se pierde al reiniciar el Space.
- El Space no es una frontera de seguridad; no expone ejecución de código de usuario.
