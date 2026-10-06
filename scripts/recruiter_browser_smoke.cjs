const {chromium}=require("playwright");
const http=require("node:http"),fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const root=path.resolve(__dirname,"../hosted_demo");
const files=new Set(["index.html","app.js","rag-demo.js","styles.css"]);
const server=http.createServer((req,res)=>{
 const file=new URL(req.url,"http://localhost").pathname.slice(1)||"index.html";
 if(!files.has(file)){res.writeHead(404);return res.end();}
 res.setHeader("Content-Type",file.endsWith(".js")?"text/javascript":file.endsWith(".css")?"text/css":"text/html");
 res.end(fs.readFileSync(path.join(root,file)));
});
(async()=>{
 await new Promise(resolve=>server.listen(0,"127.0.0.1",resolve));
 const browser=await chromium.launch({headless:true});
 try {
  const page=await browser.newPage({viewport:{width:390,height:844}});
  const errors=[];page.on("pageerror",e=>errors.push(e.message));
  await page.goto("http://127.0.0.1:"+server.address().port+"/#governed-rag");
  assert.match(await page.locator("#rag-answer").innerText(),/withheld/);
  await page.locator("#rag-approve").click();
  assert.match(await page.locator("#rag-answer").innerText(),/internal owner/);
  const [download]=await Promise.all([page.waitForEvent("download"),page.locator("#rag-export").click()]);
  const trace=JSON.parse(fs.readFileSync(await download.path(),"utf8"));
  assert.equal(trace.synthetic,true);assert.equal(trace.release_status,"approved");
  await page.getByRole("button",{name:"Policy conflict",exact:true}).click();
  assert(await page.locator("#rag-approve").isDisabled());
  assert.match(await page.locator("#rag-flags").innerText(),/conflicting_policy/);
  await page.locator("#rag-reject").click();
  assert.match(await page.locator("#rag-answer").innerText(),/rejected/);
  await page.getByRole("button",{name:"Question injection",exact:true}).click();
  assert.equal(await page.locator("#rag-decision").innerText(),"BLOCK");
  await page.getByRole("button",{name:"Document injection",exact:true}).click();
  assert.match(await page.locator("#rag-flags").innerText(),/document_prompt_injection/);
  await page.locator("#rag-question").fill("<img src=x onerror='window.bad=true'>");
  await page.locator("#rag-run").click();assert.equal(await page.evaluate(()=>window.bad),undefined);
  await page.locator("#rag-question").fill(" ");await page.locator("#rag-run").click();
  assert(await page.locator("#rag-export").isDisabled());
  await page.reload();assert.equal(await page.locator("#rag-release").innerText(),"PENDING");
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:"/tmp/rag-recruiter-mobile.png",fullPage:true});
  // Verify each remaining hosted miniature independently of the Python apps.
  await page.goto("http://127.0.0.1:"+server.address().port+"/#polyglot-relay");
  for(const [language,translation] of [["es","hola"],["fr","bonjour"],["ja","こんにちは"]]){
   await page.locator('#poly-target').selectOption(language);await page.locator('#poly-run').click();
   assert.equal(await page.locator('#poly-output').innerText(),translation);
  }
  await page.getByRole('button',{name:'unsupported phrase',exact:true}).click();
  assert.equal(await page.locator('#poly-decision').innerText(),'BLOCK');
  await page.getByRole('button',{name:'high-risk unsupported',exact:true}).click();
  assert.equal(await page.locator('#poly-decision').innerText(),'REVIEW');
  assert.match(await page.locator('#poly-output').innerText(),/unavailable/);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.goto("http://127.0.0.1:"+server.address().port+"/#context-atlas");
  assert.match(await page.locator('#atlas-reasons').innerText(),/explicit/);
  await page.locator('#atlas-svg circle').nth(3).focus();await page.keyboard.press('Enter');
  assert.equal(await page.locator('#atlas-title').innerText(),'Draft');
  assert.match(await page.locator('#atlas-reasons').innerText(),/Missing Note/);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.goto("http://127.0.0.1:"+server.address().port+"/#monetary-simulator");
  const initial=await page.locator('#sim-ranking').innerText();
  await page.locator('#sim-run').click();assert.equal(await page.locator('#sim-ranking').innerText(),initial);
  const shares=(await page.locator('#sim-ranking strong').allTextContents()).map(x=>parseFloat(x));
  assert.equal(shares.length,6);assert(shares.every(Number.isFinite));assert(Math.abs(shares.reduce((a,b)=>a+b,0)-100)<.04);
  await page.locator('#sim-intensity').fill('0');await page.locator('#sim-run').click();
  assert.notEqual(await page.locator('#sim-ranking').innerText(),initial);
  await page.locator('#sim-seed').fill('');await page.locator('#sim-run').click();
  assert.match(await page.locator('#sim-error').innerText(),/Seed/);
  assert.equal(await page.locator('#sim-ranking').innerText(),'');
  await page.locator('#sim-seed').fill('42');await page.locator('#sim-run').click();
  assert.equal(await page.locator('#sim-error').innerText(),'');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.deepEqual(errors,[]);
  console.log("PASS: four hosted miniatures; RAG review/export, translation boundaries, keyboard graph inspection, deterministic finite shares and invalid-input withholding.");
 } finally {await browser.close();server.close();}
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
