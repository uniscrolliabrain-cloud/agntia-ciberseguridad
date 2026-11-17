# VS-05 — Rollback

Una prueba nueva y la restauración de `typescript/src/client.ts` desde VS-00. Sin cambios de esquema.

```bash
git revert <commit-de-VS-05>
```

Al revertir, el contract test de Node vuelve a fallar hasta fusionar VS-00. El resto no cambia.
