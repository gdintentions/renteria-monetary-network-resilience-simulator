/* Exercise actual Python in Chromium; assertions match the native Python acceptance cases. */
const {chromium}=require('playwright');
const http=require('node:http'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../hosted_demo');
const artifacts=path.resolve(process.env.RELIABILITY_ARTIFACTS||path.join(__dirname,'../artifacts/reliability/browser'));
fs.mkdirSync(artifacts,{recursive:true});
fs.rmSync(path.join(artifacts,'failure.json'),{force:true});
const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.wasm':'application/wasm','.py':'text/plain','.zip':'application/zip'};
const server=http.createServer((req,res)=>{const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);let file=path.resolve(root,'.'+pathname);if(pathname.endsWith('/'))file=path.join(file,'index.html');if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);return res.end();}res.setHeader('Content-Type',mime[path.extname(file)]||'text/plain');res.end(fs.readFileSync(file));});
const checks=[],errors=[],network=[];let base;
function check(name,fn){fn();checks.push({name,status:'PASS'});}
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 base=process.env.RELIABILITY_BASE_URL||'http://127.0.0.1:'+server.address().port+'/reliability/';
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844}});page.setDefaultTimeout(20000);
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>network.push(r.url()));
  await page.goto(base+'#tracelens');await page.locator('#runtime').filter({hasText:'Python ready'}).waitFor({timeout:60000});
  async function run(scenario){if(scenario)await page.locator('#scenario').selectOption(scenario);await page.locator('#run').click();await page.locator('#run:not([disabled])').waitFor();const raw=await page.locator('#output').textContent();return raw==='No result yet.'?null:JSON.parse(raw);}
  async function layout(name){check(name,()=>assert.equal(errors.length,0,errors.join('\n')));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));}
  let out=await run('selection-miss');check('TraceLens actual ranking → selection miss → top-k replay',()=>{assert.equal(out.result.diagnosis.status,'SELECTION_MISS');assert.equal(out.result.replay[2].diagnosis.gold_metrics.selected_recall,1);});
  const manifest=out.source_manifest;check('Exact Python source hashes attached',()=>{assert.equal(Object.keys(manifest.sources).length,4);assert.equal(manifest.runtime,'Pyodide 0.27.7');});
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#download').click()]);
  const exported=JSON.parse(fs.readFileSync(await download.path(),'utf8'));check('Download contains exact displayed evidence',()=>assert.deepEqual(exported,out));
  await page.screenshot({path:path.join(artifacts,'tracelens-mobile.png'),fullPage:true});
  for(const [mode,status] of [['candidate-miss','CANDIDATE_MISS'],['unknown','INSUFFICIENT_EVIDENCE'],['judge-disagreement','JUDGE_DISAGREEMENT'],['corpus-gap','CORPUS_GAP_CONFIRMED'],['judge-unavailable','JUDGE_UNAVAILABLE']]){out=await run(mode);check('TraceLens '+mode,()=>assert.equal(out.result.diagnosis.status,status));}
  await page.locator('#trace').fill('{');check('Editing clears stale result and export',()=>assert.equal(out.synthetic,true));assert(await page.locator('#download').isDisabled());assert.equal(await page.locator('#output').textContent(),'No result yet.');await run();assert.equal(await page.locator('#decision').textContent(),'INPUT REJECTED');checks.push({name:'Malformed JSON rejected without stale export',status:'PASS'});
  await page.locator('#trace').fill(JSON.stringify({candidates:[{}],kept_ids:[],judge_labels:{}}));await run();assert.equal(await page.locator('#decision').textContent(),'INPUT REJECTED');checks.push({name:'Python schema failure displayed safely',status:'PASS'});
  const evil='<img src=x onerror="window.injected=true">';await page.locator('#trace').fill(JSON.stringify({candidates:[{id:evil}],kept_ids:[evil],judge_labels:{[evil]:'answers'},gold_ids:[evil]}));out=await run();check('User IDs rendered as text, never HTML',()=>assert.equal(out.result.diagnosis.status,'SUPPORTED_CONTEXT'));assert.equal(await page.evaluate(()=>window.injected),undefined);await layout('TraceLens mobile layout and no JS errors');
  await page.locator('#reset').click();assert(await page.locator('#download').isDisabled());
  await page.goto(base+'#continuity-router');await page.locator('#runtime').filter({hasText:'Python ready'}).waitFor({timeout:60000});
  out=await run('failover');check('Router failover and circuit-open sequence',()=>{assert.equal(out.result.requests[0].provider,'backup');assert.equal(out.result.requests[1].events[0].event,'CIRCUIT_SKIP');});
  await page.locator('#classification').selectOption('restricted');out=await run();check('Restricted data never calls either provider',()=>{assert.deepEqual(out.result.provider_calls,[]);assert.equal(out.result.requests[0].text,null);});
  await page.locator('#classification').selectOption('internal');out=await run('failover');check('Internal data cannot fail over to public backup',()=>assert(!out.result.provider_calls.includes('backup')));
  await page.locator('#classification').selectOption('public');out=await run('recovery');check('Real async cooldown and recovery probe',()=>assert.deepEqual(out.result.requests.map(r=>r.provider),['backup','backup','primary']));
  await page.screenshot({path:path.join(artifacts,'continuity-router-mobile.png'),fullPage:true});
  out=await run('deadline');check('Total deadline withholds output',()=>{assert.equal(out.result.requests[0].status,'NEEDS_REVIEW');assert.equal(out.result.requests[0].text,null);});
  out=await run('auth-failure');check('Authentication failure never retried',()=>assert.equal(out.result.provider_calls.filter(x=>x==='primary').length,1));
  await page.locator('#budget').fill('');await run();assert.equal(await page.locator('#decision').textContent(),'INPUT REJECTED');assert(await page.locator('#download').isDisabled());checks.push({name:'Blank budget rejected and previous output cleared',status:'PASS'});await layout('Router mobile layout and no JS errors');
  await page.goto(base+'#sourcegate');await page.locator('#runtime').filter({hasText:'Python ready'}).waitFor({timeout:60000});
  out=await run('complete');check('SourceGate fallback off means no search',()=>{assert.deepEqual(out.result.search_calls,[]);assert.equal(out.result.result.reason,'MISSING_EVIDENCE');});
  await page.locator('#web-allowed').check();out=await run();check('SourceGate permitted correction yields exact citations',()=>assert.deepEqual(out.result.result.answer.map(a=>a.citation),['kb-access','web-duration']));
  await page.screenshot({path:path.join(artifacts,'sourcegate-mobile.png'),fullPage:true});
  for(const [mode,reason] of [['conflict','CONFLICT'],['untrusted','MISSING_EVIDENCE'],['expired','MISSING_EVIDENCE'],['bad-grade','ADAPTER_OR_SCHEMA_FAILURE'],['bad-metadata','ADAPTER_OR_SCHEMA_FAILURE']]){out=await run(mode);check('SourceGate '+mode+' withheld',()=>{assert.equal(out.result.result.reason,reason);assert.equal(out.result.result.answer,null);});}
  await layout('SourceGate mobile layout and no JS errors');
  await page.locator('#run').focus();await page.keyboard.press('Enter');await page.locator('#run:not([disabled])').waitFor();checks.push({name:'Keyboard run activation',status:'PASS'});
  await page.reload();await page.locator('#runtime').filter({hasText:'Python ready'}).waitFor({timeout:60000});assert(await page.locator('#download').isDisabled());assert.equal(await page.locator('#web-allowed').isChecked(),false);checks.push({name:'Reload resets evidence and search permission',status:'PASS'});
  await page.setViewportSize({width:1440,height:1000});await run('complete');await page.screenshot({path:path.join(artifacts,'sourcegate-desktop.png'),fullPage:true});await layout('Desktop layout and no JS errors');
  await page.route('**/source-manifest.json',route=>route.fulfill({status:503,body:'unavailable'}));
  await page.locator('#restart').click();
  await page.locator('#runtime').filter({hasText:'Runtime unavailable'}).waitFor();
  assert(await page.locator('#run').isDisabled());assert(await page.locator('#download').isDisabled());
  checks.push({name:'Runtime resource failure fails closed',status:'PASS'});
  await page.unroute('**/source-manifest.json');await page.locator('#restart').click();
  await page.locator('#runtime').filter({hasText:'Python ready'}).waitFor({timeout:60000});
  await run('complete');assert(!(await page.locator('#download').isDisabled()));checks.push({name:'Runtime restart recovers without retaining old results',status:'PASS'});
  check('All resource requests remain on the hosting origin',()=>assert(network.every(url=>url.startsWith(new URL(base).origin+'/'))));
  fs.writeFileSync(path.join(artifacts,'source-manifest.json'),JSON.stringify(manifest,null,2));
 }finally{await browser.close();server.close();}
 fs.writeFileSync(path.join(artifacts,'results.json'),JSON.stringify({timestamp_utc:new Date().toISOString(),base_url:base,scope:'Chromium desktop/mobile; actual Python with synthetic fixtures',checks,errors},null,2));
 console.log('PASS: '+checks.length+' browser acceptance checks.');
})().catch(e=>{fs.writeFileSync(path.join(artifacts,'failure.json'),JSON.stringify({error:e.stack,checks,errors},null,2));console.error(e);server.close();process.exitCode=1;});
