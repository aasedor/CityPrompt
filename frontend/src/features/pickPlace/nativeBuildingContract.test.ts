import { describe, expect, it } from 'vitest';
import { assetForZone, placeAsset, placementProperties } from './catalogue';
import { nativeBuildingContract, nativeBuildingUrl } from './nativeBuildingContract';
import { isStandaloneNativeBuilding } from './validationNativeBuildingBinding';
import preserved from '@/data/savedModelRevisions.json';

const current = placeAsset('validation_minimalist_infill_brick_monolith');
describe('authored building identity and dimensions', () => {
  it('uses authored geometry rather than generic/stale height properties', () => {
    const properties = { ...placementProperties(current), height: 30, height_m: 6.4 };
    const contract = nativeBuildingContract({ properties })!;
    expect(contract.heightM).toBeCloseTo(10.68, 2);
    expect(contract.storeys).toBe(2);
    expect(contract.rigid).toBe(true);
    expect(properties.height).toBe(30);
    expect(placementProperties(current).height).toBe(contract.heightM);
    expect(placementProperties(current).building_geometry_basis).toBe('placement_plot');
  });
  it('binds the preserved revision without migrating the saved design', () => {
    const row = preserved.revisions[0];
    const properties = { ...placementProperties(current), pick_place_model_revision: row.revision, validation_native_url: undefined };
    const contract = nativeBuildingContract({ properties })!;
    expect(contract.heightM).toBeCloseTo(10.48, 2);
    expect(contract.asset.nativeDimensions).toEqual(row.nativeDimensions);
    expect(nativeBuildingUrl({ properties })).toBe(row.url);
    expect(assetForZone({ properties })?.model.revision).toBe(row.revision);
    expect(properties.validation_native_url).toBeUndefined();
  });
  it('does not silently substitute current bytes for an unknown saved revision', () => {
    const properties = { ...placementProperties(current), pick_place_model_revision: 'unknown-saved-revision' };
    expect(assetForZone({ properties })).toBeUndefined();
    expect(nativeBuildingUrl({ properties })).toBeUndefined();
  });
  it.each([
    ['london_crescent_terrace_bath_stone', 'london-crescent-terrace-bath-stone',
      'crescent-terrace-bath-stone-clay-v006', '705fc02b21d5704bf6b97a565b1c48df079b47d8d4f38f5304f5fb0d623b0284'],
    ['plus15_brutalist_concrete_office', 'brutalist_concrete_slab',
      'plus15-brutalist-concrete-office-clay-v006', '2c94066899b883c1dc1afc351006077e25e3fe3b76e509850e977b372bd28cc0'],
  ])('opens the exact %s model from its saved named revision', (id, variant, revision, sha256) => {
    const properties = {
      pick_place_asset: id,
      pick_place_model_revision: revision,
      development_selected_variant_id: variant,
    };
    expect(nativeBuildingUrl({ properties })).toBe('/model-revisions/' + sha256 + '.glb');
    expect(isStandaloneNativeBuilding({ properties })).toBe(true);
    const otherRevision = { ...properties, pick_place_model_revision: 'unavailable' };
    expect(nativeBuildingUrl({ properties: otherRevision })).toBeUndefined();
    expect(isStandaloneNativeBuilding({ properties: otherRevision })).toBe(false);
  });
  it.each([
    {floor_count:1,floors:1,height:7.34,height_m:7.34,development_height_override_m:7.34},
    {building_footprint_scale:0.85},
    {floor_count:3,floors:3,height:13.62,height_m:13.62,development_height_override_m:13.62},
    {building_footprint_scale:NaN},
  ])('uses the compiled house assembly instead of a mismatched native preview for %o', change=>{
    const properties={...placementProperties(placeAsset('validation_clapboard_north_end')),...change};
    expect(nativeBuildingUrl({properties})).toBeUndefined();
  });
});
