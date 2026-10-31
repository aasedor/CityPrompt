import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { productionRuntimeSourceText } from './runtime-release-source.mjs';

const registryPath = 'src/data/publicRealmRelease20261023.json';
const source = readFileSync(new URL('../src/data/publicRealmRelease20261023.json', import.meta.url), 'utf8');
const manifest = JSON.parse(source);
const urls = text => [...new Set([...text.matchAll(/\/(?:park|street)-kits\/claude-20261023\/[a-f0-9]{64}\.(?:glb|png|jpg)/g)].map(match => match[0]))].sort();
const projected = value => productionRuntimeSourceText(registryPath, JSON.stringify(value));

test('bridge receipts inventory complete profiles without escaped canonical-string phantom URLs', () => {
  const text = readFileSync(new URL('../src/data/nativeBridgeRelease.json', import.meta.url), 'utf8');
  const original = JSON.parse(text);
  const filtered = JSON.parse(productionRuntimeSourceText('src/data/nativeBridgeRelease.json', text));
  assert.equal(filtered.entries.length, 10);
  assert.ok(filtered.entries.every(entry=>!Object.hasOwn(entry,'profileCanonical')));
  assert.deepEqual(filtered.entries.map(entry=>entry.profile), original.entries.map(entry=>entry.profile));
  assert.equal(filtered.entries.reduce((sum,entry)=>sum+Object.keys(entry.profile.modules).length,0),34);
  assert.deepEqual(JSON.parse(text), original, 'Inventory projection never rewrites admission receipts');
  assert.deepEqual(JSON.parse(productionRuntimeSourceText('src\\data\\nativeBridgeRelease.json',text)),filtered);
  for (const malformed of [{...original,schema:'unknown'},{...original,entries:null},
    {...original,entries:[{profile:null,profileCanonical:'{}'}]}]) {
    assert.throws(()=>productionRuntimeSourceText('src/data/nativeBridgeRelease.json',JSON.stringify(malformed)),/Invalid native bridge receipt/);
  }
});

test('the exact production registry requires only the twelve approved model and thumbnail pairs', () => {
  const selected = manifest.models.filter(row => row.status === 'ready');
  assert.equal(selected.length, 12);
  const expected = selected.flatMap(row => [row.fixture.url, row.asset.thumbnail]).sort();
  assert.equal(new Set(expected).size, 24);
  const filtered = productionRuntimeSourceText(registryPath, source);
  assert.deepEqual(urls(filtered), expected);
  const decoded = JSON.parse(filtered);
  assert.deepEqual(decoded, { ...manifest, models: selected });
  for (const row of manifest.models.filter(row => row.status === 'prepared')) {
    assert.ok(!urls(filtered).includes(row.fixture.url));
  }
});

test('unrelated sources, similarly named files and source evidence stay unchanged', () => {
  for (const path of ['src/data/nativeParks.json', 'src/data/other/publicRealmRelease20261023.json',
    'src/data/publicRealmRelease20261024.json', 'src/data/publicRealmRelease20261023.json?raw']) {
    assert.equal(productionRuntimeSourceText(path, source), source);
  }
  assert.deepEqual(JSON.parse(productionRuntimeSourceText(registryPath.replaceAll('/', '\\'), source)),
    JSON.parse(productionRuntimeSourceText(registryPath, source)));
});

test('a ready row with pending, forged or malformed review/identity locks fails closed', () => {
  for (const mutate of [
    row => { row.visual_review.status = 'pending'; },
    row => { row.runtime_review.status = 'pending'; },
    row => { row.visual_review.evidence_sha256 = null; },
    row => { row.runtime_review.evidence_sha256 = null; },
    row => { row.visual_review.runtime_sha256 = '0'.repeat(64); },
    row => { row.runtime_review.runtime_sha256 = '0'.repeat(64); },
    row => { row.visual_review.scope = 'context_removal_only'; },
    row => { row.visual_review.unresolved_p0 = 1; },
    row => { row.visual_review.unresolved_p1 = 1; },
    row => { row.source_sha256 = null; },
    row => { row.review_sha256 = null; },
    row => { row.asset.model.revision = '0'.repeat(64); },
    row => { row.asset.properties.validation_native_url = row.fixture.url; },
    row => { row.fixture.dimensions[0] += 1; },
    row => { row.fixture = null; },
    row => { row.fixture.url = '/park-kits/claude-20261023/'+'0'.repeat(64)+'.glb'; },
    row => { row.asset.thumbnail = '/street-kits/claude-20261023/'+'0'.repeat(64)+'.png'; },
    row => { row.asset.properties.native_public_realm_url = '/wrong.glb'; },
  ]) {
    const data = structuredClone(manifest);
    mutate(data.models.find(row => row.status === 'ready'));
    assert.throws(() => projected(data), /Invalid production fixed public-realm/);
  }
});

test('disabled local trials stay excluded while approved retired revisions retain saved-scene dependencies', () => {
  const data = structuredClone(manifest);
  const row = data.models.find(row => row.status === 'ready');
  row.status = 'runtime_trial';
  row.runtime_review.status = 'pending';
  assert.ok(!urls(projected(data)).includes(row.fixture.url));
  row.status = 'retired';
  assert.throws(() => projected(data), /Invalid production fixed public-realm/);
  row.runtime_review.status = 'passed';
  assert.ok(urls(projected(data)).includes(row.fixture.url));
  assert.ok(urls(projected(data)).includes(row.asset.thumbnail));
});

test('unsupported registry schemas and malformed model/status lists fail closed', () => {
  for (const value of [{ ...manifest, schema: 'unknown' }, { ...manifest, release_id: 'unknown' }, { ...manifest, models: null },
    { ...manifest, models: [...manifest.models, { status: 'unknown' }] },
    { ...manifest, models: [...manifest.models, manifest.models.find(row => row.status === 'ready')] }]) {
    assert.throws(() => projected(value), /Invalid production fixed public-realm/);
  }
  assert.throws(() => productionRuntimeSourceText(registryPath, '{'), /JSON|position|property|Unexpected/);
});
