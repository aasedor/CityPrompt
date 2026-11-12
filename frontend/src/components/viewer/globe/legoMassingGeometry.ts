import * as THREE from 'three';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

export interface LegoMassingMeshData {
  positions: number[];
  indices: number[];
  vertexCount: number;
}

const MASSING_PALETTE = [
  '#c8c2b8',
  '#bbc5c1',
  '#d0bfac',
  '#bcc0c5',
  '#c9b7a8',
] as const;

/** Stable muted architecture colour; never reuse neon plan-zone fills. */
export function legoMassingColor(seed: string): string {
  let hash = 2166136261;
  for (let index = 0; index < seed.length; index += 1) {
    hash ^= seed.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return MASSING_PALETTE[Math.abs(hash) % MASSING_PALETTE.length];
}

function cleanRing(ring: readonly number[][]): number[][] {
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
 * Build a low-cost exact-footprint prism for district-scale LEGO LOD.
 * Coordinates stay in the same local ENU convention as GlobeZoneLayer:
 * X=east, Y=north, Z=up.
 */
export function buildLegoMassingMeshData(
  ring: readonly number[][],
  centroidLng: number,
  centroidLat: number,
  heightMeters: number,
): LegoMassingMeshData | null {
  const cleaned = cleanRing(ring);
  if (cleaned.length < 3 || !(heightMeters > 0)) return null;

  const metresPerDegreeLongitude = metersPerDegLon(centroidLat);
  const local = cleaned.map(([longitude, latitude]) => new THREE.Vector2(
    (longitude - centroidLng) * metresPerDegreeLongitude,
    (latitude - centroidLat) * METERS_PER_DEG_LAT,
  ));
  const triangles = THREE.ShapeUtils.triangulateShape(local, []);
  if (triangles.length === 0) return null;

  const positions: number[] = [];
  for (const point of local) positions.push(point.x, point.y, 0);
  for (const point of local) positions.push(point.x, point.y, heightMeters);

  const count = local.length;
  const indices: number[] = [];
  for (const triangle of triangles) {
    // Double-sided material makes winding immaterial visually; opposing base
    // and roof windings still give computeVertexNormals a coherent shell.
    indices.push(triangle[0], triangle[1], triangle[2]);
    indices.push(triangle[0] + count, triangle[2] + count, triangle[1] + count);
  }
  for (let index = 0; index < count; index += 1) {
    const next = (index + 1) % count;
    indices.push(index, next, next + count);
    indices.push(index, next + count, index + count);
  }

  return { positions, indices, vertexCount: count * 2 };
}

/** Dressing for a massing prism: floor lines and window bays. Every length is
 * a real-world metre value supplied by the caller; nothing here is tuned. */
export interface LegoMassingDressingOptions {
  storeys: number;
  /** null draws one line per storey at heightMeters / storeys. */
  floorLineSpacingM: number | null;
  bayModuleM: number;
  windowWidthM: number;
  windowHeightM: number;
  windowSillM: number;
  wallEndMarginM: number;
  floorLineHeightM: number;
  surfaceOffsetM: number;
}

export interface LegoMassingDressingData {
  floorLines: LegoMassingMeshData;
  windows: LegoMassingMeshData;
  /** Whole window bays on each wall, in ring order. */
  baysPerWall: number[];
  /** Heights of the drawn floor lines above the base. */
  floorLevelsM: number[];
}

/**
 * Floor lines and window bays for an exact-footprint massing prism.
 *
 * Window bays sit on a fixed module. A longer wall gains whole bays and a
 * shorter wall loses them; a window is never widened or narrowed to fit, so
 * the facade keeps a believable rhythm at any outline. Coordinates share the
 * prism's local ENU frame (X=east, Y=north, Z=up).
 */
export function buildLegoMassingDressingData(
  ring: readonly number[][],
  centroidLng: number,
  centroidLat: number,
  heightMeters: number,
  options: LegoMassingDressingOptions,
): LegoMassingDressingData | null {
  const cleaned = cleanRing(ring);
  const storeys = Math.floor(options.storeys);
  if (cleaned.length < 3 || !(heightMeters > 0) || !(storeys >= 1)
    || !(options.bayModuleM > 0) || !(options.windowWidthM > 0) || options.windowWidthM >= options.bayModuleM) return null;

  const metresPerDegreeLongitude = metersPerDegLon(centroidLat);
  const local = cleaned.map(([longitude, latitude]) => [
    (longitude - centroidLng) * metresPerDegreeLongitude,
    (latitude - centroidLat) * METERS_PER_DEG_LAT,
  ]);
  const signedArea = local.reduce((sum, point, index) => {
    const next = local[(index + 1) % local.length];
    return sum + point[0] * next[1] - next[0] * point[1];
  }, 0) / 2;
  if (!signedArea) return null;
  // Outward is to the right of travel on a counter-clockwise ring.
  const outward = signedArea > 0 ? 1 : -1;

  const spacing = options.floorLineSpacingM && options.floorLineSpacingM > 0
    ? options.floorLineSpacingM : heightMeters / storeys;
  const rows = Math.max(1, Math.floor(heightMeters / spacing + 1e-6));
  const floorLevelsM = Array.from({ length: rows - 1 }, (_, index) => (index + 1) * spacing);
  // A window stays inside its own storey, below the floor line above it.
  const windowHeight = Math.min(options.windowHeightM,
    spacing - options.windowSillM - options.floorLineHeightM);

  const floorLines: LegoMassingMeshData = { positions: [], indices: [], vertexCount: 0 };
  const windows: LegoMassingMeshData = { positions: [], indices: [], vertexCount: 0 };
  const quad = (target: LegoMassingMeshData, a: number[], b: number[], bottom: number, top: number) => {
    const base = target.vertexCount;
    target.positions.push(a[0], a[1], bottom, b[0], b[1], bottom, b[0], b[1], top, a[0], a[1], top);
    target.indices.push(base, base + 1, base + 2, base, base + 2, base + 3);
    target.vertexCount += 4;
  };

  const baysPerWall: number[] = [];
  for (let index = 0; index < local.length; index += 1) {
    const start = local[index], end = local[(index + 1) % local.length];
    const length = Math.hypot(end[0] - start[0], end[1] - start[1]);
    if (length < 1e-6) { baysPerWall.push(0); continue; }
    const along = [(end[0] - start[0]) / length, (end[1] - start[1]) / length];
    const normal = [outward * along[1], -outward * along[0]];
    const at = (distance: number) => [
      start[0] + along[0] * distance + normal[0] * options.surfaceOffsetM,
      start[1] + along[1] * distance + normal[1] * options.surfaceOffsetM,
    ];
    for (const level of floorLevelsM) {
      quad(floorLines, at(0), at(length), level - options.floorLineHeightM / 2, level + options.floorLineHeightM / 2);
    }
    const bays = Math.max(0, Math.floor((length - 2 * options.wallEndMarginM) / options.bayModuleM + 1e-9));
    baysPerWall.push(bays);
    if (!bays || !(windowHeight > 0)) continue;
    // Centre the whole group; leftover wall is shared between both ends.
    const first = (length - bays * options.bayModuleM) / 2 + (options.bayModuleM - options.windowWidthM) / 2;
    for (let row = 0; row < rows; row += 1) {
      const sill = row * spacing + options.windowSillM;
      for (let bay = 0; bay < bays; bay += 1) {
        const left = first + bay * options.bayModuleM;
        quad(windows, at(left), at(left + options.windowWidthM), sill, sill + windowHeight);
      }
    }
  }
  return { floorLines, windows, baysPerWall, floorLevelsM };
}
