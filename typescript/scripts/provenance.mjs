// Content identity for the server SDK. The tarball hash depends on tar metadata,
// so CI pins the digest of the actual package files instead.
import {createHash} from 'node:crypto';
import {readFileSync,readdirSync} from 'node:fs';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const target=join(root,'PROVENANCE.json');
const pkg=JSON.parse(readFileSync(join(root,'package.json'),'utf8'));
const sha256=value=>createHash('sha256').update(value).digest('hex');
const files=[
  'README.md',
  'package.json',
  ...readdirSync(join(root,'dist')).filter(name=>name.endsWith('.js')||name.endsWith('.d.ts')).sort().map(name=>'dist/'+name),
];
export const manifest={
  generator:'typescript/scripts/provenance.mjs',
  name:pkg.name,
  version:pkg.version,
  files:Object.fromEntries(files.map(file=>[file,sha256(readFileSync(join(root,file)))])),
};
manifest.content_digest=sha256(JSON.stringify({name:manifest.name,version:manifest.version,files:manifest.files}));
const write=process.argv.includes('--write');
const check=process.argv.includes('--check');
if(write){
  const {writeFileSync}=await import('node:fs');
  writeFileSync(target,JSON.stringify(manifest,null,2)+'\n');
  console.log(JSON.stringify({written:target,content_digest:manifest.content_digest}));
}else if(check){
  let recorded;
  try{recorded=JSON.parse(readFileSync(target,'utf8'));}catch{throw Error('PROVENANCE.json missing; run npm run provenance:write');}
  if(recorded.content_digest!==manifest.content_digest||JSON.stringify(recorded.files)!==JSON.stringify(manifest.files))
    throw Error('SDK content does not match PROVENANCE.json; run npm run provenance:write and review the diff');
  console.log(JSON.stringify({verified:target,content_digest:manifest.content_digest}));
}else{
  console.log(JSON.stringify({content_digest:manifest.content_digest,files:Object.keys(manifest.files).length}));
}
