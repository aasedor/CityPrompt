import type { SiteZone } from '@/types';
import { assetForZone } from './catalogue';

/** Read resolved facts without rewriting saved project geometry or metadata. */
export function nativeBuildingContract(zone: Pick<SiteZone, 'properties'>) {
  const asset = assetForZone(zone);
  if (!asset || asset.zoneType !== 'building' || asset.reshapeMode !== 'fixed_native') return undefined;
  const heightM = asset.nativeDimensions?.[2];
  if (!Number.isFinite(heightM) || Number(heightM) <= 0) return undefined;
  const rigid = !asset.storeyProgram || asset.storeyProgram.mode === 'fixed_authored_assembly';
  const floors = asset.storeyProgram?.nativeStoreys ?? Number(asset.properties.floor_count ?? asset.properties.floors);
  return { asset, revision: asset.model.revision, heightM: Number(heightM),
    storeys: Number.isInteger(floors) && floors > 0 ? floors : undefined, rigid,
    url: typeof asset.properties.validation_native_url === 'string' ? asset.properties.validation_native_url : undefined };
}

export function nativeBuildingUrl(zone: Pick<SiteZone, 'properties'>): string | undefined {
  const contract = nativeBuildingContract(zone);
  if (contract?.url) return contract.url;
  // An unregistered saved revision must not inherit the current catalogue URL.
  if (zone.properties?.pick_place_model_revision && zone.properties?.pick_place_asset && !assetForZone(zone)) return undefined;
  return typeof zone.properties?.validation_native_url === 'string' && zone.properties.validation_native_url
    ? zone.properties.validation_native_url : undefined;
}
