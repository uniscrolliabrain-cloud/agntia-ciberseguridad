// Deterministic package artifact: npm pack + normalized tar headers + fixed gzip.
// The sha256 of this file is stable across runs; npm's raw .tgz is not.
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdirSync,mkdtempSync,readFileSync,readdirSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {gzipSync,gunzipSync} from 'node:zlib';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const outFlag=process.argv.indexOf('--out');
const out=outFlag>0?resolve(process.argv[outFlag+1]):join(root,'.pack');
const octal=(buffer,offset,length,value)=>{buffer.write(value.toString(8).padStart(length-1,'0')+'\0',offset,length,'ascii');};
const size=(header)=>{
  const field=header.subarray(124,136);
  if(field[0]&0x80){let value=0;for(const byte of field.subarray(1))value=value*256+byte;return value;}
  return parseInt(field.toString('ascii').replace(/\0.*$/,'').trim()||'0',8);
};
export function normalizeTar(tar){
  let offset=0;
  while(offset+512<=tar.length){
    const header=tar.subarray(offset,offset+512);
    if(header.every(byte=>byte===0))break;
    const bytes=size(header);
    if(!Number.isSafeInteger(bytes)||bytes<0)throw Error('invalid tar header');
    octal(header,136,12,0);octal(header,108,8,0);octal(header,116,8,0);
    header.fill(0,265,297);header.fill(0,297,329);
    header.fill(0x20,148,156);
    let sum=0;for(const byte of header)sum+=byte;
    header.write(sum.toString(8).padStart(6,'0')+'\0 ',148,8,'ascii');
    offset+=512+Math.ceil(bytes/512)*512;
  }
  return tar;
}
const scratch=mkdtempSync(join(tmpdir(),'cyber-pack-'));
const packed=spawnSync('npm',['pack','--ignore-scripts','--pack-destination',scratch],{cwd:root,encoding:'utf8'});
if(packed.status!==0)throw Error(packed.stderr||'npm pack failed');
const name=readdirSync(scratch).find(entry=>entry.endsWith('.tgz'));
if(!name)throw Error('npm pack produced no tarball');
const artifact=gzipSync(normalizeTar(gunzipSync(readFileSync(join(scratch,name)))),{level:9});
mkdirSync(out,{recursive:true});
const target=join(out,name);
writeFileSync(target,artifact);
console.log(JSON.stringify({file:target,sha256:createHash('sha256').update(artifact).digest('hex'),bytes:artifact.length}));
