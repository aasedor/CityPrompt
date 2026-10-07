import { describe, expect, it } from 'vitest';
import { assetForZone, placeAsset, placementProperties } from './catalogue';
import { nativeBuildingContract, nativeBuildingUrl } from './nativeBuildingContract';
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
});
