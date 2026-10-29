import contracts from '@/features/legoAssembly/buildingOnlyContracts.json';
import type { CatalogueAsset, PlaceAsset } from './assetRegistry';

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
  const [width,depth]=nativeDimensions.slice(0,2).map(value=>Math.ceil((value+.02)*10)/10);
  return {...asset,definitionVersion:Math.max(2,asset.definitionVersion),width,depth,
    minWidth:width,minDepth:depth,nativeDimensions};
}
