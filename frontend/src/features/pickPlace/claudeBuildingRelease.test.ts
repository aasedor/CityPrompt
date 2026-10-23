import { afterEach, describe, expect, it, vi } from 'vitest';
import { CATALOGUE_BUILDING_ASSETS, PUBLISHED_BUILDING_ASSETS } from './publishedBuildingAssets';
import { CATALOGUE_ASSETS } from './assetRegistry';
import cohort from '@/data/claudeBuildingRelease.json';

describe('finite Claude architectural-clay building release', () => {
  afterEach(() => { vi.unstubAllEnvs(); vi.resetModules(); });
  it('preserves the exact warehouse pilot identity with canonical native dimensions', () => {
    const warehouse = CATALOGUE_BUILDING_ASSETS.find(asset => asset.id === 'claude_trial_cmu_dock_warehouse');
    expect(warehouse).toMatchObject({
      model: { variantId: 'cmu_dock_utilitarian', revision: 'clay-cmu-dock-warehouse-clay-v006' },
      reshapeMode: 'fixed_native',
      width: 60,
      depth: 48,
    });
    expect(warehouse?.nativeDimensions?.[0]).toBe(57);
    expect(warehouse?.properties.validation_native_url).toBeUndefined();
  });

  it('registers staged members of the finite eighteen-building cohort at native scale', () => {
    expect(cohort.entries).toHaveLength(18);
    const staged = CATALOGUE_BUILDING_ASSETS.filter(asset => asset.id.startsWith('claude_trial_'));
    expect(staged.length).toBeGreaterThan(0);
    for (const asset of staged) {
      const row = cohort.entries.find(candidate => candidate.asset_id === asset.id);
      expect(row, asset.id).toBeDefined();
      expect(asset, row!.candidate).toMatchObject({
        model: { variantId: row!.variant_id, revision: row!.candidate, method: 'RLASM 6.1' },
        reshapeMode: 'fixed_native',
        properties: { development_archetype_id: row!.archetype_id },
      });
      expect(asset?.properties.native_home_plot).toBeUndefined();
    }
    for (const [revision, floors] of [['clay-slab-balcony-tower-clay-v007', 13], ['clay-energy-centre-clay-v010', 2]]) {
      const asset = CATALOGUE_BUILDING_ASSETS.find(candidate => candidate.model.revision === revision);
      if (asset) expect(asset.properties.floor_count).toBe(floors);
    }
  });

  it('keeps unpublished exact Claude candidates out of the release roster in test/production mode', () => {
    const unpublished = CATALOGUE_BUILDING_ASSETS.filter(asset => asset.id.startsWith('claude_trial_') && asset.readiness === 'pilot');
    for (const asset of unpublished) {
      expect(PUBLISHED_BUILDING_ASSETS.some(row => row.id === asset.id)).toBe(false);
      expect(CATALOGUE_ASSETS.some(row => row.id === asset.id)).toBe(false);
    }
  });

  it('publishes every reviewed release member once through the canonical production catalogue', () => {
    for (const member of cohort.entries) {
      const matches = CATALOGUE_BUILDING_ASSETS.filter(asset => asset.id === member.asset_id);
      expect(matches, member.candidate).toHaveLength(1);
      expect(matches[0].readiness, member.candidate).toBe('ready');
      expect(PUBLISHED_BUILDING_ASSETS.filter(asset => asset.id === member.asset_id), member.candidate).toHaveLength(1);
      expect(CATALOGUE_ASSETS.filter(asset => asset.id === member.asset_id), member.candidate).toHaveLength(1);
    }
  });

  it('uses one canonical seeded warehouse binding instead of the previous DEV fixture', async () => {
    vi.stubEnv('DEV', true);
    vi.stubEnv('MODE', 'development');
    vi.resetModules();
    const registry = await import('./assetRegistry');
    const assets = registry.CATALOGUE_ASSETS.filter(asset => asset.id === 'claude_trial_cmu_dock_warehouse');
    expect(assets).toHaveLength(1);
    expect(assets[0].properties.validation_native_url).toBeUndefined();
    expect(assets[0].properties.validation_fixed_fixture).toBeUndefined();
    expect(assets[0].model.revision).toBe('clay-cmu-dock-warehouse-clay-v006');
    const catalogue = await import('./canonicalCatalogue');
    expect(catalogue.CANONICAL_CHOICES.filter(choice => choice.placements.some(asset => asset.id === assets[0].id))).toHaveLength(1);
  });
});
