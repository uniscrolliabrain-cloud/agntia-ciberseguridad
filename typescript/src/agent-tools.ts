import {CyberClient} from './client.js';
import {closed,id} from './contracts.js';
type Capability='assets.read'|'findings.read'|'jobs.read';
type Scope={client:CyberClient;resourceId:string;oneUseToken:string};
export function agentTools(resolve:(capability:Capability)=>Promise<Scope>){
 return Object.fromEntries((['assets.read','findings.read','jobs.read'] as const).map(capability=>['cyber_'+capability.replace('.','_'),{
  description:`Read authorized ${capability}; single-use server delegation required.`,inputSchema:{type:'object',properties:{},additionalProperties:false},
  execute:async(input:unknown)=>{closed(input,[]);const scope=await resolve(capability);return scope.client.governedRead({token:scope.oneUseToken,capability,resource_id:id(scope.resourceId)});}
 }]));
}
