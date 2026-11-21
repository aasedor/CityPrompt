import contracts from '@/features/legoAssembly/buildingOnlyContracts.json';
import type { CatalogueAsset, PlaceAsset } from './assetRegistry';

// Round outward to the editor's 0.1 m precision with 2 cm total fit tolerance.
const snugDimension = (metres: number) => Math.ceil((metres + .02) * 10) / 10;

export function hasBuildingOnlyFootprint(asset: CatalogueAsset): asset is PlaceAsset {
  return asset.kind==='object' && asset.zoneType==='building' && asset.reshapeMode==='fixed_native'
    && Boolean(asset.model.revision && Object.prototype.hasOwnProperty.call(contracts,asset.model.revision));
}

/** Outward 10cm input rounding and 2cm TOTAL numeric tolerance, no site setback.
 * Bounds include every retained step, podium and architectural projection. */
export function withBuildingOnlyFootprint(asset: CatalogueAsset): CatalogueAsset {
  if(!hasBuildingOnlyFootprint(asset)) return asset;
  const c=contracts[asset.model.revision as keyof typeof contracts];
  const nativeDimensions: [number,number,number]=[
    c.bounds.max[0]-c.bounds.min[0],c.bounds.max[2]-c.bounds.min[2],c.bounds.max[1]-c.bounds.min[1]];
  const [width,depth]=nativeDimensions.slice(0,2).map(snugDimension);
  return {...asset,definitionVersion:Math.max(2,asset.definitionVersion),width,depth,
    minWidth:width,minDepth:depth,nativeDimensions};
}

/** Use the retained model envelope when the plot has no role in changing the building's size. */
export function withCompactBuildingPlacement(asset: CatalogueAsset): CatalogueAsset {
  if (asset.kind !== 'object' || asset.zoneType !== 'building' || asset.reshapeMode !== 'fixed_native'
    || !asset.model.revision || asset.properties.native_plot_axes !== true || asset.properties.native_home_plot === true
    || asset.footprintProgram || (asset.storeyProgram && asset.storeyProgram.mode !== 'fixed_authored_assembly')) return asset;
  const [nativeWidth, nativeDepth] = asset.nativeDimensions ?? [];
  if (nativeWidth == null || nativeDepth == null || !Number.isFinite(nativeWidth) || !Number.isFinite(nativeDepth)
    || nativeWidth <= 0 || nativeDepth <= 0 || nativeWidth > asset.width || nativeDepth > asset.depth) return asset;
  const width = Math.min(asset.width, snugDimension(nativeWidth));
  const depth = Math.min(asset.depth, snugDimension(nativeDepth));
  return {
    ...asset,
    width,
    depth,
    minWidth: width,
    minDepth: depth,
    referenceLotAreaM2: asset.width * asset.depth,
  };
}
