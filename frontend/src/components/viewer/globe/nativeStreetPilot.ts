import pilots from '@/data/nativeStreetPilots.json';
import bounds from '@/data/nativeStreetModuleBounds.json';
import type { NativeStreetProgram } from './nativeStreetProgram';
import type { SiteZone } from '@/types';
import { extractZoneCenterline } from '@/utils/roadGeometry';
import { validateStreetRecipeProperties } from './streetLegoContract';
import {
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_SHARED_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS,
} from './publicRealmDepthPolicy';

export type NativeStreetPilot = typeof pilots[number] & {program?:NativeStreetProgram;programSha256?:string};
export interface StreetRouteStation { x: number; y: number; z?: number }
export interface NativeStreetPose {
  kind: string;
  url: string;
  sha256: string;
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

export function nativeStreetRouteProblem(zone:Pick<SiteZone,'coordinates'|'properties'>,boundary?:SiteZone|null):string|null {
  if(zone.properties?.validation_fixed_fixture)return null;
  const pilot=nativeStreetPilot(String(zone.properties?.road_selected_variant_id)),program=pilot?.program;
  if(!program)return null;
  if(program.preparedLevelOnly && (!boundary || boundary.properties?.terrain_strategy==='landscape'
    || boundary.properties?.community_3d_mask_existing_tiles!==true))return 'Prepare a level site and clear existing site surfaces before drawing this native street.';
  const points=extractZoneCenterline(zone),scale=111320*Math.cos((points[0]?.[1]??0)*Math.PI/180);
  const length=points.slice(1).reduce((sum,p,i)=>sum+Math.hypot((p[0]-points[i][0])*scale,(p[1]-points[i][1])*111320),0);
  return length<program.minLengthM-.01 || length>program.maxLengthM+.01
    ? `${pilot.title} needs a route ${program.minLengthM}–${program.maxLengthM} m long so its complete garden and access program fits.` : null;
}

/** Saved production zones require the same module locks as the server compiler.
 * Section cards may request a draft profile before there is a saved recipe. */
export function nativeStreetPilotForZone(zone: Pick<SiteZone, 'zone_type' | 'properties'>, preview = false): NativeStreetPilot | undefined {
  if (zone.zone_type !== 'road') return undefined;
  if (zone.properties?.validation_fixed_fixture) return undefined;
  const selected = pilots.find(pilot => pilot.id === zone.properties?.road_selected_variant_id);
  if (selected) {
    if (zone.properties?.road_archetype_id !== selected.sourceArchetypeId || zone.properties?.width !== selected.widthM) return undefined;
    if (preview && !zone.properties?.public_realm_lego) return selected;
    return validateStreetRecipeProperties(zone.properties).valid ? selected : undefined;
  }
  // Preserve isolated historical candidate review pages; never execute this
  // marker in a production build or use it as proof of capture readiness.
  if (!import.meta.env.DEV) return undefined;
  const id = zone.properties?.native_street_pilot_id;
  const pilot = typeof id === 'string' ? nativeStreetPilot(id) : undefined;
  return pilot && zone.properties?.width === pilot.widthM
    && zone.properties?.road_archetype_id === pilot.sourceArchetypeId ? pilot : undefined;
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
  // Every authored repetition is required. Rendering batches identical meshes;
  // performance must never change the inventory by skipping furnishing cycles.
  const placed: NativeStreetPose[] = [];
  for (let cycle = 0; cycle < centers.length; cycle += 1) for (const item of source) {
    const centerM = centers[cycle];
    const stationM = centerM + item.y;
    const module = pilot.modules[item.kind as keyof typeof pilot.modules];
    if (!module) throw new Error('A required native street component has no asset binding.');
    // Co-located source objects (notably tree + well) share one clearance
    // envelope so clipping cannot strand a tree without its supporting well.
    const group = source.filter(other => Math.abs(other.x-item.x)<1e-5 && Math.abs(other.y-item.y)<1e-5);
    const corners = group.flatMap(other => {
      const asset = pilot.modules[other.kind as keyof typeof pilot.modules];
      if (!asset) throw new Error('A required native street component has no asset binding.');
      const envelope = bounds[asset.sha256 as keyof typeof bounds]?.plan;
      if (!envelope) throw new Error('The street component has no verified occupied bounds.');
      const c = Math.cos(other.yaw), s = Math.sin(other.yaw);
      return [envelope[0][0],envelope[1][0]].flatMap(x => [envelope[0][1],envelope[1][1]].map(y =>
        ({x:(x*c-y*s)*other.scale,y:(x*s+y*c)*other.scale})));
    });
    if (corners.some(corner => stationM+corner.y < -1e-5 || stationM+corner.y > totalM+1e-5)) continue;
    const segment = segments.find(segment => stationM <= segment.startM + segment.lengthM + 1e-6)
      ?? last;
    const t = Math.max(0, Math.min(1, (stationM - segment.startM) / segment.lengthM));
    const routeX = segment.from.x + (segment.to.x - segment.from.x) * t;
    const routeY = segment.from.y + (segment.to.y - segment.from.y) * t;
    const routeZ = (segment.from.z ?? 0) + ((segment.to.z ?? 0) - (segment.from.z ?? 0)) * t;
    const x = routeX + Math.sin(segment.angle) * item.x;
    const y = routeY - Math.cos(segment.angle) * item.x;
    // Circle against the complete rigid occupied rectangle, including crowns
    // and roof overhangs. A centre-only test can leave a canopy in a junction.
    const minX=Math.min(...corners.map(p=>p.x)), maxX=Math.max(...corners.map(p=>p.x));
    const minY=Math.min(...corners.map(p=>p.y)), maxY=Math.max(...corners.map(p=>p.y));
    const rotation=segment.angle-Math.PI/2, c=Math.cos(rotation), s=Math.sin(rotation);
    if (clearances.some(node => {
      const dx=node.x-x,dy=node.y-y,nx=dx*c+dy*s,ny=-dx*s+dy*c;
      const distance=Math.hypot(nx-Math.max(minX,Math.min(maxX,nx)),ny-Math.max(minY,Math.min(maxY,ny)));
      return distance<Math.max(node.clearanceM,pilot.widthM/2+4);
    })) continue;
    const well = item.kind === 'tree_well_grate' ? pilot.treeWells.find(candidate =>
      Math.abs(candidate.x - item.x) < 1e-5 && Math.abs(candidate.y - item.y) < 1e-5) : undefined;
    const sourceBand = pilot.sections.find(band => Math.abs(item.x - band.x) <= band.width / 2 + 1e-5);
    const surfaceLiftM = pilot.program ? pilot.program.baseLiftM : pilot.id === 'student_market_street_v1'
      ? PUBLIC_REALM_STREET_SHARED_SURFACE_LIFT_METERS
      : sourceBand?.material === 'asphalt'
        ? PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS
        : PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS;
    placed.push({ kind: item.kind, url: module.url, sha256: module.sha256, x, y, z: routeZ + item.z,
      yaw: segment.angle - Math.PI / 2 + item.yaw, scale: item.scale, stationM, surfaceLiftM,
      ...(well ? { wellWidthM: well.width, wellDepthM: well.depth } : {}) });
  }
  return placed;
}
