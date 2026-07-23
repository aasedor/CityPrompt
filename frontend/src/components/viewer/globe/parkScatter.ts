/**
 * Deterministic park prop scatter — pure geometry, no three.js.
 *
 * computeParkPlacements(zone, recipe, plantingStructure?) turns an arbitrary
 * zone polygon into prop placements (lng/lat + yaw + scale). Without a
 * structure it keeps the legacy layout: edge-biased trees with minimum
 * spacing, inward-facing benches along the boundary, and area-gated
 * playground/pavilion clusters with tree clearance.
 *
 * With a `planting_structure` (stamped into green-zone properties by the
 * backend plan generator) trees follow landscape-architecture patterns
 * instead of random scatter — formal allées, naturalistic groves, open
 * meadows, courtyard grids/gardens, plaza rows, screening buffers. Absent or
 * unknown values keep the legacy behavior byte-for-byte.
 *
 * Determinism: seeded by zone.id only — re-renders, sessions, and unrelated
 * edits never reshuffle a park.
 */

import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { pointInPolygon } from '@/utils/coordTransform';
import { seededRandom } from '@/utils/seededRandom';
import {
  NEIGHBORHOOD_PARK,
  PAVED_PLAZA,
  URBAN_POCKET_PARK,
  isDefaultParkRecipe,
  resolveParkRecipe,
  type ParkKitRecipe,
} from '@/data/parkKitRecipes';
import {
  resolveParkLegoContract,
  type ParkProgramAnchorLayout,
} from './parkLegoFamilies';

export type ParkPropId = 'tree' | 'bench' | 'playground' | 'pavilion';

export interface PropPlacement {
  propId: ParkPropId;
  lng: number;
  lat: number;
  yawRad: number;
  scale: number;
}

interface ScatterZone {
  id: string;
  coordinates: number[][];
}

/** Landscape-architecture planting patterns the backend plan generator stamps
 *  into green-zone properties. Anything else falls back to legacy scatter. */
export const PLANTING_STRUCTURES = [
  'formal_allee',
  'naturalistic_grove',
  'open_meadow',
  'active_recreation',
  'formal_quad',
  'garden_courtyard',
  'japanese_stroll_garden',
  'sports_perimeter',
  'reservoir_perimeter',
  'botanical_collection',
  'nature_play_grove',
  'paved_plaza',
  'buffer_edge',
] as const;

export type PlantingStructure = (typeof PLANTING_STRUCTURES)[number];

export function resolvePlantingStructure(value: unknown): PlantingStructure | null {
  return typeof value === 'string' && (PLANTING_STRUCTURES as readonly string[]).includes(value)
    ? (value as PlantingStructure)
    : null;
}

/** Which recipe furniture each structure keeps. Formal/courtyard/plaza
 *  treatments keep benches but drop the big clusters (their centers stay
 *  open by design); a screening buffer is planting only. */
const STRUCTURE_FURNITURE: Record<
  PlantingStructure,
  { playground: boolean; pavilion: boolean; benches: boolean }
> = {
  formal_allee: { playground: false, pavilion: false, benches: true },
  naturalistic_grove: { playground: true, pavilion: true, benches: true },
  open_meadow: { playground: false, pavilion: true, benches: true },
  active_recreation: { playground: true, pavilion: true, benches: true },
  formal_quad: { playground: false, pavilion: false, benches: true },
  garden_courtyard: { playground: false, pavilion: false, benches: true },
  japanese_stroll_garden: { playground: false, pavilion: false, benches: true },
  sports_perimeter: { playground: false, pavilion: false, benches: true },
  reservoir_perimeter: { playground: false, pavilion: false, benches: true },
  botanical_collection: { playground: false, pavilion: false, benches: true },
  nature_play_grove: { playground: false, pavilion: false, benches: true },
  paved_plaza: { playground: false, pavilion: false, benches: true },
  buffer_edge: { playground: false, pavilion: false, benches: false },
};

const LEGACY_FURNITURE = { playground: true, pavilion: true, benches: true };

function polygonAreaM2(pts: number[][]): number {
  let sum = 0;
  for (let i = 0; i < pts.length; i++) {
    const j = (i + 1) % pts.length;
    sum += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1];
  }
  return Math.abs(sum) / 2;
}

/** Even stations along the ring perimeter with inward-pointing normals. */
function perimeterStations(pts: number[][], count: number): Array<{ x: number; y: number; nx: number; ny: number }> {
  const segs: Array<{ ax: number; ay: number; bx: number; by: number; len: number }> = [];
  let total = 0;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i];
    const b = pts[(i + 1) % pts.length];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (len > 0) {
      segs.push({ ax: a[0], ay: a[1], bx: b[0], by: b[1], len });
      total += len;
    }
  }
  if (!segs.length || count <= 0) return [];

  const out: Array<{ x: number; y: number; nx: number; ny: number }> = [];
  for (let k = 0; k < count; k++) {
    let dist = ((k + 0.5) / count) * total;
    for (const seg of segs) {
      if (dist > seg.len) {
        dist -= seg.len;
        continue;
      }
      const t = dist / seg.len;
      const x = seg.ax + (seg.bx - seg.ax) * t;
      const y = seg.ay + (seg.by - seg.ay) * t;
      // candidate normal; flipped below if it points outside
      let nx = -(seg.by - seg.ay) / seg.len;
      let ny = (seg.bx - seg.ax) / seg.len;
      if (!pointInPolygon(x + nx * 0.5, y + ny * 0.5, pts)) {
        nx = -nx;
        ny = -ny;
      }
      out.push({ x, y, nx, ny });
      break;
    }
  }
  return out;
}

interface RingEdge {
  ax: number;
  ay: number;
  /** unit direction along the edge */
  ux: number;
  uy: number;
  /** inward-pointing unit normal */
  nx: number;
  ny: number;
  len: number;
}

/** Ring edges with unit direction and inward-pointing normal. */
function ringEdges(pts: number[][]): RingEdge[] {
  const out: RingEdge[] = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i];
    const b = pts[(i + 1) % pts.length];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (len <= 0) continue;
    const ux = (b[0] - a[0]) / len;
    const uy = (b[1] - a[1]) / len;
    let nx = -uy;
    let ny = ux;
    const mx = (a[0] + b[0]) / 2;
    const my = (a[1] + b[1]) / 2;
    if (!pointInPolygon(mx + nx * 0.5, my + ny * 0.5, pts)) {
      nx = -nx;
      ny = -ny;
    }
    out.push({ ax: a[0], ay: a[1], ux, uy, nx, ny, len });
  }
  return out;
}

/** Uniform stations along an edge, inset inward. The run is centred (equal
 *  end margins) so a row reads as intentional; `shift` staggers a second row
 *  half a bay for screening belts. */
function rowPoints(
  edge: RingEdge,
  inset: number,
  spacing: number,
  endMargin: number,
  shift = 0,
): Array<{ x: number; y: number }> {
  const usable = edge.len - 2 * endMargin;
  if (usable < 0 || spacing <= 0) return [];
  const count = Math.floor(usable / spacing) + 1;
  const start = (edge.len - (count - 1) * spacing) / 2 + shift;
  const out: Array<{ x: number; y: number }> = [];
  for (let k = 0; k < count; k++) {
    const t = start + k * spacing;
    if (t < endMargin || t > edge.len - endMargin) continue;
    out.push({
      x: edge.ax + edge.ux * t + edge.nx * inset,
      y: edge.ay + edge.uy * t + edge.ny * inset,
    });
  }
  return out;
}

interface AxisFrame {
  yaw: number;
  umin: number;
  umax: number;
  vmin: number;
  vmax: number;
  toXY: (u: number, v: number) => { x: number; y: number };
}

/** Frame aligned to the polygon's longest edge — the courtyard "long axis".
 *  u runs along that edge, v across it; extents bound the whole ring. */
function longAxisFrame(pts: number[][]): AxisFrame | null {
  let ux = 0;
  let uy = 0;
  let best = 0;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i];
    const b = pts[(i + 1) % pts.length];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (len > best) {
      best = len;
      ux = (b[0] - a[0]) / len;
      uy = (b[1] - a[1]) / len;
    }
  }
  if (best === 0) return null;
  let umin = Infinity;
  let umax = -Infinity;
  let vmin = Infinity;
  let vmax = -Infinity;
  for (const [x, y] of pts) {
    const u = x * ux + y * uy;
    const v = -x * uy + y * ux;
    umin = Math.min(umin, u);
    umax = Math.max(umax, u);
    vmin = Math.min(vmin, v);
    vmax = Math.max(vmax, v);
  }
  return {
    yaw: Math.atan2(uy, ux),
    umin,
    umax,
    vmin,
    vmax,
    toXY: (u, v) => ({ x: u * ux - v * uy, y: u * uy + v * ux }),
  };
}

/** Distance from a point to the nearest ring edge. */
function distanceToBoundary(pts: number[][], x: number, y: number): number {
  let best = Infinity;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i];
    const b = pts[(i + 1) % pts.length];
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const l2 = dx * dx + dy * dy;
    const t = l2 > 0 ? Math.max(0, Math.min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / l2)) : 0;
    best = Math.min(best, Math.hypot(x - (a[0] + dx * t), y - (a[1] + dy * t)));
  }
  return best;
}

interface ParkProgramExclusion {
  x: number;
  y: number;
  r: number;
}

export interface ContainedParkProgramAnchor {
  x: number;
  y: number;
  /** Oriented parcel long-axis bearing in local ENU radians. */
  yawRad: number;
}

interface OrientedProgramFrame {
  ux: number;
  uy: number;
  vx: number;
  vy: number;
  minU: number;
  maxU: number;
  minV: number;
  maxV: number;
  yawRad: number;
}

function orientedProgramFrame(ring: number[][]): OrientedProgramFrame | null {
  let best: (OrientedProgramFrame & { area: number; angleKey: number }) | null = null;
  for (let index = 0; index < ring.length; index += 1) {
    const start = ring[index];
    const end = ring[(index + 1) % ring.length];
    const dx = end[0] - start[0];
    const dy = end[1] - start[1];
    if (Math.hypot(dx, dy) < 1e-6) continue;
    let angle = Math.atan2(dy, dx);
    // Rectangle axes are undirected. Keep the long axis as U and choose the
    // eastward representative so V consistently points toward local north.
    angle = ((angle % Math.PI) + Math.PI) % Math.PI;
    const measure = (candidateAngle: number) => {
      const ux = Math.cos(candidateAngle);
      const uy = Math.sin(candidateAngle);
      const vx = -uy;
      const vy = ux;
      const projectionsU = ring.map(([x, y]) => x * ux + y * uy);
      const projectionsV = ring.map(([x, y]) => x * vx + y * vy);
      return {
        ux,
        uy,
        vx,
        vy,
        minU: Math.min(...projectionsU),
        maxU: Math.max(...projectionsU),
        minV: Math.min(...projectionsV),
        maxV: Math.max(...projectionsV),
      };
    };
    let candidate = measure(angle);
    const candidateWidth = candidate.maxU - candidate.minU;
    const candidateHeight = candidate.maxV - candidate.minV;
    const squareTolerance = Math.max(candidateWidth, candidateHeight) * 0.001;
    if (candidateWidth + squareTolerance < candidateHeight) {
      angle = (angle + Math.PI / 2) % Math.PI;
      candidate = measure(angle);
    }
    // cos(angle) may be negative after the 90-degree long-axis swap. Flip
    // both axes without changing bounds semantics so U remains eastward.
    if (candidate.ux < -1e-9 || (Math.abs(candidate.ux) <= 1e-9 && candidate.uy < 0)) {
      angle = (angle + Math.PI) % (Math.PI * 2);
      candidate = measure(angle);
    }
    const width = candidate.maxU - candidate.minU;
    const height = candidate.maxV - candidate.minV;
    const area = width * height;
    const angleKey = ((angle % Math.PI) + Math.PI) % Math.PI;
    if (
      !best
      || area < best.area - 1e-5
      || (Math.abs(area - best.area) <= 1e-5 && angleKey < best.angleKey)
    ) {
      best = { ...candidate, area, angleKey, yawRad: angle };
    }
  }
  return best;
}

/**
 * Resolve a normalized authored anchor inside the polygon's minimum-area
 * oriented frame, then deterministically find the nearest whole-disc fit when
 * a concavity or exclusion blocks that exact point.
 */
export function resolveContainedParkProgramAnchor(
  ring: number[][],
  normalizedAnchor: readonly [number, number],
  clearanceM: number,
  exclusions: readonly ParkProgramExclusion[] = [],
): ContainedParkProgramAnchor | null {
  const frame = orientedProgramFrame(ring);
  if (!frame || clearanceM < 0) return null;
  const width = frame.maxU - frame.minU;
  const height = frame.maxV - frame.minV;
  const toPoint = (normalizedX: number, normalizedY: number) => {
    const u = frame.minU + width * normalizedX;
    // Program coordinates are image-like: y=0 is the oriented north edge.
    const v = frame.maxV - height * normalizedY;
    return {
      x: frame.ux * u + frame.vx * v,
      y: frame.uy * u + frame.vy * v,
      yawRad: frame.yawRad,
    };
  };
  const desired = toPoint(normalizedAnchor[0], normalizedAnchor[1]);
  const fits = (candidate: ContainedParkProgramAnchor) => (
    pointInPolygon(candidate.x, candidate.y, ring)
    && distanceToBoundary(ring, candidate.x, candidate.y) >= clearanceM - 1e-6
    && exclusions.every((exclusion) => (
      Math.hypot(candidate.x - exclusion.x, candidate.y - exclusion.y)
        >= clearanceM + exclusion.r - 1e-6
    ))
  );
  if (fits(desired)) return desired;

  const candidates: ContainedParkProgramAnchor[] = [toPoint(0.5, 0.5)];
  const gridSteps = 20;
  for (let yIndex = 0; yIndex <= gridSteps; yIndex += 1) {
    for (let xIndex = 0; xIndex <= gridSteps; xIndex += 1) {
      candidates.push(toPoint(xIndex / gridSteps, yIndex / gridSteps));
    }
  }
  return candidates
    .filter(fits)
    .sort((left, right) => (
      Math.hypot(left.x - desired.x, left.y - desired.y)
        - Math.hypot(right.x - desired.x, right.y - desired.y)
      || left.x - right.x
      || left.y - right.y
    ))[0] ?? null;
}

// ---- planting structures ---------------------------------------------------
// Each function places TREES only; furniture (benches/playground/pavilion) is
// gated per structure in computeParkPlacements. Every candidate goes through
// ctx.canPlace, so containment, clearance discs, and min spacing hold for all
// structures. Row gaps/spacings sit 0.25m+ above minSpacing so float noise on
// rotated edges never lands exactly on the rejection knife-edge.

interface TreeCtx {
  local: number[][];
  rng: () => number;
  tr: ParkKitRecipe['trees'];
  /** recipe-normal tree count for this area (perHectare x area) */
  target: number;
  bbox: { minX: number; minY: number; maxX: number; maxY: number };
  /** containment + clearance-disc + min-spacing guard */
  canPlace: (x: number, y: number) => boolean;
  /** append a tree (no re-check — call canPlace first) */
  push: (x: number, y: number, yawRad: number, scale: number) => void;
  count: () => number;
}

/** Legacy scatter: edge-biased rejection sampling. Also the fallback when no
 *  structure is present — rng call order is load-bearing here, it must keep
 *  producing today's layouts for existing parks. */
function placeLegacyScatter(ctx: TreeCtx): void {
  const { rng, tr, bbox } = ctx;
  const edgeStations = perimeterStations(ctx.local, Math.max(16, ctx.target));
  let attempts = 0;
  const maxAttempts = ctx.target * 25;
  while (ctx.count() < ctx.target && attempts < maxAttempts) {
    attempts++;
    let x: number;
    let y: number;
    if (rng() < tr.edgeBias && edgeStations.length) {
      const st = edgeStations[Math.floor(rng() * edgeStations.length)];
      const inset = 2 + rng() * Math.max(0.1, tr.bandDepth_m - 2);
      x = st.x + st.nx * inset;
      y = st.y + st.ny * inset;
    } else {
      x = bbox.minX + rng() * (bbox.maxX - bbox.minX);
      y = bbox.minY + rng() * (bbox.maxY - bbox.minY);
    }
    if (!ctx.canPlace(x, y)) continue;
    ctx.push(
      x,
      y,
      rng() * Math.PI * 2,
      tr.scaleJitter[0] + rng() * (tr.scaleJitter[1] - tr.scaleJitter[0]),
    );
  }
}

/** Urban pocket parks need to read as complete outdoor rooms from every
 * approach. Distribute an irregular but balanced mature canopy around the
 * full perimeter instead of allowing seeded rejection sampling to cluster on
 * one or two edges. The center remains open for the authored lawn and paths. */
function placePocketParkFrame(ctx: TreeCtx): void {
  const { rng, tr, target } = ctx;
  const candidateCount = Math.max(24, target * 4);
  const stations = perimeterStations(ctx.local, candidateCount);
  if (!stations.length) return;
  const rotation = Math.floor(rng() * stations.length);
  for (let slot = 0; slot < target; slot += 1) {
    const base = Math.floor(((slot + 0.2 + rng() * 0.6) * stations.length) / target);
    for (let probe = 0; probe < 4; probe += 1) {
      const st = stations[(rotation + base + probe) % stations.length];
      const inset = 2.2 + rng() * Math.max(0.5, tr.bandDepth_m - 2.2);
      const tangentJitter = (rng() - 0.5) * 1.4;
      const x = st.x + st.nx * inset - st.ny * tangentJitter;
      const y = st.y + st.ny * inset + st.nx * tangentJitter;
      if (!ctx.canPlace(x, y)) continue;
      ctx.push(
        x,
        y,
        rng() * Math.PI * 2,
        tr.scaleJitter[0] + rng() * (tr.scaleJitter[1] - tr.scaleJitter[0]),
      );
      break;
    }
  }
}

/** Modern pocket/courtyard variant: the same restrained specimen count is
 * organized as an exact, evenly spaced perimeter frame. It preserves the
 * clear lawn room while making the formal planting selection visible; unlike
 * the general formal-quad routine it never fills the compact park centre. */
function placePocketParkFormalFrame(ctx: TreeCtx): void {
  const target = Math.max(1, ctx.target);
  const stations = perimeterStations(ctx.local, target);
  if (!stations.length) return;
  const rotation = Math.floor(ctx.rng() * stations.length);
  for (let slot = 0; slot < stations.length; slot += 1) {
    const station = stations[(slot + rotation) % stations.length];
    const inset = Math.min(4.2, Math.max(2.4, ctx.tr.bandDepth_m * 0.48));
    const x = station.x + station.nx * inset;
    const y = station.y + station.ny * inset;
    if (!ctx.canPlace(x, y)) continue;
    ctx.push(x, y, Math.atan2(station.ny, station.nx) + Math.PI / 2, 1);
  }
}

/** formal_allee — Parisian jardin: double rows at uniform spacing/scale along
 *  the two longest edges, a single row on the remaining edges when they have
 *  room, and an open centre (no interior scatter). */
function placeFormalAllee(ctx: TreeCtx): void {
  const { rng, tr } = ctx;
  const edges = ringEdges(ctx.local).slice().sort((a, b) => b.len - a.len);
  if (!edges.length) return;
  // one spacing draw per zone keeps every row in step
  const spacing = Math.max(tr.minSpacing_m + 0.25, 7 + rng() * 2);
  const rowGap = Math.max(tr.minSpacing_m + 0.25, 6);
  const inset = 2.5;
  edges.forEach((edge, rank) => {
    const rows = rank < 2 ? 2 : 1;
    if (rows === 1 && edge.len < spacing * 3) return; // no room for a legible row
    const yaw = Math.atan2(edge.uy, edge.ux);
    for (let r = 0; r < rows; r++) {
      for (const pt of rowPoints(edge, inset + r * rowGap, spacing, spacing * 0.5)) {
        if (ctx.canPlace(pt.x, pt.y)) ctx.push(pt.x, pt.y, yaw, 1);
      }
    }
  });
}

/** naturalistic_grove — Olmsted park: 2-4 grove clusters at varied scale with
 *  open meadow preserved between them, plus a handful of scattered singles. */
function placeNaturalisticGrove(ctx: TreeCtx): void {
  const { rng, bbox } = ctx;
  const groveCount = 2 + Math.floor(rng() * 3); // 2..4
  const groves: Array<{ x: number; y: number; r: number }> = [];
  let seeds = 0;
  while (groves.length < groveCount && seeds < groveCount * 30) {
    seeds++;
    const r = 12 + rng() * 8; // 12..20m
    const x = bbox.minX + rng() * (bbox.maxX - bbox.minX);
    const y = bbox.minY + rng() * (bbox.maxY - bbox.minY);
    if (!pointInPolygon(x, y, ctx.local)) continue;
    // keep groves apart so the meadow between them survives
    if (groves.some((g) => Math.hypot(x - g.x, y - g.y) < (g.r + r) * 0.9)) continue;
    groves.push({ x, y, r });
  }
  if (!groves.length) {
    placeLegacyScatter(ctx); // pathological ring — behave like an unplanned park
    return;
  }
  const groveTarget = Math.max(groves.length * 3, Math.round(ctx.target * 0.85));
  let attempts = 0;
  const maxAttempts = groveTarget * 30;
  while (ctx.count() < groveTarget && attempts < maxAttempts) {
    attempts++;
    const g = groves[Math.floor(rng() * groves.length)];
    const ang = rng() * Math.PI * 2;
    const rad = g.r * Math.sqrt(rng());
    const x = g.x + Math.cos(ang) * rad;
    const y = g.y + Math.sin(ang) * rad;
    if (!ctx.canPlace(x, y)) continue;
    ctx.push(x, y, rng() * Math.PI * 2, 0.8 + rng() * 0.5); // varied 0.8..1.3
  }
  // a handful of scattered singles in the meadow between groves
  const singleTarget = ctx.count() + Math.min(6, Math.max(2, Math.round(ctx.target * 0.15)));
  attempts = 0;
  while (ctx.count() < singleTarget && attempts < 180) {
    attempts++;
    const x = bbox.minX + rng() * (bbox.maxX - bbox.minX);
    const y = bbox.minY + rng() * (bbox.maxY - bbox.minY);
    if (!ctx.canPlace(x, y)) continue;
    ctx.push(x, y, rng() * Math.PI * 2, 0.8 + rng() * 0.5);
  }
}

/** open_meadow — sparse passive lawn: ~30% of the normal tree count as
 *  scattered singles plus 1-3 outsized specimens near (never on) the
 *  centroid, with the perimeter belt kept light. */
function placeOpenMeadow(ctx: TreeCtx): void {
  const { rng, tr, bbox } = ctx;
  const specimens = 1 + Math.floor(rng() * 3); // 1..3
  const reach = Math.min(bbox.maxX - bbox.minX, bbox.maxY - bbox.minY);
  let placed = 0;
  let attempts = 0;
  while (placed < specimens && attempts < specimens * 20) {
    attempts++;
    const ang = rng() * Math.PI * 2;
    const rad = reach * (0.08 + rng() * 0.17); // near, never on, the centroid
    const x = Math.cos(ang) * rad;
    const y = Math.sin(ang) * rad;
    if (!ctx.canPlace(x, y)) continue;
    ctx.push(x, y, rng() * Math.PI * 2, 1.3 + rng() * 0.2); // 1.3..1.5
    placed++;
  }
  const singleTarget = ctx.count() + Math.max(2, Math.round(ctx.target * 0.3));
  attempts = 0;
  const maxAttempts = Math.max(60, ctx.target * 25);
  while (ctx.count() < singleTarget && attempts < maxAttempts) {
    attempts++;
    const x = bbox.minX + rng() * (bbox.maxX - bbox.minX);
    const y = bbox.minY + rng() * (bbox.maxY - bbox.minY);
    if (distanceToBoundary(ctx.local, x, y) < 5) continue; // light perimeter belt
    if (!ctx.canPlace(x, y)) continue;
    ctx.push(
      x,
      y,
      rng() * Math.PI * 2,
      tr.scaleJitter[0] + rng() * (tr.scaleJitter[1] - tr.scaleJitter[0]),
    );
  }
}

/** active_recreation — programmed park: playground/pavilion/benches as today,
 *  but trees gather into shade clusters just outside the equipment clearance
 *  rings and around benches instead of uniform scatter. */
function placeActiveRecreation(
  ctx: TreeCtx,
  shadeAnchors: Array<{ x: number; y: number; standoff: number }>,
): void {
  if (!shadeAnchors.length) {
    placeLegacyScatter(ctx); // nothing to shade — plain park behavior
    return;
  }
  const { rng, tr, bbox } = ctx;
  let attempts = 0;
  const maxAttempts = ctx.target * 30;
  while (ctx.count() < ctx.target && attempts < maxAttempts) {
    attempts++;
    let x: number;
    let y: number;
    if (rng() < 0.7) {
      // shade cluster: hug the clearance ring / bench, never inside it
      const a = shadeAnchors[Math.floor(rng() * shadeAnchors.length)];
      const ang = rng() * Math.PI * 2;
      const rad = a.standoff + 1.5 + rng() * 6;
      x = a.x + Math.cos(ang) * rad;
      y = a.y + Math.sin(ang) * rad;
    } else {
      x = bbox.minX + rng() * (bbox.maxX - bbox.minX);
      y = bbox.minY + rng() * (bbox.maxY - bbox.minY);
    }
    if (!ctx.canPlace(x, y)) continue;
    ctx.push(
      x,
      y,
      rng() * Math.PI * 2,
      tr.scaleJitter[0] + rng() * (tr.scaleJitter[1] - tr.scaleJitter[0]),
    );
  }
}

/** formal_quad — courtyard bosque: a regular grid aligned to the polygon's
 *  long axis (degrading to a single axis row on narrow courts), uniform
 *  scale and yaw. */
function placeFormalQuad(ctx: TreeCtx): void {
  const frame = longAxisFrame(ctx.local);
  if (!frame) return;
  const { rng, tr } = ctx;
  const spacing = Math.max(tr.minSpacing_m + 0.5, 7 + rng() * 2);
  const inset = 3;
  const uSpan = frame.umax - frame.umin - inset * 2;
  const vSpan = frame.vmax - frame.vmin - inset * 2;
  if (uSpan < 0 || vSpan < 0) return;
  const nu = Math.floor(uSpan / spacing) + 1;
  const nv = Math.floor(vSpan / spacing) + 1;
  const u0 = frame.umin + (frame.umax - frame.umin - (nu - 1) * spacing) / 2;
  const v0 = frame.vmin + (frame.vmax - frame.vmin - (nv - 1) * spacing) / 2;
  for (let i = 0; i < nu; i++) {
    for (let j = 0; j < nv; j++) {
      const { x, y } = frame.toXY(u0 + i * spacing, v0 + j * spacing);
      if (ctx.canPlace(x, y)) ctx.push(x, y, frame.yaw, 1);
    }
  }
}

/** garden_courtyard — informal court: small 2-3 tree clusters tucked into the
 *  corners plus one off-centre specimen. */
function placeGardenCourtyard(ctx: TreeCtx, includeSpecimen = true): void {
  const frame = longAxisFrame(ctx.local);
  if (!frame) return;
  const { rng, tr } = ctx;
  const inset = Math.max(3, tr.minSpacing_m * 0.6);
  const corners = [
    frame.toXY(frame.umin + inset, frame.vmin + inset),
    frame.toXY(frame.umax - inset, frame.vmin + inset),
    frame.toXY(frame.umax - inset, frame.vmax - inset),
    frame.toXY(frame.umin + inset, frame.vmax - inset),
  ];
  for (const corner of corners) {
    if (!pointInPolygon(corner.x, corner.y, ctx.local)) continue;
    const clusterSize = 2 + Math.floor(rng() * 2); // 2..3
    let placed = 0;
    let attempts = 0;
    while (placed < clusterSize && attempts < clusterSize * 12) {
      attempts++;
      // first tree sits on the corner anchor, the rest crowd around it
      const ang = rng() * Math.PI * 2;
      const rad = placed === 0 ? 0 : tr.minSpacing_m * (1.05 + rng() * 0.35);
      const x = corner.x + Math.cos(ang) * rad;
      const y = corner.y + Math.sin(ang) * rad;
      if (!ctx.canPlace(x, y)) continue;
      ctx.push(x, y, rng() * Math.PI * 2, 0.85 + rng() * 0.3);
      placed++;
    }
  }
  // Japanese stroll gardens omit the centre specimen so the pond and bridge
  // program stay clear; generic garden courts keep the focal tree.
  if (!includeSpecimen) return;
  // one specimen, deliberately off-centre
  const reach = Math.min(frame.umax - frame.umin, frame.vmax - frame.vmin);
  let attempts = 0;
  while (attempts < 15) {
    attempts++;
    const ang = rng() * Math.PI * 2;
    const rad = reach * (0.1 + rng() * 0.12);
    const x = Math.cos(ang) * rad;
    const y = Math.sin(ang) * rad;
    if (!ctx.canPlace(x, y)) continue;
    ctx.push(x, y, rng() * Math.PI * 2, 1.3 + rng() * 0.15);
    break;
  }
}

/** Botanical collections use the naturalistic grove rhythm, but their exact
 * diagram has four no-plant program rooms plus a continuous elliptical path.
 * Keep that source-of-truth geometry clear before the live tree kit is
 * instanced; the final render receives the same spatial hierarchy. */
function botanicalProgramBlocks(
  bbox: TreeCtx['bbox'],
  x: number,
  y: number,
): boolean {
  const width = bbox.maxX - bbox.minX;
  const height = bbox.maxY - bbox.minY;
  const at = (nx: number, nyFromNorth: number) => ({
    x: bbox.minX + nx * width,
    y: bbox.maxY - nyFromNorth * height,
  });

  const conservatory = at(0.22, 0.24);
  if (
    Math.abs(x - conservatory.x) <= 24 / 2 + 2.5
    && Math.abs(y - conservatory.y) <= 14 / 2 + 2.5
  ) return true;

  const beds = [
    { ...at(0.48, 0.35), rx: 28 / 2 + 2.5, ry: 16 / 2 + 2.5 },
    { ...at(0.70, 0.66), rx: 30 / 2 + 2.5, ry: 17 / 2 + 2.5 },
    { ...at(0.35, 0.72), rx: 26 / 2 + 2.5, ry: 14 / 2 + 2.5 },
  ];
  if (beds.some((bed) => (
    ((x - bed.x) / bed.rx) ** 2 + ((y - bed.y) / bed.ry) ** 2 <= 1
  ))) return true;

  // The guide loop is 82% x 66% of the site bbox and 2.8 m wide. A 2.6 m
  // trunk/crown safety offset keeps even varied tree scales out of its clear
  // walking width.
  const center = at(0.5, 0.5);
  const rx = Math.max(1, width * 0.82 / 2);
  const ry = Math.max(1, height * 0.66 / 2);
  const ellipseRadius = Math.hypot((x - center.x) / rx, (y - center.y) / ry);
  const distanceFromLoopM = Math.abs(ellipseRadius - 1) * Math.min(rx, ry);
  return distanceFromLoopM < 4;
}

/** sports_perimeter — keep the entire programmed field/track interior clear.
 * Trees form a sparse, deterministic perimeter row outside safety areas. */
function placeSportsPerimeter(ctx: TreeCtx): void {
  const { rng, tr } = ctx;
  const spacing = Math.max(12, tr.minSpacing_m);
  for (const edge of ringEdges(ctx.local)) {
    for (const point of rowPoints(edge, 3.5, spacing, spacing * 0.5)) {
      if (ctx.count() >= ctx.target) return;
      if (!ctx.canPlace(point.x, point.y)) continue;
      ctx.push(
        point.x,
        point.y,
        Math.atan2(edge.uy, edge.ux),
        tr.scaleJitter[0] + rng() * (tr.scaleJitter[1] - tr.scaleJitter[0]),
      );
    }
  }
}

/** reservoir_perimeter — distribute a sparse tree belt evenly around the
 * outer parcel edge. The central programmed water body and its continuous
 * trail loop remain completely free of standing vegetation. */
function placeReservoirPerimeter(ctx: TreeCtx): void {
  const { rng, tr } = ctx;
  const spacing = Math.max(9, tr.minSpacing_m + 0.5);
  const candidates = ringEdges(ctx.local).flatMap((edge) => (
    rowPoints(edge, 4.5, spacing, spacing * 0.5).map((point) => ({ point, edge }))
  ));
  const count = Math.min(ctx.target, candidates.length);
  for (let index = 0; index < count; index += 1) {
    const candidate = candidates[Math.floor(((index + 0.5) * candidates.length) / count)];
    const { x, y } = candidate.point;
    if (!ctx.canPlace(x, y)) continue;
    ctx.push(
      x,
      y,
      Math.atan2(candidate.edge.uy, candidate.edge.ux),
      tr.scaleJitter[0] + rng() * (tr.scaleJitter[1] - tr.scaleJitter[0]),
    );
  }
}

/** paved_plaza — hard plaza: one modest row along the single longest edge,
 *  capped at six trees; the floor stays open. */
function placePavedPlaza(ctx: TreeCtx): void {
  const { rng, tr } = ctx;
  const edges = ringEdges(ctx.local).slice().sort((a, b) => b.len - a.len);
  if (!edges.length) return;
  const edge = edges[0];
  const spacing = Math.max(tr.minSpacing_m + 0.25, 7 + rng() * 2);
  const pts = rowPoints(edge, 2.5, spacing, spacing * 0.5);
  const start = Math.max(0, Math.floor((pts.length - 6) / 2)); // centre the capped run
  const yaw = Math.atan2(edge.uy, edge.ux);
  for (const pt of pts.slice(start, start + 6)) {
    if (ctx.canPlace(pt.x, pt.y)) ctx.push(pt.x, pt.y, yaw, 1);
  }
}

/** buffer_edge — screening belt: a dense, staggered double row around the
 *  whole perimeter with only sparse interior fill. */
function placeBufferEdge(ctx: TreeCtx): void {
  const { rng, tr, bbox } = ctx;
  const spacing = Math.max(5, tr.minSpacing_m + 0.25);
  const rowGap = spacing;
  for (const edge of ringEdges(ctx.local)) {
    for (let r = 0; r < 2; r++) {
      // half-bay stagger: the standard screening pattern, and it keeps the
      // cross-row diagonal above min spacing
      for (const pt of rowPoints(edge, 2 + r * rowGap, spacing, 2, r === 1 ? spacing / 2 : 0)) {
        if (!ctx.canPlace(pt.x, pt.y)) continue;
        ctx.push(
          pt.x,
          pt.y,
          rng() * Math.PI * 2,
          tr.scaleJitter[0] + rng() * (tr.scaleJitter[1] - tr.scaleJitter[0]),
        );
      }
    }
  }
  // sparse interior fill, clear of the belt
  const interiorTarget = ctx.count() + Math.max(1, Math.round(ctx.target * 0.15));
  const standoff = 2 + rowGap + tr.minSpacing_m;
  let attempts = 0;
  const maxAttempts = Math.max(40, ctx.target * 10);
  while (ctx.count() < interiorTarget && attempts < maxAttempts) {
    attempts++;
    const x = bbox.minX + rng() * (bbox.maxX - bbox.minX);
    const y = bbox.minY + rng() * (bbox.maxY - bbox.minY);
    if (distanceToBoundary(ctx.local, x, y) < standoff) continue;
    if (!ctx.canPlace(x, y)) continue;
    ctx.push(
      x,
      y,
      rng() * Math.PI * 2,
      tr.scaleJitter[0] + rng() * (tr.scaleJitter[1] - tr.scaleJitter[0]),
    );
  }
}

/** Geodesic ring area in m² (local-ENU shoelace about the vertex centroid). */
function ringAreaM2(ring: number[][]): number {
  if (!ring || ring.length < 3) return 0;
  let lng0 = 0;
  let lat0 = 0;
  for (const c of ring) {
    lng0 += c[0];
    lat0 += c[1];
  }
  lng0 /= ring.length;
  lat0 /= ring.length;
  const mPerLon = metersPerDegLon(lat0);
  return polygonAreaM2(
    ring.map((c) => [(c[0] - lng0) * mPerLon, (c[1] - lat0) * METERS_PER_DEG_LAT]),
  );
}

/** Same pocket-vs-neighborhood banding as resolvePlanZoneArchetypes'
 *  resolveOpenSpace — keep the two thresholds in sync. */
const POCKET_PARK_MAX_M2 = 1500;

/**
 * Zone-level recipe resolution — THE shared entry point for the 3D kit layer
 * (GlobeParkKitLayer) and the AI ground-texture diagram (parkGroundTexture).
 * Both MUST use this so painted pads and standing props can never disagree.
 *
 * Order: an archetype id that matches a real recipe wins; otherwise
 * plan-generated greens fall back by role — courtyards get the pocket recipe
 * (benches only), open_space parks band by area exactly like the render-time
 * resolver (resolvePlanZoneArchetypes.resolveOpenSpace). Toolbar plazas get a
 * restrained hardscape recipe; other hand-drawn zones without a recognized
 * id keep the trees-only default.
 */
export function resolveParkRecipeForZone(zone: {
  properties?: unknown;
  coordinates: number[][];
  zone_type?: string;
}): ParkKitRecipe {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const legoContract = resolveParkLegoContract(zone);
  const id = legoContract?.supported
    ? legoContract.archetypeId
    : props.green_space_archetype_id ?? props.plaza_archetype_id;
  const byId = resolveParkRecipe(typeof id === 'string' ? id : undefined);
  if (!isDefaultParkRecipe(byId)) return byId;
  const role = props._plan_role;
  if (role === 'courtyard') return URBAN_POCKET_PARK;
  if (role === 'open_space') {
    return ringAreaM2(zone.coordinates) < POCKET_PARK_MAX_M2
      ? URBAN_POCKET_PARK
      : NEIGHBORHOOD_PARK;
  }
  const isPlaza = zone.zone_type === 'parking'
    || zone.zone_type === 'plaza'
    || typeof props.plaza_archetype_id === 'string'
    || typeof props.plaza_aesthetic === 'string';
  if (isPlaza) return PAVED_PLAZA;
  return byId;
}

export function computeParkPlacements(
  zone: ScatterZone,
  recipe: ParkKitRecipe,
  plantingStructure?: string,
  programAnchors?: Readonly<ParkProgramAnchorLayout>,
): PropPlacement[] {
  const ring = zone.coordinates;
  if (!ring || ring.length < 3) return [];

  // lng/lat -> local ENU metres about the centroid
  let lng0 = 0;
  let lat0 = 0;
  for (const c of ring) {
    lng0 += c[0];
    lat0 += c[1];
  }
  lng0 /= ring.length;
  lat0 /= ring.length;
  const mPerLon = metersPerDegLon(lat0);
  const local = ring.map((c) => [(c[0] - lng0) * mPerLon, (c[1] - lat0) * METERS_PER_DEG_LAT]);

  const area = polygonAreaM2(local);
  if (area < 50) return [];
  const rng = seededRandom(zone.id);
  const placements: Array<PropPlacement & { x: number; y: number }> = [];
  const clearances: Array<{ x: number; y: number; r: number }> = [];

  const structure = resolvePlantingStructure(plantingStructure);
  // An executable family anchor layout owns its fixed program independently
  // from planting character. For example an English-pastoral open meadow
  // still retains the family's playground and pavilion modules.
  const furniture = programAnchors
    ? LEGACY_FURNITURE
    : structure
      ? STRUCTURE_FURNITURE[structure]
      : LEGACY_FURNITURE;

  const toLngLat = (x: number, y: number) => ({
    lng: lng0 + x / mPerLon,
    lat: lat0 + y / METERS_PER_DEG_LAT,
  });
  const blocked = (x: number, y: number) =>
    clearances.some((c) => Math.hypot(x - c.x, y - c.y) < c.r);

  // bbox for interior rejection sampling
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const [x, y] of local) {
    minX = Math.min(minX, x);
    minY = Math.min(minY, y);
    maxX = Math.max(maxX, x);
    maxY = Math.max(maxY, y);
  }
  // ---- clusters first (they claim clearance discs) ------------------------
  // The local origin is the VERTEX-MEAN centroid, which can fall outside a
  // concave (L-shaped) polygon — every cluster instance must be containment-
  // checked or playgrounds land on the neighbouring parcel.
  if (
    furniture.playground &&
    recipe.playground &&
    area >= recipe.playground.minArea_m2
  ) {
    const rule = recipe.playground;
    const center = programAnchors?.playground
      ? resolveContainedParkProgramAnchor(
          local,
          programAnchors.playground,
          rule.clearance_m,
        )
      : { x: 0, y: 0, yawRad: 0 };
    // Whole-element rule: claim the clearance/safety disc only when it fits
    // completely. Never scatter a partial playground across a concavity.
    if (center && (
      pointInPolygon(center.x, center.y, local)
      && distanceToBoundary(local, center.x, center.y) >= rule.clearance_m
    )) {
      clearances.push({ x: center.x, y: center.y, r: rule.clearance_m });
      const startAngle = rng() * Math.PI * 2;
      const moduleRadius = rule.instances > 1 ? rule.clusterRadius_m * 0.62 : 0;
      for (let i = 0; i < rule.instances; i++) {
        // Equal angular stations keep the complete equipment set centered on
        // the exact safety-pad anchor instead of allowing random centroid
        // drift between the ground guide and standing modules.
        const angle = startAngle + (i / rule.instances) * Math.PI * 2;
        const x = center.x + Math.cos(angle) * moduleRadius;
        const y = center.y + Math.sin(angle) * moduleRadius;
        placements.push({ propId: 'playground', ...toLngLat(x, y), x, y, yawRad: rng() * Math.PI * 2, scale: 1 });
      }
      // Preserve the legacy seeded stream position for downstream benches and
      // trees. The former scatter consumed angle/radius/yaw per module; the
      // executable ring uses fewer values but unrelated planting must not
      // reshuffle when a project is reopened after this upgrade.
      for (let draw = 0; draw < rule.instances * 2 - 1; draw += 1) rng();
    }
  }

  if (furniture.pavilion && recipe.pavilion && area >= recipe.pavilion.minArea_m2) {
    const rule = recipe.pavilion;
    // Executable families use the oriented whole-disc solver; legacy parks
    // retain the historical axis-aligned offset.
    const authored = programAnchors?.pavilion
      ? resolveContainedParkProgramAnchor(
          local,
          programAnchors.pavilion,
          rule.clearance_m,
          clearances,
        )
      : {
          x: (maxX + minX) / 2 + (maxX - minX) * 0.2,
          y: (maxY + minY) / 2 + (maxY - minY) * 0.2,
          yawRad: 0,
        };
    const x = authored?.x ?? 0;
    const y = authored?.y ?? 0;
    if (
      authored
      && pointInPolygon(x, y, local)
      && distanceToBoundary(local, x, y) >= rule.clearance_m
      && !blocked(x, y)
    ) {
      clearances.push({ x, y, r: rule.clearance_m });
      placements.push({ propId: 'pavilion', ...toLngLat(x, y), x, y, yawRad: authored.yawRad, scale: 1 });
    }
  }

  // ---- benches on the boundary, facing inward ------------------------------
  if (furniture.benches && recipe.benches) {
    const rule = recipe.benches;
    const count = Math.min(rule.max, Math.max(rule.min, Math.round(area / rule.areaPerBench_m2)));
    for (const st of perimeterStations(local, count)) {
      const x = st.x + st.nx * rule.edgeInset_m;
      const y = st.y + st.ny * rule.edgeInset_m;
      if (!pointInPolygon(x, y, local) || blocked(x, y)) continue;
      placements.push({
        propId: 'bench',
        ...toLngLat(x, y),
        x,
        y,
        // +90°: the bench's LONG axis (local X) must run parallel to the
        // edge, back to the boundary — atan2 alone seats it end-on.
        yawRad: Math.atan2(st.ny, st.nx) + Math.PI / 2,
        scale: 1,
      });
    }
  }

  // ---- trees ---------------------------------------------------------------
  const tr = recipe.trees;
  const target = Math.round((tr.perHectare * area) / 10000);
  const placedTrees: Array<[number, number]> = [];
  const ctx: TreeCtx = {
    local,
    rng,
    tr,
    target,
    bbox: { minX, minY, maxX, maxY },
    canPlace: (x, y) => {
      if (!pointInPolygon(x, y, local) || blocked(x, y)) return false;
      if (
        structure === 'botanical_collection'
        && botanicalProgramBlocks({ minX, minY, maxX, maxY }, x, y)
      ) {
        return false;
      }
      for (const [px, py] of placedTrees) {
        if (Math.hypot(x - px, y - py) < tr.minSpacing_m) return false;
      }
      return true;
    },
    push: (x, y, yawRad, scale) => {
      placedTrees.push([x, y]);
      placements.push({ propId: 'tree', ...toLngLat(x, y), x, y, yawRad, scale });
    },
    count: () => placedTrees.length,
  };

  if (recipe === URBAN_POCKET_PARK) {
    if (structure === 'formal_quad') placePocketParkFormalFrame(ctx);
    else placePocketParkFrame(ctx);
  } else {
    switch (structure) {
      case 'formal_allee':
        placeFormalAllee(ctx);
        break;
      case 'naturalistic_grove':
        placeNaturalisticGrove(ctx);
        break;
      case 'open_meadow':
        placeOpenMeadow(ctx);
        break;
      case 'active_recreation':
        // shade anchors: equipment clearance rings + the benches placed above
        placeActiveRecreation(ctx, [
          ...clearances.map((c) => ({ x: c.x, y: c.y, standoff: c.r })),
          ...placements.filter((p) => p.propId === 'bench').map((b) => ({ x: b.x, y: b.y, standoff: 1.5 })),
        ]);
        break;
      case 'formal_quad':
        placeFormalQuad(ctx);
        break;
      case 'garden_courtyard':
        placeGardenCourtyard(ctx);
        break;
      case 'japanese_stroll_garden':
        placeGardenCourtyard(ctx, false);
        break;
      case 'sports_perimeter':
        placeSportsPerimeter(ctx);
        break;
      case 'reservoir_perimeter':
        placeReservoirPerimeter(ctx);
        break;
      case 'botanical_collection':
        placeNaturalisticGrove(ctx);
        break;
      case 'nature_play_grove':
        placeOpenMeadow(ctx);
        break;
      case 'paved_plaza':
        placePavedPlaza(ctx);
        break;
      case 'buffer_edge':
        placeBufferEdge(ctx);
        break;
      default:
        placeLegacyScatter(ctx);
    }
  }

  return placements.map(({ x: _x, y: _y, ...p }) => p);
}
