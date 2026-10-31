import { describe, expect, it, vi } from 'vitest';
import { CATALOGUE_BUILDING_ASSETS } from './publishedBuildingAssets';
import roster from '@/data/claudeBuildingRelease.json';

describe('approved practical building release', () => {
  it.each([
    ['claude_hospital_v006', 'clay-braced-frame-hospital-clay-v006', 'regional_hospital_contemporary_teaching', 9, 76, 68],
    ['claude_student_residence_v004', 'clay-student-residence-tower-clay-v004', 'contemporary_curtainwall_biophilic', 12, 37, 33],
  ] as const)('offers %s without dragging a surrounding road scene into the plot', (id, revision, variantId, floors, maxWidth, maxDepth) => {
    const asset = CATALOGUE_BUILDING_ASSETS.find(row => row.id === id);
    expect(asset).toMatchObject({ readiness: 'ready', reshapeMode: 'fixed_native',
      model: { revision, variantId }, properties: { floor_count: floors } });
    expect(asset!.width).toBeLessThan(maxWidth);
    expect(asset!.depth).toBeLessThan(maxDepth);
    expect(asset!.width - asset!.nativeDimensions![0]).toBeGreaterThanOrEqual(3);
    expect(asset!.depth - asset!.nativeDimensions![1]).toBeGreaterThanOrEqual(3);
    expect(roster.entries.some(row => row.asset_id === id && row.candidate === revision)).toBe(true);
  });

  it('binds the corrected fire station to its exact reviewed native assembly', () => {
    const asset = CATALOGUE_BUILDING_ASSETS.find(row => row.id === 'claude_fire_station_v010');
    expect(asset).toMatchObject({
      readiness: 'ready', reshapeMode: 'fixed_native',
      model: { revision: 'clay-cantilever-fire-station-clay-v010', variantId: 'fire_cantilevered_modern' },
      properties: { development_archetype_id: 'modern_fire_station', floor_count: 2 },
    });
    expect(asset!.width).toBeLessThan(54);
    expect(asset!.depth).toBeLessThan(45);
    expect(asset!.width - asset!.nativeDimensions![0]).toBeGreaterThanOrEqual(3);
    expect(asset!.depth - asset!.nativeDimensions![1]).toBeGreaterThanOrEqual(3);
    expect(roster.entries.find(row => row.asset_id === asset!.id)?.model_sha256)
      .toBe('acf653e6ad58c420228fab2447ccddc106af7833f814c45431637e1b0180e2be');
  });

  it('makes the approved fire station available in production discovery', async () => {
    vi.stubEnv('DEV', false); vi.stubEnv('MODE', 'production'); vi.resetModules();
    try {
      const { CATALOGUE_ASSETS } = await import('./assetRegistry');
      expect(CATALOGUE_ASSETS.filter(row => row.id === 'claude_fire_station_v010')).toHaveLength(1);
    } finally { vi.unstubAllEnvs(); vi.resetModules(); }
  });
});
