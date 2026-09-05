/** Exact simple-polygon coverage for world-space tile masks. No hull or buffer. */
export interface TileMaskPoint { x: number; y: number }

const EPSILON = 1e-6;
const cross = (a: TileMaskPoint, b: TileMaskPoint, c: TileMaskPoint) => (
  (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
);
const samePoint = (a: TileMaskPoint, b: TileMaskPoint) => (
  Math.abs(a.x - b.x) <= EPSILON && Math.abs(a.y - b.y) <= EPSILON
);

function onSegment(point: TileMaskPoint, a: TileMaskPoint, b: TileMaskPoint): boolean {
  return Math.abs(cross(a, b, point)) <= EPSILON * Math.max(1, Math.hypot(b.x - a.x, b.y - a.y))
    && point.x >= Math.min(a.x, b.x) - EPSILON && point.x <= Math.max(a.x, b.x) + EPSILON
    && point.y >= Math.min(a.y, b.y) - EPSILON && point.y <= Math.max(a.y, b.y) + EPSILON;
}

function intersects(a: TileMaskPoint, b: TileMaskPoint, c: TileMaskPoint, d: TileMaskPoint): boolean {
  const abC = cross(a, b, c);
  const abD = cross(a, b, d);
  const cdA = cross(c, d, a);
  const cdB = cross(c, d, b);
  return ((abC > 0) !== (abD > 0) && (cdA > 0) !== (cdB > 0))
    || onSegment(c, a, b) || onSegment(d, a, b) || onSegment(a, c, d) || onSegment(b, c, d);
}

/** Strip only redundant closure/consecutive duplicates and collinear vertices.
 * Invalid/non-simple rings are refused, rather than repaired into a larger site. */
export function normalizeTileMaskRing(input: readonly TileMaskPoint[]): TileMaskPoint[] | null {
  if (input.some((point) => !Number.isFinite(point.x) || !Number.isFinite(point.y))) return null;
  const ring = input.filter((point, index) => index === 0 || !samePoint(point, input[index - 1]));
  if (ring.length > 1 && samePoint(ring[0], ring[ring.length - 1])) ring.pop();
  if (ring.length < 3) return null;
  let changed = true;
  while (changed && ring.length >= 3) {
    changed = false;
    for (let index = 0; index < ring.length; index += 1) {
      const before = ring[(index + ring.length - 1) % ring.length];
      const after = ring[(index + 1) % ring.length];
      if (onSegment(ring[index], before, after)) {
        ring.splice(index, 1);
        changed = true;
        break;
      }
    }
  }
  if (ring.length < 3) return null;
  const doubleArea = ring.reduce((sum, point, index) => {
    const next = ring[(index + 1) % ring.length];
    return sum + point.x * next.y - next.x * point.y;
  }, 0);
  if (Math.abs(doubleArea) <= EPSILON) return null;
  for (let first = 0; first < ring.length; first += 1) {
    for (let second = first + 1; second < ring.length; second += 1) {
      if (second === first + 1 || (first === 0 && second === ring.length - 1)) continue;
      if (intersects(ring[first], ring[(first + 1) % ring.length], ring[second], ring[(second + 1) % ring.length])) return null;
    }
  }
  return ring;
}

/** Even/odd crossing rule shared with the fragment shader. Winding-independent;
 * a re-entrant corner excludes its notch, including rays through a vertex. */
export function pointInTileMaskRing(point: TileMaskPoint, ring: readonly TileMaskPoint[]): boolean {
  let inside = false;
  for (let index = 0; index < ring.length; index += 1) {
    const a = ring[index];
    const b = ring[(index + 1) % ring.length];
    if (onSegment(point, a, b)) return true;
    if ((a.y > point.y) !== (b.y > point.y)
      && point.x < (b.x - a.x) * (point.y - a.y) / (b.y - a.y) + a.x) inside = !inside;
  }
  return inside;
}
