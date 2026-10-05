import * as THREE from 'three';
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';
import type { Position, ZoningOverlay } from './zoningLabels';
import { zoningColor } from './zoningAppearance';

/** One batched fill and one shared edge set. Holes and exact City coordinates
 * survive triangulation; neighbouring districts do not darken their shared edge.
 * This is a cartographic overlay at the site's reference elevation, not grading.
 */
export function zoningSurfaceGeometry(data: ZoningOverlay, terrainHeight: number) {
  const lat = (data.bounds[1] + data.bounds[3]) * Math.PI / 360;
  const lon = (data.bounds[0] + data.bounds[2]) * Math.PI / 360;
  const height = (Number.isFinite(terrainHeight) ? terrainHeight : 0) + 1;
  const origin = new THREE.Vector3(), east = new THREE.Vector3(), north = new THREE.Vector3(), up = new THREE.Vector3();
  WGS84_ELLIPSOID.getCartographicToPosition(lat, lon, height, origin);
  WGS84_ELLIPSOID.getEastNorthUpAxes(lat, lon, east, north, up);
  const world = new THREE.Vector3();
  const local = ([x, y]: Position) => {
    WGS84_ELLIPSOID.getCartographicToPosition(y * Math.PI / 180, x * Math.PI / 180, height, world);
    world.sub(origin);
    return [world.dot(east), world.dot(north), world.dot(up)];
  };
  const positions: number[] = [], colors: number[] = [], lines: number[] = [];
  const edges = new Set<string>();
  for (const district of data.districts) {
    const rings = district.polygon.map(ring => {
      const last = ring.length - 1;
      return ring.length > 1 && ring[0][0] === ring[last][0] && ring[0][1] === ring[last][1] ? ring.slice(0, -1) : ring;
    });
    if (!rings[0] || rings[0].length < 3) continue;
    const localRings = rings.map(ring => ring.map(local));
    const points = localRings.flat();
    const contour = localRings[0].map(([x, y]) => new THREE.Vector2(x, y));
    const holes = localRings.slice(1).map(ring => ring.map(([x, y]) => new THREE.Vector2(x, y)));
    const color = new THREE.Color(zoningColor(district));
    for (const face of THREE.ShapeUtils.triangulateShape(contour, holes)) {
      for (const index of face) { positions.push(...points[index]); colors.push(color.r, color.g, color.b); }
    }
    for (let r = 0; r < rings.length; r++) for (let i = 0; i < rings[r].length; i++) {
      const next = (i + 1) % rings[r].length;
      const a = rings[r][i].join(','), b = rings[r][next].join(',');
      const key = a < b ? `${a}:${b}` : `${b}:${a}`;
      if (a === b || edges.has(key)) continue;
      edges.add(key); lines.push(...localRings[r][i], ...localRings[r][next]);
    }
  }
  const fill = new THREE.BufferGeometry();
  fill.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  fill.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  return { lat, lon, height, fill, lines };
}
