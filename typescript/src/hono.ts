import {Hono,type Context} from 'hono';
import {CyberClient,CyberError} from './client.js';
// Resolver authenticates the host session and authorizes a tenant-bound client.
// Never derive identity or service credential from browser headers/query/body.
export function cyberRoutes(resolve:(context:Context)=>Promise<CyberClient>){
 const app=new Hono();app.use('*',async(c,next)=>{c.header('Cache-Control','no-store');await next();});
 app.get('/assets',async c=>{const q=c.req.query();if(Object.keys(q).some(k=>!['after','limit'].includes(k)))return c.json({code:'validation'},422);return c.json(await(await resolve(c)).assets({...q,limit:q.limit===undefined?50:Number(q.limit)}));});
 app.get('/jobs/:id',async c=>{if(Object.keys(c.req.query()).length)return c.json({code:'validation'},422);return c.json(await(await resolve(c)).job(c.req.param('id')));});
 app.get('/findings',async c=>{const q=c.req.query();if(Object.keys(q).some(k=>!['after','limit'].includes(k)))return c.json({code:'validation'},422);return c.json(await(await resolve(c)).findings({...q,limit:q.limit===undefined?50:Number(q.limit)}));});
 app.get('/reports/:id',async c=>{if(Object.keys(c.req.query()).length)return c.json({code:'validation'},422);return c.json(await(await resolve(c)).report(c.req.param('id')));});
 app.get('/budget',async c=>{if(Object.keys(c.req.query()).length)return c.json({code:'validation'},422);return c.json(await(await resolve(c)).budget());});
 app.onError((e,c)=>{const error=e instanceof CyberError?e:new CyberError('validation',422);return new Response(JSON.stringify({code:error.kind,retryable:error.retryable,correlation_id:error.correlationId}),{status:error.status,headers:{'Content-Type':'application/json','Cache-Control':'no-store'}});});
 app.all('*',c=>c.json({code:'not_found'},404));return app;
}
