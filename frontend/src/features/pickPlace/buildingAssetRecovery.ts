import type { SiteZone } from '@/types';

export function buildingAssetRevision(zone: SiteZone): string {
  return JSON.stringify([zone.updated_at, zone.properties?.pick_place_model_revision ?? null]);
}

export function retryBuildingAssets(): void {
  window.dispatchEvent(new Event('cityprompt:retry-native-buildings'));
}
