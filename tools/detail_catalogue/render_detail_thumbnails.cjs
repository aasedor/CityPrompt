// Render one catalogue-card WebP per item of a built detail batch, beside its GLBs.
// Usage (repository root served at 127.0.0.1:8765, frontend dependencies installed):
//   node tools/detail_catalogue/render_detail_thumbnails.cjs artifacts/<batch> [slug:half-width,...]
// The framing and lighting copy frontend/src/features/parks/detailThumbnail.ts, so a
// static card looks like the live preview it replaces. Pixels depend on the renderer,
// so thumbnails are reviewed outputs locked by hash, not rebuilt by tests.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const [, , dir, focus = ''] = process.argv;
if (!dir) { console.error('usage: render_detail_thumbnails.cjs <batch-directory> [slug:half-width,...]'); process.exit(2); }
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 800, height: 600 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (error) => errors.push(String(error)));
  const query = `dir=${dir.replace(/^\/+|\/+$/g, '')}&mode=thumb&w=480&h=315&focus=${encodeURIComponent(focus)}`;
  await page.goto(`http://127.0.0.1:8765/tools/detail_catalogue/review_local_foliage.html?${query}`);
  await page.waitForFunction(() => document.title === 'done', null, { timeout: 600000 });
  const thumbs = await page.evaluate(() => window.__thumbs);
  for (const { slug, dataUrl } of thumbs) {
    if (!dataUrl.startsWith('data:image/webp;base64,')) throw new Error(`No WebP for ${slug}`);
    fs.writeFileSync(path.join(dir, `${slug}.webp`), Buffer.from(dataUrl.slice('data:image/webp;base64,'.length), 'base64'));
  }
  console.log(JSON.stringify({ written: thumbs.length, errors }));
  await browser.close();
  if (errors.length) process.exit(1);
})().catch((error) => { console.error(error); process.exit(1); });
