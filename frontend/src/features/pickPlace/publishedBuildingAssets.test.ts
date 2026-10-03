import { describe, expect, it } from 'vitest';
import { CATALOGUE_BUILDING_ASSETS, PUBLISHED_BUILDING_ASSETS } from './publishedBuildingAssets';
import { CATALOGUE_ASSETS, validateRegistry } from './assetRegistry';
import { placementPlanRequest } from './catalogue';

describe('published building catalogue', () => {
  it('preserves approved entries in the release registry', () => {
    for (const asset of PUBLISHED_BUILDING_ASSETS) {
      expect(CATALOGUE_BUILDING_ASSETS.find(row => row.id === asset.id)).toMatchObject({ model: asset.model, readiness: 'ready' });
      expect(asset.readiness).toBe('ready');
      expect(asset.label).not.toContain('trial');
    }
  });
  it('keeps unpublished local pilots out of the release catalogue', () => {
    const pilots = CATALOGUE_BUILDING_ASSETS.filter(asset => asset.readiness === 'pilot');
    for (const pilot of pilots) expect(PUBLISHED_BUILDING_ASSETS.some(asset => asset.id === pilot.id)).toBe(false);
    expect(PUBLISHED_BUILDING_ASSETS).toEqual(CATALOGUE_BUILDING_ASSETS.filter(asset => asset.readiness === 'ready'));
    // Local trial discovery is tested separately from release approval.
    for (const pilot of pilots.filter(asset => asset.id.startsWith('clay_mass_timber') || asset.id.startsWith('clay_parisian'))) {
      expect(CATALOGUE_ASSETS.find(row => row.id === pilot.id)).toMatchObject({ model: pilot.model, readiness: 'pilot' });
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
    expect(PUBLISHED_BUILDING_ASSETS.find(asset => asset.id === 'trial_postwar_bungalow')?.reshapeMode).toBe('repeat_native');
    expect(PUBLISHED_BUILDING_ASSETS.find(asset => asset.id === 'trial_edwardian_foursquare')?.reshapeMode).toBe('repeat_native');
    expect(PUBLISHED_BUILDING_ASSETS.find(asset => asset.id === 'trial_sandstone_civic')?.reshapeMode).toBe('fixed_native');
  });
});
