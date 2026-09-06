import { describe, expect, it } from 'vitest';
import { LOCAL_TRIO_ASSETS } from './localTrioAssets';
import { CATALOGUE_ASSETS, validateRegistry } from './assetRegistry';
import { placementPlanRequest } from './catalogue';

describe('explicit local building trio', () => {
  it('keeps trial entries out of the default catalogue', () => {
    expect(CATALOGUE_ASSETS.some(asset => asset.id.startsWith('trial_'))).toBe(false);
  });
  it('uses valid categories, exact variants and plots larger than complete envelopes', () => {
    expect(validateRegistry(LOCAL_TRIO_ASSETS)).toEqual([]);
    for (const asset of LOCAL_TRIO_ASSETS) {
      expect(asset.width).toBeGreaterThan(asset.nativeDimensions![0] + 2.9);
      expect(asset.depth).toBeGreaterThan(asset.nativeDimensions![1] + 2.9);
      expect(placementPlanRequest(asset, asset.width, asset.depth)).toMatchObject({
        archetype_id: asset.model.variantId, target_floors: asset.properties.floor_count,
        allow_forced_fit: false,
      });
    }
  });
  it('repeats whole homes and preserves the civic landmark', () => {
    expect(LOCAL_TRIO_ASSETS.map(asset => asset.reshapeMode)).toEqual(['repeat_native', 'repeat_native', 'fixed_native']);
  });
});
