import pilots from '@/data/nativeStreetPilots.json';
import type { SiteZone } from '@/types';
import {
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_SHARED_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS,
} from './publicRealmDepthPolicy';

export type NativeStreetPilot = typeof pilots[number];
export interface StreetRouteStation { x: number; y: number; z?: number }
export interface NativeStreetPose {
  kind: string;
  url: string;
  x: number;
  y: number;
  z: number;
  yaw: number;
  scale: number;
  stationM: number;
  surfaceLiftM: number;
  wellWidthM?: number;
  wellDepthM?: number;
}

export function nativeStreetPilot(variantId: string): NativeStreetPilot | undefined {
  return pilots.find(pilot => pilot.id === variantId);
}

/** Candidate-only development view. This is not a student catalogue release. */
export function nativeStreetPilotForZone(zone: Pick<SiteZone, 'zone_type' | 'properties'>): NativeStreetPilot | undefined {
  if (!import.meta.env.DEV || zone.zone_type !== 'road') return undefined;
  const id = zone.properties?.native_street_pilot_id;
  const pilot = typeof id === 'string' ? nativeStreetPilot(id) : undefined;
  return pilot && zone.properties?.width === pilot.widthM ? pilot : undefined;
}

interface RouteSegment {
  from: StreetRouteStation;
  to: StreetRouteStation;
  startM: number;
  lengthM: number;
  angle: number;
}

/** Metric, rigid component placement on a student route. Preview assemblies are
 * never transformed; only their independent modules repeat along the centreline.
 * A junction owns its footprint, so furniture and trees yield around a node. */
export function placeNativeStreetModules(
  pilot: NativeStreetPilot,
  route: StreetRouteStation[],
  junctions: Array<{ x: number; y: number; clearanceM: number }> = [],
): NativeStreetPose[] {
  const segments: RouteSegment[] = [];
  for (let index = 1; index < route.length; index++) {
    const from = route[index - 1], to = route[index];
    const lengthM = Math.hypot(to.x - from.x, to.y - from.y);
    if (!Number.isFinite(lengthM) || lengthM < 1e-5) continue;
    const previous = segments[segments.length - 1];
    segments.push({ from, to, startM: (previous?.startM ?? 0) + (previous?.lengthM ?? 0),
      lengthM, angle: Math.atan2(to.y - from.y, to.x - from.x) });
  }
  const last = segments[segments.length - 1];
  const totalM = last ? last.startM + last.lengthM : 0;
  if (totalM < 6) return [];
  const bendClearances = segments.slice(1).flatMap((segment, index) => {
    const previous = segments[index];
    const angle = Math.atan2(Math.sin(segment.angle - previous.angle), Math.cos(segment.angle - previous.angle));
    return Math.abs(angle) > Math.PI / 12
      ? [{ x: segment.from.x, y: segment.from.y, clearanceM: pilot.widthM / 2 + 4 }]
      : [];
  });
  const clearances = [...junctions, ...bendClearances];
  const source = pilot.placements;
  const centers = totalM <= pilot.fixtureLengthM
    ? [totalM / 2]
    : Array.from({ length: Math.ceil(totalM / pilot.fixtureLengthM) }, (_, index) =>
      pilot.fixtureLengthM / 2 + index * pilot.fixtureLengthM);
  // Keep a long concept corridor responsive without ending its furniture row
  // abruptly halfway down the route. Components remain native-size.
  const cycleStride = Math.max(1, Math.ceil(centers.length * source.length / 750));
  const placed: NativeStreetPose[] = [];
  for (let cycle = 0; cycle < centers.length; cycle += cycleStride) for (const item of source) {
    const centerM = centers[cycle];
    const stationM = centerM + item.y;
    if (stationM < 2 || stationM > totalM - 2) continue;
    const segment = segments.find(segment => stationM <= segment.startM + segment.lengthM + 1e-6)
      ?? last;
    const t = Math.max(0, Math.min(1, (stationM - segment.startM) / segment.lengthM));
    const routeX = segment.from.x + (segment.to.x - segment.from.x) * t;
    const routeY = segment.from.y + (segment.to.y - segment.from.y) * t;
    const routeZ = (segment.from.z ?? 0) + ((segment.to.z ?? 0) - (segment.from.z ?? 0)) * t;
    const x = routeX + Math.sin(segment.angle) * item.x;
    const y = routeY - Math.cos(segment.angle) * item.x;
    if (clearances.some(node => Math.hypot(node.x - x, node.y - y) < Math.max(node.clearanceM, pilot.widthM / 2 + 4))) continue;
    const module = pilot.modules[item.kind as keyof typeof pilot.modules];
    if (!module) continue;
    const well = item.kind === 'tree_well_grate' ? pilot.treeWells.find(candidate =>
      Math.abs(candidate.x - item.x) < 1e-5 && Math.abs(candidate.y - item.y) < 1e-5) : undefined;
    const sourceBand = pilot.sections.find(band => Math.abs(item.x - band.x) <= band.width / 2 + 1e-5);
    const surfaceLiftM = pilot.id === 'student_market_street_v1'
      ? PUBLIC_REALM_STREET_SHARED_SURFACE_LIFT_METERS
      : sourceBand?.material === 'asphalt'
        ? PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS
        : PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS;
    placed.push({ kind: item.kind, url: module.url, x, y, z: routeZ + item.z,
      yaw: segment.angle - Math.PI / 2 + item.yaw, scale: item.scale, stationM, surfaceLiftM,
      ...(well ? { wellWidthM: well.width, wellDepthM: well.depth } : {}) });
  }
  return placed;
}
