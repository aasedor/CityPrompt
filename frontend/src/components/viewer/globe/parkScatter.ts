/**
 * Deterministic park prop scatter — pure geometry, no three.js.
 *
 * computeParkPlacements(zone, recipe) turns an arbitrary zone polygon into
 * prop placements (lng/lat + yaw + scale): edge-biased trees with minimum
 * spacing, inward-facing benches along the boundary, and area-gated
 * playground/pavilion clusters with tree clearance.
 *
 * Determinism: seeded by zone.id only — re-renders, sessions, and unrelated
 * edits never reshuffle a park.
 */

import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { pointInPolygon } from '@/utils/coordTransform';
import { seededRandom } from '@/utils/seededRandom';
import type { ParkKitRecipe } from '@/data/parkKitRecipes';

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

export function computeParkPlacements(zone: ScatterZone, recipe: ParkKitRecipe): PropPlacement[] {
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
    recipe.playground &&
    area >= recipe.playground.minArea_m2 &&
    pointInPolygon(0, 0, local)
  ) {
    const rule = recipe.playground;
    clearances.push({ x: 0, y: 0, r: rule.clearance_m });
    for (let i = 0; i < rule.instances; i++) {
      const ang = rng() * Math.PI * 2;
      const rad = rule.clusterRadius_m * Math.sqrt(rng());
      const x = Math.cos(ang) * rad;
      const y = Math.sin(ang) * rad;
      if (!pointInPolygon(x, y, local)) continue;
      placements.push({ propId: 'playground', ...toLngLat(x, y), x, y, yawRad: rng() * Math.PI * 2, scale: 1 });
    }
  }

  if (recipe.pavilion && area >= recipe.pavilion.minArea_m2) {
    const rule = recipe.pavilion;
    // offset away from the playground toward the widest half
    const x = (maxX + minX) / 2 + (maxX - minX) * 0.2;
    const y = (maxY + minY) / 2 + (maxY - minY) * 0.2;
    if (pointInPolygon(x, y, local) && !blocked(x, y)) {
      clearances.push({ x, y, r: rule.clearance_m });
      placements.push({ propId: 'pavilion', ...toLngLat(x, y), x, y, yawRad: 0, scale: 1 });
    }
  }

  // ---- benches on the boundary, facing inward ------------------------------
  if (recipe.benches) {
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

  // ---- trees: edge-biased rejection sampling with min spacing -------------
  const tr = recipe.trees;
  const target = Math.round((tr.perHectare * area) / 10000);
  const placedTrees: Array<[number, number]> = [];
  const edgeStations = perimeterStations(local, Math.max(16, target));
  let attempts = 0;
  const maxAttempts = target * 25;
  while (placedTrees.length < target && attempts < maxAttempts) {
    attempts++;
    let x: number;
    let y: number;
    if (rng() < tr.edgeBias && edgeStations.length) {
      const st = edgeStations[Math.floor(rng() * edgeStations.length)];
      const inset = 2 + rng() * Math.max(0.1, tr.bandDepth_m - 2);
      x = st.x + st.nx * inset;
      y = st.y + st.ny * inset;
    } else {
      x = minX + rng() * (maxX - minX);
      y = minY + rng() * (maxY - minY);
    }
    if (!pointInPolygon(x, y, local) || blocked(x, y)) continue;
    let tooClose = false;
    for (const [px, py] of placedTrees) {
      if (Math.hypot(x - px, y - py) < tr.minSpacing_m) {
        tooClose = true;
        break;
      }
    }
    if (tooClose) continue;
    placedTrees.push([x, y]);
    placements.push({
      propId: 'tree',
      ...toLngLat(x, y),
      x,
      y,
      yawRad: rng() * Math.PI * 2,
      scale: tr.scaleJitter[0] + rng() * (tr.scaleJitter[1] - tr.scaleJitter[0]),
    });
  }

  return placements.map(({ x: _x, y: _y, ...p }) => p);
}
