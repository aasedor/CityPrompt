import { Box3, Matrix4, Vector3 } from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import { detailPlacementMatrix, type DetailPlacement } from './detailInstances';

/** Source Y-up coordinates. Duplicate stations represent vertical step risers. */
export interface DetailWalkSurface {
  type: 'profile';
  width: number;
  stations: readonly { z: number; height: number }[];
}

interface SurfaceInstance {
  surface: DetailWalkSurface;
  world: Matrix4;
  inverse: Matrix4;
  ground: number;
}
const cells = new Map<string, Set<SurfaceInstance>>();
const CELL_SIZE = 32;
const cell = (n: number) => Math.floor(n / CELL_SIZE);
const key = (x: number, y: number, z: number) => `${x}:${y}:${z}`;
const EPSILON = 0.0001;

/** Mount-time spatial index; walking never scans the scene or raycasts GLBs. */
export function registerDetailWalkSurfaces(surface: DetailWalkSurface, placements: readonly DetailPlacement[], offset?: readonly number[]) {
  const entries: [string, SurfaceInstance][] = [];
  const stations = surface.stations;
  if (!(surface.width > 0) || !Number.isFinite(surface.width) || stations.length < 2 || stations.some((s, i) =>
    !Number.isFinite(s.z) || !Number.isFinite(s.height) || (i > 0 && s.z < stations[i - 1].z))) return () => {};
  const low = Math.min(...stations.map(s => s.height)) - .5;
  const high = Math.max(...stations.map(s => s.height)) + .5;
  for (const placement of placements) {
    if (!placement.id || placement.id.startsWith('detail-preview:')) continue;
    const world = detailPlacementMatrix(placement, new Matrix4(), offset);
    const instance = { surface, world, inverse: world.clone().invert(), ground: placement.height };
    const bounds = new Box3();
    for (const x of [-surface.width / 2 - EPSILON, surface.width / 2 + EPSILON])
      for (const y of [low, high])
        for (const z of [stations[0].z - EPSILON, stations[stations.length - 1].z + EPSILON])
          bounds.expandByPoint(new Vector3(x, y, z).applyMatrix4(world));
    for (let x = cell(bounds.min.x); x <= cell(bounds.max.x); x++)
      for (let y = cell(bounds.min.y); y <= cell(bounds.max.y); y++)
        for (let z = cell(bounds.min.z); z <= cell(bounds.max.z); z++) {
          const k = key(x,y,z), bucket = cells.get(k) ?? new Set<SurfaceInstance>();
          bucket.add(instance); cells.set(k,bucket); entries.push([k,instance]);
        }
  }
  return () => { for (const [k, instance] of entries) {
    const bucket = cells.get(k); bucket?.delete(instance);
    if (!bucket?.size) cells.delete(k);
  } };
}

function profileHeight(surface: DetailWalkSurface, x: number, z: number): number | null {
  const s = surface.stations;
  if (Math.abs(x) > surface.width / 2 + EPSILON || z < s[0].z - EPSILON || z > s[s.length - 1].z + EPSILON) return null;
  // Use the last station at a riser, so adjacent steps never become a slope.
  let i = 0;
  while (i + 1 < s.length && s[i + 1].z <= z + EPSILON) i++;
  if (i === s.length - 1) return s[i].height;
  const a = s[i], b = s[i + 1];
  return a.height + (b.height - a.height) * Math.max(0, Math.min(1, (z - a.z) / (b.z - a.z)));
}

function surfaceHeight(instance: SurfaceInstance, point: Vector3): number | null {
  const local = point.clone().applyMatrix4(instance.inverse);
  const h = profileHeight(instance.surface, local.x, local.z);
  if (h === null) return null;
  const world = local.setY(h).applyMatrix4(instance.world);
  return WGS84_ELLIPSOID.getPositionToCartographic(world, {lat:0,lon:0,height:0}).height;
}

/** Explicit walkable profiles only; furniture and roofs cannot become floors.
 * A 35cm upward limit permits ordinary treads but rejects entry through a high
 * side. Outside the profile, the existing unrestricted ground policy applies. */
export function detailWalkGround(lng: number, lat: number, ground: number, previous: number,
  previousPosition?: {lng: number; lat: number} | null): number {
  if (!cells.size) return ground;
  // Off prepared terrain the existing resolver inherits the previous feet
  // height. Recover this detail's placement ground before descending or leaving
  // it, but never replace a newly resolved authored terrain elevation.
  if (previousPosition && ground === previous) {
    const prior = WGS84_ELLIPSOID.getCartographicToPosition(previousPosition.lat * Math.PI / 180,
      previousPosition.lng * Math.PI / 180, previous, new Vector3());
    for (const instance of cells.get(key(cell(prior.x),cell(prior.y),cell(prior.z))) ?? []) {
      const h = surfaceHeight(instance, prior);
      if (h !== null && Math.abs(h - previous) < .01) ground = Math.min(ground, instance.ground);
    }
  }
  const point = WGS84_ELLIPSOID.getCartographicToPosition(lat * Math.PI / 180, lng * Math.PI / 180, previous, new Vector3());
  const candidates = cells.get(key(cell(point.x),cell(point.y),cell(point.z)));
  let result = ground;
  for (const instance of candidates ?? []) {
    const height = surfaceHeight(instance, point);
    if (height !== null && height <= previous + .35 && height > result) result = height;
  }
  return result;
}
