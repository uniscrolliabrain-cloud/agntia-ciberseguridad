# Fuentes primarias y fijación

Consulta selectiva del2026-11-10; no auditoría exhaustiva de upstream.

- [Semgrep1.185.0](https://github.com/semgrep/semgrep/releases/tag/v1.185.0) y [licencia LGPL2.1](https://github.com/semgrep/semgrep/blob/v1.185.0/LICENSE).
- [Flags del CLI Semgrep](https://github.com/semgrep/semgrep/blob/v1.185.0/cli/src/semgrep/commands/scan.py): CE, métricas, version checks, suppressions, ignores, formato/error.
- [Dockerfile upstream](https://github.com/semgrep/semgrep/blob/v1.185.0/Dockerfile): ubicación del motor y PATH. Imagen fijada semgrep/semgrep@sha256:67518c174185a2043fdbed16c70631b79209499b3671178e7194379b48295a0d.
- [Trivy0.76.2](https://github.com/aquasecurity/trivy/releases/tag/v0.76.2), asset Linux64bit SHA256bc0fc726e017b8927a62b2d3531d7a84ee01769daf5c99ed866dced54089fdbf.
- [Licencia Trivy](https://github.com/aquasecurity/trivy/blob/v0.76.2/LICENSE), [flags misconfiguration](https://github.com/aquasecurity/trivy/blob/v0.76.2/pkg/flag/misconf_flags.go), [flags scan](https://github.com/aquasecurity/trivy/blob/v0.76.2/pkg/flag/scan_flags.go). Se verificó el CLI real: offline-scan no aplica a config; aislamiento de red se impone por Docker y check updates se desactivan.
- [Esquema CycloneDX1.5](https://github.com/CycloneDX/specification/blob/c320fc0f0b46873864927d9d5684eea7ba439728/schema/bom-1.5.schema.json), bundle SPDX/JSF y licencia de ese commit. Archivos vendorizados y hashes verificados dentro del wheel por CI.

Licencias del core no se extrapolan automáticamente a reglas, feeds, Pro, SaaS/MSSP o datos. Bundle Semgrep original de este proyecto; no se copian reglas de registry. La licencia propia del repo sigue pendiente de decisión.

Datos inventados: canarios no funcionales, paquete/advisory ficticios, snippets de eval y Dockerfile de laboratorio. Ninguna comprobación intenta autenticar una credencial real ni escanear un cliente.
