import { describe, expect, it } from 'vitest';
import { CANONICAL_CHOICES } from './canonicalCatalogue';
import { canonicalBuildingAsset, canonicalBuildingById } from './canonicalBuildingPlacement';
import { assetForZone, placeAsset, placementPlanRequest, placementProperties } from './catalogue';

describe('canonical building placement', () => {
  it('supplies usable initial dimensions without claiming reviewed geometry', () => {
    for (const choice of CANONICAL_CHOICES.filter(c => c.domain === 'building')) {
      for (const variant of choice.option.variants ?? [undefined]) {
        const asset = canonicalBuildingAsset({ choice, variant });
        expect(Number.isFinite(asset.width) && asset.width >= asset.minWidth).toBe(true);
        expect(Number.isFinite(asset.depth) && asset.depth >= asset.minDepth).toBe(true);
        expect(asset.nativeDimensions).toBeUndefined();
        expect(asset.properties.native_home_plot).toBeUndefined();
        expect(placementPlanRequest(asset, asset.width, asset.depth)).toBeNull();
        expect(canonicalBuildingById(asset.id)).toBe(asset);
      }
    }
  });
  it('does not promise fixed native proportions after the authored height changes', () => {
    const native = placeAsset('infill_home');
    const properties = { ...placementProperties(native), development_height_override_m: 12 };
    expect(assetForZone({ properties })?.reshapeMode).toBe('authored_footprint');
    expect(assetForZone({ properties })?.model.variantId).toBe(native.model.variantId);
  });
  it('restores selected identity after JSON persistence and does not keep another native asset after a type change', () => {
    const choice = CANONICAL_CHOICES.find(c => c.option.id === 'brownstone_rowhouse_frontage')!;
    const variant = choice.option.variants![1];
    const asset = canonicalBuildingAsset({ choice, variant });
    const properties = JSON.parse(JSON.stringify(placementProperties(asset)));
    expect(assetForZone({ properties })?.model.variantId).toBe(variant.id);
    expect(assetForZone({ properties: { ...properties, pick_place_asset: 'infill_home' } })?.id).toBe(asset.id);
    expect(canonicalBuildingById('canonical-building:missing:unknown')).toBeUndefined();
  });
});
