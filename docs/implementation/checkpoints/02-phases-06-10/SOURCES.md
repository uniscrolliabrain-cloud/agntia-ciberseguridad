# Fuentes primarias del bloque6–10

Consultadas el2026-11-10 mediante el conector GitHub; revisión selectiva, no auditoría de todo upstream.

- [Gitleaks release8.30.1](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1): asset/digest, binario construido y versión comprobada en Docker.
- [Gitleaks README8.30.1](https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md): modo dir, redacción y distinción del core respecto a la action.
- [Gitleaks licencia MIT](https://github.com/gitleaks/gitleaks/blob/v8.30.1/LICENSE): notice conservado en infra/scanners/licenses.
- [OSV-Scanner release2.7.1](https://github.com/google/osv-scanner/releases/tag/v2.7.1): asset/digest y versión comprobada.
- [OSV README](https://github.com/google/osv-scanner/blob/v2.7.1/README.md): privacidad/fuentes y riesgo de fix sobre proyectos no confiables. No usamos fix.
- [Modo offline](https://github.com/google/osv-scanner/blob/v2.7.1/docs/offline-mode.md): ubicación `osv-scalibr/{ecosystem}/all.zip`, prohibición de red y ausencia de DB.
- [Configuración](https://github.com/google/osv-scanner/blob/v2.7.1/docs/configuration.md): `--config` sobrescribe configs por directorio. La fixture real incluye un ignore hostil y el finding sigue detectándose.
- [Flags](https://github.com/google/osv-scanner/blob/v2.7.1/cmd/osv-scanner/internal/helper/flags.go) y [source command](https://github.com/google/osv-scanner/blob/v2.7.1/cmd/osv-scanner/scan/source/command.go): offline, no-call-analysis, no-resolve, JSON y all-packages.
- [Modelo JSON de resultados](https://github.com/google/osv-scanner/blob/v2.7.1/pkg/models/results.go): estructura de fuentes/componentes/advisories contrastada además con ejecución real.
- [OSV licencia Apache2.0](https://github.com/google/osv-scanner/blob/v2.7.1/LICENSE): notice conservado. La licencia del motor no decide automáticamente la de cada feed, regla o servicio comercial.

Hashes exactos, URLs de descarga y plataforma: `infra/scanners/releases.json`. Imagen/policy/hash y SHA de prueba real: `evidence/ci.json`. No se atribuye a los vendors ninguna certificación o revisión de Agntia.
