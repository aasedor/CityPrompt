import type { SiteZone } from '@/types';
import { siteZonesApi } from '@/services/api';
import { resolveCommunity3DKind } from '@/features/community3d/community3d';
import { isPersistedZoneId } from '@/utils/zoneIdentity';
import {
  generateParkGroundTexture,
  getParkGroundMeta,
  MAX_PARK_GROUND_BATCH_CALLS,
} from './parkGroundTexture';
import {
  generateStreetNetworkGroundTexture,
  getCurrentStreetNetworkGroundMeta,
} from './streetNetworkGroundTexture';

export interface PublicRealmDrapePlan {
  parkZones: SiteZone[];
  parksNeedingDrape: SiteZone[];
  streetZones: SiteZone[];
  streetNetworkNeedsDrape: boolean;
  totalImageCalls: number;
}

export interface PublicRealmDrapeProgress {
  completed: number;
  total: number;
  label: string;
}

export interface PublicRealmDrapeResult {
  zones: SiteZone[];
  generatedParks: number;
  generatedStreetNetwork: boolean;
  remainingParks: number;
  imageCalls: number;
}

export function planPublicRealmDrapes(zones: SiteZone[]): PublicRealmDrapePlan {
  const parkZones = zones.filter((zone) => (
    resolveCommunity3DKind(zone) === 'park'
    && zone.coordinates.length >= 3
    && isPersistedZoneId(zone.id)
  ));
  const streetZones = zones.filter((zone) => (
    resolveCommunity3DKind(zone) === 'street'
    && zone.coordinates.length >= 3
    && isPersistedZoneId(zone.id)
  ));
  const parksNeedingDrape = parkZones.filter((zone) => !getParkGroundMeta(zone));
  const streetNetworkNeedsDrape = (
    streetZones.length > 0 && !getCurrentStreetNetworkGroundMeta(zones)
  );
  return {
    parkZones,
    parksNeedingDrape,
    streetZones,
    streetNetworkNeedsDrape,
    totalImageCalls: parksNeedingDrape.length + (streetNetworkNeedsDrape ? 1 : 0),
  };
}

async function reloadExactScope(projectId: string, sourceZones: SiteZone[]): Promise<SiteZone[]> {
  const refreshed = await siteZonesApi.list(projectId);
  const refreshedById = new Map(refreshed.map((zone) => [zone.id, zone]));
  const missing = sourceZones.filter((zone) => !refreshedById.has(zone.id));
  if (missing.length > 0) {
    throw new Error(
      `${missing.length} plan zone${missing.length === 1 ? '' : 's'} changed while the AI ground drape was being prepared. Refresh and retry.`,
    );
  }
  return sourceZones.map((zone) => refreshedById.get(zone.id)!);
}

/** Generate only missing/stale public-realm material skins, then return the
 * authoritative revisions produced by those writes. A retry never re-spends
 * for a current drape. Streets cost one call for the complete network; parks
 * remain one geometry-locked call each until the coordinated park-atlas phase. */
export async function generatePublicRealmDrapes(
  projectId: string,
  zones: SiteZone[],
  options: {
    sceneContextImageBase64?: string | null;
    onProgress?: (progress: PublicRealmDrapeProgress) => void;
  } = {},
): Promise<PublicRealmDrapeResult> {
  const plan = planPublicRealmDrapes(zones);
  const parkBatch = plan.parksNeedingDrape.slice(0, MAX_PARK_GROUND_BATCH_CALLS);
  const scheduledCalls = parkBatch.length + (plan.streetNetworkNeedsDrape ? 1 : 0);
  let completed = 0;
  let generatedParks = 0;
  let generatedStreetNetwork = false;
  options.onProgress?.({
    completed,
    total: scheduledCalls,
    label: scheduledCalls > 0 ? 'Preparing coordinated AI ground drapes' : 'AI ground drapes are current',
  });

  if (plan.streetNetworkNeedsDrape) {
    options.onProgress?.({
      completed,
      total: scheduledCalls,
      label: `Draping ${plan.streetZones.length} connected street${plan.streetZones.length === 1 ? '' : 's'}`,
    });
    await generateStreetNetworkGroundTexture(projectId, zones, {
      sceneContextImageBase64: options.sceneContextImageBase64,
    });
    generatedStreetNetwork = true;
    completed += 1;
    options.onProgress?.({
      completed,
      total: scheduledCalls,
      label: 'Connected street atlas saved',
    });
  }

  // Sequential deliberately: each item is a paid full-image request and the
  // proxy enforces spend/rate controls. All calls share the same frozen site.
  for (const park of parkBatch) {
    const label = park.name || `Park ${generatedParks + 1}`;
    options.onProgress?.({ completed, total: scheduledCalls, label: `Draping ${label}` });
    await generateParkGroundTexture(park, {
      siteZones: zones,
      sceneContextImageBase64: options.sceneContextImageBase64,
    });
    generatedParks += 1;
    completed += 1;
    options.onProgress?.({ completed, total: scheduledCalls, label: `${label} drape saved` });
  }

  const authoritativeZones = scheduledCalls > 0
    ? await reloadExactScope(projectId, zones)
    : zones;
  return {
    zones: authoritativeZones,
    generatedParks,
    generatedStreetNetwork,
    remainingParks: Math.max(0, plan.parksNeedingDrape.length - parkBatch.length),
    imageCalls: scheduledCalls,
  };
}
