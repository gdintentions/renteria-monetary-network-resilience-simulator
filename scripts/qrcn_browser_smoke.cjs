"use strict";
// Browser-only verification of a synthetic, client-side QRCN visualization.
// This does NOT verify the Python journal or represent live transactions.
const {chromium} = require("playwright");
const assert = require("node:assert/strict");
const path = require("node:path");
const fs = require("node:fs");

async function main(){
  const browser = await chromium.launch({headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1280,height:900}});
    const errors=[];
    page.on("pageerror",e=>errors.push(e.message));
    await page.goto("file://" + path.resolve("hosted_demo/qrcn/index.html"));
    assert.match(await page.title(),/QRCN/);
    const examples = [
      ["normal", "accepted", 1],
      ["tamper", "rejected_integrity", 0],
      ["crash", "accepted_after_restart", 1],
      ["fenced", "stale_writer_rejected", 0],
      ["concurrent", "one_commit_only", 1],
      ["split", "requires_adjudication", 2]
    ];
    for (const [scenario,status,count] of examples) {
      await page.selectOption("#scenario",scenario);
      await page.click("#run");
      const receipt=JSON.parse(await page.locator("#receipt").innerText());
      assert.equal(receipt.scenario,scenario);
      assert.equal(receipt.status,status);
      assert.equal(receipt.local_commits,count);
      assert.equal(receipt.demo_only,true);
    }
    assert.equal(errors.length,0,"Browser JavaScript errors: "+errors.join("; "));
    const folder=path.resolve("artifacts/qrcn");
    fs.mkdirSync(folder,{recursive:true});
    await page.screenshot({path:path.join(folder,"phase2-browser.png"),fullPage:true});
    console.log(JSON.stringify({status:"PASS",scenarios:examples.length,
      claim_boundary:"visualizes fixed synthetic fixtures, not Python clearing",
      browser_errors:errors.length},null,2));
  } finally {
    await browser.close();
  }
}
main().catch(e=>{console.error(e);process.exitCode=1});
