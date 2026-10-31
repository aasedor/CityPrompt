import type { PlaceAsset } from './assetRegistry';

/** A fixed GLB has no horizontal edit unless its exact family publishes a
 * reviewed footprint programme. Storey controls are a separate capability. */
export function hasFixedBuildingFootprint(asset?: PlaceAsset): boolean {
  const reviewedPlotBand = asset?.maxWidth != null && asset.maxDepth != null
    && asset.maxWidth > asset.minWidth && asset.maxDepth > asset.minDepth;
  return asset?.kind === 'object' && asset.zoneType === 'building'
    && asset.reshapeMode === 'fixed_native'
    && !reviewedPlotBand
    && (!asset.footprintProgram || asset.footprintProgram.editable === false);
}
