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
