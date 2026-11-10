# Evidencia de escenarios · D1P1–D1P5

PASS significa el caso descrito realmente ejercitado, no toda la fase. PARTIAL conserva el aspecto futuro sin probar. Los nombres de test pueden localizarse con `rg` en `tests`.

| Gate | Estado | Evidencia y límite |
|---|---|---|
| D1P1-TEST-1 | PASS | Baseline real: Docker socket denegado; test de inventario simula indisponibilidad y conserva scans=0. Ningún test runtime de Docker aprobado |
| D1P1-TEST-2 | PASS | `test_inventory_preserves_unrelated_edits_and_reports_unavailable_docker`: checkout temporal con cambio versionado y fichero ajeno conservados |
| D1P2-TEST-1 | PASS | `test_closed_fields_and_schema_roundtrip`, `test_grant_cannot_expand_consent_or_accept_llm_identity`: identidad/context/shell ajenos rechazados |
| D1P2-TEST-2 | PASS | Contratos rechazan no finitos/float para dinero; ausencia de configuración impide factoría; API acota cuerpo y frames. No representa una auditoría de toda configuración productiva |
| D1P3-TEST-1 | PASS | `test_tenant_asset_isolation_and_no_server_paths`: IDs de otro tenant y principal intercambiado devuelven404 sin rutas |
| D1P3-TEST-2 | PARTIAL | `test_revoked_principal_and_rotated_token_fail_closed`: principal capturado no conserva permiso; no hay job asíncrono que ejecutar todavía |
| D1P4-TEST-1 | PASS | `test_failed_upgrade_rolls_back_existing_data_and_audit`: DDL inválido revierte, esquema/auditoría previos permanecen |
| D1P4-TEST-2 | PARTIAL | `test_concurrent_duplicate_asset_yields_one_object` y dos procesos de migración pasan; duplicación de reservas pendiente porque no existe ledger |
| D1P5-TEST-1 | PASS | Suite `test_network_scope`: metadata, CIDR, redirect, puerto y ruta inválidos fallan en preflight sin abrir conexión |
| D1P5-TEST-2 | PARTIAL | Grant revocado/caducado y revocado durante DNS impiden preflight; inicio/retry de runner pendiente |

Integridad de evidencia: `evidence/tests.json` contiene SHA256 del log real `tests.txt`; `evidence/contention.json` conserva medición sintética y hash final de cadena. Logs con tokens sintéticos no se imprimen; IDs de correlación son aleatorios, sin datos reales. El fallo inicial del generador de evidencia se conserva por separado.
