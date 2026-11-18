import test from 'node:test';
import assert from 'node:assert/strict';
import {CyberClient,CyberError} from '../dist/client.js';
const base=process.env.CYBER_AGENT_CONTRACT_URL,asset=process.env.CYBER_AGENT_CONTRACT_ASSET;
const expires=()=>new Date(Date.now()+120000).toISOString();
test('live manifest, human delegation, governed read and revoke',async t=>{
 if(!base||!asset){t.skip('Run Python test_agent_sdk_live');return;}
 const client=token=>new CyberClient({baseUrl:base,approvedOrigins:[base],tenantId:'tenantA',credential:()=>token,timeoutMs:10000});
 const creator=client(process.env.CYBER_AGENT_CONTRACT_OWNER_TOKEN);
 const reviewer=client(process.env.CYBER_AGENT_CONTRACT_REVIEWER_TOKEN);
 const agent=client(process.env.CYBER_AGENT_CONTRACT_AGENT_TOKEN);
 const manifest=await creator.createManifest({agent_binding:'agentA',version:'v1',artifact_hash:'a'.repeat(64),capabilities:['assets.read','findings.read'],resource_ids:[asset]});
 assert.equal(manifest.state,'pending_review');assert.equal(manifest.revision,0);
 const approved=await reviewer.approveManifest(manifest.id,0);
 assert.equal(approved.state,'approved');assert.equal(approved.revision,1);
 const first=await reviewer.issueDelegation({manifest_id:manifest.id,capabilities:['assets.read'],resource_ids:[asset],expires_at:expires()});
 assert.equal(first.one_use,true);assert.equal(first.executor,'governed_read_only');
 const read=await agent.governedRead({token:first.token,capability:'assets.read',resource_id:asset});
 assert.equal(read.data[0].id,asset);assert.equal(read.data[0].tenant_id,'tenantA');assert.equal(read.security_guarantee,false);
 const second=await reviewer.issueDelegation({manifest_id:manifest.id,capabilities:['assets.read'],resource_ids:[asset],expires_at:expires()});
 assert.equal((await reviewer.revokeDelegation(second.id)).revoked,true);
 await assert.rejects(agent.governedRead({token:second.token,capability:'assets.read',resource_id:asset}),e=>e instanceof CyberError&&e.kind==='forbidden');
 await assert.rejects(agent.createManifest({agent_binding:'agentA',version:'v1',artifact_hash:'a'.repeat(64),capabilities:['assets.read'],resource_ids:[asset]}),e=>e.kind==='forbidden');
});
