import type { PlaceAsset } from './assetRegistry';

export type ReviewedEntrance = NonNullable<PlaceAsset['entranceSnap']> & { fixedNative?: boolean };

/** Runtime measurements are separate from generated catalogue cards. An exact
 * revision must match before a new asset inherits a measured entrance.
 * Evidence: CLASSROOM_CATALOGUE_PILOT_2026-09-22.md. */
export function reviewedEntranceForAsset(asset: PlaceAsset): ReviewedEntrance | undefined {
  if (asset.entranceSnap) return asset.entranceSnap;
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
