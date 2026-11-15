# 06 — Tablero vivo de ejecución
**Estado inicial al 2026-11-15:** ningún gate de esta guía está cerrado por esta auditoría documental. La rama advlab contiene código y reportes previos, pero requiere rerun independiente. Actualizar solo con links a evidencia.

| ID | Owner | Estado inicial | Dependencia | Gate |
|---|---|---|---|---|
| A01 inventario | Agente | TODO | ninguna | diff+matriz |
| A02 rerun | Agente | TODO | A01 | logs+SHA |
| A03 threat model | Agente+Founder | TODO | A02 | revisión |
| B01 vault paths | Agente | TODO | A03 | negativos |
| B02 claves/restore | Agente+Founder | BLOCKED | F04,F05 | rotación+restore |
| B03 OCI real | Agente+Founder | BLOCKED | F02,F06 | aislamiento |
| B04 broker | Agente | TODO | A03 | revocación |
| B05 release | Agente | TODO | A02 | audit fail-closed |
| C01 provider | Agente+Founder | BLOCKED | F03,B03,B04 | misión real sintética |
| C02 segundo provider | Agente | BLOCKED | C01 | comparación |
| C03 tools OSS | Agente | TODO | B03 | probes |
| C04 misiones | Agente | TODO | B04 | oráculos |
| D01 scheduler | Agente | TODO | B03,C01 | recovery |
| D02 alertas | Agente+Founder | BLOCKED | F07 | simulacro |
| D03 backups | Agente+Founder | BLOCKED | F05 | restore |
| E01 bridge padre | Agente+Founder | BLOCKED | D01 | contrato+tenancy |
| E02 piloto interno | Founder+Agente | BLOCKED | E01 | dos tenants |
| E03 legal/comercial | Founder | BLOCKED | F08 | ROE/DPA |
| E04 primer cliente | Founder | BLOCKED | E02,E03 | GO firmado |

## Registro de decisiones (completar sin secretos)
| ID | Fecha | Decisión | Alternativas | Motivo | Riesgo | Aprobó |
|---|---|---|---|---|---|---|
| F01–F08 | pendiente | pendiente | pendiente | pendiente | pendiente | founder |

## Registro de riesgos
- R01 sandbox host: abierto P0.
- R02 paths/keys de vault: abierto P0, explotación no confirmada.
- R03 release audit BLOCKED: abierto P0.
- R04 proveedores externos: BLOCKED.
- R05 aceptación de clientes: BLOCKED.

## Convenciones de estados
`TODO` no empezado; `IN_PROGRESS` con branch; `PASS` evidencia adjunta; `PARTIAL` parte funcional; `BLOCKED` dependencia concreta; `FAIL` prueba ejecutada fallida; `NOT_VERIFIED` afirmación sin prueba; `ACCEPTED` aprobación founder. Nunca cambiar estado sin enlazar SHA y reporte.

## Próxima reunión founder/agente
Revisar A01/A02, elegir F02/F04/F05, decidir si B01/B02/B03 se implementan en paralelo con ownership disjunto. Mantener producción deshabilitada.
