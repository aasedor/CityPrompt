import * as THREE from 'three';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import type { SharedSiteGroundSnapshot } from './sharedSiteGround';

export type GroundPoint = [number, number];
export interface LegoGroundingIssue { buildingId: string; reason: string }

export function updateBuildingGroundingIssues(previous: ReadonlyMap<string, LegoGroundingIssue>, buildingId: string, rendererId: string, reason: string | null): ReadonlyMap<string, LegoGroundingIssue> {
  const before = previous.get(rendererId);
  if (reason === null ? !before : before?.buildingId === buildingId && before.reason === reason) return previous;
  const next = new Map(previous);
  if (reason === null) next.delete(rendererId);
  else next.set(rendererId, { buildingId, reason });
  return next;
}

export function currentBuildingGroundingIssues(issues: ReadonlyMap<string, LegoGroundingIssue>, buildingIds: ReadonlySet<string>): LegoGroundingIssue[] {
  const unique = new Map<string, LegoGroundingIssue>();
  for (const issue of issues.values()) if (buildingIds.has(issue.buildingId)) unique.set(`${issue.buildingId}:${issue.reason}`, issue);
  return [...unique.values()];
}
export interface PlacedModuleBounds {
  bounds: THREE.Box3;
  transform: { position: [number, number, number]; scale: [number, number, number]; rotationYRad: number };
}

/** Mirror the actual GLB instance → Y-up/ENU wrapper → stack yaw. Bounds
 * are measured after native-clay bottom centering (or at the preserved legacy
 * module origin). Separate detached modules never become a whole-plot pad. */
export function placedNativeFootprints(modules: readonly PlacedModuleBounds[], yaw: number, offset: GroundPoint): GroundPoint[][] {
  if (!modules.length) return [];
  const lowest = Math.min(...modules.map(({ bounds, transform }) => bounds.min.y * transform.scale[1] + transform.position[1]));
  return modules.filter(({ bounds, transform }) => bounds.min.y * transform.scale[1] + transform.position[1] <= lowest + 0.15)
    .map(({ bounds, transform }) => {
      const matrix = new THREE.Matrix4().makeTranslation(offset[0], offset[1], 0)
        .multiply(new THREE.Matrix4().makeRotationZ(yaw))
        .multiply(new THREE.Matrix4().makeRotationX(Math.PI / 2))
        .multiply(new THREE.Matrix4().makeTranslation(...transform.position))
        .multiply(new THREE.Matrix4().makeRotationY(transform.rotationYRad))
        .multiply(new THREE.Matrix4().makeScale(...transform.scale));
      return [[bounds.min.x, bounds.min.z], [bounds.max.x, bounds.min.z], [bounds.max.x, bounds.max.z], [bounds.min.x, bounds.max.z]]
        .map(([x, z]): GroundPoint => {
          const point = new THREE.Vector3(x, bounds.min.y, z).applyMatrix4(matrix);
          return [point.x, point.y];
        });
    });
}

export function geographicFootprint(ring: readonly number[][], lng: number, lat: number): GroundPoint[] {
  const points = ring.map((point): GroundPoint => [(point[0] - lng) * metersPerDegLon(lat), (point[1] - lat) * METERS_PER_DEG_LAT]);
  if (points.length > 1 && Math.hypot(points[0][0] - points[points.length - 1][0], points[0][1] - points[points.length - 1][1]) < 1e-6) points.pop();
  return points;
}

export type BuildingGroundContact =
  | { status: 'outside' | 'unresolved'; reason?: string }
  | { status: 'ready'; anchorHeight: number; reliefM: number; positions: number[]; indices: number[] };

function footprintContains(ring: readonly GroundPoint[], point: GroundPoint): boolean {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [ax, ay] = ring[j], [bx, by] = ring[i];
    const dx = bx - ax, dy = by - ay;
    const t = ((point[0] - ax) * dx + (point[1] - ay) * dy) / (dx * dx + dy * dy || 1);
    if (t >= 0 && t <= 1 && Math.hypot(point[0] - ax - t * dx, point[1] - ay - t * dy) < 1e-7) return true;
    if ((ay > point[1]) !== (by > point[1]) && point[0] < (bx - ax) * (point[1] - ay) / (by - ay) + ax) inside = !inside;
  }
  return inside;
}

/** In normalized grid coordinates, every terrain triangle edge lies on x=i,
 * y=j or y-x=k. Split at those exact crossings so the skirt bottom follows
 * each shared plane rather than spanning an unobserved ridge between probes. */
function terrainEdgeCrossings(a: GroundPoint, b: GroundPoint, snapshot: SharedSiteGroundSnapshot, lng: number, lat: number): number[] {
  const { west, south, stepLng, stepLat, columns, rows } = snapshot.grid;
  const normalized = ([x, y]: GroundPoint): GroundPoint => [
    (lng + x / metersPerDegLon(lat) - west) / stepLng,
    (lat + y / METERS_PER_DEG_LAT - south) / stepLat,
  ];
  const start = normalized(a), end = normalized(b), times: number[] = [];
  for (const [from, to, minimum, maximum] of [
    [start[0], end[0], 0, columns - 1],
    [start[1], end[1], 0, rows - 1],
    [start[1] - start[0], end[1] - end[0], -(columns - 1), rows - 1],
  ]) {
    if (Math.abs(to - from) < 1e-12) continue;
    for (let line = Math.max(minimum, Math.ceil(Math.min(from, to))); line <= Math.min(maximum, Math.floor(Math.max(from, to))); line += 1) {
      const t = (line - from) / (to - from);
      if (t > 1e-9 && t < 1 - 1e-9) times.push(t);
    }
  }
  return times;
}

/** A rigid building sits above the highest measured footprint contact. A
 * separate, footprint-bounded foundation meets the shared mesh at each edge.
 * This is display seating, not a geotechnical or foundation-design claim. */
export function resolveBuildingGroundContact(
  footprints: readonly GroundPoint[][],
  lng: number,
  lat: number,
  ground: { status: string; snapshot?: SharedSiteGroundSnapshot | null; contains: (lng: number, lat: number) => boolean; heightAt: (lng: number, lat: number) => number | null },
): BuildingGroundContact {
  const toGeo = ([east, north]: GroundPoint): GroundPoint => [lng + east / metersPerDegLon(lat), lat + north / METERS_PER_DEG_LAT];
  const points = footprints.flat();
  if (!points.length || footprints.some((ring) => ring.length < 3) || points.some((point) => !point.every(Number.isFinite))) return { status: 'unresolved', reason: 'missing_footprint' };
  if (!points.some((point) => ground.contains(...toGeo(point))) && !ground.contains(lng, lat)) return { status: 'outside' };
  if (ground.status !== 'ready') return { status: 'unresolved', reason: 'ground_not_ready' };
  const probeCount = footprints.reduce((sum, ring) => sum + ring.reduce((count, point, index) => {
    const next = ring[(index + 1) % ring.length];
    return count + Math.max(2, Math.ceil(Math.hypot(next[0] - point[0], next[1] - point[1]) / 2));
  }, 0), 0);
  if (probeCount > 4096) return { status: 'unresolved', reason: 'footprint_probe_budget' };
  const rings = footprints.map((ring) => ring.flatMap((point, index) => {
    const next = ring[(index + 1) % ring.length];
    // At least the corners and edge midpoints; longer edges get 2 m probes.
    const count = Math.max(2, Math.ceil(Math.hypot(next[0] - point[0], next[1] - point[1]) / 2));
    const times = Array.from({ length: count }, (_, step) => step / count);
    if (ground.snapshot) times.push(...terrainEdgeCrossings(point, next, ground.snapshot, lng, lat));
    times.sort((a, b) => a - b);
    return times.filter((t, index) => index === 0 || t - times[index - 1] > 1e-9)
      .map((t): GroundPoint => [point[0] + (next[0] - point[0]) * t, point[1] + (next[1] - point[1]) * t]);
  }));
  const sample = (point: GroundPoint) => {
    const geo = toGeo(point);
    return ground.contains(...geo) ? ground.heightAt(...geo) : null;
  };
  const edgeHeights = rings.map((ring) => ring.map(sample));
  // A linear height field reaches extrema at the vertices of each triangle's
  // intersection with the footprint: footprint corners, triangle-edge
  // crossings above, and terrain vertices inside each individual pad below.
  const interior: GroundPoint[] = [];
  if (ground.snapshot) {
    const { west, south, stepLng, stepLat, columns, rows } = ground.snapshot.grid;
    for (let row = 0; row < rows; row += 1) for (let column = 0; column < columns; column += 1) {
      const point: GroundPoint = [(west + column * stepLng - lng) * metersPerDegLon(lat), (south + row * stepLat - lat) * METERS_PER_DEG_LAT];
      if (footprints.some((ring) => footprintContains(ring, point))) interior.push(point);
    }
  } else {
    footprints.forEach((ring) => {
      const center: GroundPoint = [ring.reduce((sum, point) => sum + point[0], 0) / ring.length, ring.reduce((sum, point) => sum + point[1], 0) / ring.length];
      if (footprintContains(ring, center)) interior.push(center);
    });
  }
  if (rings.reduce((sum, ring) => sum + ring.length, interior.length) > 8192) return { status: 'unresolved', reason: 'footprint_probe_budget' };
  const heights = [...edgeHeights.flat(), ...interior.map(sample)];
  if (heights.some((height) => height === null || !Number.isFinite(height))) return { status: 'unresolved', reason: 'incomplete_footprint_ground' };
  const measured = heights as number[];
  const anchorHeight = Math.max(...measured) + 0.04;
  const reliefM = Math.max(...measured) - Math.min(...measured);
  if (anchorHeight - Math.min(...measured) + 0.02 > 3) return { status: 'unresolved', reason: 'foundation_exceeds_3m' };
  const positions: number[] = [], indices: number[] = [];
  for (let r = 0; r < rings.length; r += 1) {
    const ring = rings[r];
    const start = positions.length / 3;
    ring.forEach(([east, north], index) => {
      positions.push(east, north, (edgeHeights[r][index] as number) - anchorHeight - 0.02, east, north, 0);
    });
    ring.forEach((_, index) => {
      const a = start + index * 2, b = start + ((index + 1) % ring.length) * 2;
      indices.push(a, b, b + 1, a, b + 1, a + 1);
    });
    // A cap stops the underlying mesh showing through an open-bottom GLB.
    for (const triangle of THREE.ShapeUtils.triangulateShape(ring.map(([x, y]) => new THREE.Vector2(x, y)), [])) {
      indices.push(...triangle.map((index) => start + index * 2 + 1));
    }
  }
  return { status: 'ready', anchorHeight, reliefM, positions, indices };
}
