import contracts from '@/data/localTowerStoreyPrograms.json';
import type { CatalogueAsset, PlaceAsset } from './assetRegistry';

/** Local availability is independent from public catalogue approval. */
export function localTowerStoreyMetadata(asset: CatalogueAsset): PlaceAsset | undefined {
  if (asset.kind !== 'object' || asset.zoneType !== 'building') return undefined;
  const contract = contracts.programmes.find(row => row.assetId === asset.id
    && row.variantId === asset.model.variantId && row.sourceRevision === asset.model.revision);
  if (!contract) return undefined;
  return { ...asset, reshapeDescription: 'Move and rotate the complete building. Use Storeys to change its supported height; the plot keeps its size.', footprintProgram: {
    id: `${contract.storeyProgram.id}-native-footprint`, mode: 'uniform_horizontal_scale',
    nativeWidthM: contract.nativeWidthM, nativeDepthM: contract.nativeDepthM,
    minScale: 1, maxScale: 1, defaultScale: 1, step: 1, editable: false,
  }, storeyProgram: contract.storeyProgram as PlaceAsset['storeyProgram'] };
}
