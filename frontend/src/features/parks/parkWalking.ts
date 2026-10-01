/** Navigation for authored park paths. Coordinates are native metres, Z-up.
 * The triangle tops are exported from the same faces as the visible paving.
 * Routes never use water, retaining walls, furniture or foliage as ground. */
export type WalkPoint = [number, number, number];
export interface ParkWalkingNetwork {
  version: number;
  triangles: number[][][];
  entrance: number[];
  maxStepM: number;
  obstacles: number[][];
  routes: { name: string; points: number[][] }[];
}

function blocked(network: ParkWalkingNetwork, x: number, y: number, z?: number) {
  const clearance = network.version === 2 ? .22 : .12;
  return network.obstacles.some(([left, right, bottom, top, low, high]) =>
    (low === undefined || z === undefined || (z + 1.8 > low && z < high - .01))
    && x > left - clearance && x < right + clearance && y > bottom - clearance && y < top + clearance);
}

export function parkWalkHeight(network: ParkWalkingNetwork, x: number, y: number, fromHeight?: number): number | null {
  if (!Number.isFinite(x) || !Number.isFinite(y)) return null;
  let height: number | null = null;
  for (const [a, b, c] of network.triangles) {
    if (x < Math.min(a[0], b[0], c[0]) - 1e-7 || x > Math.max(a[0], b[0], c[0]) + 1e-7
      || y < Math.min(a[1], b[1], c[1]) - 1e-7 || y > Math.max(a[1], b[1], c[1]) + 1e-7) continue;
    const det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1]);
    if (Math.abs(det) < 1e-10) continue;
    const u = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / det;
    const v = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / det;
    const w = 1 - u - v;
    if (Math.min(u, v, w) < -1e-7) continue;
    const z = u * a[2] + v * b[2] + w * c[2];
    if (Number.isFinite(z) && !blocked(network, x, y, z)) {
      const layered = network.version === 2 && fromHeight !== undefined;
      if (height === null || (layered ? Math.abs(z - fromHeight) < Math.abs(height - fromHeight) : z > height)) height = z;
    }
  }
  return height;
}

/** Nearest point is for a deliberate entry/recovery or a small edge slide.
 * Ordinary movement cannot teleport to a disconnected path or another level. */
export function nearestParkWalkPoint(network: ParkWalkingNetwork, x: number, y: number, maxDistance = Infinity, fromHeight?: number): WalkPoint | null {
  let best: WalkPoint | null = null, distance = maxDistance;
  const consider = (px: number, py: number) => {
    const d = Math.hypot(px - x, py - y);
    if (d > distance + 1e-8) return;
    const z = parkWalkHeight(network, px, py, fromHeight);
    if (z === null || (fromHeight !== undefined && Math.abs(z - fromHeight) > network.maxStepM + maxDistance * .5)) return;
    best = [px, py, z]; distance = d;
  };
  consider(x, y);
  if (distance < 1e-8) return best;
  for (const triangle of network.triangles) {
    for (let i = 0; i < 3; i++) {
      const a = triangle[i], b = triangle[(i + 1) % 3];
      const dx = b[0] - a[0], dy = b[1] - a[1], length2 = dx * dx + dy * dy;
      const t = length2 ? Math.max(0, Math.min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / length2)) : 0;
      consider(a[0] + t * dx, a[1] + t * dy);
    }
    if (maxDistance === Infinity) consider(triangle.reduce((n, p) => n + p[0], 0) / 3, triangle.reduce((n, p) => n + p[1], 0) / 3);
  }
  // A click on a bench/tree can recover to its perimeter rather than stay inside it.
  if (maxDistance === Infinity) for (const [left, right, bottom, top] of network.obstacles) {
    for (const px of [left - .2, right + .2]) consider(px, Math.max(bottom - .2, Math.min(top + .2, y)));
    for (const py of [bottom - .2, top + .2]) consider(Math.max(left - .2, Math.min(right + .2, x)), py);
  }
  return best;
}

export function advanceParkWalk(network: ParkWalkingNetwork, from: WalkPoint, target: [number, number]): WalkPoint {
  const distance = Math.hypot(target[0] - from[0], target[1] - from[1]);
  if (!Number.isFinite(distance) || distance === 0) return from;
  // Long frames cannot tunnel across pools or jump down a retaining wall.
  const count = Math.ceil(Math.min(distance, 1) / .07);
  const scale = Math.min(1, 1 / distance);
  const dx = (target[0] - from[0]) * scale / count, dy = (target[1] - from[1]) * scale / count;
  let current = from;
  for (let i = 0; i < count; i++) {
    const x = current[0] + dx, y = current[1] + dy;
    const stepLength = Math.hypot(dx, dy);
    const safe = (px: number, py: number): WalkPoint | null => {
      const z = parkWalkHeight(network, px, py, current[2]);
      return z !== null && Math.abs(z - current[2]) <= network.maxStepM + stepLength * .5 ? [px, py, z] : null;
    };
    let next = safe(x, y);
    if (!next) {
      const projected = nearestParkWalkPoint(network, x, y, stepLength, current[2]);
      const alternatives = [projected, safe(x, current[1]), safe(current[0], y)].filter((p): p is WalkPoint => !!p);
      // Preserve progress along the edge while allowing the user to turn/back away.
      next = alternatives.filter(p => Math.hypot(p[0] - current[0], p[1] - current[1]) <= stepLength * 1.01)
        .sort((a, b) => Math.hypot(a[0] - x, a[1] - y) - Math.hypot(b[0] - x, b[1] - y))[0] ?? null;
    }
    if (!next) break;
    current = next;
  }
  return current;
}
