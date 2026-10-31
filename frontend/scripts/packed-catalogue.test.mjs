import { readFileSync } from 'node:fs';
import { performance } from 'node:perf_hooks';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { test } from 'node:test';
import assert from 'node:assert/strict';
import ts from 'typescript';
import { deflateSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import { minify } from 'terser';
import { packCatalogue, packedCatalogue, productionStarter } from './packed-catalogue.mjs';

const inflater = pathToFileURL(resolve('node_modules/three/examples/jsm/libs/fflate.module.js')).href;

for (const [filename, minimumSaving] of [['buildingArchetypes.json', 20000], ['nativeStreetPilots.json', 4000], ['openSpaceArchetypes.json', 8000]]) {
  test(`${filename}: production transport recovers bridge headroom without changing catalogue values`, async () => {
    const path = resolve('src/data', filename), source = readFileSync(path, 'utf8');
    const module = packedCatalogue().transform('', path).code.replace('three/examples/jsm/libs/fflate.module.js', inflater);
    const decoded = await import(`data:text/javascript,${encodeURIComponent(module)}`);
    assert.deepEqual(decoded.default, JSON.parse(source));
    const minified = await minify(module, { module: true, compress: { passes: 3 } });
    const runtime = await import(`data:text/javascript;base64,${Buffer.from(minified.code).toString('base64')}`);
    assert.deepEqual(runtime.default, JSON.parse(source));
    assert.ok(module.length < packCatalogue(source).length - minimumSaving, 'Recover bundle space through lossless transport, retaining every catalogue field');
  });
}

test('denser transport retains UTF8, signed zero and short final binary blocks', async () => {
  for (let length = 0; length < 24; length++) {
    const source = JSON.stringify({ label: 'é — "quoted" '+ 'abcdefghijk'.slice(0, length % 11).repeat(length), offset: [-1, 0] }).replace('[-1,0]', '[-1,-0]');
    const module = packCatalogue(source, { encoding: 'z85' }).replace('three/examples/jsm/libs/fflate.module.js', inflater);
    const minified = await minify(module, { module: true, compress: { passes: 3 } });
    const decoded = await import(`data:text/javascript,${encodeURIComponent(minified.code)}`);
    assert.deepEqual(decoded.default, JSON.parse(source));
    assert.ok(Object.is(decoded.default.offset[1], -0));
  }
});

test('unused denser transport is eliminated with its decoding work', async () => {
  const source = readFileSync(resolve('src/data/nativeStreetPilots.json'), 'utf8');
  const module = packCatalogue(source, { encoding: 'z85' }).replace('export default ', 'const unused = ');
  const result = await minify(module + '\nexport const ready = true;', { module: true, compress: { passes: 3 } });
  assert.ok(result.code.length < 1024);
});

test('production minification removes only unused catalogue decoding and preserves used bridge values', async () => {
  const source = readFileSync(resolve('src/data/nativeBridgePilots.json'), 'utf8');
  const module = packCatalogue(source).replace('three/examples/jsm/libs/fflate.module.js', inflater);
  const options = { module: true, compress: { passes: 3 } };
  const used = await minify(module, options);
  const decoded = await import(`data:text/javascript;base64,${Buffer.from(used.code).toString('base64')}`);
  assert.deepEqual(decoded.default, JSON.parse(source));
  const unused = await minify(module.replace('export default ', 'const unused = ') + '\nexport const ready = true;', options);
  assert.ok(unused.code.length < 1024, 'An unreferenced registry must not retain its compressed data or decoding work');
});

for (const relative of [
  'data/cataloguePlanningHistory.json', 'data/catalogueTeaching.json',
  'data/localTeachingBuildings.json', 'data/classroomStarter.json',
  'data/buildingPlacementEdges.json', 'data/catalogueHeroImages.json',
  'data/claudeAssetLocalTrial.json',
  'features/legoAssembly/buildingOnlyContracts.json',
  'features/parks/curbBulbContracts.json', 'features/parks/calgarySafetyCatalogue.json',
  'features/zoningCatalogue/parkUseRules.json',
  'features/pickPlace/publicRealmOwnershipContracts.json',
  'components/viewer/globe/publicRealmTrialAssets.json',
  'data/archetypeVisualSystem.json', 'data/catalogueOctober2026.json',
  'data/claudeBuildingRelease.json', 'data/claudeFiveTrial.json',
  'data/courtOnlySports.json',
  'data/finalFiveBuildingBatch.json', 'data/flexibleParks.json',
  'data/localTowerStoreyPrograms.json', 'data/neighborhoodParkV0StickerKit.json',
  'data/parkadeFamilyTrial.json', 'data/stickerMethodPilots.json',
  'data/transportStandardEntries.json', 'data/aiRenderStylePresets.json',
  'data/streetViewStylePresets.json',
  'features/policyPlans/data/beltlinePlanIndex.json',
  'features/policyPlans/data/localPlanIndex.json',
  'features/referenceLayers/calgaryBylawCatalogue.json',
]) {
  test(`${relative}: combined handoff metadata packs without changing any field`, async () => {
    const path = resolve('src', relative);
    const source = readFileSync(path, 'utf8');
    const transformed = packedCatalogue().transform('', path);
    assert.notEqual(transformed, null);
    const module = transformed.code.replace('three/examples/jsm/libs/fflate.module.js', inflater);
    const decoded = await import(`data:text/javascript,${encodeURIComponent(module)}`);
    assert.deepEqual(decoded.default, JSON.parse(relative === 'data/classroomStarter.json' ? productionStarter(source) : source));
    assert.ok(module.length < JSON.stringify(JSON.parse(source)).length);
  });
}

test('production starter omits only local trials and exclusively trial-owned dependencies', () => {
  const source = JSON.stringify({ schema: 1, entries: [
    { placementId: 'published', status: 'ready', dependencies: ['shared', 'public'] },
    { placementId: 'trial', status: 'local-pilot-runtime-pending', dependencies: ['shared', 'private'] },
  ], dependencies: ['shared', 'public', 'private', 'unrelated'].map(id => ({ id, sha256: id })) });
  const before = JSON.parse(source), result = JSON.parse(productionStarter(source));
  assert.deepEqual(result.entries, [before.entries[0]]);
  assert.deepEqual(result.dependencies.map(dep => dep.id), ['shared', 'public', 'unrelated']);
  assert.deepEqual(JSON.parse(source), before);
});

test('extracted static registries preserve every original transport fact and render preset', () => {
  for (const [name, count, hash] of [
    ['transportStandardEntries.json', 56, '3b445ced12bcc0087b9f95e74632d72a8d1858d9d5273acca999ba8ca3a53749'],
    ['aiRenderStylePresets.json', 14, '138ff3588a9445559a4fef8188e2fe25e63711200a4539eeb669a4618cfb68d2'],
    ['streetViewStylePresets.json', 14, '38a24f8d56744a3c264dc756f1aedf19ab5bb40c8be9d88d98661bd9d8183ccf'],
  ]) {
    const original = JSON.parse(readFileSync(resolve('src/data', name), 'utf8'));
    assert.equal(original.length, count);
    assert.equal(createHash('sha256').update(JSON.stringify(original)).digest('hex'), hash);
  }
});

test('fixed public-realm packing preserves exact review gates, variants and native placement', async () => {
  const path = resolve('src/data/publicRealmRelease20261023.json');
  const source = readFileSync(path, 'utf8');
  const transformed = packedCatalogue().transform('', path);
  assert.notEqual(transformed, null);
  const module = transformed.code.replace('three/examples/jsm/libs/fflate.module.js', inflater);
  const decoded = await import(`data:text/javascript,${encodeURIComponent(module)}`);
  assert.deepEqual(decoded.default, JSON.parse(source));
  assert.ok(module.length < JSON.stringify(JSON.parse(source)).length * .55);
});

test('generated building packing preserves all entries and the exact ready-only export', async () => {
  const path = resolve('src/features/pickPlace/publishedBuildingAssets.ts');
  const source = readFileSync(path, 'utf8');
  const referenceCode = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext } }).outputText;
  const reference = await import(`data:text/javascript,${encodeURIComponent(referenceCode)}`);
  const transformed = packedCatalogue().transform('', path);
  assert.notEqual(transformed, null);
  const module = transformed.code.replace('three/examples/jsm/libs/fflate.module.js', inflater);
  const decoded = await import(`data:text/javascript,${encodeURIComponent(module)}`);
  assert.deepEqual(decoded.CATALOGUE_BUILDING_ASSETS, reference.CATALOGUE_BUILDING_ASSETS);
  assert.deepEqual(decoded.PUBLISHED_BUILDING_ASSETS, reference.PUBLISHED_BUILDING_ASSETS);
  assert.ok(module.length < referenceCode.length * .55);
});

test('building packing rejects changes to generated export semantics', async () => {
  const { packPublishedBuildingCatalogue } = await import('./packed-catalogue.mjs');
  assert.equal(typeof packPublishedBuildingCatalogue, 'function');
  const source = readFileSync(resolve('src/features/pickPlace/publishedBuildingAssets.ts'), 'utf8');
  assert.throws(() => packPublishedBuildingCatalogue(source.replace("asset.readiness === 'ready'", "asset.readiness === 'pilot'")), /generated building catalogue/i);
  assert.throws(() => packPublishedBuildingCatalogue(source + '\nexport const another = true;'), /generated building catalogue/i);
});

for (const filename of ['peopleCatalogue.json', 'inclusivePeopleCatalogue.json', 'peopleAppearancePreviews.json']) {
  test(`${filename}: production People packing preserves exact models, wardrobe and image locks`, async () => {
    const path = resolve('src/features/people', filename);
    const source = readFileSync(path, 'utf8');
    const transformed = packedCatalogue().transform('', path);
    assert.notEqual(transformed, null);
    const module = transformed.code.replace('three/examples/jsm/libs/fflate.module.js', inflater);
    const decoded = await import(`data:text/javascript,${encodeURIComponent(module)}`);
    assert.deepEqual(decoded.default, JSON.parse(source));
    assert.ok(module.length < JSON.stringify(JSON.parse(source)).length * 0.55);
  });
}

for (const filename of ['streetManual.json', 'nativeStreetModuleBounds.json', 'nativeBridgePilots.json']) {
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

test('packing creates smaller street output without regressing the previous building output', () => {
  for (const filename of ['nativeStreetPilots.json', 'buildingArchetypes.json']) {
    const source = readFileSync(resolve('src/data', filename), 'utf8');
    const canonical = source.replace(/("(?:\\.|[^"\\])*")|\s+/g, (_match, quoted) => quoted ?? '');
    const candidates = [8, 6].map(memLevel => deflateSync(Buffer.from(canonical), { level: 9, memLevel }));
    const smallest = candidates.reduce((a, b) => b.length < a.length ? b : a);
    const packed = packCatalogue(source).match(/atob\(("[A-Za-z0-9+/=]+")\)/);
    assert.ok(packed, filename);
    const emitted = Buffer.from(JSON.parse(packed[1]), 'base64');
    assert.ok(emitted.length <= smallest.length, filename);
    if (filename === 'nativeStreetPilots.json') assert.ok(emitted.length < smallest.length * 0.99, 'Create headroom for account security without relaxing the bundle budget');
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
