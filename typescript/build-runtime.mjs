// Offline runtime verification only. CI must additionally run TypeScript's strict checker.
import {stripTypeScriptTypes} from 'node:module';
import {mkdir,readFile,readdir,writeFile} from 'node:fs/promises';
await mkdir(new URL('./dist',import.meta.url),{recursive:true});
for(const name of await readdir(new URL('./src',import.meta.url))){if(!name.endsWith('.ts'))continue;const source=await readFile(new URL('./src/'+name,import.meta.url),'utf8');await writeFile(new URL('./dist/'+name.replace(/\.ts$/,'.js'),import.meta.url),stripTypeScriptTypes(source,{mode:'transform'}));}
console.log('Runtime transpilation only; no TypeScript typecheck implied.');
