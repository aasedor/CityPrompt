import policy from '@/data/canalRoutePolicy.json';
import { stationNormals } from './streetMesh3D';

export const CANAL_ROUTE_POLICY = policy;
export type CanalPoint = { x: number; y: number };

/** Same station frame as ordinary curved streets; the original straight study
 * remains byte-for-byte assembled when it fits the student's route. */
export function canalRoute(route: CanalPoint[]) {
  let length = 0;
  const segments = route.slice(1).map((to, i) => {
    const from = route[i], size = Math.hypot(to.x - from.x, to.y - from.y);
    const segment = { from, to, size, start: length };
    length += size;
    return segment;
  }).filter(s => s.size > 1e-6);
  const first = segments[0], last = segments[segments.length - 1];
  const dx = last ? last.to.x - first.from.x : 0, dy = last ? last.to.y - first.from.y : 0;
  const chord = Math.hypot(dx, dy);
  const straight = chord > 0 && Math.abs(length - chord) < .001
    && route.every(p => Math.abs((p.x - first.from.x) * dy - (p.y - first.from.y) * dx) / chord < .01);
  const original = straight && length >= 80 - 1e-5;
  // A rigid arch needs a straight run for its complete approaches. Coalesce
  // collinear sampled segments before choosing the most central fitting run.
  const runs: Array<{ start: number; size: number; dx: number; dy: number }> = [];
  for (const s of segments) {
    const ux = (s.to.x - s.from.x) / s.size, uy = (s.to.y - s.from.y) / s.size;
    const prev = runs[runs.length - 1];
    if (prev && Math.abs(prev.dx - ux) < 1e-6 && Math.abs(prev.dy - uy) < 1e-6) prev.size += s.size;
    else runs.push({ start: s.start, size: s.size, dx: ux, dy: uy });
  }
  const margin = policy.crossingHalfLengthM + 1;
  const crossings = runs.filter(r => r.size >= 2 * margin).map(r =>
    Math.max(r.start + margin, Math.min(length / 2, r.start + r.size - margin)));
  const crossing = original ? 60 : crossings.sort((a, b) => Math.abs(a - length / 2) - Math.abs(b - length / 2))[0] ?? null;
  const normals = stationNormals(first ? [first.from, ...segments.map(s => s.to)] : []);
  const point = (x: number, station: number, z: number): number[] => {
    let i = segments.findIndex(s => station <= s.start + s.size + 1e-7);
    if (i < 0) i = segments.length - 1;
    const s = segments[i];
    if (!s) return [0, 0, z];
    const t = (station - s.start) / s.size;
    const nx = normals[i].x + (normals[i + 1].x - normals[i].x) * t;
    const ny = normals[i].y + (normals[i + 1].y - normals[i].y) * t;
    return [s.from.x + (s.to.x - s.from.x) * t - nx * x,
      s.from.y + (s.to.y - s.from.y) * t - ny * x, z];
  };
  return { length, segments, original, crossing, point };
}

export function canalRouteProblem(route: CanalPoint[]): string | null {
  if (route.length < 2) return 'Place two points to draw the canal.';
  if (route.some(p => !Number.isFinite(p.x) || !Number.isFinite(p.y))) return 'Choose valid canal route points.';
  const { length, segments } = canalRoute(route);
  if (length < policy.minLengthM - .01) return 'Extend the canal to at least 36 m so its full banks fit.';
  if (length > policy.maxLengthM + .01) return 'Use another canal route to continue beyond 2 km.';
  for (let i = 1; i < segments.length; i++) {
    const a = segments[i - 1], b = segments[i];
    const cos = ((a.to.x - a.from.x) * (b.to.x - b.from.x) + (a.to.y - a.from.y) * (b.to.y - b.from.y)) / a.size / b.size;
    if (cos < -.5) return 'Use a gentler canal bend so the banks do not fold over each other.';
  }
  return null;
}

export function canalWalkingHeight(x: number, station: number, length: number, crossing: number | null, original: boolean) {
  if (station < 0 || station > length || Math.abs(x) > 18) return null;
  const ax = Math.abs(x), halfdepth = 3.2 + Math.max(0, ax - 9) * .3;
  if (crossing !== null) {
    const y = station - crossing;
    if (ax <= 16 && Math.abs(y) <= halfdepth) return .12 + 1.6 * Math.max(0, 1 - (x / 16) ** 2);
    if (ax >= 9 && ax < 16 && Math.abs(y) <= 12)
      return .123 + 1.6 * Math.max(0, 1 - (x / 16) ** 2) * Math.max(0, Math.min(1, (12 - Math.abs(y)) / (12 - halfdepth)));
  }
  if (ax >= 9) return .12;
  if (original ? station <= 8 || (ax > 5 && station < 12 - Math.sqrt(Math.max(0, 16 - (ax - 5) ** 2)))
    : station < 2) return .12;
  return -2.05;
}
