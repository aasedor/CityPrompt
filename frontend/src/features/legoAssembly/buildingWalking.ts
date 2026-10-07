import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { SiteZone } from '@/types';
import type { WalkPose } from '@/components/viewer/globe/walkNavigation';
import { advanceParkWalk, parkWalkHeight, type ParkWalkingNetwork, type WalkPoint } from '@/features/parks/parkWalking';

export interface BuildingWalkNetwork extends ParkWalkingNetwork {
  version: 2;
  footprint: [number, number];
  footprintCenter?: [number, number];
  entryDirection?: [number, number];
  portals: number[][];
}
interface MountedWalk {
  zoneId: string;
  revision: string;
  object: THREE.Object3D;
  network: BuildingWalkNetwork;
  openDoors?: (open: boolean) => void;
}
const mounted = new Map<string, MountedWalk>();
let doorsOpen = false;
export function setBuildingWalkingDoorsOpen(open: boolean) {
  doorsOpen = open;
  for (const record of mounted.values()) record.openDoors?.(open);
}
export const buildingWalkRevision = (zone: SiteZone) => JSON.stringify([zone.coordinates, zone.properties, zone.updated_at]);

/** Read only the explicit, bounded public circulation shipped inside a model.
 * Ordinary buildings have no walking extras and retain their existing behavior. */
export function readBuildingWalking(scene: THREE.Object3D): BuildingWalkNetwork | null {
  let result: BuildingWalkNetwork | null = null;
  scene.traverse(object => {
    const text = object.userData?.cityprompt_walking_json;
    if (result || typeof text !== 'string' || text.length > 2_000_000) return;
    try {
      const n = JSON.parse(text) as BuildingWalkNetwork;
      const finite = (p: unknown, size: number): boolean => Array.isArray(p) && p.length === size && p.every(Number.isFinite);
      if (n.version !== 2 || !finite(n.footprint, 2) || n.footprint.some(v => v <= 0 || v > 500)
        || !finite(n.entrance, 3) || !(n.maxStepM > 0 && n.maxStepM <= .25)
        || !Array.isArray(n.triangles) || !n.triangles.length || n.triangles.length > 20_000
        || !n.triangles.every(t => Array.isArray(t) && t.length === 3 && t.every(p => finite(p, 3)))
        || !Array.isArray(n.obstacles) || !n.obstacles.every(p => finite(p, 6))
        || (n.barriers !== undefined && (!Array.isArray(n.barriers) || n.barriers.length > 30_000 || !n.barriers.every(p => finite(p, 6))))
        || (n.footprintCenter !== undefined && !finite(n.footprintCenter, 2))
        || (n.entryDirection !== undefined && !finite(n.entryDirection, 2))
        || !Array.isArray(n.portals) || !n.portals.length || !n.portals.every(p => finite(p, 4))) return;
      if (parkWalkHeight(n, n.entrance[0], n.entrance[1], n.entrance[2]) === null) return;
      result = n;
    } catch { /* A malformed optional network cannot take down the model or viewer. */ }
  });
  return result;
}

/** Register only after the exact detailed model and its ground are mounted.
 * The actual scene transform owns yaw, centering and elevation; no second fit. */
export function mountBuildingWalking(id: string, zone: SiteZone, object: THREE.Object3D, network: BuildingWalkNetwork, openDoors?: (open: boolean) => void) {
  const record = { zoneId: zone.id, revision: buildingWalkRevision(zone), object, network, openDoors };
  openDoors?.(doorsOpen);
  mounted.set(id, record);
  return () => { openDoors?.(false); if (mounted.get(id) === record) mounted.delete(id); };
}

function local(record: MountedWalk, pose: WalkPose): WalkPoint {
  const point = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(pose.lat * Math.PI / 180, pose.lng * Math.PI / 180, pose.groundHeight, point);
  record.object.updateWorldMatrix(true, false);
  record.object.worldToLocal(point);
  return [point.x, -point.z, point.y];
}
function world(record: MountedWalk, point: WalkPoint, heading: number): WalkPose {
  record.object.updateWorldMatrix(true, false);
  const p = record.object.localToWorld(new THREE.Vector3(point[0], point[2], -point[1]));
  const geographic = WGS84_ELLIPSOID.getPositionToCartographic(p, { lat: 0, lon: 0, height: 0 });
  return { lng: geographic.lon * 180 / Math.PI, lat: geographic.lat * 180 / Math.PI, groundHeight: geographic.height, heading };
}
function inside(n: BuildingWalkNetwork, p: WalkPoint) {
  const center = n.footprintCenter ?? [0, 0];
  return Math.abs(p[0] - center[0]) <= n.footprint[0] / 2 + .001 && Math.abs(p[1] - center[1]) <= n.footprint[1] / 2 + .001;
}
function context(zones: SiteZone[], pose: WalkPose) {
  for (const record of mounted.values()) {
    const zone = zones.find(z => z.id === record.zoneId);
    if (!zone || record.revision !== buildingWalkRevision(zone)) continue;
    const p = local(record, pose);
    if (inside(record.network, p)) return { record, p };
  }
  return null;
}

export function buildingWalkEntrance(zones: SiteZone[], pose: WalkPose): WalkPose | null {
  const ctx = context(zones, pose);
  return ctx ? world(ctx.record, ctx.record.network.entrance as WalkPoint, pose.heading) : null;
}

/** Start a selected exact model at its authored, walkable entrance. This does
 * not assert a continuous route from an arbitrary sidewalk to that door. */
export function buildingWalkStartForZone(zones: SiteZone[], zoneId: string): WalkPose | null {
  const zone = zones.find(candidate => candidate.id === zoneId);
  if (!zone) return null;
  for (const record of mounted.values()) {
    if (record.zoneId !== zoneId || record.revision !== buildingWalkRevision(zone)) continue;
    const entry = record.network.entrance as WalkPoint;
    const origin = world(record, entry, 0);
    const direction = record.network.entryDirection ?? [0, 1];
    const inward = world(record, [entry[0] + direction[0], entry[1] + direction[1], entry[2]], 0);
    const north = (inward.lat - origin.lat) * Math.PI / 180;
    const east = (inward.lng - origin.lng) * Math.PI / 180 * Math.cos(origin.lat * Math.PI / 180);
    return { ...origin, heading: (Math.atan2(east, north) * 180 / Math.PI + 360) % 360 };
  }
  return null;
}
export function buildingWalkEntry(zones: SiteZone[], pose: WalkPose): WalkPose {
  // Deliberate entry always starts at the signed front door, never on a roof,
  // an inaccessible clock chamber, a rail bed or a bench.
  return buildingWalkEntrance(zones, pose) ?? pose;
}
export function buildingWalkGround(zones: SiteZone[], pose: WalkPose): number | null {
  const ctx = context(zones, pose);
  if (!ctx) return null;
  const z = parkWalkHeight(ctx.record.network, ctx.p[0], ctx.p[1], ctx.p[2], true);
  return z === null ? null
    : world(ctx.record, [ctx.p[0], ctx.p[1], z], pose.heading).groundHeight;
}
export function constrainBuildingWalk(zones: SiteZone[], previous: WalkPose, next: WalkPose): WalkPose {
  const ctx = context(zones, previous) ?? context(zones, next);
  if (!ctx) return next;
  const { record } = ctx, n = record.network, from = local(record, previous), to = local(record, next);
  const portal = (p: WalkPoint) => n.portals.some(([x0,x1,y0,y1]) => p[0] >= x0 && p[0] <= x1 && p[1] >= y0 && p[1] <= y1);
  // The real entry paving can end before the roof/overhang bounding box. Allow
  // a ground-floor portal to join the surrounding verified site at that edge.
  if (n.groundFloorOnly && portal(from) && portal(to) && parkWalkHeight(n, to[0], to[1], from[2], true) === null
    && Math.abs(from[2] - n.entrance[2]) < .25) return next;
  if (n.groundFloorOnly && portal(to) && parkWalkHeight(n, from[0], from[1], from[2], true) === null) {
    const z = parkWalkHeight(n, to[0], to[1], from[2]);
    return z !== null && Math.abs(z - from[2]) <= n.maxStepM + .05 ? world(record, [to[0], to[1], z], next.heading)
      : { ...previous, heading: next.heading };
  }
  if (!inside(n, to) && portal(from) && Math.abs(from[2] - n.entrance[2]) < .25) return next;
  if (!inside(n, from)) {
    if (!portal(to)) return { ...previous, heading: next.heading };
    const z = parkWalkHeight(n, to[0], to[1], n.entrance[2]);
    return z === null ? previous : world(record, [to[0], to[1], z], next.heading);
  }
  const z = parkWalkHeight(n, from[0], from[1], from[2]);
  if (z === null) return { ...previous, heading: next.heading };
  const result = advanceParkWalk(n, [from[0],from[1],z], [to[0],to[1]]);
  return world(record, result, next.heading);
}
