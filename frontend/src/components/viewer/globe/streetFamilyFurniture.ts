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
export const MAX_WOONERF_PLAY_NODES_PER_ZONE = 3;
export const MAX_NARROW_RESIDENTIAL_TREES_PER_ZONE = 48;
export const MAX_NARROW_RESIDENTIAL_LIGHTS_PER_ZONE = 16;
export const MAX_NARROW_RESIDENTIAL_VEHICLES_PER_ZONE = 16;
export const MAX_MAIN_STREET_TREES_PER_ZONE = 48;
export const MAX_MAIN_STREET_LIGHTS_PER_ZONE = 20;
export const MAX_MAIN_STREET_VEHICLES_PER_ZONE = 40;
export const NARROW_RESIDENTIAL_TREE_SPACING_M = 10.5;
export const NARROW_RESIDENTIAL_LIGHT_SPACING_M = 21;
export const NARROW_RESIDENTIAL_VEHICLE_SPACING_M = 18;
export const MAIN_STREET_TREE_SPACING_M = 10;
export const MAIN_STREET_LIGHT_SPACING_M = 20;
export const MAIN_STREET_VEHICLE_SPACING_M = 12;
export const STREET_BENCH_DEPTH_M = 0.64;
export const STREET_BENCH_EDGE_CLEARANCE_M = 0.08;
export const STREET_NODE_FIXTURE_CLEARANCE_M = 12;
export const STREET_PARKED_VEHICLE_EDGE_CLEARANCE_M = 0.06;
export const STREET_TRANSIT_SHELTER_NOMINAL_DEPTH_M = 1.62;
export const STREET_TRANSIT_SHELTER_EDGE_CLEARANCE_M = 0.04;
export const STREET_TRANSIT_SHELTER_MAX_SCALE = 0.84;

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

export type StreetTreeCanopyClass =
  | 'standard'
  | 'mature_deciduous'
  | 'columnar_deciduous'
  | 'pollarded_deciduous'
  | 'tropical_palm';

export interface StreetTreePlacement extends LandscapeTreePlacement, StreetFixturePose {
  canopyClass?: StreetTreeCanopyClass;
}

export type StreetLightStyle = 'contemporary' | 'traditional';

export interface StreetLightPlacement extends StreetFixturePose {
  fixtureStyle?: StreetLightStyle;
}

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

export type StreetParkedVehicleType = 'sedan' | 'suv';

/** One parallel-parked vehicle authored in the street's local ENU frame.
 * Dimensions are the actual rendered footprint after fitting to the authored
 * parking band; narrow legacy bands therefore produce a deliberately compact
 * vehicle rather than allowing bodywork to spill into a travel lane. */
export interface StreetParkedVehiclePlacement extends StreetFixturePose {
  vehicleType: StreetParkedVehicleType;
  lengthM: number;
  widthM: number;
  heightM: number;
  bodyColor: string;
  bandStartM: number;
  bandEndM: number;
}

export interface StreetTransitShelterPlacement extends StreetFixturePose {
  scale: number;
  bandStartM: number;
  bandEndM: number;
  footprintDepthM: number;
  surfaceLiftM: number;
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
  parkedVehicles: StreetParkedVehiclePlacement[];
  transitShelters: StreetTransitShelterPlacement[];
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

export interface WoonerfPlayPlacement {
  x: number;
  y: number;
  z: number;
  rotation: number;
  scale: number;
}

export interface YieldStreetSignPlacement extends StreetFixturePose {
  side: -1 | 1;
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
  parkedVehicles: frozenEmpty<StreetParkedVehiclePlacement>(),
  transitShelters: frozenEmpty<StreetTransitShelterPlacement>(),
  stationCount: 0,
});

interface ScaledBand extends Pick<StreetSectionBand, 'kind' | 'liftM'> {
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

/** Build a centreline frame at an exact metric station rather than snapping
 * archetype-signature fixtures to the input polyline sampling interval. This
 * keeps a 10.5 m tree rhythm stable whether the source line was sampled every
 * metre or every ten metres. */
function stationFrameAtDistance(
  points: readonly LocalPt[],
  distances: readonly number[],
  stationZ: StreetStationElevationInput | null | undefined,
  requestedStationM: number,
): StationFrame {
  const finalIndex = points.length - 1;
  const lengthM = distances[finalIndex] ?? 0;
  const stationM = Math.max(0, Math.min(lengthM, requestedStationM));
  let upperIndex = 1;
  while (upperIndex < finalIndex && distances[upperIndex] < stationM) upperIndex += 1;
  const lowerIndex = Math.max(0, upperIndex - 1);
  const lowerM = distances[lowerIndex];
  const upperM = distances[upperIndex];
  const segmentLengthM = Math.max(1e-8, upperM - lowerM);
  const mix = Math.max(0, Math.min(1, (stationM - lowerM) / segmentLengthM));
  const lower = points[lowerIndex];
  const upper = points[upperIndex];
  const dx = upper.x - lower.x;
  const dy = upper.y - lower.y;
  const tangentLength = Math.hypot(dx, dy) || 1;
  const tangentX = dx / tangentLength;
  const tangentY = dy / tangentLength;
  const stationShiftM = stationM - lowerM;
  return {
    index: lowerIndex,
    stationM,
    x: lower.x + dx * mix,
    y: lower.y + dy * mix,
    tangentX,
    tangentY,
    normalX: -tangentY,
    normalY: tangentX,
    yawRad: Math.atan2(dy, dx),
    elevationAtPlacement: (offsetM: number, tangentShiftM: number) => (
      interpolateStreetFixtureElevation(
        stationZ,
        distances,
        lowerIndex,
        offsetM,
        stationShiftM + tangentShiftM,
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
    liftM: band.liftM,
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

function signatureStationDistances(
  lengthM: number,
  spacingM: number,
  maxCount: number,
): number[] {
  const firstM = STREET_NODE_FIXTURE_CLEARANCE_M + spacingM / 2;
  const lastM = lengthM - STREET_NODE_FIXTURE_CLEARANCE_M - spacingM / 2;
  if (firstM > lastM || maxCount <= 0) return [];
  const naturalCount = Math.floor((lastM - firstM) / spacingM + 1e-8) + 1;
  if (naturalCount <= maxCount) {
    return Array.from({ length: naturalCount }, (_, index) => firstM + index * spacingM);
  }

  // Preserve the authored rhythm on normal blocks. On exceptionally long
  // corridors, distribute the bounded instances across the whole segment so
  // the far end does not lose its canopy, lights, or parked-car context.
  if (maxCount === 1) return [(firstM + lastM) / 2];
  return Array.from(
    { length: maxCount },
    (_, index) => firstM + ((lastM - firstM) * index) / (maxCount - 1),
  );
}

function fixtureFootprintFitsNodeClearance(
  pose: Pick<StreetFixturePose, 'x' | 'y'>,
  clearancePoints: readonly LocalPt[],
  footprintRadiusM = 0,
): boolean {
  return !clearancePoints.some((clearance) => (
    Math.hypot(clearance.x - pose.x, clearance.y - pose.y)
      < STREET_NODE_FIXTURE_CLEARANCE_M + footprintRadiusM
  ));
}

interface StreetSignaturePlacements {
  trees: StreetTreePlacement[];
  lights: StreetLightPlacement[];
  parkedVehicles: StreetParkedVehiclePlacement[];
}

/** Archetype-defining fixtures for the residential and complete-main visual
 * variants. Their
 * positions are authored in metres, are deterministic, and use the complete
 * parking footprint for containment and node-clearance checks. */
function buildStreetSignaturePlacements({
  points,
  distances,
  stationZ,
  treeBands,
  lightBands,
  parkingBands,
  clearancePoints,
  treeSpacingM,
  lightSpacingM,
  vehicleSpacingM,
  maxTrees,
  maxLights,
  maxVehicles,
  treeScaleBase,
  bilateralVehicles,
  bilateralLights,
  canopyClass,
  lightStyle,
}: {
  points: readonly LocalPt[];
  distances: readonly number[];
  stationZ: StreetStationElevationInput | null | undefined;
  treeBands: readonly ScaledBand[];
  lightBands: readonly ScaledBand[];
  parkingBands: readonly ScaledBand[];
  clearancePoints: readonly LocalPt[];
  treeSpacingM: number;
  lightSpacingM: number;
  vehicleSpacingM: number;
  maxTrees: number;
  maxLights: number;
  maxVehicles: number;
  treeScaleBase: number;
  bilateralVehicles: boolean;
  bilateralLights: boolean;
  canopyClass: StreetTreeCanopyClass;
  lightStyle: StreetLightStyle;
}): StreetSignaturePlacements {
  const lengthM = distances[distances.length - 1] ?? 0;
  const endpointNodes = [points[0], points[points.length - 1], ...clearancePoints];
  const trees: StreetTreePlacement[] = [];
  const lights: StreetLightPlacement[] = [];
  const parkedVehicles: StreetParkedVehiclePlacement[] = [];

  const treeStationCap = Math.floor(
    maxTrees / Math.max(1, treeBands.length),
  );
  signatureStationDistances(
    lengthM,
    treeSpacingM,
    treeStationCap,
  ).forEach((stationM, stationOrdinal) => {
    const frame = stationFrameAtDistance(points, distances, stationZ, stationM);
    treeBands.forEach((band, sideIndex) => {
      if (trees.length >= maxTrees) return;
      const pose = fixturePose(
        frame,
        band.centerM,
        0,
        frame.yawRad + stationOrdinal * 0.61 + sideIndex * 1.73,
      );
      if (!fixtureFootprintFitsNodeClearance(pose, endpointNodes)) return;
      trees.push({
        ...pose,
        z: pose.z + 0.16,
        scale: treeScaleBase + ((stationOrdinal + sideIndex * 2) % 4) * 0.04,
        canopyClass,
      });
    });
  });

  const lightStationCap = bilateralLights
    ? Math.floor(maxLights / Math.max(1, lightBands.length))
    : maxLights;
  signatureStationDistances(
    lengthM,
    lightSpacingM,
    lightStationCap,
  ).forEach((stationM, stationOrdinal) => {
    if (lightBands.length === 0) return;
    const frame = stationFrameAtDistance(points, distances, stationZ, stationM);
    const candidateBands = bilateralLights
      ? lightBands
      : [lightBands[stationOrdinal % lightBands.length]];
    candidateBands.forEach((band) => {
      if (lights.length >= maxLights) return;
      const inwardYaw = frame.yawRad + (band.centerM < 0 ? Math.PI / 2 : -Math.PI / 2);
      const pose = fixturePose(frame, band.centerM, 0, inwardYaw);
      if (!fixtureFootprintFitsNodeClearance(pose, endpointNodes)) return;
      lights.push({ ...pose, fixtureStyle: lightStyle });
    });
  });

  const vehicleColors = ['#34506a', '#7b817d', '#6f2f2d', '#d2d0c8', '#383a3d'];
  signatureStationDistances(
    lengthM,
    vehicleSpacingM,
    bilateralVehicles ? Math.ceil(maxVehicles / Math.max(1, parkingBands.length)) : maxVehicles,
  ).forEach((stationM, stationOrdinal) => {
    if (parkingBands.length === 0) return;
    const candidateBands = bilateralVehicles
      ? parkingBands
      : [parkingBands[stationOrdinal % parkingBands.length]];
    candidateBands.forEach((band, sideIndex) => {
      if (parkedVehicles.length >= maxVehicles) return;
      const vehicleType: StreetParkedVehicleType = (stationOrdinal + sideIndex) % 3 === 1
        ? 'suv'
        : 'sedan';
      const nominalWidthM = vehicleType === 'suv' ? 1.86 : 1.78;
      const availableWidthM = Math.max(
        0,
        band.widthM - STREET_PARKED_VEHICLE_EDGE_CLEARANCE_M * 2,
      );
      const widthM = Math.min(nominalWidthM, availableWidthM);
      if (widthM < 1.1) return;
      const lengthMForVehicle = vehicleType === 'suv' ? 4.75 : 4.45;
      const heightM = vehicleType === 'suv' ? 1.72 : 1.48;
      const frame = stationFrameAtDistance(points, distances, stationZ, stationM);
      const pose = fixturePose(
        frame,
        band.centerM,
        0,
        frame.yawRad + (band.centerM > 0 ? Math.PI : 0),
      );
      const footprintRadiusM = Math.hypot(lengthMForVehicle, widthM) / 2;
      if (!fixtureFootprintFitsNodeClearance(pose, endpointNodes, footprintRadiusM)) return;
      const bandStartM = Math.min(band.startM, band.endM);
      const bandEndM = Math.max(band.startM, band.endM);
      if (
        pose.offsetM - widthM / 2
          < bandStartM + STREET_PARKED_VEHICLE_EDGE_CLEARANCE_M - 1e-8
        || pose.offsetM + widthM / 2
          > bandEndM - STREET_PARKED_VEHICLE_EDGE_CLEARANCE_M + 1e-8
      ) return;
      parkedVehicles.push({
        ...pose,
        vehicleType,
        lengthM: lengthMForVehicle,
        widthM,
        heightM,
        bodyColor: vehicleColors[(stationOrdinal + sideIndex * 2) % vehicleColors.length],
        bandStartM,
        bandEndM,
      });
    });
  });

  return { trees, lights, parkedVehicles };
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

/** Small social-play moments repeat at an approximately 48 m cadence beside
 * the planter chicane. They stay on the same edge as the planter so the
 * emergency/walking route remains continuous through the shared centre. */
export function buildWoonerfPlayPlacements(
  planters: readonly WoonerfPlanterPlacement[],
): WoonerfPlayPlacement[] {
  return planters
    .filter((_, index) => index % 4 === 2)
    .slice(0, MAX_WOONERF_PLAY_NODES_PER_ZONE)
    .map((planter, index) => ({
      x: planter.x + Math.cos(planter.rotation) * 2.35,
      y: planter.y + Math.sin(planter.rotation) * 2.35,
      z: planter.z,
      rotation: planter.rotation + (index % 2 === 0 ? 0 : Math.PI),
      scale: 0.9 + index * 0.04,
    }));
}

/** Yield signs live only at the two entry thresholds, outside the shared
 * running surface. Short fragments receive one centered threshold sign rather
 * than two overlapping fixtures. */
export function buildYieldStreetEntrySignPlacements(
  points: readonly LocalPt[],
  halfWidthM: number,
  stationZ?: StreetStationElevationInput | null,
): YieldStreetSignPlacement[] {
  if (points.length < 2 || !(halfWidthM > 0.6)) return [];
  const distances = cumulativeDistances(points);
  const lengthM = distances[distances.length - 1] ?? 0;
  if (lengthM < 4) return [];
  const insetM = Math.min(6, Math.max(2, lengthM * 0.15));
  const stations = lengthM >= insetM * 2 + 4
    ? [insetM, lengthM - insetM]
    : [lengthM / 2];
  const edgeOffsetM = Math.max(0.25, halfWidthM - 0.48);
  return stations.map((stationM, index) => {
    const frame = stationFrameAtDistance(points, distances, stationZ, stationM);
    const side = (index % 2 === 0 ? -1 : 1) as -1 | 1;
    return {
      ...fixturePose(
        frame,
        edgeOffsetM * side,
        0,
        frame.yawRad + (index === 0 ? 0 : Math.PI),
      ),
      side,
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
  const parkingBands = bands.filter((band) => band.kind === 'parking');
  const sidewalkBands = bands.filter((band) => band.kind === 'sidewalk');
  const cycleBands = bands.filter((band) => band.kind === 'cycle');
  const bufferBands = bands.filter((band) => band.kind === 'buffer');
  const isMain = [
    'street_complete_main_18m',
    'street_complete_main_22m',
  ].includes(profile.familyId);
  const isNarrowResidential = profile.archetypeId === 'narrow_residential_street';
  const sidePlantingBands = plantingBands.filter((band) => !(
    Math.min(band.startM, band.endM) < 0
    && Math.max(band.startM, band.endM) > 0
  ));
  const hasCenterPlantingBand = sidePlantingBands.length < plantingBands.length;
  // A planted centre median remains a valid tree site, but not a safe place
  // for benches, lights, bins, racks or a transit shelter. When an authored
  // section has no side furnishing strip (the tropical profiles), use its
  // outer sidewalks as the bounded furnishing surface instead.
  const furnishingBands = sidePlantingBands.length > 0
    ? sidePlantingBands
    : (hasCenterPlantingBand ? sidewalkBands : []);
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
        !isNarrowResidential
        && !isMain
        && trees.length < MAX_STREET_TREES_PER_ZONE
        && fixtureFitsClearance(basePose, clearancePoints)
      ) {
        trees.push({
          ...basePose,
          z: basePose.z + 0.16,
          yawRad: frame.yawRad + sideIndex * 1.37 + index * 0.11,
          scale: (isMain ? 0.82 : 0.72) + ((index + sideIndex) % 3) * 0.06,
        });
      }
    });

    furnishingBands.forEach((band) => {
      if (
        !isNarrowResidential
        && !isMain
        && lights.length < MAX_STREET_LIGHTS_PER_ZONE
      ) {
        const lightPose = fixturePose(frame, band.centerM, 1.05);
        if (fixtureFitsClearance(lightPose, clearancePoints)) lights.push(lightPose);
      }
    });

    sidePlantingBands.forEach((band) => {
      const basePose = fixturePose(frame, band.centerM);
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
    });

    furnishingBands.forEach((band, sideIndex) => {
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

  const signatureStyle = (() => {
    switch (profile.appearanceKitId) {
      case 'modern_minimalist_v1':
        return {
          canopyClass: 'columnar_deciduous' as const,
          lightStyle: 'contemporary' as const,
          treeScaleFactor: 0.92,
        };
      case 'european_cobblestone_v1':
        return {
          canopyClass: 'pollarded_deciduous' as const,
          lightStyle: 'traditional' as const,
          treeScaleFactor: 0.94,
        };
      case 'tropical_boulevard_v1':
        return {
          canopyClass: 'tropical_palm' as const,
          lightStyle: 'contemporary' as const,
          treeScaleFactor: 1,
        };
      default:
        return {
          canopyClass: 'mature_deciduous' as const,
          lightStyle: 'traditional' as const,
          treeScaleFactor: 1,
        };
    }
  })();
  const streetSignature = isNarrowResidential || isMain
    ? buildStreetSignaturePlacements({
      points,
      distances,
      stationZ,
      treeBands: plantingBands,
      lightBands: furnishingBands,
      parkingBands,
      clearancePoints,
      treeSpacingM: isMain ? MAIN_STREET_TREE_SPACING_M : NARROW_RESIDENTIAL_TREE_SPACING_M,
      lightSpacingM: isMain ? MAIN_STREET_LIGHT_SPACING_M : NARROW_RESIDENTIAL_LIGHT_SPACING_M,
      vehicleSpacingM: isMain ? MAIN_STREET_VEHICLE_SPACING_M : NARROW_RESIDENTIAL_VEHICLE_SPACING_M,
      maxTrees: isMain ? MAX_MAIN_STREET_TREES_PER_ZONE : MAX_NARROW_RESIDENTIAL_TREES_PER_ZONE,
      maxLights: isMain ? MAX_MAIN_STREET_LIGHTS_PER_ZONE : MAX_NARROW_RESIDENTIAL_LIGHTS_PER_ZONE,
      maxVehicles: isMain ? MAX_MAIN_STREET_VEHICLES_PER_ZONE : MAX_NARROW_RESIDENTIAL_VEHICLES_PER_ZONE,
      treeScaleBase: (isMain ? 1.1 : 1.05) * signatureStyle.treeScaleFactor,
      bilateralVehicles: isMain,
      bilateralLights: isMain,
      canopyClass: signatureStyle.canopyClass,
      lightStyle: signatureStyle.lightStyle,
    })
    : null;

  const transitShelters: StreetTransitShelterPlacement[] = [];
  if (isMain && furnishingBands.length > 0 && lengthM >= 60) {
    const band = furnishingBands[0];
    const availableDepthM = Math.max(
      0,
      band.widthM - STREET_TRANSIT_SHELTER_EDGE_CLEARANCE_M * 2,
    );
    const scale = Math.min(
      STREET_TRANSIT_SHELTER_MAX_SCALE,
      availableDepthM / STREET_TRANSIT_SHELTER_NOMINAL_DEPTH_M,
    );
    if (scale >= 0.55) {
      const stationM = Math.max(24, Math.min(lengthM - 24, lengthM * 0.35));
      const frame = stationFrameAtDistance(points, distances, stationZ, stationM);
      const pose = fixturePose(
        frame,
        band.centerM,
        0,
        frame.yawRad + (band.centerM < 0 ? Math.PI : 0),
      );
      if (fixtureFootprintFitsNodeClearance(pose, [points[0], points[points.length - 1], ...clearancePoints], 2.35)) {
        transitShelters.push({
          ...pose,
          scale,
          bandStartM: Math.min(band.startM, band.endM),
          bandEndM: Math.max(band.startM, band.endM),
          footprintDepthM: STREET_TRANSIT_SHELTER_NOMINAL_DEPTH_M * scale,
          surfaceLiftM: band.liftM,
        });
      }
    }
  }

  return {
    trees: streetSignature?.trees ?? trees,
    benches,
    lights: streetSignature?.lights ?? lights,
    drains,
    sidewalkJoints,
    wasteBins,
    bikeRacks,
    bollards,
    plantingCells,
    parkedVehicles: streetSignature?.parkedVehicles ?? [],
    transitShelters,
    stationCount: selectedIndices.length,
  };
}
