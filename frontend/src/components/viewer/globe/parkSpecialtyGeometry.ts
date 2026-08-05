import {
  JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M,
  type ParkGroundGuide,
  type ParkSpecialtyStructureKind,
} from './parkGroundProfiles';
import { fitFixedParkProgram, fitSkateParkV0Program } from './skateParkFit';

export interface ParkSpecialtyPoint {
  x: number;
  y: number;
}

export interface ParkSpecialtyProgramFrame {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  width: number;
  height: number;
  points?: ParkSpecialtyPoint[];
}

export interface ParkSpecialtyRectangle {
  center: ParkSpecialtyPoint;
  width: number;
  height: number;
  rotationRad: number;
}

export const MAX_PARK_SPECIALTY_TERRAIN_ANCHORS = 24 as const;

function guideCenter(
  guide: ParkGroundGuide,
  frame: ParkSpecialtyProgramFrame,
): ParkSpecialtyPoint {
  return {
    x: frame.minX + frame.width * guide.x,
    y: frame.maxY - frame.height * guide.y,
  };
}

function guideDimensions(
  guide: ParkGroundGuide,
  frame: ParkSpecialtyProgramFrame,
): { width: number; height: number } {
  return {
    width: guide.widthM ?? guide.width * frame.width,
    height: guide.heightM ?? guide.height * frame.height,
  };
}

/** Resolve the two authored stormwater service rectangles after parcel fitting.
 * Their west/east order is part of the park-family contract: inlet first,
 * outlet/weir second. Keeping this resolution shared prevents the live 3D
 * infrastructure from drifting away from the ground diagram. */
export function resolveStormwaterInfrastructureGuides(
  guides: readonly ParkGroundGuide[],
  frame: ParkSpecialtyProgramFrame,
): { inlet: ParkSpecialtyRectangle; outlet: ParkSpecialtyRectangle } | null {
  const rectangles = guides
    .filter((guide) => guide.kind === 'rectangle')
    .map((guide): ParkSpecialtyRectangle => {
      const dimensions = guideDimensions(guide, frame);
      return {
        center: guideCenter(guide, frame),
        width: Math.max(0.5, dimensions.width),
        height: Math.max(0.5, dimensions.height),
        rotationRad: -((guide.rotationDeg ?? 0) * Math.PI) / 180,
      };
    })
    .sort((left, right) => left.center.x - right.center.x);
  if (rectangles.length < 2) return null;
  return {
    inlet: rectangles[0],
    outlet: rectangles[rectangles.length - 1],
  };
}

export function parkSpecialtyGuideRoute(
  guide: ParkGroundGuide,
  frame: ParkSpecialtyProgramFrame,
): ParkSpecialtyPoint[] {
  if (guide.points && guide.points.length >= 2) {
    return guide.points.map(([x, y]) => ({
      x: frame.minX + frame.width * x,
      y: frame.maxY - frame.height * y,
    }));
  }
  const center = guideCenter(guide, frame);
  const dimensions = guideDimensions(guide, frame);
  const angle = -((guide.rotationDeg ?? 0) * Math.PI) / 180;
  const length = Math.max(0.5, Math.hypot(dimensions.width, dimensions.height));
  const dx = Math.cos(angle) * length / 2;
  const dy = Math.sin(angle) * length / 2;
  return [
    { x: center.x - dx, y: center.y - dy },
    { x: center.x + dx, y: center.y + dy },
  ];
}

/** Place gateway markers on the first route-segment normal while preserving
 * the full authored clear route between them. */
export function buildGreenwayGatewayBollardAnchors(
  route: readonly ParkSpecialtyPoint[],
  clearRouteWidthM = 3.5,
  edgeClearanceM = 0.45,
): ParkSpecialtyPoint[] {
  if (route.length < 2) return [];
  const first = route[0];
  const second = route[1];
  const length = Math.hypot(second.x - first.x, second.y - first.y);
  if (length <= 1e-6) return [];
  const nx = -(second.y - first.y) / length;
  const ny = (second.x - first.x) / length;
  const offset = Math.max(0, clearRouteWidthM) / 2 + Math.max(0, edgeClearanceM);
  return [-1, 1].map((side) => ({
    x: first.x + nx * offset * side,
    y: first.y + ny * offset * side,
  }));
}

function rectangleAnchors(
  center: ParkSpecialtyPoint,
  width: number,
  height: number,
  angleRad = 0,
): ParkSpecialtyPoint[] {
  const cos = Math.cos(angleRad);
  const sin = Math.sin(angleRad);
  return [
    center,
    ...([[-1, -1], [1, -1], [1, 1], [-1, 1]] as const).map(([sx, sy]) => {
      const dx = sx * width / 2;
      const dy = sy * height / 2;
      return {
        x: center.x + dx * cos - dy * sin,
        y: center.y + dx * sin + dy * cos,
      };
    }),
  ];
}

function boundedUniqueAnchors(points: readonly ParkSpecialtyPoint[]): ParkSpecialtyPoint[] {
  const unique: ParkSpecialtyPoint[] = [];
  const seen = new Set<string>();
  for (const point of points) {
    if (!Number.isFinite(point.x) || !Number.isFinite(point.y)) continue;
    const key = `${point.x.toFixed(3)}:${point.y.toFixed(3)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    unique.push(point);
  }
  if (unique.length <= MAX_PARK_SPECIALTY_TERRAIN_ANCHORS) return unique;
  return Array.from({ length: MAX_PARK_SPECIALTY_TERRAIN_ANCHORS }, (_, index) => (
    unique[Math.round(index * (unique.length - 1) / (MAX_PARK_SPECIALTY_TERRAIN_ANCHORS - 1))]
  ));
}

/** Actual assembly anchors used to fit contact for long fixed park structures.
 * The bounded probe set includes endpoints/corners and intermediate supports,
 * rather than translating an entire assembly by a single parcel centroid ray. */
export function buildParkSpecialtyTerrainAnchors(
  structureKind: ParkSpecialtyStructureKind | null,
  guides: readonly ParkGroundGuide[],
  frame: ParkSpecialtyProgramFrame,
): ParkSpecialtyPoint[] {
  if (!structureKind) return [];
  const points: ParkSpecialtyPoint[] = [];
  const linearGuides = guides.filter((guide) => (
    guide.kind === 'axis'
    || guide.kind === 'line'
    || guide.kind === 'polyline'
    || guide.kind === 'path_loop'
  ));

  const exactProgram = structureKind === 'inclusive_playground_v0_assembly' ? { widthM: 50, depthM: 40, clearanceM: 0.5 }
    : structureKind === 'dog_park_v0_assembly' ? { widthM: 80, depthM: 50, clearanceM: 0.5 }
      : structureKind === 'splash_pad_v0_assembly' ? { widthM: 30, depthM: 25, clearanceM: 0.5 }
        : structureKind === 'community_garden_v0_assembly' ? { widthM: 50, depthM: 50, clearanceM: 0.5 }
          : structureKind === 'tennis_cluster_v0_assembly' ? { widthM: 82, depthM: 46, clearanceM: 0.5 }
            : structureKind === 'nature_play_v0_assembly' ? { widthM: 40, depthM: 30, clearanceM: 0.5 }
              : structureKind === 'pump_track_v0_assembly' ? { widthM: 50, depthM: 30, clearanceM: 0.5 }
                : structureKind === 'outdoor_fitness_v0_assembly' ? { widthM: 30, depthM: 25, clearanceM: 0.5 }
                  : structureKind === 'memorial_garden_v0_assembly' ? { widthM: 50, depthM: 40, clearanceM: 0.5 }
          : null;
  if (structureKind === 'skate_park_v0_assembly' || exactProgram) {
    const boundary = frame.points ?? [
      { x: frame.minX, y: frame.minY },
      { x: frame.maxX, y: frame.minY },
      { x: frame.maxX, y: frame.maxY },
      { x: frame.minX, y: frame.maxY },
    ];
    const fit = exactProgram
      ? fitFixedParkProgram(boundary, exactProgram)
      : fitSkateParkV0Program(boundary);
    if (fit) points.push(...rectangleAnchors(
      fit.center,
      fit.widthM,
      fit.depthM,
      fit.rotationRad,
    ));
  } else if (structureKind === 'greenway_edge_assembly') {
    const guide = linearGuides[0];
    if (guide) {
      const route = parkSpecialtyGuideRoute(guide, frame);
      points.push(...route, ...buildGreenwayGatewayBollardAnchors(
        route,
        Math.max(3.5, guide.strokeWidthM ?? 3.5),
      ));
      route.slice(1).forEach((point, index) => points.push({
        x: (route[index].x + point.x) / 2,
        y: (route[index].y + point.y) / 2,
      }));
    }
  } else if (structureKind === 'wetland_boardwalk') {
    for (const guide of linearGuides) {
      const route = parkSpecialtyGuideRoute(guide, frame);
      points.push(...route);
      route.slice(1).forEach((point, index) => points.push({
        x: (route[index].x + point.x) / 2,
        y: (route[index].y + point.y) / 2,
      }));
    }
  } else if (structureKind === 'stormwater_control_assembly') {
    for (const guide of guides.filter((candidate) => (
      candidate.kind === 'ellipse'
      || candidate.kind === 'rectangle'
      || candidate.kind === 'polyline'
      || candidate.kind === 'line'
    ))) {
      if (guide.kind === 'polyline' || guide.kind === 'line') {
        const route = parkSpecialtyGuideRoute(guide, frame);
        points.push(...route);
        route.slice(1).forEach((point, index) => points.push({
          x: (route[index].x + point.x) / 2,
          y: (route[index].y + point.y) / 2,
        }));
        continue;
      }
      const center = guideCenter(guide, frame);
      const dimensions = guideDimensions(guide, frame);
      points.push(...rectangleAnchors(
        center,
        dimensions.width,
        dimensions.height,
        -((guide.rotationDeg ?? 0) * Math.PI) / 180,
      ));
    }
  } else if (structureKind === 'japanese_garden_bridge') {
    const center = {
      x: frame.minX + frame.width * 0.43,
      y: frame.maxY - frame.height * 0.54,
    };
    points.push(
      center,
      { x: center.x - JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.length / 2, y: center.y },
      { x: center.x + JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.length / 2, y: center.y },
      { x: center.x, y: center.y - JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.width / 2 },
      { x: center.x, y: center.y + JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.width / 2 },
    );
  } else if (structureKind === 'botanical_conservatory') {
    const center = {
      x: frame.minX + frame.width * 0.22,
      y: frame.maxY - frame.height * 0.24,
    };
    points.push(...rectangleAnchors(center, 24, 14));
  } else {
    for (const guide of guides) {
      const center = guideCenter(guide, frame);
      const dimensions = guideDimensions(guide, frame);
      points.push(...rectangleAnchors(
        center,
        Math.max(1, dimensions.width),
        Math.max(1, dimensions.height),
        -((guide.rotationDeg ?? 0) * Math.PI) / 180,
      ));
    }
  }

  if (points.length === 0) {
    points.push(
      { x: (frame.minX + frame.maxX) / 2, y: (frame.minY + frame.maxY) / 2 },
      { x: frame.minX, y: frame.minY },
      { x: frame.maxX, y: frame.maxY },
    );
  }
  return boundedUniqueAnchors(points);
}
