import type {
  LandscapeBenchPlacement,
  LandscapeTreePlacement,
} from './GlobeLandscapeKit';
import type { LocalPt } from './streetMesh3D';
import type { StreetSectionProfile } from './streetSectionProfiles';

export const MAX_STREET_FIXTURE_STATIONS = 8;
export const MAX_STREET_TREES_PER_ZONE = 16;
export const MAX_STREET_LIGHTS_PER_ZONE = 16;
export const MAX_STREET_BENCHES_PER_ZONE = 8;
export const STREET_BENCH_DEPTH_M = 0.64;
export const STREET_BENCH_EDGE_CLEARANCE_M = 0.08;
export const STREET_NODE_FIXTURE_CLEARANCE_M = 12;

export interface StreetLightPlacement {
  x: number;
  y: number;
  z: number;
  yawRad: number;
}

export interface StreetBenchPlacement extends LandscapeBenchPlacement {
  bandStartM: number;
  bandEndM: number;
  footprintDepthM: number;
}

export interface StreetFamilyFixturePlacements {
  trees: LandscapeTreePlacement[];
  benches: StreetBenchPlacement[];
  lights: StreetLightPlacement[];
  stationCount: number;
}

export interface StreetFamilyFixtureOptions {
  points: LocalPt[];
  stationZ?: readonly number[] | null;
  profile: StreetSectionProfile | null;
  sectionScale: number;
  clearancePoints?: readonly LocalPt[];
  enabled: boolean;
}

const EMPTY_FIXTURES: StreetFamilyFixturePlacements = Object.freeze({
  trees: Object.freeze([]) as unknown as LandscapeTreePlacement[],
  benches: Object.freeze([]) as unknown as StreetBenchPlacement[],
  lights: Object.freeze([]) as unknown as StreetLightPlacement[],
  stationCount: 0,
});

/** Clamp the bench centre so its complete transverse footprint, including a
 * small construction tolerance, remains inside the furnishing band. */
export function resolveBenchCenterInBand(
  bandStartM: number,
  bandEndM: number,
  preferredCenterM: number,
  scale: number,
): number | null {
  const halfFootprint = STREET_BENCH_DEPTH_M * scale / 2 + STREET_BENCH_EDGE_CLEARANCE_M;
  const minimum = Math.min(bandStartM, bandEndM) + halfFootprint;
  const maximum = Math.max(bandStartM, bandEndM) - halfFootprint;
  if (minimum > maximum) return null;
  return Math.max(minimum, Math.min(maximum, preferredCenterM));
}

function cumulativeDistances(points: readonly LocalPt[]): number[] {
  const distances = [0];
  for (let index = 1; index < points.length; index += 1) {
    distances.push(distances[index - 1] + Math.hypot(
      points[index].x - points[index - 1].x,
      points[index].y - points[index - 1].y,
    ));
  }
  return distances;
}

function nearestStationIndex(distances: readonly number[], targetM: number): number {
  let bestIndex = 0;
  let bestDistance = Number.POSITIVE_INFINITY;
  distances.forEach((distance, index) => {
    const delta = Math.abs(distance - targetM);
    if (delta < bestDistance) {
      bestIndex = index;
      bestDistance = delta;
    }
  });
  return bestIndex;
}

/** Deterministic, bounded street-family furniture placement. Geometry and
 * instance counts depend only on the compiled section and centreline. */
export function buildStreetFamilyFixturePlacements({
  points,
  stationZ,
  profile,
  sectionScale,
  clearancePoints = [],
  enabled,
}: StreetFamilyFixtureOptions): StreetFamilyFixturePlacements {
  if (
    !enabled
    || !profile?.familyId
    || points.length < 3
    || !(sectionScale > 0)
    || ['woonerf_shared_street', 'multi_use_trail', 'toronto_laneway', 'green_alley']
      .includes(profile.archetypeId)
  ) return EMPTY_FIXTURES;

  const plantingBands = profile.bands
    .filter((band) => band.kind === 'planting')
    .map((band) => ({
      startM: band.startM * sectionScale,
      endM: band.endM * sectionScale,
      centerM: band.centerM * sectionScale,
    }));
  if (plantingBands.length === 0) return EMPTY_FIXTURES;

  const isMain = profile.familyId === 'street_complete_main_22m';
  const distances = cumulativeDistances(points);
  const lengthM = distances[distances.length - 1];
  const spacingM = isMain ? 24 : 28;
  const endClearanceM = 12;
  if (lengthM <= endClearanceM * 2) return EMPTY_FIXTURES;

  const selectedIndices: number[] = [];
  for (
    let targetM = endClearanceM + spacingM / 2;
    targetM <= lengthM - endClearanceM && selectedIndices.length < MAX_STREET_FIXTURE_STATIONS;
    targetM += spacingM
  ) {
    const index = nearestStationIndex(distances, targetM);
    if (index <= 0 || index >= points.length - 1 || selectedIndices.includes(index)) continue;
    const point = points[index];
    if (clearancePoints.some((clearance) => (
      Math.hypot(clearance.x - point.x, clearance.y - point.y) < STREET_NODE_FIXTURE_CLEARANCE_M
    ))) continue;
    selectedIndices.push(index);
  }

  const trees: LandscapeTreePlacement[] = [];
  const benches: StreetBenchPlacement[] = [];
  const lights: StreetLightPlacement[] = [];
  selectedIndices.forEach((index, stationOrdinal) => {
    const point = points[index];
    const previous = points[index - 1];
    const next = points[index + 1];
    const dx = next.x - previous.x;
    const dy = next.y - previous.y;
    const tangentLength = Math.hypot(dx, dy) || 1;
    const tangentX = dx / tangentLength;
    const tangentY = dy / tangentLength;
    const normalX = -tangentY;
    const normalY = tangentX;
    const yawRad = Math.atan2(dy, dx);
    const z = stationZ?.[index] ?? 0;

    plantingBands.forEach((band, sideIndex) => {
      if (trees.length < MAX_STREET_TREES_PER_ZONE) {
        trees.push({
          x: point.x + normalX * band.centerM,
          y: point.y + normalY * band.centerM,
          z: z + 0.16,
          yawRad: yawRad + sideIndex * 1.37 + index * 0.11,
          scale: (isMain ? 0.82 : 0.72) + ((index + sideIndex) % 3) * 0.06,
        });
      }
      if (lights.length < MAX_STREET_LIGHTS_PER_ZONE) {
        lights.push({
          x: point.x + normalX * band.centerM + tangentX * 1.05,
          y: point.y + normalY * band.centerM + tangentY * 1.05,
          z,
          yawRad,
        });
      }
      if (
        isMain
        && benches.length < MAX_STREET_BENCHES_PER_ZONE
        && (stationOrdinal + sideIndex) % 2 === 0
      ) {
        const benchScale = 0.9;
        const benchCenterM = resolveBenchCenterInBand(
          band.startM,
          band.endM,
          band.centerM,
          benchScale,
        );
        if (benchCenterM !== null) {
          benches.push({
            x: point.x + normalX * benchCenterM - tangentX * 1.15,
            y: point.y + normalY * benchCenterM - tangentY * 1.15,
            z: z + 0.16,
            // The bench asset's back is local +Y, so the negative-offset
            // boulevard needs a half-turn for both sides to face the street.
            yawRad: yawRad + (benchCenterM < 0 ? Math.PI : 0),
            scale: benchScale,
            bandStartM: Math.min(band.startM, band.endM),
            bandEndM: Math.max(band.startM, band.endM),
            footprintDepthM: STREET_BENCH_DEPTH_M * benchScale,
          });
        }
      }
    });
  });

  return { trees, benches, lights, stationCount: selectedIndices.length };
}
