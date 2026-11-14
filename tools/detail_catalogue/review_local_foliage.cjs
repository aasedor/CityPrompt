// Screenshot the prairie foliage review grid with the preinstalled Playwright Chromium.
// Usage (repository root served at 127.0.0.1:8765, e.g. python -m http.server 8765 --bind 127.0.0.1):
//   node tools/detail_catalogue/review_local_foliage.cjs "dir=artifacts/prairie-foliage-final&mode=eye" eye.png
// Review evidence only: nothing here writes catalogue, registry or project data.
const { chromium } = require('playwright');
const [, , query = 'dir=artifacts/prairie-foliage-final&mode=eye', out = 'prairie-foliage-review.png', width = '1840'] = process.argv;
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: Number(width), height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (error) => errors.push(String(error)));
  page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto(`http://127.0.0.1:8765/tools/detail_catalogue/review_local_foliage.html?${query}`);
  await page.waitForFunction(() => document.title === 'done', null, { timeout: 180000 });
  await page.screenshot({ path: out, fullPage: true });
  console.log(JSON.stringify({ out, errors }));
  await browser.close();
  if (errors.length) process.exit(1);
})().catch((error) => { console.error(error); process.exit(1); });
