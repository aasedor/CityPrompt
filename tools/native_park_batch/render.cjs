// Render review views of one clay GLB with headless Chromium.
// Usage (repository root served at 127.0.0.1:8765, frontend dependencies installed):
//   node tools/native_park_batch/render.cjs <park> <model.glb> <output dir> [view,view,...]
// Cameras come from cameras.json beside this file, in the authoring frame.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const [, , park, model, out, only = ''] = process.argv;
if (!model || !out) { console.error('usage: render.cjs <model.glb> <output dir> [views]'); process.exit(2); }
const roster = JSON.parse(fs.readFileSync(path.join(__dirname, 'cameras.json'), 'utf8'))[park];
const cameras = roster.views;
const wanted = only ? only.split(',') : Object.keys(cameras);
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1700, height: 1300 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (error) => errors.push(String(error)));
  page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto(`http://127.0.0.1:8765/tools/native_park_batch/review.html?model=${encodeURIComponent(model.replace(/^\/+/, ''))}${roster.hole ? `&hole=${roster.hole.join(',')}` : ''}`);
  await page.waitForFunction(() => document.title === 'ready', null, { timeout: 180000 });
  fs.mkdirSync(out, { recursive: true });
  for (const name of wanted) {
    const view = cameras[name];
    if (!view) throw new Error(`No camera named ${name}`);
    const url = await page.evaluate((spec) => window.renderView(spec), view);
    const file = path.join(out, `${name}.${view.jpeg ? 'jpg' : 'png'}`);
    if (fs.existsSync(file)) throw new Error(`${file} exists; renders are never overwritten`);
    fs.writeFileSync(file, Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'));
  }
  console.log(JSON.stringify({ rendered: wanted.length, stats: await page.evaluate(() => window.__stats), errors }));
  await browser.close();
  if (errors.length) process.exit(1);
})().catch((error) => { console.error(error); process.exit(1); });
