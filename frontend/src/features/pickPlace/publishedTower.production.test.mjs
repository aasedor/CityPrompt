import { beforeAll, describe, expect, it } from 'vitest';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';

const towerId = 'clay_twisting_glass_sky_garden_tower';
const choiceId = 'building:glass_tower_podium_modern:glass_tower_twisted';
// Explicitly authorized additions after the original tower-only release.
// Keep the original fingerprints below unchanged for every older placement.
const approvedBuildingIds = [
  'claude_climbing_crucible_v004', 'claude_climbing_overhang_v007', 'claude_climbing_reef_v009',
  'claude_sandstone_clock_tower_v006', 'claude_fire_station_v010', 'claude_hospital_v006',
  'claude_student_residence_v004',
];
const digest = values => createHash('sha256').update([...values].sort().join('\n')).digest('hex');

// These are the source-roster fingerprints recorded before this additive
// release. They protect every existing saved/discovery ID in both profiles.
const previousProfiles = [
  { trial: false, count: 186,
    choices: 'f4a0ac377529cb55ff14e062068734c810fa3cadb039e36ac0d2cf6d1814cfd0',
    placements: '271be42d3c380d28d1a89112a6cb4db0f1fd386100893eb24092cc1fc4e61c2f' },
  { trial: true, count: 191,
    choices: '8bca49bc745b0f590edfe9ea3d5e7d60ea3320ec71898a62559a62fd84d20287',
    placements: '2ec579c6dc5d965c2c2883dd20f248d90e9952ec7c64a295d32f3d551d9eed43' },
];

function productionCatalogue(trial) {
  // Bundle the real consumers with production constants in native Node. No
  // runtime profile or external environment file is read by this build.
  const output = execFileSync(process.execPath, ['--input-type=module', '-e', `
    import { build } from 'esbuild';
    import path from 'node:path';
    const result = await build({
      stdin: { contents: ${JSON.stringify(`
        import { CLASSROOM_CHOICES } from './canonicalCatalogue';
        import { CATALOGUE_ASSETS, CLAUDE_FIVE_TRIAL_ASSETS, validateRegistry } from './assetRegistry';
        import { assetForZone, placementProperties } from './catalogue';
        import { storeyProgramSupports } from './buildingStoreyProgram';
        import { hasFixedBuildingFootprint } from './fixedBuildingFootprint';
        const tower = CATALOGUE_ASSETS.find(asset => asset.id === '${towerId}');
        const saved = tower && JSON.parse(JSON.stringify({ properties: placementProperties(tower) }));
        console.log(JSON.stringify({
          choices: CLASSROOM_CHOICES.map(choice => ({ id: choice.id, placements: choice.placements.map(asset => asset.id) })),
          tower,
          savedId: saved && assetForZone(saved)?.id,
          fixedFootprint: hasFixedBuildingFootprint(tower),
          supportedHeights: tower?.storeyProgram && [
            [20, 79.7], [30, 113.7], [39, 144.3], [40, 147.7], [41, 151.1],
          ].map(([storeys, height]) => storeyProgramSupports(tower.storeyProgram, storeys, height)),
          claudeTrialCount: CLAUDE_FIVE_TRIAL_ASSETS.length,
          registryErrors: validateRegistry(CATALOGUE_ASSETS),
        }));
      `)}, resolveDir: path.resolve('src/features/pickPlace'), loader: 'ts' },
      bundle: true, write: false, treeShaking: true, platform: 'node', format: 'esm',
      tsconfig: path.resolve('tsconfig.json'),
      define: { 'import.meta.env': '{}', 'import.meta.env.DEV': 'false',
        'import.meta.env.PROD': 'true', 'import.meta.env.MODE': '"production"',
        'import.meta.env.VITE_CLAUDE_FIVE_TRIAL': ${JSON.stringify(JSON.stringify(String(trial)))} },
    });
    await import('data:text/javascript;base64,' + Buffer.from(result.outputFiles[0].text).toString('base64'));
  `], { encoding: 'utf8' });
  return JSON.parse(output);
}

describe('published native twisting tower in production', () => {
  const profiles = new Map();
  beforeAll(() => {
    for (const { trial } of previousProfiles) profiles.set(trial, productionCatalogue(trial));
  });

  it.each(previousProfiles)('discovers and reopens only native40 with Claude trial=$trial', ({ trial }) => {
    const profile = profiles.get(trial);
    expect(profile.choices.filter(choice => choice.id === choiceId)).toEqual([
      { id: choiceId, placements: [towerId] },
    ]);
    expect(profile.tower).toMatchObject({ id: towerId, readiness: 'ready', reshapeMode: 'fixed_native',
      model: { variantId: 'glass_tower_twisted', revision: 'glass-tower-twisted-clay-v005', method: 'RLASM 6.1' },
      storeyProgram: { mode: 'fixed_authored_assembly', nativeStoreys: 40, minStoreys: 40, maxStoreys: 40,
        podiumStoreys: 40, repeatedStoreyHeightM: 0, roofHeightM: 0 } });
    expect(profile.tower.storeyProgram.supportedStoreys).toBeUndefined();
    expect(profile.tower.nativeDimensions).toEqual([43.4902229309082, 44.02606964111328, 147.6999969482422]);
    expect(profile.supportedHeights).toEqual([false, false, false, true, false]);
    expect(profile.fixedFootprint).toBe(true);
    expect(profile.savedId).toBe(towerId);
    expect(profile.registryErrors).toEqual([]);
  });

  it.each(previousProfiles)('preserves the previous $count choices with Claude trial=$trial', expected => {
    const profile = profiles.get(expected.trial);
    const additions = profile.choices.filter(choice => choice.placements.some(id => approvedBuildingIds.includes(id)));
    expect(additions.flatMap(choice => choice.placements).sort()).toEqual([...approvedBuildingIds].sort());
    const previous = profile.choices.filter(choice => choice.id !== choiceId && !additions.includes(choice));
    expect(previous).toHaveLength(expected.count);
    expect(digest(previous.map(choice => choice.id))).toBe(expected.choices);
    expect(digest(previous.flatMap(choice => choice.placements))).toBe(expected.placements);
    expect(profile.claudeTrialCount).toBe(expected.trial ? 5 : 0);
  });
});
