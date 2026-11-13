const assert = require("node:assert/strict");
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const { chromium } = require("playwright");

const root = path.join(__dirname, "../hosted_demo/guardrails-lab");
const files = {
  "/": ["index.html", "text/html"],
  "/lab.css": ["lab.css", "text/css"],
  "/lab.js": ["lab.js", "text/javascript"],
  "/results.json": ["results.json", "application/json"],
};
const server = http.createServer((req, res) => {
  const asset = files[req.url];
  if (!asset) {
    res.writeHead(404).end();
    return;
  }
  const [name, mime] = asset;
  res.writeHead(200, { "Content-Type": mime }).end(fs.readFileSync(path.join(root, name)));
});

async function main() {
  const live = process.env.GUARDRAILS_BASE_URL;
  if (!live) await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const base = live || `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    const errors = [];
    const origins = new Set();
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("request", (request) => origins.add(new URL(request.url()).origin));
    await page.goto(base);
    const picker = page.locator("#case-picker");
    const title = page.locator("#case-result h3");
    const metrics = page.locator("#metrics dd");
    const stages = page.locator("#stages button");
    await page.locator("#case-picker:not([disabled])").waitFor();
    assert.equal(await picker.locator("option").count(), 7);
    assert.equal(await stages.count(), 4);
    assert.equal(await title.textContent(), "Answer released");
    assert.equal(await metrics.first().textContent(), "5/7");
    await picker.selectOption("correction");
    assert.equal(await title.textContent(), "Answer released");
    await stages.nth(1).press("Enter");
    assert.equal(await title.textContent(), "Legitimate request wrongly blocked");
    assert.equal(await metrics.nth(1).textContent(), "1");
    await picker.selectOption("unapproved-action");
    assert.equal(await title.textContent(), "Action denied");
    assert.equal(await page.locator("#case-result dd").last().textContent(), "No");
    await picker.selectOption("wrong-account");
    assert.equal(await title.textContent(), "Account access denied");
    assert.equal(await page.locator("#case-result dd").first().textContent(), "No");
    await picker.selectOption("contact");
    assert.equal(await metrics.nth(2).textContent(), "1");
    await stages.nth(2).click();
    assert.equal(await title.textContent(), "Answer released with contact detail masked");
    assert.equal(await metrics.nth(2).textContent(), "0");
    await picker.selectOption("exception");
    assert.equal(await title.textContent(), "Answer released");
    await stages.nth(3).click();
    assert.equal(await title.textContent(), "Draft held for human review");
    assert.equal(await metrics.first().textContent(), "6/7");
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    assert.deepEqual(errors, []);
    assert.deepEqual([...origins], [new URL(base).origin]);
    console.log("Guardrails browser checks passed.");
  } finally {
    await browser.close();
  }
}

main()
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  })
  .finally(() => {
    if (server.listening) server.close();
  });
