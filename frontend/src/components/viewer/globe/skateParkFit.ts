export interface SkateParkPoint {
  x: number;
  y: number;
}

export interface FixedParkProgramSpec {
  widthM: number;
  depthM: number;
  clearanceM: number;
}

export interface FixedParkProgramFit {
  center: SkateParkPoint;
  rotationRad: number;
  widthM: number;
  depthM: number;
  clearanceM: number;
  scale: 1;
}

export type SkateParkProgramFit = FixedParkProgramFit;

export const SKATE_PARK_V0_PROGRAM = Object.freeze({
  widthM: 40 as const,
  depthM: 30 as const,
  clearanceM: 0.5 as const,
  scale: 1 as const,
});

const EPSILON = 1e-7;

function pointOnSegment(point: SkateParkPoint, start: SkateParkPoint, end: SkateParkPoint): boolean {
  const cross = (point.y - start.y) * (end.x - start.x)
    - (point.x - start.x) * (end.y - start.y);
  if (Math.abs(cross) > EPSILON) return false;
  const dot = (point.x - start.x) * (end.x - start.x)
    + (point.y - start.y) * (end.y - start.y);
  if (dot < -EPSILON) return false;
  const lengthSquared = (end.x - start.x) ** 2 + (end.y - start.y) ** 2;
  return dot <= lengthSquared + EPSILON;
}

function pointInRing(point: SkateParkPoint, ring: readonly SkateParkPoint[]): boolean {
  let inside = false;
  for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index++) {
    const start = ring[previous];
    const end = ring[index];
    if (pointOnSegment(point, start, end)) return true;
    if (
      (start.y > point.y) !== (end.y > point.y)
      && point.x < ((end.x - start.x) * (point.y - start.y)) / (end.y - start.y) + start.x
    ) inside = !inside;
  }
  return inside;
}

function distanceToSegment(point: SkateParkPoint, start: SkateParkPoint, end: SkateParkPoint): number {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const lengthSquared = dx * dx + dy * dy;
  if (lengthSquared <= EPSILON) return Math.hypot(point.x - start.x, point.y - start.y);
  const t = Math.max(0, Math.min(1, (
    (point.x - start.x) * dx + (point.y - start.y) * dy
  ) / lengthSquared));
  return Math.hypot(point.x - (start.x + t * dx), point.y - (start.y + t * dy));
}

function distanceToRing(point: SkateParkPoint, ring: readonly SkateParkPoint[]): number {
  let distance = Number.POSITIVE_INFINITY;
  for (let index = 0; index < ring.length; index += 1) {
    distance = Math.min(distance, distanceToSegment(
      point,
      ring[index],
      ring[(index + 1) % ring.length],
    ));
  }
  return distance;
}

function normalizeHalfTurn(angle: number): number {
  let normalized = angle % Math.PI;
  if (normalized < 0) normalized += Math.PI;
  return Math.abs(normalized - Math.PI) < EPSILON ? 0 : normalized;
}

function candidateAngles(ring: readonly SkateParkPoint[]): number[] {
  const values = [0, Math.PI / 2];
  for (let index = 0; index < ring.length; index += 1) {
    const start = ring[index];
    const end = ring[(index + 1) % ring.length];
    if (Math.hypot(end.x - start.x, end.y - start.y) < 2) continue;
    const angle = Math.atan2(end.y - start.y, end.x - start.x);
    values.push(normalizeHalfTurn(angle), normalizeHalfTurn(angle + Math.PI / 2));
  }
  const unique = new Map<string, number>();
  for (const value of values) {
    const normalized = normalizeHalfTurn(value);
    unique.set(normalized.toFixed(7), normalized);
  }
  return [...unique.values()].sort((left, right) => left - right);
}

function candidateCenters(ring: readonly SkateParkPoint[]): SkateParkPoint[] {
  const centroid = ring.reduce(
    (sum, point) => ({ x: sum.x + point.x / ring.length, y: sum.y + point.y / ring.length }),
    { x: 0, y: 0 },
  );
  const xs = ring.map(({ x }) => x);
  const ys = ring.map(({ y }) => y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const centers: SkateParkPoint[] = [centroid];
  for (let xIndex = 0; xIndex <= 16; xIndex += 1) {
    for (let yIndex = 0; yIndex <= 16; yIndex += 1) {
      centers.push({
        x: minX + (maxX - minX) * xIndex / 16,
        y: minY + (maxY - minY) * yIndex / 16,
      });
    }
  }
  return centers.sort((left, right) => (
    Math.hypot(left.x - centroid.x, left.y - centroid.y)
      - Math.hypot(right.x - centroid.x, right.y - centroid.y)
  ));
}

function edgeSamples(
  center: SkateParkPoint,
  rotationRad: number,
  widthM: number,
  depthM: number,
): SkateParkPoint[] {
  const cos = Math.cos(rotationRad);
  const sin = Math.sin(rotationRad);
  const place = (x: number, y: number): SkateParkPoint => ({
    x: center.x + x * cos - y * sin,
    y: center.y + x * sin + y * cos,
  });
  const halfWidth = widthM / 2;
  const halfDepth = depthM / 2;
  const points: SkateParkPoint[] = [place(0, 0)];
  const widthSteps = Math.ceil(widthM);
  const depthSteps = Math.ceil(depthM);
  for (let index = 0; index <= widthSteps; index += 1) {
    const x = -halfWidth + widthM * index / widthSteps;
    points.push(place(x, -halfDepth), place(x, halfDepth));
  }
  for (let index = 0; index <= depthSteps; index += 1) {
    const y = -halfDepth + depthM * index / depthSteps;
    points.push(place(-halfWidth, y), place(halfWidth, y));
  }
  return points;
}

export function fitFixedParkProgram(
  ring: readonly SkateParkPoint[],
  program: FixedParkProgramSpec,
): FixedParkProgramFit | null {
  if (ring.length < 3 || ring.some(({ x, y }) => !Number.isFinite(x) || !Number.isFinite(y))) {
    return null;
  }
  const { widthM, depthM, clearanceM } = program;
  if (
    !Number.isFinite(widthM)
    || !Number.isFinite(depthM)
    || !Number.isFinite(clearanceM)
    || widthM <= 0
    || depthM <= 0
    || clearanceM < 0
  ) return null;
  for (const center of candidateCenters(ring)) {
    for (const rotationRad of candidateAngles(ring)) {
      const samples = edgeSamples(center, rotationRad, widthM, depthM);
      if (samples.every((point) => (
        pointInRing(point, ring) && distanceToRing(point, ring) + EPSILON >= clearanceM
      ))) {
        return { center, rotationRad, widthM, depthM, clearanceM, scale: 1 };
      }
    }
  }
  return null;
}

export function fitSkateParkV0Program(
  ring: readonly SkateParkPoint[],
): SkateParkProgramFit | null {
  return fitFixedParkProgram(ring, SKATE_PARK_V0_PROGRAM);
}
