import type {
  LandscapeBenchPlacement,
  LandscapeTreePlacement,
} from './GlobeLandscapeKit';
import {
  streetStationElevationAt,
  type LocalPt,
  type StreetStationElevationInput,
} from './streetMesh3D';
import type { StreetSectionBand, StreetSectionProfile } from './streetSectionProfiles';

export const MAX_STREET_FIXTURE_STATIONS = 8;
export const MAX_STREET_TREES_PER_ZONE = 16;
export const MAX_STREET_LIGHTS_PER_ZONE = 16;
export const MAX_STREET_BENCHES_PER_ZONE = 8;
export const MAX_STREET_DRAINS_PER_ZONE = 24;
export const MAX_STREET_SIDEWALK_JOINTS_PER_ZONE = 48;
export const MAX_STREET_WASTE_BINS_PER_ZONE = 6;
export const MAX_STREET_BIKE_RACKS_PER_ZONE = 6;
export const MAX_STREET_BOLLARDS_PER_ZONE = 24;
export const MAX_STREET_PLANTING_CELLS_PER_ZONE = 16;
export const MAX_WOONERF_PLANTERS_PER_ZONE = 12;
export const STREET_BENCH_DEPTH_M = 0.64;
export const STREET_BENCH_EDGE_CLEARANCE_M = 0.08;
export const STREET_NODE_FIXTURE_CLEARANCE_M = 12;

/** Shared local-ENU station frame for every street-family fixture. `yawRad`
 * is the fixture rotation around local up; tangent/normal remain available to
 * renderers that need to construct multi-part assemblies without re-sampling
 * the centreline. */
export interface StreetFixturePose {
  x: number;
  y: number;
  z: number;
  yawRad: number;
  stationIndex: number;
  stationM: number;
  tangentX: number;
  tangentY: number;
  normalX: number;
  normalY: number;
  offsetM: number;
}

export interface StreetTreePlacement extends LandscapeTreePlacement, StreetFixturePose {}

export interface StreetLightPlacement extends StreetFixturePose {}

export interface StreetBenchPlacement extends LandscapeBenchPlacement, StreetFixturePose {
  bandStartM: number;
  bandEndM: number;
  footprintDepthM: number;
}

export interface StreetDrainPlacement extends StreetFixturePose {
  lengthM: number;
  widthM: number;
}

export interface StreetSidewalkJointPlacement extends StreetFixturePose {
  lengthM: number;
  widthM: number;
  bandStartM: number;
  bandEndM: number;
}

export interface StreetWasteBinPlacement extends StreetFixturePose {
  scale: number;
  bandStartM: number;
  bandEndM: number;
}

export interface StreetBikeRackPlacement extends StreetFixturePose {
  rackCount: number;
  spacingM: number;
  bandStartM: number;
  bandEndM: number;
}

export interface StreetBollardPlacement extends StreetFixturePose {
  radiusM: number;
  heightM: number;
}

export type StreetPlantingCellStyle = 'tree_grate' | 'low_planting_cell';

export interface StreetPlantingCellPlacement extends StreetFixturePose {
  style: StreetPlantingCellStyle;
  lengthM: number;
  widthM: number;
  bandStartM: number;
  bandEndM: number;
}

export interface StreetFamilyFixturePlacements {
  trees: StreetTreePlacement[];
  benches: StreetBenchPlacement[];
  lights: StreetLightPlacement[];
  drains: StreetDrainPlacement[];
  sidewalkJoints: StreetSidewalkJointPlacement[];
  wasteBins: StreetWasteBinPlacement[];
  bikeRacks: StreetBikeRackPlacement[];
  bollards: StreetBollardPlacement[];
  plantingCells: StreetPlantingCellPlacement[];
  stationCount: number;
}

export interface StreetFamilyFixtureOptions {
  points: LocalPt[];
  stationZ?: StreetStationElevationInput | null;
  profile: StreetSectionProfile | null;
  sectionScale: number;
  clearancePoints?: readonly LocalPt[];
  enabled: boolean;
}

export interface WoonerfPlanterPlacement {
  x: number;
  y: number;
  centerX: number;
  centerY: number;
  /** Contact under the planter at its signed cross-section offset. */
  z: number;
  /** Contact under the transverse traffic-calming strip at the centreline. */
  centerZ: number;
  rotation: number;
}

const frozenEmpty = <T>(): T[] => Object.freeze([]) as unknown as T[];

const EMPTY_FIXTURES: StreetFamilyFixturePlacements = Object.freeze({
  trees: frozenEmpty<StreetTreePlacement>(),
  benches: frozenEmpty<StreetBenchPlacement>(),
  lights: frozenEmpty<StreetLightPlacement>(),
  drains: frozenEmpty<StreetDrainPlacement>(),
  sidewalkJoints: frozenEmpty<StreetSidewalkJointPlacement>(),
  wasteBins: frozenEmpty<StreetWasteBinPlacement>(),
  bikeRacks: frozenEmpty<StreetBikeRackPlacement>(),
  bollards: frozenEmpty<StreetBollardPlacement>(),
  plantingCells: frozenEmpty<StreetPlantingCellPlacement>(),
  stationCount: 0,
});

interface ScaledBand extends Pick<StreetSectionBand, 'kind'> {
  startM: number;
  endM: number;
  centerM: number;
  widthM: number;
}

interface StationFrame {
  index: number;
  stationM: number;
  x: number;
  y: number;
  tangentX: number;
  tangentY: number;
  normalX: number;
  normalY: number;
  yawRad: number;
  elevationAtPlacement: (offsetM: number, tangentShiftM: number) => number;
}

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

/** Interpolate a shifted fixture's terrain contact along the sampled
 * centreline. Shifts are clamped to the sampled corridor and the same signed
 * cross-section offset is evaluated at both bracketing stations, so a bench,
 * bin or rack follows both longitudinal grade and cross-slope without adding
 * any terrain rays. */
export function interpolateStreetFixtureElevation(
  stationElevation: StreetStationElevationInput | null | undefined,
  stationDistances: readonly number[],
  stationIndex: number,
  signedOffsetM: number,
  tangentShiftM: number,
): number {
  const clampedIndex = Math.max(0, Math.min(stationDistances.length - 1, stationIndex));
  const baseElevation = streetStationElevationAt(
    stationElevation ?? undefined,
    clampedIndex,
    signedOffsetM,
  );
  if (
    !stationElevation
    || stationDistances.length < 2
    || !Number.isFinite(tangentShiftM)
    || Math.abs(tangentShiftM) < 1e-8
  ) return baseElevation;

  const firstM = stationDistances[0];
  const lastM = stationDistances[stationDistances.length - 1];
  const targetM = Math.max(
    firstM,
    Math.min(lastM, stationDistances[clampedIndex] + tangentShiftM),
  );
  if (targetM <= firstM) {
    return streetStationElevationAt(stationElevation, 0, signedOffsetM);
  }
  if (targetM >= lastM) {
    return streetStationElevationAt(
      stationElevation,
      stationDistances.length - 1,
      signedOffsetM,
    );
  }

  let upperIndex = 1;
  while (
    upperIndex < stationDistances.length - 1
    && stationDistances[upperIndex] < targetM
  ) upperIndex += 1;
  const lowerIndex = upperIndex - 1;
  const lowerM = stationDistances[lowerIndex];
  const upperM = stationDistances[upperIndex];
  const spanM = upperM - lowerM;
  const mix = spanM > 1e-8 ? (targetM - lowerM) / spanM : 0;
  const lowerZ = streetStationElevationAt(stationElevation, lowerIndex, signedOffsetM);
  const upperZ = streetStationElevationAt(stationElevation, upperIndex, signedOffsetM);
  return lowerZ + (upperZ - lowerZ) * mix;
}

function isClearOfNodes(
  x: number,
  y: number,
  clearancePoints: readonly LocalPt[],
): boolean {
  return !clearancePoints.some((clearance) => (
    Math.hypot(clearance.x - x, clearance.y - y) < STREET_NODE_FIXTURE_CLEARANCE_M
  ));
}

/** Select a bounded number of stations across the complete usable segment.
 * The prior spacing loop stopped after the first eight candidates, leaving
 * the far end of long streets bare. Even target interpolation preserves the
 * desired density on short streets while covering both ends when capped. */
function selectEvenlyDistributedStationIndices({
  points,
  distances,
  spacingM,
  maxStations,
  clearancePoints,
}: {
  points: readonly LocalPt[];
  distances: readonly number[];
  spacingM: number;
  maxStations: number;
  clearancePoints: readonly LocalPt[];
}): number[] {
  if (maxStations <= 0 || points.length < 3) return [];
  const lengthM = distances[distances.length - 1] ?? 0;
  const usableLengthM = lengthM - STREET_NODE_FIXTURE_CLEARANCE_M * 2;
  if (!(usableLengthM > 0)) return [];

  const eligibleIndices = points.flatMap((point, index) => (
    index > 0
    && index < points.length - 1
    && distances[index] >= STREET_NODE_FIXTURE_CLEARANCE_M
    && distances[index] <= lengthM - STREET_NODE_FIXTURE_CLEARANCE_M
    && isClearOfNodes(point.x, point.y, clearancePoints)
      ? [index]
      : []
  ));
  if (eligibleIndices.length === 0) return [];

  const desiredCount = Math.min(
    maxStations,
    eligibleIndices.length,
    Math.max(1, Math.floor(usableLengthM / spacingM)),
  );
  const targetInsetM = Math.min(spacingM / 2, usableLengthM / 2);
  const firstTargetM = STREET_NODE_FIXTURE_CLEARANCE_M + targetInsetM;
  const lastTargetM = lengthM - STREET_NODE_FIXTURE_CLEARANCE_M - targetInsetM;
  const selectedIndices: number[] = [];

  for (let ordinal = 0; ordinal < desiredCount; ordinal += 1) {
    const mix = desiredCount === 1 ? 0.5 : ordinal / (desiredCount - 1);
    const targetM = firstTargetM + (lastTargetM - firstTargetM) * mix;
    let bestIndex = -1;
    let bestDistance = Number.POSITIVE_INFINITY;
    eligibleIndices.forEach((index) => {
      if (selectedIndices.includes(index)) return;
      const delta = Math.abs(distances[index] - targetM);
      if (delta < bestDistance) {
        bestIndex = index;
        bestDistance = delta;
      }
    });
    if (bestIndex >= 0) selectedIndices.push(bestIndex);
  }
  return selectedIndices.sort((left, right) => distances[left] - distances[right]);
}

function stationFrame(
  points: readonly LocalPt[],
  distances: readonly number[],
  stationZ: StreetStationElevationInput | null | undefined,
  index: number,
): StationFrame {
  const point = points[index];
  const previous = points[index - 1];
  const next = points[index + 1];
  const dx = next.x - previous.x;
  const dy = next.y - previous.y;
  const tangentLength = Math.hypot(dx, dy) || 1;
  const tangentX = dx / tangentLength;
  const tangentY = dy / tangentLength;
  return {
    index,
    stationM: distances[index],
    x: point.x,
    y: point.y,
    tangentX,
    tangentY,
    normalX: -tangentY,
    normalY: tangentX,
    yawRad: Math.atan2(dy, dx),
    elevationAtPlacement: (offsetM: number, tangentShiftM: number) => (
      interpolateStreetFixtureElevation(
        stationZ,
        distances,
        index,
        offsetM,
        tangentShiftM,
      )
    ),
  };
}

function fixturePose(
  frame: StationFrame,
  offsetM: number,
  tangentShiftM = 0,
  yawRad = frame.yawRad,
): StreetFixturePose {
  return {
    x: frame.x + frame.normalX * offsetM + frame.tangentX * tangentShiftM,
    y: frame.y + frame.normalY * offsetM + frame.tangentY * tangentShiftM,
    z: frame.elevationAtPlacement(offsetM, tangentShiftM),
    yawRad,
    stationIndex: frame.index,
    stationM: frame.stationM,
    tangentX: frame.tangentX,
    tangentY: frame.tangentY,
    normalX: frame.normalX,
    normalY: frame.normalY,
    offsetM,
  };
}

function scaleBand(band: StreetSectionBand, sectionScale: number): ScaledBand {
  return {
    kind: band.kind,
    startM: band.startM * sectionScale,
    endM: band.endM * sectionScale,
    centerM: band.centerM * sectionScale,
    widthM: band.widthM * sectionScale,
  };
}

function fixtureFitsClearance(
  pose: Pick<StreetFixturePose, 'x' | 'y'>,
  clearancePoints: readonly LocalPt[],
): boolean {
  return isClearOfNodes(pose.x, pose.y, clearancePoints);
}

/** Bounded alternating chicanes for the flush woonerf family. Candidate
 * stations are evenly sampled when a long corridor exceeds the cap. */
export function buildWoonerfPlanterPlacements(
  points: readonly LocalPt[],
  halfWidthM: number,
  stationZ?: StreetStationElevationInput | null,
): WoonerfPlanterPlacement[] {
  if (points.length < 5 || !(halfWidthM > 0)) return [];
  const candidates: number[] = [];
  for (let index = 2; index < points.length - 2; index += 3) candidates.push(index);
  const selected = candidates.length <= MAX_WOONERF_PLANTERS_PER_ZONE
    ? candidates
    : Array.from({ length: MAX_WOONERF_PLANTERS_PER_ZONE }, (_, ordinal) => (
      candidates[Math.round(
        ordinal * (candidates.length - 1) / (MAX_WOONERF_PLANTERS_PER_ZONE - 1),
      )]
    ));
  return selected.map((index, ordinal) => {
    const previous = points[index - 1];
    const next = points[index + 1];
    const dx = next.x - previous.x;
    const dy = next.y - previous.y;
    const length = Math.hypot(dx, dy) || 1;
    const normalX = -dy / length;
    const normalY = dx / length;
    const side = ordinal % 2 === 0 ? -1 : 1;
    const offset = Math.max(0.8, halfWidthM * 0.72) * side;
    return {
      x: points[index].x + normalX * offset,
      y: points[index].y + normalY * offset,
      centerX: points[index].x,
      centerY: points[index].y,
      z: streetStationElevationAt(stationZ ?? undefined, index, offset),
      centerZ: streetStationElevationAt(stationZ ?? undefined, index, 0),
      rotation: Math.atan2(dy, dx),
    };
  });
}

/** Deterministic, bounded street-family furniture and surface-detail
 * placement. Geometry and instance counts depend only on the compiled
 * section and centreline. */
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
    || ['woonerf_shared_street', 'multi_use_trail', 'toronto_laneway']
      .includes(profile.archetypeId)
  ) return EMPTY_FIXTURES;

  const bands = profile.bands.map((band) => scaleBand(band, sectionScale));
  const plantingBands = bands.filter((band) => band.kind === 'planting');
  const sidewalkBands = bands.filter((band) => band.kind === 'sidewalk');
  const cycleBands = bands.filter((band) => band.kind === 'cycle');
  const bufferBands = bands.filter((band) => band.kind === 'buffer');
  const isMain = profile.familyId === 'street_complete_main_22m';
  const distances = cumulativeDistances(points);
  const lengthM = distances[distances.length - 1];
  if (lengthM <= STREET_NODE_FIXTURE_CLEARANCE_M * 2) return EMPTY_FIXTURES;

  const selectStations = (spacingM: number, maxStations: number) => (
    selectEvenlyDistributedStationIndices({
      points,
      distances,
      spacingM,
      maxStations,
      clearancePoints,
    })
  );
  const selectedIndices = selectStations(isMain ? 24 : 28, MAX_STREET_FIXTURE_STATIONS);

  const trees: StreetTreePlacement[] = [];
  const benches: StreetBenchPlacement[] = [];
  const lights: StreetLightPlacement[] = [];
  const drains: StreetDrainPlacement[] = [];
  const sidewalkJoints: StreetSidewalkJointPlacement[] = [];
  const wasteBins: StreetWasteBinPlacement[] = [];
  const bikeRacks: StreetBikeRackPlacement[] = [];
  const bollards: StreetBollardPlacement[] = [];
  const plantingCells: StreetPlantingCellPlacement[] = [];

  selectedIndices.forEach((index, stationOrdinal) => {
    const frame = stationFrame(points, distances, stationZ, index);
    plantingBands.forEach((band, sideIndex) => {
      const basePose = fixturePose(frame, band.centerM);
      if (
        trees.length < MAX_STREET_TREES_PER_ZONE
        && fixtureFitsClearance(basePose, clearancePoints)
      ) {
        trees.push({
          ...basePose,
          z: basePose.z + 0.16,
          yawRad: frame.yawRad + sideIndex * 1.37 + index * 0.11,
          scale: (isMain ? 0.82 : 0.72) + ((index + sideIndex) % 3) * 0.06,
        });
      }
      if (
        lights.length < MAX_STREET_LIGHTS_PER_ZONE
      ) {
        const lightPose = fixturePose(frame, band.centerM, 1.05);
        if (fixtureFitsClearance(lightPose, clearancePoints)) lights.push(lightPose);
      }

      const plantingWidthM = Math.max(0, band.widthM - STREET_BENCH_EDGE_CLEARANCE_M * 2);
      if (
        plantingCells.length < MAX_STREET_PLANTING_CELLS_PER_ZONE
        && plantingWidthM >= 0.3
        && fixtureFitsClearance(basePose, clearancePoints)
      ) {
        plantingCells.push({
          ...basePose,
          style: isMain ? 'tree_grate' : 'low_planting_cell',
          lengthM: isMain ? Math.min(1.05, plantingWidthM) : 1.5,
          widthM: Math.min(isMain ? 1.05 : 0.9, plantingWidthM),
          bandStartM: Math.min(band.startM, band.endM),
          bandEndM: Math.max(band.startM, band.endM),
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
          const benchPose = fixturePose(
            frame,
            benchCenterM,
            -1.15,
            frame.yawRad + (benchCenterM < 0 ? Math.PI : 0),
          );
          if (fixtureFitsClearance(benchPose, clearancePoints)) {
            benches.push({
              ...benchPose,
              z: benchPose.z + 0.16,
              scale: benchScale,
              bandStartM: Math.min(band.startM, band.endM),
              bandEndM: Math.max(band.startM, band.endM),
              footprintDepthM: STREET_BENCH_DEPTH_M * benchScale,
            });
          }
        }
      }

      if (
        isMain
        && wasteBins.length < MAX_STREET_WASTE_BINS_PER_ZONE
        && (stationOrdinal + sideIndex) % 4 === 0
      ) {
        const pose = fixturePose(frame, band.centerM, 2.1);
        if (fixtureFitsClearance(pose, clearancePoints)) {
          wasteBins.push({
            ...pose,
            scale: 0.92,
            bandStartM: Math.min(band.startM, band.endM),
            bandEndM: Math.max(band.startM, band.endM),
          });
        }
      }

      if (
        isMain
        && bikeRacks.length < MAX_STREET_BIKE_RACKS_PER_ZONE
        && (stationOrdinal + sideIndex) % 4 === 2
      ) {
        const pose = fixturePose(frame, band.centerM, -2.25);
        if (fixtureFitsClearance(pose, clearancePoints)) {
          bikeRacks.push({
            ...pose,
            rackCount: 3,
            spacingM: 0.72,
            bandStartM: Math.min(band.startM, band.endM),
            bandEndM: Math.max(band.startM, band.endM),
          });
        }
      }
    });
  });

  const scaledCurbOffsets = profile.renderCurbs
    ? profile.curbOffsetsM.map((offsetM) => offsetM * sectionScale)
    : [];
  const drainStationCap = scaledCurbOffsets.length > 0
    ? Math.floor(MAX_STREET_DRAINS_PER_ZONE / scaledCurbOffsets.length)
    : 0;
  selectStations(30, drainStationCap).forEach((index) => {
    const frame = stationFrame(points, distances, stationZ, index);
    scaledCurbOffsets.forEach((offsetM) => {
      if (drains.length >= MAX_STREET_DRAINS_PER_ZONE) return;
      const pose = fixturePose(frame, offsetM);
      if (!fixtureFitsClearance(pose, clearancePoints)) return;
      drains.push({ ...pose, lengthM: 0.56, widthM: 0.3 });
    });
  });

  const jointStationCap = sidewalkBands.length > 0
    ? Math.floor(MAX_STREET_SIDEWALK_JOINTS_PER_ZONE / sidewalkBands.length)
    : 0;
  selectStations(8, jointStationCap).forEach((index) => {
    const frame = stationFrame(points, distances, stationZ, index);
    sidewalkBands.forEach((band) => {
      if (sidewalkJoints.length >= MAX_STREET_SIDEWALK_JOINTS_PER_ZONE) return;
      const pose = fixturePose(frame, band.centerM);
      if (!fixtureFitsClearance(pose, clearancePoints)) return;
      sidewalkJoints.push({
        ...pose,
        lengthM: 0.035,
        widthM: Math.max(0.2, band.widthM - 0.16),
        bandStartM: Math.min(band.startM, band.endM),
        bandEndM: Math.max(band.startM, band.endM),
      });
    });
  });

  const cycleProtectionOffsets = bufferBands.length > 0
    ? bufferBands.map((band) => band.centerM)
    : cycleBands.map((band) => (
      Math.abs(band.startM) < Math.abs(band.endM) ? band.startM : band.endM
    ));
  const bollardStationCap = cycleProtectionOffsets.length > 0
    ? Math.floor(MAX_STREET_BOLLARDS_PER_ZONE / cycleProtectionOffsets.length)
    : 0;
  selectStations(10, bollardStationCap).forEach((index) => {
    const frame = stationFrame(points, distances, stationZ, index);
    cycleProtectionOffsets.forEach((offsetM) => {
      if (bollards.length >= MAX_STREET_BOLLARDS_PER_ZONE) return;
      const pose = fixturePose(frame, offsetM);
      if (!fixtureFitsClearance(pose, clearancePoints)) return;
      bollards.push({ ...pose, radiusM: 0.08, heightM: 0.82 });
    });
  });

  return {
    trees,
    benches,
    lights,
    drains,
    sidewalkJoints,
    wasteBins,
    bikeRacks,
    bollards,
    plantingCells,
    stationCount: selectedIndices.length,
  };
}
