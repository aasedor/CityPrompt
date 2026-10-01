import type { SiteZone } from '@/types';
import type { WalkPose } from '@/components/viewer/globe/walkNavigation';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { resolvePreparedSiteTerrainForZone } from '@/components/viewer/globe/sitePreparationSurface';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readNativePark, nativeParkFitProblem } from './nativeParkRegistry';
import { verifiedScene } from './nativeParkAssets';
import { advanceParkWalk, nearestParkWalkPoint, parkWalkHeight, type ParkWalkingNetwork, type WalkPoint } from './parkWalking';

/** Opt-in: all existing parks keep their prior camera behavior. */
function context(zones: SiteZone[], pose: WalkPose) {
  const boundary = getActiveSiteBoundary(zones);
  if (!boundary?.properties?.community_3d_mask_existing_tiles || boundary.properties.terrain_strategy === 'landscape') return null;
  for (const zone of zones) {
    const resolved = readNativePark(zone);
    if (!resolved) continue;
    const network = (resolved.layout as typeof resolved.layout & { walking?: ParkWalkingNetwork }).walking;
    if (!network || network.version !== 1 || nativeParkFitProblem(zone)) continue;
    const f = resolved.selection.frame, c = Math.cos(f.yaw), s = Math.sin(f.yaw), sx = metersPerDegLon(f.latitude);
    const local = (p: WalkPose): WalkPoint => {
      const x = (p.lng - f.longitude) * sx, y = (p.lat - f.latitude) * METERS_PER_DEG_LAT;
      return [x * c + y * s, -x * s + y * c, p.groundHeight];
    };
    const p = local(pose);
    if (Math.abs(p[0]) > resolved.layout.widthM / 2 + .01 || Math.abs(p[1]) > resolved.layout.depthM / 2 + .01) continue;
    const level = resolvePreparedSiteTerrainForZone(zone, zones, pose.groundHeight);
    if (level === null) continue;
    // No invisible walking surface before the exact model is ready.
    try { verifiedScene(resolved.layout.assets.assembly!); } catch { return null; }
    const world = (p: WalkPoint, heading: number): WalkPose => ({
      lng: f.longitude + (p[0] * c - p[1] * s) / sx,
      lat: f.latitude + (p[0] * s + p[1] * c) / METERS_PER_DEG_LAT,
      groundHeight: level + p[2], heading,
    });
    return { network, local, world, level, layout: resolved.layout };
  }
  return null;
}

export function nativeParkWalkEntry(zones: SiteZone[], pose: WalkPose): WalkPose {
  const ctx = context(zones, pose);
  if (!ctx) return pose;
  const p = ctx.local(pose), nearest = nearestParkWalkPoint(ctx.network, p[0], p[1]);
  return nearest ? ctx.world(nearest, pose.heading) : pose;
}

export function nativeParkWalkEntrance(zones: SiteZone[], pose: WalkPose): WalkPose | null {
  const ctx = context(zones, pose);
  return ctx ? ctx.world(ctx.network.entrance as WalkPoint, pose.heading) : null;
}

/** Keep both ascent and descent on connected treads. A ground-level portal is
 * the only transition to/from the surrounding site; turning always works. */
export function constrainNativeParkWalk(zones: SiteZone[], previous: WalkPose, next: WalkPose): WalkPose {
  const ctx = context(zones, previous) ?? context(zones, next);
  if (!ctx) return next;
  const from = ctx.local(previous), to = ctx.local(next);
  const inside = (p: WalkPoint) => Math.abs(p[0]) <= ctx.layout.widthM / 2 + .001 && Math.abs(p[1]) <= ctx.layout.depthM / 2 + .001;
  const entrance = ctx.network.entrance;
  const atPortal = (p: WalkPoint) => Math.abs(p[0] - entrance[0]) <= 1.5 && p[1] <= entrance[1] + .5;
  if (!inside(to) && inside(from) && atPortal(from) && Math.abs(previous.groundHeight - ctx.level) < .25) return next;
  if (!inside(from)) {
    if (!atPortal(to)) return { ...previous, heading: next.heading };
    const z = parkWalkHeight(ctx.network, to[0], to[1]);
    return z !== null && Math.abs(z) < .25 ? ctx.world([to[0], to[1], z], next.heading) : { ...previous, heading: next.heading };
  }
  const z = parkWalkHeight(ctx.network, from[0], from[1]);
  const safeFrom = z === null ? nearestParkWalkPoint(ctx.network, from[0], from[1]) : [from[0], from[1], z] as WalkPoint;
  if (!safeFrom) return { ...previous, heading: next.heading };
  return ctx.world(advanceParkWalk(ctx.network, safeFrom, [to[0], to[1]]), next.heading);
}
