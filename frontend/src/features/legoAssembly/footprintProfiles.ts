import type {
  BuildingFootprintProfile,
  FootprintCompatibility,
} from '@/components/viewer/aestheticCatalog';

const METRES_PER_DEG_LAT = 110540;
const METRES_PER_DEG_LNG_EQUATOR = 111320;

export interface FootprintAnalysis {
  profile: BuildingFootprintProfile;
  width_m: number;
  depth_m: number;
  wing_depth_m?: number;
  concave_vertices: number;
  within_recommended_size: boolean;
}

function validRing(coordinates: number[][] | undefined): Array<[number, number]> {
  const points = (coordinates ?? []).flatMap((point) => (
    Array.isArray(point) && point.length >= 2 && Number.isFinite(point[0]) && Number.isFinite(point[1])
      ? [[Number(point[0]), Number(point[1])] as [number, number]]
      : []
  ));
  if (points.length > 3) {
    const first = points[0];
    const last = points[points.length - 1];
    if (Math.abs(first[0] - last[0]) < 1e-12 && Math.abs(first[1] - last[1]) < 1e-12) {
      points.pop();
    }
  }
  return points;
}

function polygonArea(points: Array<{ x: number; y: number }>): number {
  let area = 0;
  for (let i = 0; i < points.length; i += 1) {
    const a = points[i];
    const b = points[(i + 1) % points.length];
    area += a.x * b.y - b.x * a.y;
  }
  return area / 2;
}

function concaveVertexCount(points: Array<{ x: number; y: number }>): number {
  const orientation = Math.sign(polygonArea(points)) || 1;
  let count = 0;
  for (let i = 0; i < points.length; i += 1) {
    const previous = points[(i - 1 + points.length) % points.length];
    const current = points[i];
    const next = points[(i + 1) % points.length];
    const cross = (current.x - previous.x) * (next.y - current.y)
      - (current.y - previous.y) * (next.x - current.x);
    if (Math.abs(cross) > 1e-6 && Math.sign(cross) !== orientation) count += 1;
  }
  return count;
}

function classifyProfile(concaveVertices: number): BuildingFootprintProfile {
  if (concaveVertices >= 3) return 'courtyard';
  if (concaveVertices === 2) return 'u_shape';
  if (concaveVertices === 1) return 'l_shape';
  return 'rectangle';
}

/**
 * Convert the user's geographic polygon into the oriented metre dimensions
 * and topology profile understood by the LEGO planner.
 */
export function analyzeLegoFootprint(
  coordinates: number[][] | undefined,
  compatibility?: FootprintCompatibility,
): FootprintAnalysis | null {
  const ring = validRing(coordinates);
  if (ring.length < 3) return null;
  const centroidLng = ring.reduce((sum, point) => sum + point[0], 0) / ring.length;
  const centroidLat = ring.reduce((sum, point) => sum + point[1], 0) / ring.length;
  const metresPerDegLng = METRES_PER_DEG_LNG_EQUATOR * Math.cos((centroidLat * Math.PI) / 180);
  const local = ring.map(([lng, lat]) => ({
    x: (lng - centroidLng) * metresPerDegLng,
    y: (lat - centroidLat) * METRES_PER_DEG_LAT,
  }));

  let longest = 0;
  let angle = 0;
  for (let i = 0; i < local.length; i += 1) {
    const a = local[i];
    const b = local[(i + 1) % local.length];
    const length = Math.hypot(b.x - a.x, b.y - a.y);
    if (length > longest) {
      longest = length;
      angle = Math.atan2(b.y - a.y, b.x - a.x);
    }
  }
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  let uMin = Infinity; let uMax = -Infinity; let vMin = Infinity; let vMax = -Infinity;
  for (const point of local) {
    const u = point.x * cos + point.y * sin;
    const v = -point.x * sin + point.y * cos;
    uMin = Math.min(uMin, u); uMax = Math.max(uMax, u);
    vMin = Math.min(vMin, v); vMax = Math.max(vMax, v);
  }
  const dimensions = [uMax - uMin, vMax - vMin].sort((a, b) => b - a);
  const width = Math.max(1, dimensions[0]);
  const depth = Math.max(1, dimensions[1]);
  const concaveVertices = concaveVertexCount(local);
  const detected = classifyProfile(concaveVertices);
  const profile = compatibility?.preferredProfiles.includes(detected) === false ? 'rectangle' : detected;
  const profileGuidance = compatibility?.profiles?.[profile];
  const recommendedWidth = profileGuidance?.recommendedWidth_m ?? compatibility?.recommendedWidth_m;
  const recommendedDepth = profileGuidance?.recommendedDepth_m ?? compatibility?.recommendedDepth_m;
  const withinRecommended = (!recommendedWidth || (width >= recommendedWidth[0] && width <= recommendedWidth[1]))
    && (!recommendedDepth || (depth >= recommendedDepth[0] && depth <= recommendedDepth[1]));
  const wingRange = profileGuidance?.wingDepth_m ?? compatibility?.wingDepth_m;

  return {
    profile,
    width_m: Math.round(width * 10) / 10,
    depth_m: Math.round(depth * 10) / 10,
    wing_depth_m: profile === 'rectangle' || !wingRange
      ? undefined
      : Math.round(((wingRange[0] + wingRange[1]) / 2) * 10) / 10,
    concave_vertices: concaveVertices,
    within_recommended_size: withinRecommended,
  };
}
