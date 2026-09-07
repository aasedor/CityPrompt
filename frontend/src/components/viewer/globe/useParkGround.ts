import { useMemo } from 'react';
import type { SiteZone } from '@/types';
import { useSharedSiteGround, type SharedSiteGroundState } from './SharedSiteGroundProvider';
import { parkTerrainContains, readParkTerrain } from './parkTerrain';
import { sampleSharedSiteGround } from './sharedSiteGround';

/** Saved park surface takes precedence over the site's level, in every layer. */
export function useParkGround(zone: SiteZone): SharedSiteGroundState {
  const shared = useSharedSiteGround();
  return useMemo(() => {
    if (!zone.properties?.park_terrain) return shared;
    const snapshot = readParkTerrain(zone);
    return { status: snapshot ? 'ready' : 'unavailable', snapshot,
      heightAt: (lng, lat) => sampleSharedSiteGround(snapshot,lng,lat),
      contains: (lng, lat) => parkTerrainContains(zone,lng,lat),
      revision: snapshot?.signature ?? 'park-terrain-needs-review', failureReason: snapshot ? null : 'Park moved or resized. Review its ground again.' };
  }, [shared, zone]);
}
