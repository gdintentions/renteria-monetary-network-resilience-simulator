const qs=(s)=>document.querySelector(s);
const qsa=(s)=>[...document.querySelectorAll(s)];

function route(){
  const id=(location.hash||"#home").slice(1);
  qsa(".view").forEach(v=>v.classList.toggle("active",v.id===id));
  if(!qs("#"+CSS.escape(id))) location.hash="#home";
  window.scrollTo({top:0,behavior:"instant"});
}
window.addEventListener("hashchange",route);route();

const stop=new Set(["the","is","a","an","what","who","how","to","of","and","are","be","from"]);
const tok=(s)=>[...s.toLowerCase().matchAll(/[a-z0-9']+/g)].map(m=>m[0]).filter(x=>!stop.has(x));
const policy=[
  {id:"vendor",title:"Vendor Access",text:"Vendor access requires approval from the internal owner before production access is granted."},
  {id:"external",title:"External Review",text:"External document access is logged and reviewed quarterly by the responsible control owner."},
  {id:"legal",title:"Legal Questions",text:"Legal interpretation questions must be escalated to qualified human review."},
  {id:"audit",title:"Audit Trail",text:"Released answers retain the question, evidence identifier, confidence, and governance decision."},
];
function cos(a,b){
  const ca={},cb={};a.forEach(x=>ca[x]=(ca[x]||0)+1);b.forEach(x=>cb[x]=(cb[x]||0)+1);
  const terms=new Set([...Object.keys(ca),...Object.keys(cb)]);
  let dot=0,na=0,nb=0;terms.forEach(t=>{dot+=(ca[t]||0)*(cb[t]||0);na+=(ca[t]||0)**2;nb+=(cb[t]||0)**2});
  return na&&nb?dot/(Math.sqrt(na)*Math.sqrt(nb)):0;
}
function runRag(){
  const question=qs("#rag-question").value.trim();const qt=tok(question);const qset=new Set(qt);
  const rows=policy.map(p=>{
    const dt=tok(p.text),matched=[...new Set(dt.filter(x=>qset.has(x)))];
    const score=cos(qt,dt);return {...p,matched,score};
  }).sort((a,b)=>b.score-a.score);
  const best=rows[0],coverage=best.matched.length/Math.max(new Set(qt).size,1);
  const confidence=Math.max(0,Math.min(1,.7*best.score+.3*coverage));
  let decision="block",answer="Insufficient approved evidence.";
  if(best.matched.length>=2&&confidence>=.18){
    decision=(confidence<.42||qset.has("legal"))?"review":"safe";
    answer=best.text;
  }
  qs("#rag-decision").textContent=decision.toUpperCase();
  qs("#rag-decision").style.color=decision==="safe"?"var(--good)":decision==="review"?"var(--warn)":"var(--bad)";
  qs("#rag-confidence").textContent=(confidence*100).toFixed(1)+"%";
  qs("#rag-answer").textContent=answer;
  qs("#rag-evidence").innerHTML=rows.map(r=>`<div class="evidence"><strong>${r.title}</strong> <span class="score">${(r.score*100).toFixed(1)} similarity</span><p>${r.text}</p><small>Matched terms: ${r.matched.join(", ")||"none"}</small></div>`).join("");
}
qs("#rag-run").addEventListener("click",runRag);qsa("[data-rag]").forEach(b=>b.addEventListener("click",()=>{qs("#rag-question").value=b.dataset.rag;runRag()}));runRag();

const trans={hello:{es:"hola",fr:"bonjour",ja:"こんにちは"},"thank you":{es:"gracias",fr:"merci",ja:"ありがとう"}};
const riskWords=new Set(["medical","legal","emergency","bank","password","account"]);
function runPoly(){
  const phrase=qs("#poly-phrase").value.trim().toLowerCase(),target=qs("#poly-target").value;
  const supported=Boolean(trans[phrase]?.[target]);const risky=tok(phrase).some(x=>riskWords.has(x));
  const output=supported?trans[phrase][target]:"Translation unavailable in this demo-safe fixture.";
  const decision=risky?"review":supported?"safe":"block";const quality=supported?".98":"0.00";
  qs("#poly-output").textContent=output;qs("#poly-supported").textContent=supported?"YES":"NO";qs("#poly-quality").textContent=quality;qs("#poly-risk").textContent=risky?"HIGH":"LOW";qs("#poly-decision").textContent=decision.toUpperCase();
}
qs("#poly-run").addEventListener("click",runPoly);qsa("[data-poly]").forEach(b=>b.addEventListener("click",()=>{qs("#poly-phrase").value=b.dataset.poly;runPoly()}));runPoly();

const notes=[
  {id:"g",title:"Governance",body:"AI systems should expose [[Evidence]] and review paths.",x:160,y:120},
  {id:"e",title:"Evidence",body:"Citations and provenance support [[Governance]].",x:520,y:120},
  {id:"r",title:"Resilience",body:"Scenario tests measure stress and recovery.",x:160,y:310},
  {id:"d",title:"Draft",body:"This references [[Missing Note]].",x:520,y:310},
];
const titleMap=Object.fromEntries(notes.map(n=>[n.title,n]));
function linkTargets(body){return [...body.matchAll(/\[\[([^\]]+)\]\]/g)].map(m=>m[1])}
function cleanWords(s){return new Set((s.toLowerCase().match(/[a-z]+/g)||[]).filter(x=>x.length>3&&!["this","that","should","with","from"].includes(x)))}
const edges=[],broken=[];
notes.forEach(n=>linkTargets(n.body).forEach(t=>titleMap[t]?edges.push({a:n.id,b:titleMap[t].id,kind:"explicit",reason:"Explicit wikilink"}):broken.push({a:n.id,target:t,kind:"missing",reason:"Missing target"})));
for(let i=0;i<notes.length;i++)for(let j=i+1;j<notes.length;j++){const a=cleanWords(notes[i].body),b=cleanWords(notes[j].body),shared=[...a].filter(x=>b.has(x));if(shared.length>=2&&!edges.some(e=>(e.a===notes[i].id&&e.b===notes[j].id)||(e.a===notes[j].id&&e.b===notes[i].id)))edges.push({a:notes[i].id,b:notes[j].id,kind:"suggested",reason:"Shared terms: "+shared.join(", ")})}
function drawAtlas(){
  const svg=qs("#atlas-svg"),ns="http://www.w3.org/2000/svg";svg.innerHTML="";
  const byId=Object.fromEntries(notes.map(n=>[n.id,n]));
  edges.forEach(e=>{const a=byId[e.a],b=byId[e.b],line=document.createElementNS(ns,"line");line.setAttribute("x1",a.x);line.setAttribute("y1",a.y);line.setAttribute("x2",b.x);line.setAttribute("y2",b.y);line.setAttribute("stroke",e.kind==="explicit"?"#73d7ff":"#8090aa");line.setAttribute("stroke-width","3");if(e.kind==="suggested")line.setAttribute("stroke-dasharray","8 8");svg.append(line)});
  notes.forEach(n=>{const g=document.createElementNS(ns,"g"),c=document.createElementNS(ns,"circle"),t=document.createElementNS(ns,"text");c.setAttribute("cx",n.x);c.setAttribute("cy",n.y);c.setAttribute("r","32");c.setAttribute("fill","#182642");c.setAttribute("stroke","#73d7ff");c.setAttribute("stroke-width","3");c.setAttribute("tabindex","0");t.setAttribute("x",n.x);t.setAttribute("y",n.y+55);t.setAttribute("text-anchor","middle");t.textContent=n.title;const pick=()=>selectNote(n.id);c.addEventListener("click",pick);c.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" ")pick()});g.append(c,t);svg.append(g)});
  broken.forEach(e=>{const a=byId[e.a],t=document.createElementNS(ns,"text");t.setAttribute("x",a.x+42);t.setAttribute("y",a.y+8);t.textContent="⚠ "+e.target;t.setAttribute("fill","#ffd27d");svg.append(t)});
}
function selectNote(id){
  const n=notes.find(x=>x.id===id);qs("#atlas-title").textContent=n.title;qs("#atlas-body").textContent=n.body;
  const rel=[...edges.filter(e=>e.a===id||e.b===id).map(e=>`${e.kind}: ${e.reason}`),...broken.filter(e=>e.a===id).map(e=>`missing: target "${e.target}" does not exist`)];
  qs("#atlas-reasons").innerHTML="<h3>Relationship reasons</h3>"+(rel.length?rel.map(x=>"<p>"+x+"</p>").join(""):"<p>No graph relationships.</p>");
}
drawAtlas();selectNote("g");

const networks=["US / USD","BRICS settlement","Europe / EUR","Gold","Bitcoin & stablecoins","Neutral / multi-aligned"];
const colors=["#73d7ff","#f7a76c","#b48cff","#ffd166","#7de2ae","#9eabc2"];
function rng(seed){let s=(seed>>>0)||1;return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296}}
function normalize(vals){const sum=vals.reduce((a,b)=>a+b,0);return vals.map(v=>v/sum*100)}
function simulate(){
  const years=+qs("#sim-years").value,seed=+qs("#sim-seed").value,intensity=+qs("#sim-intensity").value/100,cal=+qs("#sim-calibration").value/100,R=rng(seed);
  let state=normalize([42,16,16,10,7,9]);
  const rows=[{year:2026,shares:[...state]}],events=[];
  for(let y=1;y<=years;y++){
    const yr=2026+y;const next=state.map((v,i)=>{
      const base=[-.006,.014,.002,.006,.020,.007][i];
      const shock=([-.020,.018,-.003,.012,.025,.010][i])*intensity*(y>2?1:0);
      const anchor=([56.7,2.11,20.6,8,6,7][i]-v)*.006*cal;
      return Math.max(.2,v*(1+base+shock+(R()-.5)*.025)+anchor);
    });
    state=normalize(next);rows.push({year:yr,shares:[...state]});
    if(y===3)events.push({year:yr,text:"Synthetic settlement-network adoption shock"});
    if(y===6)events.push({year:yr,text:"Synthetic payment-infrastructure disruption"});
    if(y===9)events.push({year:yr,text:"Synthetic digital-currency acceleration"});
  }
  renderSim(rows,events);
}
function renderSim(rows,events){
  const canvas=qs("#sim-chart"),ctx=canvas.getContext("2d"),w=canvas.width,h=canvas.height,pad={l:56,r:24,t:30,b:46};ctx.clearRect(0,0,w,h);ctx.fillStyle="#09101e";ctx.fillRect(0,0,w,h);
  ctx.strokeStyle="#293553";ctx.fillStyle="#9eabc2";ctx.font="14px system-ui";
  for(let p=0;p<=100;p+=20){const y=pad.t+(100-p)/100*(h-pad.t-pad.b);ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(w-pad.r,y);ctx.stroke();ctx.fillText(p+"%",10,y+5)}
  networks.forEach((name,i)=>{ctx.strokeStyle=colors[i];ctx.lineWidth=3;ctx.beginPath();rows.forEach((r,j)=>{const x=pad.l+j/(rows.length-1)*(w-pad.l-pad.r),y=pad.t+(100-r.shares[i])/100*(h-pad.t-pad.b);j?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke()});
  rows.forEach((r,j)=>{if(j%3===0||j===rows.length-1){const x=pad.l+j/(rows.length-1)*(w-pad.l-pad.r);ctx.fillStyle="#9eabc2";ctx.fillText(r.year,x-16,h-16)}});
  networks.forEach((name,i)=>{ctx.fillStyle=colors[i];ctx.fillRect(82+i*165,8,12,12);ctx.fillStyle="#dce8ff";ctx.font="12px system-ui";ctx.fillText(name,99+i*165,19)});
  const final=rows.at(-1).shares;const sorted=networks.map((n,i)=>({n,v:final[i]})).sort((a,b)=>b.v-a.v);
  const hhi=final.reduce((s,v)=>s+(v/100)**2,0),effective=1/hhi,div=1-hhi;
  qs("#sim-metrics").innerHTML=`<div class="card"><span>Leading network</span><strong>${sorted[0].n}</strong></div><div class="card"><span>Leading share</span><strong>${sorted[0].v.toFixed(1)}%</strong></div><div class="card"><span>Effective networks</span><strong>${effective.toFixed(2)}</strong></div><div class="card"><span>Diversification index</span><strong>${div.toFixed(3)}</strong></div>`;
  qs("#sim-ranking").innerHTML=sorted.map((x,i)=>`<div class="rankrow"><span>${i+1}. ${x.n}</span><strong>${x.v.toFixed(2)}%</strong></div>`).join("");
  qs("#sim-events").innerHTML=events.map(e=>`<div class="event"><strong>${e.year}</strong><br>${e.text}</div>`).join("");
}
["#sim-years","#sim-intensity","#sim-calibration"].forEach(id=>qs(id).addEventListener("input",()=>{qs(id+"-out").textContent=qs(id).value+(id==="#sim-years"?" years":"%")}));
qs("#sim-run").addEventListener("click",simulate);simulate();
