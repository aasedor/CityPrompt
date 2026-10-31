import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';
import { packedCatalogue, productionStarter } from './packed-catalogue.mjs';
const routeIds = ['timber_covered_bridge_route_v1', 'planted_green_bridge_route_v1', 'brick_arch_viaduct_route_v1',
  'rail_through_truss_route_v1', 'stone_arch_road_bridge_route_v1', 'tied_arch_shared_bridge_route_v1',
  'steel_truss_road_bridge_route_v1', 'swooping_cycle_flyover_route_v1', 'cable_stayed_cycle_ring_route_v1',
  'weathering_steel_v_footbridge_route_v1'];

test('production bridge lookup ships exactly the finite ten-route release cohort', async () => {
  const result = await build({
    stdin: { contents: "export { nativeBridgeSources } from '../src/components/viewer/globe/nativeBridgeSources';", resolveDir: fileURLToPath(new URL('.', import.meta.url)) },
    alias: { '@': fileURLToPath(new URL('../src', import.meta.url)) },
    bundle: true, write: false, format: 'esm', minify: true,
    define: { 'import.meta.env.DEV': 'false', 'import.meta.env.MODE': '"production"' },
  });
  const code = result.outputFiles[0].text;
  const runtime = await import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`);
  assert.deepEqual(runtime.nativeBridgeSources.map(row=>row.id), routeIds);
});

test('production roster closes all ten bridge dependencies while unrelated pending entries stay held', () => {
  const source = readFileSync(new URL('../src/data/classroomStarter.json',import.meta.url),'utf8');
  const roster = JSON.parse(productionStarter(source));
  for (const routeId of routeIds) {
    const entry = roster.entries.find(item=>item.variantId===routeId);
    assert.ok(entry, routeId);
    for (const id of entry.dependencies) assert.ok(roster.dependencies.some(dep=>dep.id===id),id);
  }
  assert.ok(!roster.entries.some(entry=>entry.status==='local-pilot-runtime-pending'));
  const input = JSON.parse(source);
  input.entries.push({...input.entries[0],variantId:'held_unreviewed_bridge_route_v1',
    placementId:'held_unreviewed_bridge_route_v1',status:'local-pilot-runtime-pending',dependencies:['public:held-bridge.glb']});
  input.dependencies.push({id:'public:held-bridge.glb'});
  const held = JSON.parse(productionStarter(JSON.stringify(input)));
  assert.ok(!held.entries.some(entry=>entry.variantId==='held_unreviewed_bridge_route_v1'));
  assert.ok(!held.dependencies.some(dep=>dep.id==='public:held-bridge.glb'));
});

test('the exact bridge release uses the existing catalogue codec', () => {
  const path = fileURLToPath(new URL('../src/data/nativeBridgeRelease.json',import.meta.url));
  assert.ok(packedCatalogue().transform('',path));
});
