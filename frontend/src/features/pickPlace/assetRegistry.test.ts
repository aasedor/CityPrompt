import { describe, expect, it } from 'vitest';
import { CATALOGUE_ASSETS, LOCAL_STREET_ASSET, browseAssets, validateRegistry } from './assetRegistry';
import { assetForZone, placeAsset, placementProperties } from './catalogue';
import { CALGARY_LOCAL_PLACEMENT, CALGARY_LOCAL_WIDTH_M, isCalgaryLocalRoute } from './streetPlacement';

describe('placeable asset registry', () => {
  it('rejects duplicate identities, incompatible categories and mismatched variants', () => {
    expect(validateRegistry(CATALOGUE_ASSETS)).toEqual([]);
    expect(validateRegistry([...CATALOGUE_ASSETS, CATALOGUE_ASSETS[0]])).toContain('Duplicate or empty asset ID: infill_home');
    expect(validateRegistry([{ ...LOCAL_STREET_ASSET, calgaryGuide: { groupId: 'detached', basis: 'form_reference' } }])).toContain('Invalid Calgary group: calgary_local_street');
    expect(validateRegistry([{ ...placeAsset('infill_home'), model: { variantId: 'wrong', revision: null, method: 'test' } }])).toContain('Variant mismatch: infill_home');
  });
  it('searches Calgary districts and purpose without promoting candidates or retired assets', () => {
    expect(browseAssets('R-C1').map(a => a.id)).toEqual(['infill_home', 'craftsman_bungalow', 'trial_postwar_bungalow', 'trial_edwardian_foursquare', 'clay_rammed_earth_infill']);
    expect(browseAssets('', 'local').map(a => a.id)).toEqual(['calgary_local_street', 'yield_street_street']);
    const candidate = { ...LOCAL_STREET_ASSET, id: 'candidate', readiness: 'candidate' as const };
    const retired = { ...candidate, id: 'retired', readiness: 'retired' as const };
    expect(browseAssets('', '', [candidate, retired])).toEqual([]);
  });
  it('reopens legacy and newly stamped placements with the same exact design', () => {
    for (const id of ['infill_home', 'craftsman_bungalow', 'neighbourhood_park']) {
      const asset = placeAsset(id);
      const legacy = { properties: { ...asset.properties, pick_place_asset: id } };
      const saved = JSON.parse(JSON.stringify({ properties: placementProperties(asset, 1042) }));
      expect(assetForZone(legacy)).toBe(asset);
      expect(assetForZone(saved)).toBe(asset);
      expect(saved.properties).toMatchObject({ ...legacy.properties, pick_place_definition_version: 1, terrain_elevation_m: 1042 });
    }
    expect(assetForZone({ properties: { pick_place_asset: 'unknown' } })).toBeUndefined();
    expect(() => placeAsset('unknown')).toThrow('Unknown placeable asset');
  });
  it('keeps the existing street identity and section for saved routes', () => {
    expect(CALGARY_LOCAL_PLACEMENT).toBe(LOCAL_STREET_ASSET);
    expect(CALGARY_LOCAL_WIDTH_M).toBe(16);
    expect(isCalgaryLocalRoute({ zone_type: 'road', properties: LOCAL_STREET_ASSET.properties })).toBe(true);
  });
});
