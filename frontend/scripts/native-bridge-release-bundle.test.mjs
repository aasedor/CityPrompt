import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';
import { packedCatalogue, productionStarter } from './packed-catalogue.mjs';

test('production bridge lookup ships timber without the nine held bridge profiles', async () => {
  const result = await build({
    stdin: { contents: "export { nativeBridgeSources } from '../src/components/viewer/globe/nativeBridgeSources';", resolveDir: fileURLToPath(new URL('.', import.meta.url)) },
    alias: { '@': fileURLToPath(new URL('../src', import.meta.url)) },
    bundle: true, write: false, format: 'esm', minify: true,
    define: { 'import.meta.env.DEV': 'false', 'import.meta.env.MODE': '"production"' },
  });
  const code = result.outputFiles[0].text;
  assert.ok(code.includes('timber_covered_bridge_route_v1'));
  for (const id of ['planted_green_bridge_route_v1','weathering_steel_v_footbridge_route_v1','cable_stayed_cycle_ring_route_v1']) assert.ok(!code.includes(id));
});

test('production roster keeps the timber pilot dependencies while the other nine stay pending', () => {
  const source = readFileSync(new URL('../src/data/classroomStarter.json',import.meta.url),'utf8');
  const roster = JSON.parse(productionStarter(source));
  const timber = roster.entries.find(entry=>entry.variantId==='timber_covered_bridge_route_v1');
  assert.ok(timber);
  for (const id of timber.dependencies) assert.ok(roster.dependencies.some(dep=>dep.id===id),id);
  assert.ok(!roster.entries.some(entry=>entry.variantId==='planted_green_bridge_route_v1'));
});

test('the exact bridge release uses the existing catalogue codec', () => {
  const path = fileURLToPath(new URL('../src/data/nativeBridgeRelease.json',import.meta.url));
  assert.ok(packedCatalogue().transform('',path));
});
