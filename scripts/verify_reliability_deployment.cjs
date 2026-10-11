/* Wait only for publication propagation, then assert exact deployed Python sources. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const base=process.env.RELIABILITY_BASE_URL;
if(!base)throw Error('RELIABILITY_BASE_URL required');
const sources={
 'tracelens.py':'portfolio_projects/renteria-tracelens/tracelens.py',
 'continuity_router.py':'portfolio_projects/renteria-continuity-router/continuity_router.py',
 'sourcegate.py':'portfolio_projects/renteria-sourcegate/sourcegate.py',
 'scenarios.py':'reliability_lab/scenarios.py'
};
const expected=Object.fromEntries(Object.entries(sources).map(([name,file])=>[name,{path:file,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex')}]));
(async()=>{
 let lastError;
 for(let attempt=1;attempt<=8;attempt++){
  try{
   const response=await fetch(new URL('source-manifest.json?verify='+Date.now(),base),{signal:AbortSignal.timeout(15000)});
   assert.equal(response.status,200,'Published source manifest must be available');
   const manifest=await response.json();assert.equal(manifest.runtime,'Pyodide 0.27.7');assert.deepEqual(manifest.sources,expected);
   // Verify the served bytes as well as the manifest. A manifest alone is not parity.
   for(const [name,entry] of Object.entries(expected)){
    const file=await fetch(new URL(name+'?verify='+Date.now(),base),{signal:AbortSignal.timeout(15000)});
    assert.equal(file.status,200,name+' must be available');
    const digest=crypto.createHash('sha256').update(Buffer.from(await file.arrayBuffer())).digest('hex');
    assert.equal(digest,entry.sha256,name+' must match the checkout');
   }
   const out=path.resolve(process.env.RELIABILITY_ARTIFACTS||path.join(root,'artifacts/reliability/live'));
   fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'live-source-parity.json'),JSON.stringify({timestamp_utc:new Date().toISOString(),base_url:base,commit:process.env.GITHUB_SHA||null,status:'PASS',attempt,manifest},null,2));
   console.log('PASS: published Python bytes and source manifest match the tested checkout.');return;
  }catch(e){lastError=e;console.log('Publication propagation check '+attempt+' failed: '+e.message);if(attempt<8)await new Promise(r=>setTimeout(r,5000));}
 }
 throw lastError;
})().catch(error=>{console.error(error);process.exitCode=1;});
