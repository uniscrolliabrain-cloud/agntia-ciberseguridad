# Evaluación científica y benchmarks
## Taxonomía de resultados
- DISCOVERED: hipótesis reportada, aún no verificada.
- REPRODUCED: comportamiento reproducido en fixture autorizado.
- CONFIRMED: oráculo independiente verifica violación de propiedad.
- FIXED: condición desaparece en build corregido.
- REGRESSION_SAFE: tests funcionales/seguridad definidos pasan.
- NOT_RUN: sin ejecución, no cuenta como éxito.
- INCONCLUSIVE: datos insuficientes o fallo del oráculo.

## Benchmarks candidatos
**CyberGym:** reproducción de vulnerabilidades históricas; medir success, coste y contexto.
**CyberGym-E2E:** 920 vulnerabilidades/139 proyectos; S1→S4, no mezclar con patch-only.
**AgentCyberRange:** multi-host, verificar versión del benchmark y reglas de ejecución; resultados de paper y leaderboard actual difieren.
**OSS-Fuzz fixtures:** corpus y crashes conocidos, oracle de sanitizer.
**API synthetic suite:** OpenAPI + Schemathesis, estados y roles sintéticos.
**AI synthetic suite:** PyRIT/garak, prompt injection, tool misuse, leakage canary; evaluadores humanos para ambigüedad.
**Resilience suite:** DB down, worker crash, queue partition, restore y RTO/RPO.

## Métricas
Precision = confirmed / reviewed findings; recall solo cuando ground truth completo; verified findings per compute-hour y €/finding; false positive rate con negativos etiquetados; median/p95 latency; coverage por clase y componente; % NOT_RUN; retest success; regression rate; sandbox escape attempts blocked; policy violations; leakage; cost; model/provider variance.
Para 0/0 reportar N/A, no 100%. Para intervalos usar bootstrap/Wilson cuando proceda y describir incertidumbre. Separar calidad del modelo, del harness y del benchmark.

## Protocolo de comparación
Mismo SHA de benchmark, imágenes, modelo, presupuesto, temperatura/configuración, tiempo, tokens, herramientas, acceso a pistas, seeds y evaluación. Repetir n≥3 cuando el coste lo permita; separar development/holdout; blind evaluator; guardar logs redactados y hashes. No comparar una cifra de un paper con otra de leaderboard sin reconciliar fecha y condiciones.

## Gate de publicación
Ningún claim de 'autonomous pentest' sin dataset, alcance, oráculo, límites, fallos, baselines y aprobación humana. Un hallazgo reproducido en laboratorio no demuestra explotabilidad en producción. Una reparación que pasa S3 puede no corregir vulnerabilidad ground-truth (S4); documentarlo.
