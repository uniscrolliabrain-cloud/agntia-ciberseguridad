import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

test('deterministic pack yields the same sha256 across runs',()=>{
 const out=mkdtempSync(join(tmpdir(),'cyber-pack-test-'));
 const run=()=>JSON.parse(execFileSync(process.execPath,['scripts/pack.mjs','--out',out],{encoding:'utf8'}));
 const first=run(),second=run();
 assert.equal(first.sha256,second.sha256);
 assert.equal(first.bytes,second.bytes);
 assert.match(first.sha256,/^[a-f0-9]{64}$/);
});
