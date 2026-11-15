# 05 — Integraciones y agentes: qué conectar, cómo y en qué orden
## I01 GitHub
Founder revisa MFA, scopes de Freebuff/Codex, permisos de PR y protección de main. Agente valida workflows, dependabot/renovaciones, checks obligatorios, releases y que secrets no aparezcan en logs. Los agentes no pueden hacer merge o deploy autónomo sin permiso.

## I02 Scanners OSS
Conectar uno por uno, no todos simultáneamente. Para cada adaptador: versión/digest, licencia de binario y reglas, descarga/actualización de feed, test fixture vulnerable, test fixture limpio, timeout, presupuesto y salida normalizada. Prioridad: Gitleaks → OSV-Scanner → Semgrep CE → Trivy; después SBOM Syft. Sin binario disponible: `BLOCKED`, no PASS simulado.

## I03 AgntiaPro /agente
El repositorio madre mantiene identidad, tenants, roles, aprobaciones, SOP, memoria y UX. El middleware recibe credencial servidor limitada, verifica tenant y autorización, crea jobs, entrega receipts/evidencias y emite eventos. SDK TS/Hono solo servidor; nunca exponer token al navegador. Contrato propuesto `/v1/tenants/{tid}`; contrastar con rutas implementadas.
**Founder:** aprobar por separado cambios en /agente. **Agente:** leer interfaces actuales, crear contrato de integración y patchset propuesto, test con tenantA/B y revocación. Pedro presenta resultados; Laia coordina; no inventar segundo kernel.

## I04 Alertas/observabilidad
OTel ya contemplado; elegir Grafana Cloud o stack existente. Enviar métricas de errores, latencia, backlog, scanner unavailable, feeds obsoletos, jobs blocked, costes, revocaciones y restores. Nunca exportar evidencia cruda ni tokens a logs. Probar alerta de fallo y recepción real por operador.

## I05 Almacenamiento y backups
Vault cifrado con claves externas, backup cifrado y segregado, retención, restore completo con claves/revisiones/identidades actuales. No confundir backup parcial con DR validado. Guardar SHA y manifiesto de cada recuperación.

## I06 Identidad y acceso
Integrar IdP/MFA solo cuando exista entorno compartido. Definir roles founder/operator/auditor/cliente, service identities, revocación y expiración. No aceptar `tenant_id` enviado por LLM como autoridad. Probar acceso cruzado y privilegios.

## I07 Proveedores LLM (opcionales)
Un proveedor si realmente mejora análisis o narración. Exigir límites de gasto, política de datos, tool manifest cerrado, revisión humana y test prompt injection. No dar al modelo acceso a shell libre, claves, cambios de política o acciones irreversibles.

## I08 Otros sistemas (posteriores)
SIEM, cloud CSPM, Wazuh, MDM, tickets, email/WhatsApp y automatización de remediaciones solo después de una demanda concreta y permisos. Cada integración requiere ownership de datos, scopes, fallback y rollback.
