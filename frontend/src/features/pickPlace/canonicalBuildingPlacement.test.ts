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
        expect(asset.properties.native_home_plot).not.toBe(true);
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
    // Exact variants have separate cards. Choose the sibling whose variant
    // is absent from the first card, so restore cannot stop at its parent.
    const siblings = CANONICAL_CHOICES.filter(c => c.option.id === 'calgary_modern_infill_house');
    expect(siblings.length).toBeGreaterThan(1);
    const choice = siblings[1];
    const variant = choice.option.variants![0];
    const asset = canonicalBuildingAsset({ choice, variant });
    const properties = JSON.parse(JSON.stringify(placementProperties(asset)));
    expect(assetForZone({ properties })?.model.variantId).toBe(variant.id);
    expect(assetForZone({ properties: { ...properties, pick_place_asset: 'infill_home' } })?.id).toBe(asset.id);
    expect(canonicalBuildingById('canonical-building:missing:unknown')).toBeUndefined();
  });
});
