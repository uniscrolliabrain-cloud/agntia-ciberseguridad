// Offline runtime verification only. CI must additionally run TypeScript's strict checker.
import {spawnSync} from 'node:child_process';
import {existsSync} from 'node:fs';
import {mkdir,readFile,readdir,writeFile} from 'node:fs/promises';
import {stripTypeScriptTypes} from 'node:module';

// Prefer the pinned compiler: parameter properties and enums are not supported by Node's
// strip-only mode, and Node >=26 rejects the transform mode outright.
const tsc=new URL('./node_modules/typescript/bin/tsc',import.meta.url);
if(existsSync(tsc)){
  const result=spawnSync(process.execPath,[tsc.pathname,'-p',new URL('./tsconfig.json',import.meta.url).pathname],{stdio:'inherit'});
  if(result.status!==0)process.exit(result.status??1);
  console.log('TypeScript compiler used; runtime verification only.');
}else{
  await mkdir(new URL('./dist',import.meta.url),{recursive:true});
  for(const name of await readdir(new URL('./src',import.meta.url))){if(!name.endsWith('.ts'))continue;const source=await readFile(new URL('./src/'+name,import.meta.url),'utf8');await writeFile(new URL('./dist/'+name.replace(/\.ts$/,'.js'),import.meta.url),stripTypeScriptTypes(source));}
  console.log('Runtime transpilation only; no TypeScript typecheck implied.');
}
