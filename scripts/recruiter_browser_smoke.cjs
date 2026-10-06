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
  assert.deepEqual(errors,[]);
  console.log("PASS: mobile review flow, conflicts/injections, safe rendering, export and reload isolation.");
 } finally {await browser.close();server.close();}
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
