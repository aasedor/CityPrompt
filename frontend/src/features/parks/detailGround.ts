import type { SiteZone } from '@/types';
import { authoredCameraGround } from '@/components/viewer/globe/authoredCameraGround';
import { sharedSiteGroundContains } from '@/components/viewer/globe/sharedSiteGround';
import { getPreparedSiteBoundaryIds, resolvePreparedSiteTerrainForZone } from '@/components/viewer/globe/sitePreparationSurface';
import { PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS } from '@/components/viewer/globe/publicRealmDepthPolicy';
import { groundSurfaceFor } from '@/features/groundSurfaces/groundSurfaces';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import type { DetailAsset } from './detailCatalogue';

/** Common placement datum for saved details and the placement cursor. */
export function detailPlacementGroundHeight(asset: Pick<DetailAsset, 'datumLift'>, zones: SiteZone[],
  lng: number, lat: number, measured: number, supportHeight?: number): number {
  // Registered road supports already include the rendered road/sidewalk lift.
  if (supportHeight !== undefined) return supportHeight;
  const ground = authoredCameraGround(zones, lng, lat, measured);
  const contains = (zone: SiteZone) => sharedSiteGroundContains(zone.coordinates as [number, number][], lng, lat);
  let visibleSurface: number | undefined;
  const boundary = getActiveSiteBoundary(zones);
  if (boundary && contains(boundary) && boundary.properties?.terrain_strategy !== 'landscape'
    && getPreparedSiteBoundaryIds(zones).has(boundary.id)) {
    const base = resolvePreparedSiteTerrainForZone(boundary, zones, measured);
    // Native park paths, terraces, bridges and canals can own a different
    // physical surface; the site's fill must not override their elevation.
    if (base !== null && Math.abs(ground - base) < .000001) visibleSurface = base + PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS;
  }
  for (const zone of zones) {
    if (!groundSurfaceFor(zone) || !contains(zone)) continue;
    const base = resolvePreparedSiteTerrainForZone(zone, zones, measured) ?? measured;
    visibleSurface = Math.max(visibleSurface ?? -Infinity, base + PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS);
  }
  // The original .084 m furniture datum already clears the .08 m surface.
  // Safety paint embeds its own .004 m reveal in its source vertices instead.
  const datumLift = asset.datumLift ?? .084;
  return visibleSurface === undefined ? ground : Math.max(ground, visibleSurface - datumLift);
}
