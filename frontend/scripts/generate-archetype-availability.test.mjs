import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, copyFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

test('availability retains a street section from canonical transport data without a hero', () => {
  const root = mkdtempSync(join(tmpdir(), 'cityprompt-availability-'));
  try {
    const frontend = join(root, 'frontend');
    mkdirSync(join(frontend, 'scripts'), { recursive: true });
    const data = join(frontend, 'src/data');
    mkdirSync(data, { recursive: true });
    copyFileSync(new URL('./generate-archetype-availability.mjs', import.meta.url), join(frontend, 'scripts/generate-archetype-availability.mjs'));
    for (const name of ['buildingArchetypes', 'openSpaceArchetypes']) {
      writeFileSync(join(data, name + '.json'), JSON.stringify({ archetypes: [] }));
    }
    writeFileSync(join(data, 'streetPathArchetypes.json'), JSON.stringify({ archetypes: [
      { id: 'local', thumbnailUrl: '/archetypes/streets/local/hero.png' },
    ] }));
    writeFileSync(join(data, 'transportStandards.ts'), 'export {};');
    writeFileSync(join(data, 'transportStandardEntries.json'), JSON.stringify([
      { archetypeId: 'local', sectionSvgUrl: '/archetypes/streets/local/section.svg' },
    ]));
    writeFileSync(join(data, 'legoFamilySignatures.json'), JSON.stringify({ families: {} }));
    const images = join(frontend, 'public/archetypes/streets/local');
    mkdirSync(images, { recursive: true });
    writeFileSync(join(images, 'section.svg'), '<svg xmlns="http://www.w3.org/2000/svg"/>');
    const result = spawnSync(process.execPath, [join(frontend, 'scripts/generate-archetype-availability.mjs')], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    const availability = JSON.parse(readFileSync(join(data, 'archetypeReferenceAvailability.json'), 'utf8'));
    assert.deepEqual(availability.streetIds, ['local']);
    assert.deepEqual(availability.domains.street.entries.local.availableUrls, ['/archetypes/streets/local/section.svg']);
    assert.deepEqual(availability.completeStreetIds, [], 'a section must not conceal a missing hero');
  } finally {
    assert.equal(dirname(root), resolve(tmpdir()));
    assert.match(basename(root), /^cityprompt-availability-/);
    rmSync(root, { recursive: true, force: true });
  }
});
