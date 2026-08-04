import { existsSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const publicRoot = resolve(frontendRoot, 'public');
const catalogPath = resolve(frontendRoot, 'src/data/openSpaceArchetypes.json');
const catalog = JSON.parse(readFileSync(catalogPath, 'utf8'));
const missing = [];
const referenced = new Set();

for (const archetype of catalog.archetypes ?? []) {
  const references = [
    archetype.thumbnailUrl,
    ...(archetype.variants ?? []).map((variant) => variant.thumbnailUrl),
  ].filter(Boolean);

  for (const url of references) {
    referenced.add(url);
    const assetPath = resolve(publicRoot, url.replace(/^\/+/, ''));
    if (!existsSync(assetPath)) missing.push(`${archetype.id}: ${url}`);
  }
}

if (missing.length > 0) {
  console.error(`Missing ${missing.length} open-space archetype reference asset(s):`);
  for (const entry of missing) console.error(`- ${entry}`);
  process.exitCode = 1;
} else {
  console.log(`Verified ${referenced.size} open-space archetype reference assets.`);
}
