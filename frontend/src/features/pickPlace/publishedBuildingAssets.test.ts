import { describe, expect, it } from 'vitest';
import { PUBLISHED_BUILDING_ASSETS } from './publishedBuildingAssets';
import { CATALOGUE_ASSETS, validateRegistry } from './assetRegistry';
import { placementPlanRequest } from './catalogue';

describe('published building catalogue', () => {
  it('includes all three approved entries in the default catalogue', () => {
    for (const asset of PUBLISHED_BUILDING_ASSETS) {
      expect(CATALOGUE_ASSETS).toContain(asset);
      expect(asset.readiness).toBe('ready');
      expect(asset.label).not.toContain('trial');
    }
  });
  it('uses valid categories, exact variants and plots larger than complete envelopes', () => {
    expect(validateRegistry(PUBLISHED_BUILDING_ASSETS)).toEqual([]);
    for (const asset of PUBLISHED_BUILDING_ASSETS) {
      expect(asset.width).toBeGreaterThan(asset.nativeDimensions![0] + 2.9);
      expect(asset.depth).toBeGreaterThan(asset.nativeDimensions![1] + 2.9);
      expect(placementPlanRequest(asset, asset.width, asset.depth)).toMatchObject({
        archetype_id: asset.model.variantId, target_floors: asset.properties.floor_count,
        allow_forced_fit: false,
      });
    }
  });
  it('repeats whole homes and preserves the civic landmark', () => {
    expect(PUBLISHED_BUILDING_ASSETS.map(asset => asset.reshapeMode)).toEqual(['repeat_native', 'repeat_native', 'fixed_native']);
  });
});
