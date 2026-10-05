import revisions from '@/data/savedModelRevisions.json';
import type { SiteZoneProperties } from '@/types';
import type { PlaceAsset } from './assetRegistry';

/** Saved revision identity wins over today's catalogue. Never guess an upgrade. */
export function savedModelRevision(asset: PlaceAsset, properties: SiteZoneProperties): PlaceAsset | undefined {
  const saved = properties.pick_place_model_revision;
  if (!saved || saved === asset.model.revision) return asset;
  const record = revisions.revisions.find(row => row.assetId === asset.id && row.revision === saved
    && row.variantId === asset.model.variantId);
  if (!record) return undefined;
  return { ...asset, model: { ...asset.model, revision: record.revision },
    width: record.plotWidthM, depth: record.plotDepthM, minWidth: record.plotWidthM, minDepth: record.plotDepthM,
    nativeDimensions: record.nativeDimensions as [number, number, number],
    storeyProgram: { id: `${record.variantId}-${record.revision}-fixed`, mode: 'fixed_authored_assembly',
      nativeStoreys: record.storeys, minStoreys: record.storeys, maxStoreys: record.storeys,
      podiumStoreys: record.storeys, podiumHeightM: record.nativeDimensions[2], repeatedStoreyHeightM: 0, roofHeightM: 0 },
    properties: { ...asset.properties, validation_fixed_fixture: true, validation_native_url: record.url,
      height: record.nativeDimensions[2], height_m: record.nativeDimensions[2],
      floors: record.storeys, floor_count: record.storeys } };
}
