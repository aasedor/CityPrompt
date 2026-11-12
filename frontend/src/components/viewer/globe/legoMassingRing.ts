import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

/**
 * Plan geometry for facade kits, in local metres (X east, Y north). Pure
 * arithmetic with no renderer imports, so figures and tests can share it.
 */

/** Drop unusable points, repeated points and the closing point of a drawn ring. */
export function cleanRing(ring: readonly number[][]): number[][] {
  const cleaned: number[][] = [];
  for (const coordinate of ring) {
    if (
      !Array.isArray(coordinate)
      || coordinate.length < 2
      || !Number.isFinite(coordinate[0])
      || !Number.isFinite(coordinate[1])
    ) continue;
    const previous = cleaned[cleaned.length - 1];
    if (!previous || previous[0] !== coordinate[0] || previous[1] !== coordinate[1]) {
      cleaned.push([coordinate[0], coordinate[1]]);
    }
  }
  if (
    cleaned.length > 1
    && cleaned[0][0] === cleaned[cleaned.length - 1][0]
    && cleaned[0][1] === cleaned[cleaned.length - 1][1]
  ) cleaned.pop();
  return cleaned;
}

/**
 * A drawn outline in local metres, counter-clockwise, with the first drawn
 * edge kept as wall 0 (the front). null for a degenerate outline.
 */
export function localKitRing(cleaned: readonly number[][], centroidLng: number, centroidLat: number): number[][] | null {
  const metresPerDegreeLongitude = metersPerDegLon(centroidLat);
  let local = cleaned.map(([longitude, latitude]) => [
    (longitude - centroidLng) * metresPerDegreeLongitude,
    (latitude - centroidLat) * METERS_PER_DEG_LAT,
  ]);
  const signedArea = kitRingArea(local);
  if (!signedArea) return null;
  if (signedArea < 0) local = [local[1], local[0], ...local.slice(2).reverse()];
  return local;
}

/** Signed area: positive for a counter-clockwise ring. */
export function kitRingArea(ring: readonly number[][]): number {
  return ring.reduce((sum, point, index) => {
    const next = ring[(index + 1) % ring.length];
    return sum + point[0] * next[1] - next[0] * point[1];
  }, 0) / 2;
}

/** True when a point is inside the ring and at least `clearance` from every edge. */
export function insideKitRing(local: readonly number[][], x: number, y: number, clearance: number): boolean {
  let within = false;
  for (let i = 0, j = local.length - 1; i < local.length; j = i, i += 1) {
    const a = local[i], b = local[j];
    if ((a[1] > y) !== (b[1] > y) && x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]) within = !within;
    const dx = b[0] - a[0], dy = b[1] - a[1];
    const t = Math.max(0, Math.min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy || 1)));
    if (Math.hypot(x - a[0] - t * dx, y - a[1] - t * dy) < clearance) return false;
  }
  return within;
}

const cross = (ax: number, ay: number, bx: number, by: number) => ax * by - ay * bx;

function segmentsCross(a: readonly number[], b: readonly number[], c: readonly number[], d: readonly number[]): boolean {
  const d1 = cross(b[0] - a[0], b[1] - a[1], c[0] - a[0], c[1] - a[1]);
  const d2 = cross(b[0] - a[0], b[1] - a[1], d[0] - a[0], d[1] - a[1]);
  const d3 = cross(d[0] - c[0], d[1] - c[1], a[0] - c[0], a[1] - c[1]);
  const d4 = cross(d[0] - c[0], d[1] - c[1], b[0] - c[0], b[1] - c[1]);
  return d1 * d2 < 0 && d3 * d4 < 0;
}

/**
 * Move every wall of a counter-clockwise ring inward by `distance`, keeping
 * each wall parallel to itself. Corner i of the result belongs to corner i of
 * the ring. null when the ring is too thin for that: a wall would vanish or
 * flip, walls would cross, or a corner would end up nearer than `distance`
 * to some other wall.
 */
export function insetKitRing(ring: readonly number[][], distance: number): number[][] | null {
  const count = ring.length;
  if (count < 3 || !(distance > 0) || !(kitRingArea(ring) > 0)) return null;
  const walls = ring.map((point, index) => {
    const next = ring[(index + 1) % count];
    const length = Math.hypot(next[0] - point[0], next[1] - point[1]);
    if (length < 1e-6) return null;
    const dx = (next[0] - point[0]) / length, dy = (next[1] - point[1]) / length;
    // Inside a counter-clockwise ring is on the left of travel.
    return { x: point[0] - dy * distance, y: point[1] + dx * distance, dx, dy };
  });
  if (walls.some(wall => wall === null)) return null;
  const inset = walls.map((wall, index) => {
    const before = walls[(index + count - 1) % count]!, current = wall!;
    const turn = cross(before.dx, before.dy, current.dx, current.dy);
    // Two walls in one straight line share the moved corner.
    if (Math.abs(turn) < 1e-9) return [current.x, current.y];
    const along = cross(current.x - before.x, current.y - before.y, current.dx, current.dy) / turn;
    return [before.x + before.dx * along, before.y + before.dy * along];
  });
  for (let index = 0; index < count; index += 1) {
    const from = inset[index], to = inset[(index + 1) % count], wall = walls[index]!;
    // A wall that vanished or turned round means the wings met in the middle.
    if ((to[0] - from[0]) * wall.dx + (to[1] - from[1]) * wall.dy < 1e-3) return null;
    if (!insideKitRing(ring, from[0], from[1], distance - 1e-4)) return null;
    for (let other = index + 2; other < count; other += 1) {
      if (index === 0 && other === count - 1) continue;
      if (segmentsCross(from, to, inset[other], inset[(other + 1) % count])) return null;
    }
  }
  return inset;
}

/**
 * The courtyard of a perimeter block: the outline with every wing given
 * `wingDepthM`. null when no courtyard at least `minClearM` across fits, in
 * which case the block is built solid.
 */
export function kitCourtyardRing(ring: readonly number[][], wingDepthM: number, minClearM: number): number[][] | null {
  const courtyard = insetKitRing(ring, wingDepthM);
  if (!courtyard) return null;
  // A courtyard that survives a further half-width inset has that clear width everywhere.
  return minClearM > 0 && !insetKitRing(courtyard, minClearM / 2 - 1e-6) ? null : courtyard;
}

/**
 * Courtyard area of a perimeter block drawn in longitude and latitude, in m².
 * 0 when the outline is built solid. Uses the same steps as the facade kit,
 * so the figures a student reads match the building they see.
 */
export function kitCourtyardAreaM2(coordinates: readonly number[][], wingDepthM: number, minClearM: number): number {
  const cleaned = cleanRing(coordinates);
  if (cleaned.length < 3) return 0;
  const longitude = cleaned.reduce((sum, point) => sum + point[0], 0) / cleaned.length;
  const latitude = cleaned.reduce((sum, point) => sum + point[1], 0) / cleaned.length;
  const local = localKitRing(cleaned, longitude, latitude);
  const courtyard = local && kitCourtyardRing(local, wingDepthM, minClearM);
  return courtyard ? kitRingArea(courtyard) : 0;
}
