# VS-06C — Rollback

Rollback documental, sin efectos técnicos:

1. `git rm reportes/VS-06C-REPORT.md reportes/VS-06C-EVIDENCE.md reportes/VS-06C-PATCHSET.md reportes/VS-06C-ROLLBACK.md`
2. Quitar la entrada y la fila de cola de `reportes/BITACORA-VIVA.md`.
3. Quitar el puntero de `reportes/VS-06B-REPORT.md`.

`python -m unittest discover -s tests` sigue en **223 tests** antes y después: esta campaña no toca
pruebas.

## Efecto

- El run verde de GitHub Actions **sigue existiendo** y no depende de este repositorio; lo que se pierde
  es su registro y la lectura correcta de su alcance.
- VS-06B vuelve a decir «aún sin run de CI», que sería inexacto a partir de ahora; por eso el rollback
  incluye restaurar ese puntero, no solo borrar ficheros.
