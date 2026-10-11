'use strict';
const $=id=>document.getElementById(id);
const definitions={
 'tracelens':{title:'TraceLens',intro:'Find where retrieval lost the evidence. Compare a top-1 lexical baseline with top-k replay and inspect disagreement.',scenarios:[['selection-miss','Selection drops the answer'],['candidate-miss','Answer missing from candidate pool'],['unknown','Labels cannot establish a corpus gap'],['judge-disagreement','Judge disagrees with gold labels'],['corpus-gap','Exhaustively labeled corpus gap'],['judge-unavailable','Judge response is incomplete']]},
 'continuity-router':{title:'ContinuityRouter',intro:'Watch authorized failover, bounded deadlines and circuit recovery. A provider is never called when classification rules prohibit it.',scenarios:[['failover','Primary outage → backup → open circuit'],['healthy','Healthy primary'],['deadline','Primary exceeds total deadline'],['auth-failure','Authentication failure is not retried'],['recovery','Outage → open circuit → recovered primary']]},
 'sourcegate':{title:'SourceGate',intro:'Follow retrieval, relevance grading, permission-controlled correction and cited extracts. Conflicts or incomplete evidence withhold the answer.',scenarios:[['complete','Missing fact supplied by fixture search'],['conflict','Contradictory approvers'],['untrusted','Look-alike source hostname'],['expired','Expired evidence'],['bad-grade','Incomplete evaluator response'],['bad-metadata','Non-finite claim metadata']]}
};
let project='tracelens',worker,ready=false,busy=false,last=null,manifest=null,sequence=0,timer=null;
function clearResult(){last=null;$('download').disabled=true;$('decision').textContent='Ready for a scenario';$('summary').textContent='Run the current inputs to inspect the outcome.';$('metrics').replaceChildren();$('events').replaceChildren();$('output').textContent='No result yet.';$('error').textContent='';}
function controls(){ $('run').disabled=!ready||busy;for(const id of ['scenario','trace','classification','budget','web-allowed','reset'])$(id).disabled=busy; }
function invalidate(){clearResult();}
function boot(){
 if(worker)worker.terminate();clearTimeout(timer);ready=false;busy=false;manifest=null;sequence++;clearResult();controls();$('runtime').textContent='Loading Python runtime…';
 worker=new Worker('worker.js');const active=worker;
 timer=setTimeout(()=>failBoot('Runtime load timed out. Check the connection and restart.'),60000);
 function failBoot(message){if(worker!==active)return;active.terminate();clearTimeout(timer);ready=false;busy=false;controls();$('runtime').textContent='Runtime unavailable';$('error').textContent=message;}
 worker.onerror=()=>failBoot('Python runtime failed to load. Restart to try again.');
 worker.onmessage=({data})=>{
  if(worker!==active)return;
  if(data.type==='ready'){clearTimeout(timer);manifest=data.manifest;ready=true;$('runtime').textContent='Python ready · source hashes verified · local execution';controls();return;}
  if(data.type==='boot-error'){failBoot(data.message);return;}
  if(data.id!==sequence)return;
  clearTimeout(timer);busy=false;controls();
  if(data.type==='error'){clearResult();$('decision').textContent='INPUT REJECTED';$('error').textContent=data.message;return;}
  last={...data.result,source_manifest:manifest};render(last);$('download').disabled=false;
 };
}
function metric(label,value){const d=document.createElement('div');d.className='metric';const span=document.createElement('span'),strong=document.createElement('strong');span.textContent=label;strong.textContent=value;d.append(span,strong);$('metrics').append(d);}
function event(text){const li=document.createElement('li');li.textContent=text;$('events').append(li);}
function render(envelope){
 const r=envelope.result;$('output').textContent=JSON.stringify(envelope,null,2);
 if(project==='tracelens'){
  $('decision').textContent=r.diagnosis.status;$('summary').textContent=r.baseline;
  const g=r.diagnosis.gold_metrics;if(g){metric('Candidate recall',g.candidate_recall??'Unknown / no gold answers');metric('Selected recall',g.selected_recall??'Unknown / no gold answers');}
  for(const [cell,ids] of Object.entries(r.diagnosis.cells||{}))event(cell.toUpperCase()+': '+(ids.join(', ')||'none'));
  for(const item of r.replay)event('Top '+item.top_k+' replay → '+item.diagnosis.status);
 }else if(project==='continuity-router'){
  const end=r.requests.at(-1);$('decision').textContent=end.status;$('summary').textContent=r.baseline;
  metric('Final provider',end.provider||'None');metric('Actual fixture calls',r.provider_calls.length);
  r.requests.forEach((req,i)=>{event('Request '+(i+1)+' → '+req.status+' ('+(req.elapsed_s*1000).toFixed(1)+' ms)');req.events.forEach(e=>event(e.provider+' · '+e.event+(e.code?' · '+e.code:'')));});
 }else{
  $('decision').textContent=r.result.reason||r.result.status;$('summary').textContent=r.baseline;
  metric('Fixture search calls',r.search_calls.length);metric('Cited extracts',(r.result.answer||[]).length);
  (r.result.events||[]).forEach(event);(r.result.rejected_ids||[]).forEach(id=>event('Rejected source: '+id));
  (r.result.answer||[]).forEach(a=>event('['+a.citation+'] '+a.text+' — '+a.url));
 }
}
function switchProject(){
 const key=location.hash.slice(1);project=definitions[key]?key:'tracelens';
 if(busy){boot();}
 const def=definitions[project];$('title').textContent=def.title;$('intro').textContent=def.intro;document.title=def.title+' · Renteria Reliability Lab';
 $('scenario').replaceChildren(...def.scenarios.map(([value,text])=>new Option(text,value)));
 $('trace-controls').hidden=project!=='tracelens';$('router-controls').hidden=project!=='continuity-router';$('source-controls').hidden=project!=='sourcegate';
 $('source-link').href='https://github.com/gdintentions/renteria-monetary-network-resilience-simulator/tree/main/portfolio_projects/renteria-'+project;
 reset();
}
function reset(){ $('trace').value='';$('classification').value='public';$('budget').value='.08';$('web-allowed').checked=false;clearResult(); }
$('run').addEventListener('click',()=>{
 clearResult();
 const payload={project,scenario:$('scenario').value};
 try{
  if(project==='tracelens'&&$('trace').value.trim())payload.trace=JSON.parse($('trace').value);
  if(project==='continuity-router'){payload.classification=$('classification').value;const text=$('budget').value;payload.budget=Number(text);if(!text||!Number.isFinite(payload.budget)||payload.budget<=0||payload.budget>1)throw Error('Budget must be greater than zero and at most one second.');}
  if(project==='sourcegate')payload.web_allowed=$('web-allowed').checked;
 }catch(e){$('error').textContent=e.message;$('decision').textContent='INPUT REJECTED';return;}
 busy=true;controls();$('decision').textContent='RUNNING';const id=++sequence;worker.postMessage({id,payload});
 timer=setTimeout(()=>{worker.terminate();busy=false;ready=false;controls();clearResult();$('decision').textContent='RUN ABORTED';$('error').textContent='Execution exceeded five seconds. Restart the runtime to continue.';$('runtime').textContent='Runtime stopped';},5000);
});
$('download').addEventListener('click',()=>{if(!last)return;const url=URL.createObjectURL(new Blob([JSON.stringify(last,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=project+'-synthetic-evidence.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
for(const id of ['scenario','trace','classification','budget','web-allowed'])$(id).addEventListener('input',invalidate);
$('reset').addEventListener('click',reset);$('restart').addEventListener('click',boot);window.addEventListener('hashchange',switchProject);switchProject();boot();
