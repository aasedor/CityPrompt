import { readFileSync } from 'node:fs';
import { performance } from 'node:perf_hooks';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deflateSync } from 'node:zlib';
import { packCatalogue, packedCatalogue } from './packed-catalogue.mjs';

const inflater = pathToFileURL(resolve('node_modules/three/examples/jsm/libs/fflate.module.js')).href;

for (const filename of ['streetManual.json', 'nativeStreetModuleBounds.json']) {
  test(`${filename}: production packing preserves every street rule and exact geometric bound`, async () => {
    const path = resolve('src/data', filename);
    const source = readFileSync(path, 'utf8');
    const transformed = packedCatalogue().transform('', path);
    assert.notEqual(transformed, null);
    const module = transformed.code.replace('three/examples/jsm/libs/fflate.module.js', inflater);
    const decoded = await import(`data:text/javascript,${encodeURIComponent(module)}`);
    assert.deepEqual(decoded.default, JSON.parse(source));
    assert.ok(module.length < JSON.stringify(JSON.parse(source)).length * 0.55);
  });
}

test('packing uses the smaller of two bounded lossless compression profiles', () => {
  for (const filename of ['nativeStreetPilots.json', 'buildingArchetypes.json']) {
    const source = readFileSync(resolve('src/data', filename), 'utf8');
    const canonical = source.replace(/("(?:\\.|[^"\\])*")|\s+/g, (_match, quoted) => quoted ?? '');
    const candidates = [8, 6].map(memLevel => deflateSync(Buffer.from(canonical), { level: 9, memLevel }));
    const smallest = candidates.reduce((a, b) => b.length < a.length ? b : a);
    assert.ok(packCatalogue(source).includes(JSON.stringify(smallest.toString('base64'))), filename);
  }
});

test('the production traffic-safety catalogue preserves all variants and placement contracts in a compact module', async () => {
  const filename = resolve('src/features/parks/trafficSafetyCatalogue.json');
  const source = readFileSync(filename, 'utf8');
  const transformed = packedCatalogue().transform('', filename);
  assert.notEqual(transformed, null);
  const module = transformed.code.replace('three/examples/jsm/libs/fflate.module.js', inflater);
  const decoded = await import(`data:text/javascript,${encodeURIComponent(module)}`);
  assert.deepEqual(decoded.default, JSON.parse(source));
  assert.ok(module.length < JSON.stringify(JSON.parse(source)).length * 0.55);
});
for (const filename of ['buildingArchetypes.json', 'openSpaceArchetypes.json', 'streetPathArchetypes.json', 'nativeParks.json', 'nativeStreetPilots.json', 'archetypeReferenceAvailability.json', 'legoFamilySignatures.json', 'validationCatalogue.json', 'buildingWalkDoors.json', 'cataloguePresentation.json', 'classroomExpansion.json', '../features/parks/detailCatalogueExtras.json', '../features/parks/recoveredDetails.json', '../features/zoningCatalogue/buildingPrograms.json', '../features/zoningCatalogue/parkPrograms.json', '../features/zoningCatalogue/districtRules.json']) {
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

test('only explicitly registered catalogue modules are packed; other plugin data is preserved', () => {
  const plugin = packedCatalogue();
  assert.equal(plugin.apply, 'build');
  assert.equal(plugin.enforce, 'post');
  assert.equal(plugin.transform('', '/app/src/data/future-unregistered.json'), null);
  assert.equal(plugin.transform('', '/app/src/data/buildingArchetypes.json?raw'), null);
  assert.notEqual(plugin.transform('', resolve('src/data/archetypeReferenceAvailability.json')), null);
  assert.notEqual(plugin.transform('', resolve('src/data/legoFamilySignatures.json')), null);
  assert.notEqual(plugin.transform('', resolve('src/data/validationCatalogue.json')), null);
  assert.notEqual(plugin.transform('', resolve('src/features/parks/recoveredDetails.json')), null);
  assert.notEqual(plugin.transform('', resolve('src/features/zoningCatalogue/buildingPrograms.json')), null);
  assert.equal(plugin.transform('', '/app/src/features/parks/recoveredDetails.json?raw'), null);
});


test('packing preserves signed zero, spaces and escaped quotes inside authored values', async () => {
  const source = JSON.stringify({ label: 'two words with "quoted" detail', offset: [-1, 0] }).replace('[-1,0]', '[-1,-0]');
  const module = packCatalogue(source).replace('three/examples/jsm/libs/fflate.module.js', inflater);
  const decoded = await import(`data:text/javascript,${encodeURIComponent(module)}`);
  assert.deepEqual(decoded.default, JSON.parse(source));
  assert.ok(Object.is(decoded.default.offset[1], -0));
});
