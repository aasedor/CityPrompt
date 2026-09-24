import type { PlaceAsset } from './assetRegistry';

export type ReviewedEntrance = NonNullable<PlaceAsset['entranceSnap']> & { fixedNative?: boolean };

/** Runtime measurements are separate from generated catalogue cards. An exact
 * revision must match before a new asset inherits a measured entrance.
 * Evidence: CLASSROOM_CATALOGUE_PILOT_2026-09-22.md. */
export function reviewedEntranceForAsset(asset: PlaceAsset): ReviewedEntrance | undefined {
  if (asset.entranceSnap) {
    if (asset.id === 'infill_home' && (asset.model.revision !== 'calgary-infill-flat-roof-minimal-clay-v006'
      || asset.model.variantId !== 'infill_flat_roof_minimal')) return undefined;
    return { ...asset.entranceSnap, ...(asset.reshapeMode === 'fixed_native' ? { fixedNative: true } : {}) };
  }
  if (asset.id === 'trial_postwar_bungalow' && asset.model.variantId === 'bungalow_postwar_ranch'
    && asset.model.revision === 'calgary-inner-city-bungalow-clay-v005' && asset.reshapeMode === 'fixed_native') {
    // Authored stair x=-.15; native GLB horizontal centre x=.019161701,
    // z=.639999866. Front stair toe z=8.664999962 becomes ENU y=-8.025.
    return { xM: -.169161701, yM: -8.025, widthM: 1.4, plotWidthM: 15, plotDepthM: 20, fixedNative: true };
  }
  if (asset.id === 'clay_beltline_brick_midrise'
    && asset.model.variantId === 'beltline_brick_modern'
    && asset.model.revision === 'calgary-beltline-mid-rise-clay-v003'
    && asset.reshapeMode === 'fixed_native') {
    // Front retail door centre x=-0.30; approach meets the complete native
    // support apron at y=-17.08, beyond the entrance canopy columns.
    return { xM: -.3, yM: -17.08, widthM: 1.8, plotWidthM: 39, plotDepthM: 39, fixedNative: true };
  }
  return undefined;
}
