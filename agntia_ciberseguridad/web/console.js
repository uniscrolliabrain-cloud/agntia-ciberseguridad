'use strict';
(() => {
 let credential='',tenant='',generation=0;
 const el=id=>document.getElementById(id);
 const node=(tag,text)=>{const n=document.createElement(tag);n.textContent=String(text);return n;};
 const button=(label,fn)=>{const b=node('button',label);b.type='button';b.className='row';b.addEventListener('click',fn);return b;};
 const clear=()=>{['overview','jobs','findings','assets','proposals','actions'].forEach(id=>el(id).replaceChildren());el('detail').textContent='Sin ejecución seleccionada.';};
 async function request(path,body){const current=generation;const response=await fetch(`/v1/tenants/${encodeURIComponent(tenant)}/${path}`,{method:body===undefined?'GET':'POST',headers:{Authorization:`Bearer ${credential}`,...(body===undefined?{}:{'Content-Type':'application/json'})},body:body===undefined?undefined:JSON.stringify(body),cache:'no-store',redirect:'error'});if(current!==generation)throw new Error('Sesión caducada.');if(!response.ok)throw new Error(`Consulta denegada o no disponible (${response.status}).`);const data=await response.json();if(current!==generation)throw new Error('Sesión caducada.');return data;}
 const show=value=>{el('detail').textContent=JSON.stringify(value,null,2);};
 async function guarded(fn,current){try{await fn();}catch(error){if(current===generation){el('actions').replaceChildren();el('detail').textContent=error.message;}}}
 function evidenceAction(id,current){return button(`Evidencia ${id.slice(0,8)} · descargar vista`,()=>guarded(async()=>{
  const meta=await request(`evidence/${encodeURIComponent(id)}`);if(current!==generation)return;show(meta);
  const response=await fetch(`/v1/tenants/${encodeURIComponent(tenant)}/evidence/${encodeURIComponent(id)}/content`,{headers:{Authorization:`Bearer ${credential}`},cache:'no-store',redirect:'error'});
  if(current!==generation)return;if(!response.ok)throw new Error(`Descarga denegada (${response.status}).`);
  const blob=await response.blob();if(current!==generation)return;
  const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=`${id}.txt`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 },current));}
 async function load(current){
  const data=await request('workspace');if(current!==generation)return;
  for(const [title,value]of [['Cobertura',data.coverage],['Frescura',data.freshness],['Collector',data.collector_status],['Presupuesto',data.budget_status]]){const card=node('article','');card.append(node('h2',title),node('strong',value));if(title==='Presupuesto'&&data.budget.available_cents!==undefined)card.append(node('p',`${(data.budget.available_cents/100).toFixed(2)} EUR disponibles · ${data.budget.period}`));el('overview').append(card);}
  for(const asset of data.assets)el('assets').append(node('p',`${asset.display_name} · ${asset.kind} · ${asset.state} · ${asset.id.slice(0,8)}`));
  if(!data.assets.length)el('assets').append(node('p','Sin activos registrados.'));
  for(const job of data.jobs)el('jobs').append(button(`${job.tool} · ${job.state} · ${job.id.slice(0,8)}`,()=>guarded(async()=>{const detail=await request(`investigation/jobs/${encodeURIComponent(job.id)}`);if(current!==generation)return;show(detail);el('actions').replaceChildren(...detail.evidence_ids.map(id=>evidenceAction(id,current)));},current)));
  if(!data.jobs.length)el('jobs').append(node('p','Sin ejecuciones. Cobertura no evaluada.'));
  for(const finding of data.findings)el('findings').append(button(`${finding.severity} · ${finding.state} · ${finding.id.slice(0,12)}`,()=>guarded(async()=>{const detail=await request(`findings/${encodeURIComponent(finding.id)}/history`);if(current!==generation)return;show(detail);el('actions').replaceChildren();},current)));
  if(!data.findings.length)el('findings').append(node('p','Sin hallazgos visibles. Esto no acredita ausencia de riesgo.'));
  for(const p of data.review_proposals)el('proposals').append(button(`${p.action} · ${p.state} · ${p.id.slice(0,8)}`,()=>guarded(async()=>{
   const detail=await request(`reviews/proposals/${encodeURIComponent(p.id)}`);if(current!==generation)return;show(detail);
   const sourceButtons=detail.evidence_ids.map(id=>evidenceAction(id,current));
   if(detail.state==='proposed'&&!detail.expired){
    const label=node('label','He leído el cambio, destino, hash, evidencias y caducidad.');const checkbox=document.createElement('input');checkbox.type='checkbox';label.append(checkbox);
    const approve=button('Aprobar cambio local',()=>guarded(async()=>{if(!checkbox.checked)return;approve.disabled=true;const result=await request(`reviews/proposals/${encodeURIComponent(p.id)}/approve`,{expected_revision:detail.revision,proposal_hash:detail.proposal_hash});if(current===generation){show(result);el('actions').replaceChildren();el('status').textContent='Revisión registrada. Consulta de nuevo para refrescar.';}},current));
    approve.disabled=true;checkbox.addEventListener('change',()=>{approve.disabled=!checkbox.checked;});sourceButtons.push(label,approve);
   }
   el('actions').replaceChildren(...sourceButtons);
  },current)));
  if(!data.review_proposals.length)el('proposals').append(node('p','Sin propuestas. La IA no puede aprobarse a sí misma.'));
  el('status').textContent=`Datos de ${data.tenant_id} · ${data.as_of}`;
 }
 el('logout').addEventListener('click',()=>{generation++;credential='';tenant='';el('token').value='';clear();el('status').textContent='Sesión cerrada.';});
 el('session').addEventListener('submit',async event=>{event.preventDefault();const current=++generation;credential=el('token').value;el('token').value='';tenant=el('tenant').value;clear();el('status').textContent='Consultando fuentes…';try{await load(current);}catch(error){if(current===generation){credential='';clear();el('status').textContent=error.message;}}});
})();
