/**
 * Pure geometry helper functions for context building architectural detail.
 * Generates roof shapes, window positions, floor lines, and parapets
 * for arbitrary polygon footprints from OpenStreetMap data.
 *
 * Roof approach: polygon inset (shrink) to create sloped sides + flat ridge cap.
 * This correctly handles concave polygons (L, T, U shapes) unlike centroid-apex.
 */
import * as THREE from 'three';
import { ShapeUtils } from 'three';
import type { ContextBuildingData } from './ContextBuildings';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export type RoofShape = 'flat' | 'pitched';

export interface WindowInstance {
  position: THREE.Vector3;
  quaternion: THREE.Quaternion;
}

// ─────────────────────────────────────────────────────────────────────────────
// Window dimensions — exported for InstancedMesh geometry creation
// ─────────────────────────────────────────────────────────────────────────────

export const WINDOW_WIDTH = 1.2;
export const WINDOW_HEIGHT = 1.5;

// ─────────────────────────────────────────────────────────────────────────────
// Polygon utilities
// ─────────────────────────────────────────────────────────────────────────────

/** Signed area via trapezoidal shoelace formula. Negative = CCW, positive = CW. */
function signedArea(pts: THREE.Vector2[]): number {
  let area = 0;
  for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
    area += (pts[j].x + pts[i].x) * (pts[j].y - pts[i].y);
  }
  return area * 0.5;
}

/** Ensure polygon winding is CCW (so inward normals point toward interior). */
export function ensureCCW(pts: THREE.Vector2[]): THREE.Vector2[] {
  return signedArea(pts) > 0 ? [...pts].reverse() : pts;
}

function centroid(pts: THREE.Vector2[]): THREE.Vector2 {
  let cx = 0, cy = 0;
  for (const p of pts) { cx += p.x; cy += p.y; }
  return new THREE.Vector2(cx / pts.length, cy / pts.length);
}

function dist2D(a: THREE.Vector2, b: THREE.Vector2): number {
  return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);
}

/** Distance from point p to line segment a→b. */
function pointToSegmentDist(p: THREE.Vector2, a: THREE.Vector2, b: THREE.Vector2): number {
  const dx = b.x - a.x, dy = b.y - a.y;
  const lenSq = dx * dx + dy * dy;
  if (lenSq < 0.0001) return dist2D(p, a);
  const t = Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / lenSq));
  return dist2D(p, new THREE.Vector2(a.x + t * dx, a.y + t * dy));
}

/** Minimum distance from a point to any edge of a polygon. */
function minDistToPolygonEdge(point: THREE.Vector2, pts: THREE.Vector2[]): number {
  let minDist = Infinity;
  for (let i = 0; i < pts.length; i++) {
    const d = pointToSegmentDist(point, pts[i], pts[(i + 1) % pts.length]);
    if (d < minDist) minDist = d;
  }
  return minDist;
}

/**
 * Inset (shrink) a CCW polygon by moving each vertex inward along its bisector.
 * Returns null if the inset collapses (self-intersects or area becomes negligible).
 */
function insetPolygon(pts: THREE.Vector2[], dist: number): THREE.Vector2[] | null {
  const n = pts.length;
  if (n < 3 || Math.abs(dist) < 0.01) return null;

  const result: THREE.Vector2[] = [];

  for (let i = 0; i < n; i++) {
    const prev = pts[(i - 1 + n) % n];
    const curr = pts[i];
    const next = pts[(i + 1) % n];

    const d1x = curr.x - prev.x, d1y = curr.y - prev.y;
    const d2x = next.x - curr.x, d2y = next.y - curr.y;
    const len1 = Math.sqrt(d1x * d1x + d1y * d1y);
    const len2 = Math.sqrt(d2x * d2x + d2y * d2y);

    if (len1 < 0.01 || len2 < 0.01) {
      result.push(curr.clone());
      continue;
    }

    // Inward normals for CCW polygon (rotate edge direction +90°)
    const n1x = -d1y / len1, n1y = d1x / len1;
    const n2x = -d2y / len2, n2y = d2x / len2;

    // Bisector of the two inward normals
    const bx = n1x + n2x, by = n1y + n2y;
    const bLen = Math.sqrt(bx * bx + by * by);

    if (bLen < 0.001) {
      // Nearly parallel edges — just offset along one normal
      result.push(new THREE.Vector2(curr.x + n1x * dist, curr.y + n1y * dist));
    } else {
      const ubx = bx / bLen, uby = by / bLen;
      const cosHalf = n1x * ubx + n1y * uby;
      // Scale so the perpendicular offset from each edge equals `dist`.
      // Cap scale at 3× to prevent extreme offsets at very acute angles.
      const scale = Math.min(cosHalf > 0.15 ? dist / cosHalf : dist * 3, dist * 3);
      result.push(new THREE.Vector2(curr.x + ubx * scale, curr.y + uby * scale));
    }
  }

  // Validate — CCW polygon should have negative signed area; reject if collapsed/flipped
  if (signedArea(result) >= -0.1) return null;
  return result;
}

// ─────────────────────────────────────────────────────────────────────────────
// Roof Shape Heuristic
// ─────────────────────────────────────────────────────────────────────────────

const FLAT_ROOF_TYPES = new Set([
  'office', 'warehouse', 'retail', 'industrial', 'commercial',
  'supermarket', 'parking', 'garage', 'garages', 'hangar',
]);

const PITCHED_TYPES = new Set([
  'house', 'detached', 'terrace', 'residential', 'semidetached_house',
  'semi', 'bungalow', 'farm', 'cabin',
  'church', 'school', 'university', 'hospital', 'civic', 'public',
  'hotel', 'dormitory',
]);

export function resolveRoofShape(building: ContextBuildingData): RoofShape {
  if (building.roof_shape) {
    const tag = building.roof_shape.toLowerCase();
    if (tag === 'flat') return 'flat';
    // All non-flat OSM tags → pitched
    return 'pitched';
  }

  const bType = (building.building_type || '').toLowerCase();
  const levels = building.levels ?? Math.round(building.height / 3);

  if (FLAT_ROOF_TYPES.has(bType)) return 'flat';
  if (PITCHED_TYPES.has(bType)) return 'pitched';

  if (bType === 'apartments') return levels <= 4 ? 'pitched' : 'flat';

  // Unknown type ('yes' or empty) — use height to guess.
  // Short buildings (≤3 storeys) are likely residential → pitched.
  return levels <= 3 ? 'pitched' : 'flat';
}

// ─────────────────────────────────────────────────────────────────────────────
// Roof Geometry — Polygon Inset Approach
// ─────────────────────────────────────────────────────────────────────────────
//
// Coordinate convention:
//   2D shape: (x, y)
//   3D after rotateX(-PI/2): vertex = (x, height, -y)

/**
 * Build a pitched roof using polygon-inset approach.
 *
 * 1. Shrink the footprint polygon inward by `insetDist`
 * 2. Connect each original edge to the corresponding inset edge → sloped side quads
 * 3. Triangulate the inset polygon → flat ridge/cap on top
 *
 * Correctly handles L-shaped, T-shaped, U-shaped, and any concave polygon.
 * For tiny/narrow buildings where the inset collapses, falls back to centroid apex.
 */
export function buildSlopedRoofGeometry(
  points2D: THREE.Vector2[],
  wallHeight: number,
  roofHeight: number,
): THREE.BufferGeometry {
  const pts = ensureCCW(points2D);
  const c = centroid(pts);

  // Inset proportional to roof height — slopes should extend ~1.5× the roof height
  // inward from the eaves, producing a visually proportional pitched roof.
  // Cap at 40% of centroid-to-nearest-edge to avoid collapse on narrow buildings.
  const minEdgeDist = minDistToPolygonEdge(c, pts);
  const insetDist = Math.min(roofHeight * 1.5, minEdgeDist * 0.4);

  // Eaves overhang: expand footprint outward by 0.3m so roof extends past walls
  const EAVE_OVERHANG = 0.3;
  const eaves = insetPolygon(pts, -EAVE_OVERHANG); // negative inset = expand

  const positions: number[] = [];
  const normals: number[] = [];

  const inset = insetDist > 0.3 ? insetPolygon(pts, insetDist) : null;
  // Use eaves as the base edge of the roof (slightly wider than walls)
  const roofBase = (eaves && eaves.length === pts.length) ? eaves : pts;

  if (inset && inset.length === pts.length) {
    // ── Sloped side quads ──
    for (let i = 0; i < pts.length; i++) {
      const j = (i + 1) % pts.length;

      const bl = new THREE.Vector3(roofBase[i].x, wallHeight, -roofBase[i].y);
      const br = new THREE.Vector3(roofBase[j].x, wallHeight, -roofBase[j].y);
      const tr = new THREE.Vector3(inset[j].x, wallHeight + roofHeight, -inset[j].y);
      const tl = new THREE.Vector3(inset[i].x, wallHeight + roofHeight, -inset[i].y);

      // Two triangles per quad, compute face normal
      const e1 = new THREE.Vector3().subVectors(br, bl);
      const e2 = new THREE.Vector3().subVectors(tl, bl);
      const n = new THREE.Vector3().crossVectors(e1, e2).normalize();
      if (n.y < -0.1) n.negate(); // ensure roof normals point generally upward

      positions.push(bl.x, bl.y, bl.z, br.x, br.y, br.z, tr.x, tr.y, tr.z);
      normals.push(n.x, n.y, n.z, n.x, n.y, n.z, n.x, n.y, n.z);
      positions.push(bl.x, bl.y, bl.z, tr.x, tr.y, tr.z, tl.x, tl.y, tl.z);
      normals.push(n.x, n.y, n.z, n.x, n.y, n.z, n.x, n.y, n.z);
    }

    // ── Flat ridge/cap from inset polygon ──
    const triIndices = ShapeUtils.triangulateShape(inset, []);
    for (const tri of triIndices) {
      const [a, b, ci] = tri;
      positions.push(
        inset[a].x, wallHeight + roofHeight, -inset[a].y,
        inset[b].x, wallHeight + roofHeight, -inset[b].y,
        inset[ci].x, wallHeight + roofHeight, -inset[ci].y,
      );
      normals.push(0, 1, 0, 0, 1, 0, 0, 1, 0); // flat cap → straight up
    }
  } else {
    // Fallback for tiny/narrow buildings: centroid apex fan (works fine on small shapes)
    const apex = new THREE.Vector3(c.x, wallHeight + roofHeight, -c.y);
    for (let i = 0; i < roofBase.length; i++) {
      const j = (i + 1) % roofBase.length;
      const v0 = new THREE.Vector3(roofBase[i].x, wallHeight, -roofBase[i].y);
      const v1 = new THREE.Vector3(roofBase[j].x, wallHeight, -roofBase[j].y);

      const e1 = new THREE.Vector3().subVectors(v1, v0);
      const e2 = new THREE.Vector3().subVectors(apex, v0);
      const n = new THREE.Vector3().crossVectors(e1, e2).normalize();

      positions.push(v0.x, v0.y, v0.z, v1.x, v1.y, v1.z, apex.x, apex.y, apex.z);
      normals.push(n.x, n.y, n.z, n.x, n.y, n.z, n.x, n.y, n.z);
    }
  }

  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geom.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  return geom;
}

// ─────────────────────────────────────────────────────────────────────────────
// Parapet (flat-roofed buildings)
// ─────────────────────────────────────────────────────────────────────────────

export function buildParapetGeometry(
  points2D: THREE.Vector2[],
  wallHeight: number,
  parapetHeight: number,
): THREE.BufferGeometry {
  const pts = ensureCCW(points2D);
  const positions: number[] = [];
  const normals: number[] = [];
  const parapetTop = wallHeight + parapetHeight;

  for (let i = 0; i < pts.length; i++) {
    const curr = pts[i];
    const next = pts[(i + 1) % pts.length];

    const dx = next.x - curr.x, dy = next.y - curr.y;
    const len = Math.sqrt(dx * dx + dy * dy);
    if (len < 0.1) continue;

    const nx = -dy / len, ny = dx / len;
    const n3 = new THREE.Vector3(nx, 0, -ny);

    const bl = new THREE.Vector3(curr.x, wallHeight, -curr.y);
    const br = new THREE.Vector3(next.x, wallHeight, -next.y);
    const tl = new THREE.Vector3(curr.x, parapetTop, -curr.y);
    const tr = new THREE.Vector3(next.x, parapetTop, -next.y);

    positions.push(bl.x, bl.y, bl.z, br.x, br.y, br.z, tr.x, tr.y, tr.z);
    normals.push(n3.x, n3.y, n3.z, n3.x, n3.y, n3.z, n3.x, n3.y, n3.z);
    positions.push(bl.x, bl.y, bl.z, tr.x, tr.y, tr.z, tl.x, tl.y, tl.z);
    normals.push(n3.x, n3.y, n3.z, n3.x, n3.y, n3.z, n3.x, n3.y, n3.z);
  }

  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geom.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
  return geom;
}

// ─────────────────────────────────────────────────────────────────────────────
// Window Position Calculator — building-type-aware spacing
// ─────────────────────────────────────────────────────────────────────────────

const WINDOW_SILL = 0.9; // sill height above each floor level

/** Types that should never get windows (doors, garage doors, sheds, etc.) */
const NO_WINDOW_TYPES = new Set([
  'garage', 'garages', 'carport', 'shed', 'roof', 'ruins', 'collapsed',
  'construction', 'barn', 'cowshed', 'stable', 'sty', 'greenhouse',
  'storage_tank', 'tank', 'bunker', 'transformer_tower', 'toilets',
  'hut', 'container', 'kiosk',
]);

interface WindowSpacing {
  spacing: number;     // center-to-center distance
  margin: number;      // distance from edge corners
  skipGround: boolean; // skip ground floor (entrances, doors, shopfronts)
  minEdge: number;     // minimum edge length to place windows on
  skip: boolean;       // skip windows entirely for this building
}

function getWindowSpacing(buildingType: string, height: number): WindowSpacing {
  const t = (buildingType || '').toLowerCase();

  // Never put windows on these types
  if (NO_WINDOW_TYPES.has(t)) {
    return { spacing: 99, margin: 99, skipGround: true, minEdge: 99, skip: true };
  }
  // Very short buildings (≤ 1 storey / ~4m) — likely garages, sheds, outbuildings
  if (height <= 4.0) {
    return { spacing: 99, margin: 99, skipGround: true, minEdge: 99, skip: true };
  }
  // Residential — fewer, wider-spaced windows; skip ground on 2+ storey
  if (['house', 'detached', 'residential', 'terrace', 'semi',
       'bungalow', 'farm', 'cabin', 'semidetached_house'].includes(t)) {
    return { spacing: 3.5, margin: 1.5, skipGround: height > 5, minEdge: 4.0, skip: false };
  }
  // Commercial / office — dense glazing, skip ground (shopfronts/entrances)
  if (['office', 'commercial'].includes(t)) {
    return { spacing: 2.2, margin: 0.8, skipGround: true, minEdge: 3.0, skip: false };
  }
  // Industrial / warehouse — very few high windows
  if (['warehouse', 'industrial', 'hangar'].includes(t)) {
    return { spacing: 8.0, margin: 3.0, skipGround: true, minEdge: 6.0, skip: false };
  }
  // Retail / supermarket — skip ground (shopfronts)
  if (['retail', 'supermarket'].includes(t)) {
    return { spacing: 3.0, margin: 1.0, skipGround: true, minEdge: 3.0, skip: false };
  }
  // Apartments — moderate density, skip ground (lobby/commercial)
  if (t === 'apartments') {
    return { spacing: 2.8, margin: 1.0, skipGround: true, minEdge: 3.0, skip: false };
  }
  // Institutional
  if (['church', 'school', 'university', 'hospital', 'civic', 'public'].includes(t)) {
    return { spacing: 4.0, margin: 1.5, skipGround: false, minEdge: 4.0, skip: false };
  }
  // Generic 'yes' or unknown — use height to guess
  // Short (2 storey) = residential-like; tall = commercial-like
  if (height <= 7) {
    return { spacing: 3.5, margin: 1.5, skipGround: false, minEdge: 4.0, skip: false };
  }
  return { spacing: 3.0, margin: 1.0, skipGround: true, minEdge: 3.0, skip: false };
}

export function computeWindowPositions(
  points2D: THREE.Vector2[],
  wallHeight: number,
  levels: number,
  floorHeight: number,
  buildingType?: string,
  buildingHeight?: number,
): WindowInstance[] {
  const cfg = getWindowSpacing(buildingType || '', buildingHeight ?? wallHeight);
  if (cfg.skip) return [];

  const pts = ensureCCW(points2D);
  const instances: WindowInstance[] = [];
  const startFloor = cfg.skipGround ? 1 : 0;

  for (let i = 0; i < pts.length; i++) {
    const curr = pts[i];
    const next = pts[(i + 1) % pts.length];

    const edgeLen = dist2D(curr, next);
    if (edgeLen < cfg.minEdge) continue;

    const dx = next.x - curr.x, dy = next.y - curr.y;
    // Outward normal for CCW polygon (rotate edge direction -90°)
    const nx = dy / edgeLen, ny = -dx / edgeLen;

    const usableLen = edgeLen - 2 * cfg.margin;
    if (usableLen < WINDOW_WIDTH) continue;
    const numWindows = Math.max(1, Math.floor(usableLen / cfg.spacing));
    const actualSpacing = usableLen / numWindows;

    const angle = Math.atan2(nx, -ny);
    const quat = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), angle);

    for (let floor = startFloor; floor < levels; floor++) {
      const floorBase = floor * floorHeight;
      const windowCenterY = floorBase + WINDOW_SILL + WINDOW_HEIGHT / 2;
      if (windowCenterY + WINDOW_HEIGHT / 2 > wallHeight - 0.2) continue;

      for (let w = 0; w < numWindows; w++) {
        const t = (cfg.margin + actualSpacing * (w + 0.5)) / edgeLen;
        const px = curr.x + dx * t + nx * 0.12;
        const py = curr.y + dy * t + ny * 0.12;

        instances.push({
          position: new THREE.Vector3(px, windowCenterY, -py),
          quaternion: quat,
        });
      }
    }
  }

  return instances;
}

// ─────────────────────────────────────────────────────────────────────────────
// Floor Line Calculator
// ─────────────────────────────────────────────────────────────────────────────

const FLOOR_LINE_OFFSET = 0.06;

export function computeFloorLines(
  points2D: THREE.Vector2[],
  wallHeight: number,
  levels: number,
  floorHeight: number,
): Float32Array {
  const pts = ensureCCW(points2D);
  const segments: number[] = [];

  for (let floor = 1; floor < levels; floor++) {
    const y = floor * floorHeight;
    if (y >= wallHeight - 0.1) continue;

    for (let i = 0; i < pts.length; i++) {
      const curr = pts[i];
      const next = pts[(i + 1) % pts.length];

      const edgeLen = dist2D(curr, next);
      if (edgeLen < 0.5) continue;

      const dx = next.x - curr.x, dy = next.y - curr.y;
      // Outward normal for CCW polygon
      const nx = (dy / edgeLen) * FLOOR_LINE_OFFSET;
      const ny = (-dx / edgeLen) * FLOOR_LINE_OFFSET;

      segments.push(
        curr.x + nx, y, -(curr.y + ny),
        next.x + nx, y, -(next.y + ny),
      );
    }
  }

  return new Float32Array(segments);
}

// ─────────────────────────────────────────────────────────────────────────────
// Door & Garage Door Position Calculator
// ─────────────────────────────────────────────────────────────────────────────

export const DOOR_WIDTH = 1.0;
export const DOOR_HEIGHT = 2.2;
export const GARAGE_DOOR_WIDTH = 2.8;
export const GARAGE_DOOR_HEIGHT = 2.4;

export type DoorKind = 'door' | 'garage';

export interface DoorInstance {
  position: THREE.Vector3;
  quaternion: THREE.Quaternion;
  kind: DoorKind;
}

const GARAGE_TYPES = new Set(['garage', 'garages', 'carport']);

const DOOR_BUILDING_TYPES = new Set([
  'house', 'detached', 'residential', 'terrace', 'semi', 'bungalow',
  'semidetached_house', 'farm', 'cabin', 'apartments', 'dormitory',
  'hotel', 'office', 'commercial', 'retail', 'supermarket',
  'school', 'university', 'hospital', 'civic', 'public', 'church',
  'yes',
]);

/** Precomputed road segment for door-facing computation. */
export interface RoadSegment2D {
  a: THREE.Vector2;
  b: THREE.Vector2;
}

/**
 * Place doors on the ground floor of buildings.
 * - Picks the edge closest to a road (so doors face the street).
 * - Falls back to longest edge if no roads are nearby.
 * - Garage/carport types get one wide garage door.
 * - Skip sheds, ruins, construction, etc.
 */
export function computeDoorPositions(
  points2D: THREE.Vector2[],
  buildingType?: string,
  buildingHeight?: number,
  roadSegments?: RoadSegment2D[],
): DoorInstance[] {
  const bType = (buildingType || '').toLowerCase();
  const height = buildingHeight ?? 9;

  // Very short buildings without a known type — skip tiny sheds etc.
  if (height <= 2.0 && !GARAGE_TYPES.has(bType) && !DOOR_BUILDING_TYPES.has(bType)) return [];
  // Skip types that shouldn't have doors at all
  if (!GARAGE_TYPES.has(bType) && !DOOR_BUILDING_TYPES.has(bType)) return [];

  const pts = ensureCCW(points2D);
  if (pts.length < 3) return [];

  // Compute footprint area (absolute value of signed area)
  const footprintArea = Math.abs(signedArea(pts));

  // Identify garages:
  // 1. Explicit garage/carport OSM tags
  // 2. Small footprint (< 45 sq m) with unknown type — likely a detached garage
  const isGarage = GARAGE_TYPES.has(bType) ||
    (footprintArea < 45 && (bType === 'yes' || bType === ''));
  const doorH = isGarage ? GARAGE_DOOR_HEIGHT : Math.min(DOOR_HEIGHT, height - 0.3);

  // Compute distance from each edge midpoint to the nearest road
  type EdgeInfo = { idx: number; roadDist: number; edgeLen: number; facesRoad: boolean };
  const edgeInfos: EdgeInfo[] = [];

  for (let i = 0; i < pts.length; i++) {
    const next = pts[(i + 1) % pts.length];
    const edgeLen = dist2D(pts[i], next);
    if (edgeLen < 1.5) continue; // skip very short edges

    const dx = next.x - pts[i].x, dy = next.y - pts[i].y;
    // Outward normal for CCW polygon
    const onx = dy / edgeLen, ony = -dx / edgeLen;
    const mx = (pts[i].x + next.x) / 2;
    const my = (pts[i].y + next.y) / 2;

    let roadDist = Infinity;
    let facesRoad = false;

    if (roadSegments && roadSegments.length > 0) {
      const mid = new THREE.Vector2(mx, my);
      let nearestRoadPt: THREE.Vector2 | null = null;
      for (const seg of roadSegments) {
        const d = pointToSegmentDist(mid, seg.a, seg.b);
        if (d < roadDist) {
          roadDist = d;
          // Find closest point on this road segment to the midpoint
          const sdx = seg.b.x - seg.a.x, sdy = seg.b.y - seg.a.y;
          const slenSq = sdx * sdx + sdy * sdy;
          const t = slenSq > 0.001 ? Math.max(0, Math.min(1, ((mx - seg.a.x) * sdx + (my - seg.a.y) * sdy) / slenSq)) : 0;
          nearestRoadPt = new THREE.Vector2(seg.a.x + t * sdx, seg.a.y + t * sdy);
        }
      }
      // Check if outward normal points toward the road
      if (nearestRoadPt && roadDist < 30) {
        const toRoadX = nearestRoadPt.x - mx;
        const toRoadY = nearestRoadPt.y - my;
        const toRoadLen = Math.sqrt(toRoadX * toRoadX + toRoadY * toRoadY);
        if (toRoadLen > 0.01) {
          const dot = onx * (toRoadX / toRoadLen) + ony * (toRoadY / toRoadLen);
          facesRoad = dot > 0.3; // normal points roughly toward road (< ~73°)
        }
      }
    }
    edgeInfos.push({ idx: i, roadDist, edgeLen, facesRoad });
  }

  if (edgeInfos.length === 0) return [];

  // Sort: road-facing edges first (by distance), then non-road-facing
  edgeInfos.sort((a, b) => {
    if (a.facesRoad !== b.facesRoad) return a.facesRoad ? -1 : 1;
    return a.roadDist - b.roadDist;
  });

  const results: DoorInstance[] = [];

  // Helper to create a door instance on an edge
  function makeDoor(edgeIdx: number, kind: DoorKind): DoorInstance | null {
    const c = pts[edgeIdx];
    const n2 = pts[(edgeIdx + 1) % pts.length];
    const el = dist2D(c, n2);
    const minW = kind === 'garage' ? GARAGE_DOOR_WIDTH : DOOR_WIDTH;
    if (el < minW + 0.5) return null;

    const ddx = n2.x - c.x, ddy = n2.y - c.y;
    // Outward normal for CCW polygon
    const nnx = ddy / el, nny = -ddx / el;
    const a = Math.atan2(nnx, -nny);
    const q = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), a);
    const h = kind === 'garage' ? GARAGE_DOOR_HEIGHT : doorH;
    const px = c.x + ddx * 0.5 + nnx * 0.12;
    const py = c.y + ddy * 0.5 + nny * 0.12;
    return { position: new THREE.Vector3(px, h / 2, -py), quaternion: q, kind };
  }

  // For standalone garage buildings: just one garage door on closest-to-road edge
  if (isGarage) {
    const d = makeDoor(edgeInfos[0].idx, 'garage');
    if (d) results.push(d);
    return results;
  }

  // Residential: garage on closest road-facing edge, front door on 2nd road-facing edge
  const RESIDENTIAL = new Set([
    'house', 'detached', 'residential', 'terrace', 'semi',
    'semidetached_house', 'bungalow', 'farm', 'cabin', 'yes', '',
  ]);

  // Collect only road-facing edges, sorted by edge length (longest first)
  // so garage goes on the widest face and door on the second widest
  const roadFacingEdges = edgeInfos.filter(e => e.facesRoad)
    .sort((a, b) => b.edgeLen - a.edgeLen);

  // Only add garage doors to residential-sized buildings (footprint < 250 sq m)
  // Larger buildings are likely commercial even if tagged 'yes'
  if (RESIDENTIAL.has(bType) && footprintArea < 250 && roadFacingEdges.length >= 1 && roadFacingEdges[0].roadDist < 30) {
    // Garage on the closest road-facing edge (if wide enough)
    const garageEdge = roadFacingEdges[0];
    let garagePlace = false;
    if (garageEdge.edgeLen >= GARAGE_DOOR_WIDTH + 0.5) {
      const g = makeDoor(garageEdge.idx, 'garage');
      if (g) { results.push(g); garagePlace = true; }
    }

    // Front door on a DIFFERENT road-facing edge — MUST also face the road
    let doorPlaced = false;
    for (let ei = 1; ei < roadFacingEdges.length; ei++) {
      const candidate = roadFacingEdges[ei];
      if (candidate.idx === garageEdge.idx) continue;
      if (candidate.roadDist > 30) break;
      if (candidate.edgeLen >= DOOR_WIDTH + 0.5) {
        const d = makeDoor(candidate.idx, 'door');
        if (d) { results.push(d); doorPlaced = true; }
        break;
      }
    }

    // If no 2nd road-facing edge for door, put door on same edge as garage
    // (same road-facing edge is better than going around the corner)
    if (!doorPlaced && garagePlace) {
      const c = pts[garageEdge.idx];
      const n2 = pts[(garageEdge.idx + 1) % pts.length];
      const el = dist2D(c, n2);
      if (el >= GARAGE_DOOR_WIDTH + DOOR_WIDTH + 1.5) {
        // Place door offset from center toward one end (garage is centered)
        const ddx = n2.x - c.x, ddy = n2.y - c.y;
        const nnx = ddy / el, nny = -ddx / el;
        const a = Math.atan2(nnx, -nny);
        const q = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), a);
        // Put door at ~25% along the edge (garage is at 50% center)
        const t = 0.2;
        const px = c.x + ddx * t + nnx * 0.12;
        const py = c.y + ddy * t + nny * 0.12;
        results.push({ position: new THREE.Vector3(px, doorH / 2, -py), quaternion: q, kind: 'door' });
      }
    }

    // If no garage was placed but we have a road-facing edge, just put a door
    if (!garagePlace && roadFacingEdges.length >= 1) {
      const d = makeDoor(roadFacingEdges[0].idx, 'door');
      if (d) results.push(d);
    }

    if (results.length > 0) return results;
  }

  // Default: single front door on closest road-FACING edge, or longest edge as fallback
  let bestIdx: number;
  if (roadFacingEdges.length > 0 && roadFacingEdges[0].roadDist < 30) {
    bestIdx = roadFacingEdges[0].idx;
  } else if (edgeInfos[0].roadDist < 30) {
    bestIdx = edgeInfos[0].idx;
  } else {
    bestIdx = edgeInfos.reduce((best, e) => e.edgeLen > best.edgeLen ? e : best, edgeInfos[0]).idx;
  }
  const d = makeDoor(bestIdx, 'door');
  if (d) results.push(d);
  return results;
}
