import { readFileSync } from 'node:fs';
import { performance } from 'node:perf_hooks';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { packCatalogue, packedCatalogue } from './packed-catalogue.mjs';

const inflater = pathToFileURL(resolve('node_modules/three/examples/jsm/libs/fflate.module.js')).href;
for (const filename of ['buildingArchetypes.json', 'openSpaceArchetypes.json', 'streetPathArchetypes.json', 'nativeParks.json', 'nativeStreetPilots.json', 'archetypeReferenceAvailability.json']) {
  test(`${filename}: browser decoder preserves every catalogue field`, async () => {
    const source = readFileSync(resolve('src/data', filename), 'utf8');
    const module = packCatalogue(source).replace('three/examples/jsm/libs/fflate.module.js', inflater);
    const started = performance.now();
    const decoded = await import(`data:text/javascript,${encodeURIComponent(module)}`);
    assert.deepEqual(decoded.default, JSON.parse(source));
    assert.ok(module.length < JSON.stringify(JSON.parse(source)).length * 0.55);
    console.log(`${filename}: decode ${Math.round(performance.now() - started)} ms; module ${Math.round(module.length / 1024)} KiB`);
  });
}

test('only the six catalogue data modules are packed; other plugin data is preserved', () => {
  const plugin = packedCatalogue();
  assert.equal(plugin.apply, 'build');
  assert.equal(plugin.enforce, 'post');
  assert.equal(plugin.transform('', '/app/src/data/validationCatalogue.json'), null);
  assert.equal(plugin.transform('', '/app/src/data/classroomExpansion.json'), null);
  assert.equal(plugin.transform('', '/app/src/data/buildingArchetypes.json?raw'), null);
  assert.notEqual(plugin.transform('', resolve('src/data/archetypeReferenceAvailability.json')), null);
});
