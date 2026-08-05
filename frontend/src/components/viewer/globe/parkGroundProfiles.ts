import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import type { SiteZone } from '@/types';
import {
  resolveParkLegoAppearance,
  resolveParkLegoContract,
  type ParkLegoFamilyId,
} from './parkLegoFamilies';
import { archetypeOwnedParkKitForFamily } from './parkArchetypeOwnedKits';

export type ParkGuideKind =
  | 'ellipse'
  | 'rectangle'
  | 'rounded_rectangle'
  | 'line'
  | 'polyline'
  | 'axis'
  | 'path_loop'
  | 'track'
  | 'soccer_field'
  | 'tennis_court';

export interface ParkGroundGuide {
  kind: ParkGuideKind;
  /** Normalized coordinates inside the park bbox, origin at top-left. */
  x: number;
  y: number;
  width: number;
  height: number;
  /** Optional authoritative real-world dimensions. When present these take
   * precedence over the normalized width/height so fixed programs never
   * stretch or shrink with the parcel. */
  widthM?: number;
  heightM?: number;
  color: string;
  strokeColor?: string;
  strokeWidthM?: number;
  /** Exact normalized route for path and boardwalk networks. Coordinates use
   * the same north-up, top-left origin as x/y. */
  points?: Array<[number, number]>;
  closed?: boolean;
  /** Fixed program elements are atomic by default when they carry metre
   * dimensions: the complete envelope fits or the complete element is
   * omitted. `clip` is reserved for non-program background regions. */
  fitPolicy?: 'whole' | 'clip';
  /** Multi-guide objects (for example a cricket oval plus its pitch) share a
   * group so one failed envelope removes the whole object, not just one part. */
  atomicGroup?: string;
  /** Clockwise orientation in the north-up diagram. The fit allocator derives
   * this from the parcel's dominant edge so regulation programs follow a
   * rotated lot instead of being clipped against its bounding box. */
  rotationDeg?: number;
  /** Controls which additional orientations the whole-element allocator may
   * test. Sports surfaces can use several angles; other area programs normally
   * test their authored direction plus its orthogonal alternative; topology-
   * critical linear structures retain their authored direction. */
  orientationPolicy?: 'fixed' | 'orthogonal' | 'flexible';
}

export function resolveParkGuideDimensionsM(
  guide: ParkGroundGuide,
  parkSizeM: { width: number; height: number },
): { width: number; height: number } {
  return {
    width: guide.widthM ?? guide.width * parkSizeM.width,
    height: guide.heightM ?? guide.height * parkSizeM.height,
  };
}

export interface ParkGroundGuideFitResult {
  guides: ParkGroundGuide[];
  omittedGuides: ParkGroundGuide[];
  originalCounts: Partial<Record<ParkGuideKind, number>>;
  fittedCounts: Partial<Record<ParkGuideKind, number>>;
}

const SEMANTIC_PLAY_SURFACE_KINDS = new Set<ParkGuideKind>([
  'soccer_field',
  'tennis_court',
  'track',
]);

/** Guides used only to keep post-drape 3D dressing off active play surfaces.
 *
 * Exact metric programs still obey `fitParkGroundGuides`: an undersized site
 * never gains a squeezed regulation field. Image models can nevertheless
 * interpret a sports archetype as a compact informal play surface even when
 * its regulation guide was omitted (a village-green cricket oval is the
 * common case). Preserve that accepted drape's semantic open room by using
 * the catalog's normalized footprint as a clearance-only guide. This does not
 * render or claim that the omitted regulation program fitted the parcel. */
export function resolveParkPlacementGuides(
  fit: ParkGroundGuideFitResult,
): ParkGroundGuide[] {
  const semanticClearances = fit.omittedGuides
    .filter((guide) => SEMANTIC_PLAY_SURFACE_KINDS.has(guide.kind))
    .map((guide): ParkGroundGuide => ({
      ...guide,
      widthM: undefined,
      heightM: undefined,
      fitPolicy: 'clip',
    }));
  return [...fit.guides, ...semanticClearances];
}

function pointOnNormalizedSegment(
  point: [number, number],
  start: [number, number],
  end: [number, number],
): boolean {
  const cross = (point[1] - start[1]) * (end[0] - start[0])
    - (point[0] - start[0]) * (end[1] - start[1]);
  if (Math.abs(cross) > 1e-7) return false;
  const dot = (point[0] - start[0]) * (end[0] - start[0])
    + (point[1] - start[1]) * (end[1] - start[1]);
  if (dot < -1e-7) return false;
  const squaredLength = (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2;
  return dot <= squaredLength + 1e-7;
}

function normalizedRingContains(
  point: [number, number],
  ring: Array<[number, number]>,
): boolean {
  for (let index = 0; index < ring.length; index += 1) {
    if (pointOnNormalizedSegment(point, ring[index], ring[(index + 1) % ring.length])) {
      return true;
    }
  }
  let inside = false;
  for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index++) {
    const [x, y] = point;
    const [xi, yi] = ring[index];
    const [xj, yj] = ring[previous];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) {
      inside = !inside;
    }
  }
  return inside;
}

function guideEnvelopeSamples(
  guide: ParkGroundGuide,
  parkSizeM: { width: number; height: number },
): Array<[number, number]> {
  const dimensions = resolveParkGuideDimensionsM(guide, parkSizeM);
  const strokeM = Math.max(0, guide.strokeWidthM ?? 0);
  const halfWidthM = (dimensions.width + strokeM) / 2;
  const halfHeightM = (dimensions.height + strokeM) / 2;
  const angle = ((guide.rotationDeg ?? 0) * Math.PI) / 180;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  // Rotate in physical metres before normalizing. Rotating already-normalized
  // offsets distorts angles whenever the parcel width and height differ.
  const place = ([localXM, localYM]: [number, number]): [number, number] => ([
    guide.x + (localXM * cos - localYM * sin) / Math.max(parkSizeM.width, 0.001),
    guide.y + (localXM * sin + localYM * cos) / Math.max(parkSizeM.height, 0.001),
  ]);
  if (guide.kind === 'ellipse' || guide.kind === 'track') {
    return Array.from({ length: 24 }, (_, index) => {
      const angle = (index / 24) * Math.PI * 2;
      return place([Math.cos(angle) * halfWidthM, Math.sin(angle) * halfHeightM]);
    });
  }
  return [
    place([-halfWidthM, -halfHeightM]),
    place([halfWidthM, -halfHeightM]),
    place([halfWidthM, halfHeightM]),
    place([-halfWidthM, halfHeightM]),
  ] as Array<[number, number]>;
}

function resolveParcelProgramRotationDeg(
  ring: Array<[number, number]>,
  parkSizeM: { width: number; height: number },
): number {
  let cosine = 0;
  let sine = 0;
  let totalWeight = 0;
  for (let index = 0; index < ring.length; index += 1) {
    const start = ring[index];
    const end = ring[(index + 1) % ring.length];
    const dx = (end[0] - start[0]) * parkSizeM.width;
    const dy = (end[1] - start[1]) * parkSizeM.height;
    if (Math.abs(dx) < Math.abs(dy)) continue;
    const length = Math.hypot(dx, dy);
    if (length <= 0.001) continue;
    const angle = Math.atan2(dy, dx);
    cosine += Math.cos(angle * 2) * length;
    sine += Math.sin(angle * 2) * length;
    totalWeight += length;
  }
  if (totalWeight <= 0.001) return 0;
  const angle = 0.5 * Math.atan2(sine / totalWeight, cosine / totalWeight);
  const degrees = (angle * 180) / Math.PI;
  return Math.abs(degrees) <= 15 ? degrees : 0;
}

function guideCollisionClass(guide: ParkGroundGuide): string {
  if (guide.kind === 'soccer_field' || guide.kind === 'tennis_court' || guide.kind === 'track') {
    return 'active-sports-surface';
  }
  return `kind:${guide.kind}`;
}

function guideEnvelopesOverlap(
  first: ParkGroundGuide,
  second: ParkGroundGuide,
  parkSizeM: { width: number; height: number },
): boolean {
  if (guideCollisionClass(first) !== guideCollisionClass(second)) return false;
  const firstPolygon = guideEnvelopeSamples(first, parkSizeM);
  const secondPolygon = guideEnvelopeSamples(second, parkSizeM);
  const tolerance = 1e-6;
  // Separating-axis test keeps adjacent rotated sports envelopes distinct.
  // Axis-aligned bounding boxes falsely overlap when the whole program follows
  // a sloped parcel edge.
  for (const polygon of [firstPolygon, secondPolygon]) {
    for (let index = 0; index < polygon.length; index += 1) {
      const start = polygon[index];
      const end = polygon[(index + 1) % polygon.length];
      const axisX = -(end[1] - start[1]);
      const axisY = end[0] - start[0];
      const length = Math.hypot(axisX, axisY);
      if (length <= tolerance) continue;
      const normalX = axisX / length;
      const normalY = axisY / length;
      const project = (point: [number, number]) => point[0] * normalX + point[1] * normalY;
      const firstValues = firstPolygon.map(project);
      const secondValues = secondPolygon.map(project);
      if (Math.max(...firstValues) <= Math.min(...secondValues) + tolerance
        || Math.max(...secondValues) <= Math.min(...firstValues) + tolerance) {
        return false;
      }
    }
  }
  return true;
}

const GUIDE_REPOSITION_OFFSETS = (() => {
  const offsets: Array<[number, number]> = [];
  // Fixed programs may move inside the parcel so the first module in a
  // multi-field archetype can recenter when later modules are omitted.
  // Dimensions never change, and the nearest valid position always wins.
  for (let xStep = -25; xStep <= 25; xStep += 1) {
    for (let yStep = -25; yStep <= 25; yStep += 1) {
      offsets.push([xStep * 0.01, yStep * 0.01]);
    }
  }
  return offsets.sort((a, b) => (
    (a[0] ** 2 + a[1] ** 2) - (b[0] ** 2 + b[1] ** 2)
    || Math.abs(a[1]) - Math.abs(b[1])
    || Math.abs(a[0]) - Math.abs(b[0])
    || a[1] - b[1]
    || a[0] - b[0]
  ));
})();

const FLEXIBLE_ORIENTATION_DELTAS_DEG = [
  0, 90, -90, 15, -15, 30, -30, 45, -45, 60, -60, 75, -75,
] as const;
const ORTHOGONAL_ORIENTATION_DELTAS_DEG = [0, 90, -90] as const;
const FIT_BEAM_WIDTH = 96;
const MAX_PLACEMENTS_PER_ORIENTATION = 12;
const MAX_PLACEMENTS_PER_UNIT = 120;

function resolveGuideOrientationPolicy(
  guide: ParkGroundGuide,
): NonNullable<ParkGroundGuide['orientationPolicy']> {
  if (guide.orientationPolicy) return guide.orientationPolicy;
  if (guide.kind === 'soccer_field' || guide.kind === 'tennis_court' || guide.kind === 'track') {
    return 'flexible';
  }
  if (guide.kind === 'rectangle' || guide.kind === 'rounded_rectangle' || guide.kind === 'ellipse') {
    return 'orthogonal';
  }
  return 'fixed';
}

function normalizeRotationDeg(value: number): number {
  let normalized = value % 180;
  if (normalized > 90) normalized -= 180;
  if (normalized <= -90) normalized += 180;
  return Math.abs(normalized) < 1e-9 ? 0 : normalized;
}

function orientationDeltasForUnit(guides: ParkGroundGuide[]): number[] {
  const policies = guides.map(resolveGuideOrientationPolicy);
  if (policies.includes('fixed')) return [0];
  const candidates = policies.includes('flexible')
    ? FLEXIBLE_ORIENTATION_DELTAS_DEG
    : ORTHOGONAL_ORIENTATION_DELTAS_DEG;
  return [...new Set(candidates.map(normalizeRotationDeg))];
}

function transformGuideUnit(
  guides: ParkGroundGuide[],
  parkSizeM: { width: number; height: number },
  parcelRotationDeg: number,
  orientationDeltaDeg: number,
  offsetX: number,
  offsetY: number,
): ParkGroundGuide[] {
  const centroidXM = guides.reduce((sum, guide) => sum + guide.x * parkSizeM.width, 0)
    / Math.max(guides.length, 1);
  const centroidYM = guides.reduce((sum, guide) => sum + guide.y * parkSizeM.height, 0)
    / Math.max(guides.length, 1);
  const totalRotationDeg = parcelRotationDeg + orientationDeltaDeg;
  const angle = (totalRotationDeg * Math.PI) / 180;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  return guides.map((guide) => {
    const localXM = guide.x * parkSizeM.width - centroidXM;
    const localYM = guide.y * parkSizeM.height - centroidYM;
    return {
      ...guide,
      x: (centroidXM + localXM * cos - localYM * sin) / Math.max(parkSizeM.width, 0.001)
        + offsetX,
      y: (centroidYM + localXM * sin + localYM * cos) / Math.max(parkSizeM.height, 0.001)
        + offsetY,
      rotationDeg: normalizeRotationDeg((guide.rotationDeg ?? 0) + totalRotationDeg),
    };
  });
}

interface GuideUnitPlacement {
  guides: ParkGroundGuide[];
  transformCost: number;
}

function enumerateGuideUnitPlacements(
  guides: ParkGroundGuide[],
  parkSizeM: { width: number; height: number },
  normalizedRing: Array<[number, number]>,
  parcelRotationDeg: number,
): GuideUnitPlacement[] {
  const offsets = [...GUIDE_REPOSITION_OFFSETS].sort((a, b) => (
    Math.hypot(a[0] * parkSizeM.width, a[1] * parkSizeM.height)
      - Math.hypot(b[0] * parkSizeM.width, b[1] * parkSizeM.height)
  ));
  const placements: GuideUnitPlacement[] = [];
  for (const orientationDeltaDeg of orientationDeltasForUnit(guides)) {
    let orientationPlacements = 0;
    for (const [offsetX, offsetY] of offsets) {
      const candidates = transformGuideUnit(
        guides,
        parkSizeM,
        parcelRotationDeg,
        orientationDeltaDeg,
        offsetX,
        offsetY,
      );
      const fitsParcel = candidates.every((guide) => (
        guideEnvelopeSamples(guide, parkSizeM)
          .every((point) => normalizedRingContains(point, normalizedRing))
      ));
      if (!fitsParcel) continue;
      placements.push({
        guides: candidates,
        transformCost: Math.hypot(offsetX * parkSizeM.width, offsetY * parkSizeM.height)
          + Math.abs(orientationDeltaDeg) * 0.01,
      });
      orientationPlacements += 1;
      if (orientationPlacements >= MAX_PLACEMENTS_PER_ORIENTATION) break;
    }
  }
  return placements
    .sort((a, b) => a.transformCost - b.transformCost)
    .slice(0, MAX_PLACEMENTS_PER_UNIT);
}

/** Applies the shared whole-element rule before a guide reaches the canvas,
 * AI prompt, or live 3D furniture layer. Metric program elements are never
 * scaled down or clipped. The allocator searches alternate orientations and
 * nearby positions for every complete element, then uses a bounded global
 * layout search to retain the highest-value non-overlapping program. */
export function fitParkGroundGuides(
  guides: ParkGroundGuide[],
  parkSizeM: { width: number; height: number },
  normalizedRing: Array<[number, number]> = [[0, 0], [1, 0], [1, 1], [0, 1]],
): ParkGroundGuideFitResult {
  const isAtomic = (guide: ParkGroundGuide) => (
    guide.fitPolicy === 'whole'
    || (guide.fitPolicy !== 'clip'
      && (guide.widthM !== undefined || guide.heightM !== undefined))
  );
  const parcelRotationDeg = resolveParcelProgramRotationDeg(normalizedRing, parkSizeM);
  const atomicUnits = new Map<string, number[]>();
  guides.forEach((guide, index) => {
    if (!isAtomic(guide)) return;
    const key = guide.atomicGroup ? `group:${guide.atomicGroup}` : `guide:${index}`;
    atomicUnits.set(key, [...(atomicUnits.get(key) ?? []), index]);
  });

  interface FitState {
    fittedByIndex: Map<number, ParkGroundGuide>;
    occupiedGuides: ParkGroundGuide[];
    retainedAreaM2: number;
    retainedUnits: number;
    transformCost: number;
  }
  let states: FitState[] = [{
    fittedByIndex: new Map(),
    occupiedGuides: [],
    retainedAreaM2: 0,
    retainedUnits: 0,
    transformCost: 0,
  }];
  for (const indices of atomicUnits.values()) {
    const unitGuides = indices.map((index) => guides[index]);
    const placements = enumerateGuideUnitPlacements(
      unitGuides,
      parkSizeM,
      normalizedRing,
      parcelRotationDeg,
    );
    const retainedAreaM2 = unitGuides.reduce((sum, guide) => {
      const dimensions = resolveParkGuideDimensionsM(guide, parkSizeM);
      return sum + dimensions.width * Math.max(dimensions.height, guide.strokeWidthM ?? 0.1);
    }, 0);
    const nextStates: FitState[] = [];
    for (const state of states) {
      nextStates.push(state);
      for (const placement of placements) {
        const overlapsPlacedProgram = placement.guides.some((candidate) => (
          state.occupiedGuides.some((placed) => (
            guideEnvelopesOverlap(candidate, placed, parkSizeM)
          ))
        ));
        if (overlapsPlacedProgram) continue;
        const fittedByIndex = new Map(state.fittedByIndex);
        indices.forEach((index, unitIndex) => fittedByIndex.set(index, placement.guides[unitIndex]));
        nextStates.push({
          fittedByIndex,
          occupiedGuides: [...state.occupiedGuides, ...placement.guides],
          retainedAreaM2: state.retainedAreaM2 + retainedAreaM2,
          retainedUnits: state.retainedUnits + 1,
          transformCost: state.transformCost + placement.transformCost,
        });
      }
    }
    states = nextStates
      .sort((a, b) => (
        b.retainedAreaM2 - a.retainedAreaM2
        || b.retainedUnits - a.retainedUnits
        || a.transformCost - b.transformCost
      ))
      .slice(0, FIT_BEAM_WIDTH);
  }

  const fittedByIndex = states[0]?.fittedByIndex ?? new Map<number, ParkGroundGuide>();
  guides.forEach((guide, index) => {
    if (!isAtomic(guide)) fittedByIndex.set(index, guide);
  });

  const countKinds = (candidates: ParkGroundGuide[]) => candidates.reduce(
    (counts, guide) => ({ ...counts, [guide.kind]: (counts[guide.kind] ?? 0) + 1 }),
    {} as Partial<Record<ParkGuideKind, number>>,
  );
  const fitted = guides.flatMap((_, index) => {
    const guide = fittedByIndex.get(index);
    return guide ? [guide] : [];
  });
  const omitted = guides.filter((_, index) => !fittedByIndex.has(index));
  return {
    guides: fitted,
    omittedGuides: omitted,
    originalCounts: countKinds(guides),
    fittedCounts: countKinds(fitted),
  };
}

const GUIDE_COUNT_LABELS: Partial<Record<ParkGuideKind, [singular: string, plural: string]>> = {
  tennis_court: ['tennis court', 'tennis courts'],
  soccer_field: ['football/soccer field', 'football/soccer fields'],
  track: ['track/oval envelope', 'track/oval envelopes'],
  rectangle: ['fixed rectangular program element', 'fixed rectangular program elements'],
  rounded_rectangle: ['fixed rounded-rectangular program element', 'fixed rounded-rectangular program elements'],
  ellipse: ['fixed elliptical program element', 'fixed elliptical program elements'],
  line: ['fixed linear structure', 'fixed linear structures'],
};

export function describeParkGroundGuideFit(result: ParkGroundGuideFitResult): string {
  if (result.omittedGuides.length === 0) return '';
  const kinds = [...new Set(result.omittedGuides.map((guide) => guide.kind))];
  const counts = kinds.map((kind) => {
    const fittedCount = result.fittedCounts[kind] ?? 0;
    const labels = GUIDE_COUNT_LABELS[kind] ?? [kind, `${kind}s`];
    const label = fittedCount === 1 ? labels[0] : labels[1];
    return `${fittedCount} complete ${label} ${fittedCount === 1 ? 'fits' : 'fit'} `
      + `out of ${result.originalCounts[kind] ?? 0}`;
  });
  return 'WHOLE-ELEMENT FIT OVERRIDE: '
    + `${counts.join('; ')}. Elements that did not fit were omitted as complete objects. `
    + 'Do not draw, reconstruct, crop, truncate, squeeze or scale any omitted element; leave its area as compatible open landscape or circulation.';
}

export interface ParkGroundProfile {
  id: string;
  version: number;
  archetypeId: string;
  title: string;
  programDescription: string;
  groundDescription: string;
  criticalConstraints: string;
  /** Canopy hierarchy used by the final mixed-scene render. The ortho ground
   * texture deliberately omits trees because the render pass adds them. */
  canopyDescription: string;
  plantingStructure?: string;
  guides: ParkGroundGuide[];
  guideLegend: string[];
  includeCentralPlaza: boolean;
  /** Short, geometry-first summary for the mixed-plan AI finishing pass. */
  renderSummary: string;
  isPilot: boolean;
  /** Present when this profile is backed by an executable Public Realm LEGO
   * family rather than only a catalog-derived visual description. */
  legoFamilyId?: ParkLegoFamilyId;
  legoFamilyVersion?: number;
  variantId?: string;
}

export const JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M = Object.freeze({
  length: 9,
  width: 2.2,
});

/** Render-derived but scale-locked wetland boardwalk topology. The latest
 * accepted render uses a looping route with a cross-link and a clear southern
 * gateway, rather than one straight bridge through the middle. Shared by the
 * diagram/drape and live 3D deck so both outputs remain spatially identical. */
export const WETLAND_BOARDWALK_PATHS = Object.freeze([
  {
    closed: true,
    points: [
      [0.10, 0.72], [0.18, 0.59], [0.27, 0.65], [0.38, 0.57],
      [0.49, 0.72], [0.60, 0.64], [0.72, 0.61], [0.84, 0.68],
      [0.90, 0.54], [0.79, 0.45], [0.86, 0.29], [0.71, 0.25],
      [0.61, 0.36], [0.49, 0.29], [0.39, 0.38], [0.29, 0.28],
      [0.18, 0.37], [0.12, 0.52],
    ] as Array<[number, number]>,
  },
  {
    closed: false,
    points: [
      [0.16, 0.52], [0.28, 0.47], [0.40, 0.55], [0.51, 0.43],
      [0.62, 0.53], [0.76, 0.44], [0.89, 0.54],
    ] as Array<[number, number]>,
  },
  {
    closed: false,
    points: [[0.49, 0.96], [0.49, 0.72]] as Array<[number, number]>,
  },
] as const);

interface CatalogVariant {
  id: string;
  label?: string;
  description?: string;
  color?: string;
}

interface CatalogEntry {
  id: string;
  title?: string;
  aestheticCategory?: string;
  spaceType?: string;
  suggestedWidth_m?: number;
  suggestedDepth_m?: number;
  generationTags?: string[];
  styleProfile?: {
    landscapeCharacter?: string;
    pavingType?: string;
    plantingType?: string;
    seatingRealm?: string;
    waterFeatures?: string;
    opennessEnclosure?: string;
  };
  renderPrompt?: { roofView?: string; mapOverlay?: string };
  variants?: CatalogVariant[];
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CATALOG = (((openSpaceCatalog as any).archetypes ?? openSpaceCatalog) as CatalogEntry[]);

const PROFILES: Record<string, Omit<ParkGroundProfile, 'archetypeId' | 'title'>> = {
  neighborhood_park: {
    id: 'neighborhood-park-v4',
    version: 4,
    programDescription:
      'A complete contemporary neighborhood park organized around one generous central social lawn, an exact continuous walking circuit, a fixed playground pad, a small pavilion pad, native meadow and rain-garden edges, and low perennial display beds. The marked primary paths link every gateway, the walking circuit and both activity pads.',
    groundDescription:
      'Natural mowed lawn with restrained mowing variation, smooth pale-concrete primary paths, narrower warm aggregate secondary paths, visibly layered native meadow, rain-garden groundcover and flowering perennial beds, plus localized sand or engineered-wood-fiber safety surfacing at the marked playground and a restrained paved pavilion pad.',
    criticalConstraints:
      'Preserve the complete marked walking circuit, all four gateway links, the playground pad and the pavilion pad exactly. Keep the generous center as usable open lawn and keep every planting room outside the clear path widths. Never omit a route, leave an activity pad isolated, use four-spoke radial symmetry or turn the parcel into a single empty grass carpet. Never use one perfect circular track. No ponds or sports stadiums.',
    canopyDescription:
      'Mature deciduous shade trees form irregular overlapping clusters along the perimeter, path junctions and activity nodes, with a few specimen trees framing the open lawn; retain clear sightlines and do not fill the usable center with canopy.',
    plantingStructure: 'active_recreation',
    guides: [
      { kind: 'ellipse', x: 0.50, y: 0.49, width: 0.46, height: 0.43, color: '#7da15e', strokeColor: '#637e4e', strokeWidthM: 0.5 },
      {
        kind: 'polyline', x: 0.50, y: 0.50, width: 0.76, height: 0.60,
        color: '#c7b89b', strokeColor: '#806e55', strokeWidthM: 3.0, closed: true,
        points: [[0.28, 0.28], [0.48, 0.20], [0.66, 0.26], [0.75, 0.42], [0.70, 0.62], [0.55, 0.74], [0.35, 0.70], [0.24, 0.54], [0.28, 0.28]],
      },
      {
        kind: 'polyline', x: 0.50, y: 0.50, width: 1, height: 1,
        color: '#c7b89b', strokeColor: '#806e55', strokeWidthM: 3.0,
        points: [[0.50, 0.00], [0.48, 0.20]],
      },
      {
        kind: 'polyline', x: 0.50, y: 0.50, width: 1, height: 1,
        color: '#c7b89b', strokeColor: '#806e55', strokeWidthM: 3.0,
        points: [[0.00, 0.50], [0.24, 0.54], [0.50, 1.00]],
      },
      {
        kind: 'polyline', x: 0.50, y: 0.50, width: 1, height: 1,
        color: '#c7b89b', strokeColor: '#806e55', strokeWidthM: 3.0,
        points: [[0.75, 0.42], [1.00, 0.40]],
      },
      { kind: 'ellipse', x: 0.18, y: 0.25, width: 0.25, height: 0.18, color: '#7f9460', strokeColor: '#596e45', strokeWidthM: 0.6 },
      { kind: 'ellipse', x: 0.82, y: 0.70, width: 0.25, height: 0.20, color: '#6f8960', strokeColor: '#4f6947', strokeWidthM: 0.6 },
      { kind: 'ellipse', x: 0.82, y: 0.22, width: 0.20, height: 0.15, color: '#b28b5e', strokeColor: '#75684d', strokeWidthM: 0.5 },
      { kind: 'rectangle', x: 0.77, y: 0.58, width: 0.11, height: 0.10, color: '#b8ad96', strokeColor: '#756f63', strokeWidthM: 0.5 },
    ],
    guideLegend: [
      'the LARGE MID-GREEN ellipse is the exact uninterrupted social lawn and must remain entirely grass with no paving or objects inside it',
      'the PALE route network is the exact continuous 3-metre walking circuit with four gateway links; preserve every segment and junction',
      'the two SAGE-GREEN ellipses are layered native meadow and rain-garden rooms outside the route clear width',
      'the OCHRE ellipse is the exact playground safety-surface pad and the SMALL GREY rectangle is the exact pavilion pad; connect both to the walking circuit',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'neighborhood park preserving one connected walking circuit with four gateway links, a central lawn, meadow/rain-garden rooms, playground and pavilion pads',
    isPilot: true,
  },
  pond_lake: {
    id: 'pond-lake-v3',
    version: 3,
    programDescription:
      'One broad formal reflecting pond with softened rectangular corners, one continuous perimeter promenade, narrow clipped-lawn bands and planted edge rooms. The pond and promenade are the complete fixed program.',
    groundDescription:
      'Deep still blue-green water, a restrained pale stone pond edge, warm fine-gravel promenade, clipped lawn bands and low layered shoreline planting. Keep the composition calm, spacious and civic rather than ornamental or theme-park-like.',
    criticalConstraints:
      'Preserve exactly one rounded-rectangular pond and one continuous promenade around it. Keep the pond, path and every planted edge inside the parcel. Do not change the pond into an ellipse, naturalistic lake, wetland cell network or multiple pools; do not invent radial paths, fountains, buildings, parking, sports fields or playground equipment.',
    canopyDescription:
      'The final architectural render may add a varied perimeter allée of mature deciduous trees and low flowering understory on eligible lawn and planting bands, while keeping the water and promenade completely open.',
    plantingStructure: 'formal_water_edge',
    guides: [
      {
        kind: 'rounded_rectangle',
        x: 0.50,
        y: 0.50,
        width: 0.70,
        height: 0.50,
        color: '#315d68',
        strokeColor: '#b8afa0',
        strokeWidthM: 1.0,
      },
      {
        kind: 'polyline',
        x: 0.50,
        y: 0.50,
        width: 0.80,
        height: 0.68,
        color: '#c7b89b',
        strokeColor: '#8b7b61',
        strokeWidthM: 3.0,
        closed: true,
        points: [
          [0.18, 0.19], [0.82, 0.19], [0.90, 0.29], [0.90, 0.71],
          [0.82, 0.81], [0.18, 0.81], [0.10, 0.71], [0.10, 0.29],
        ],
      },
    ],
    guideLegend: [
      'the BLUE-GREEN rounded rectangle is the exact single reflecting-pond footprint with softened corners',
      'the PALE closed route is the exact continuous 3-metre perimeter promenade and must remain dry and unobstructed',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'formal reflecting pond preserving one softened rectangular water body, one continuous perimeter promenade and restrained lawn/planting bands',
    isPilot: true,
  },
  urban_pocket_park: {
    id: 'urban-pocket-park-v1',
    version: 1,
    programDescription:
      'A compact, intensely used urban pocket park organized around one small, irregular open lawn room. A decomposed-granite walking path connects every marked street gateway and bends around the lawn to reach shaded seating niches. Low perennial and ornamental-grass borders create enclosure without hiding the entries.',
    groundDescription:
      'Freshly mown but naturally varied lawn, warm decomposed-granite paths with narrow stone edging, compact concrete seating pads, layered perennial beds and a low clipped perimeter hedge. Keep materials fine-grained and credible at pocket-park scale.',
    criticalConstraints:
      'Keep the diagrammed lawn as one usable clear room and connect every marked gateway with one continuous, direct path network. This is a small urban refuge, not a neighborhood field: no playground, pavilion, pond, sports surface, circular running track or oversized plaza. Cover the complete parcel with real ground material and leave no blank margins.',
    canopyDescription:
      'Two to four mature deciduous shade-tree crowns frame the lawn and seating edges with varied species and overlap, while gateways and the compact usable center remain open.',
    plantingStructure: 'garden_courtyard',
    guides: [
      { kind: 'ellipse', x: 0.50, y: 0.51, width: 0.48, height: 0.40, color: '#82a863', strokeColor: '#607c4d', strokeWidthM: 0.45 },
    ],
    guideLegend: [
      'the MID-GREEN ellipse is the exact clear central lawn room; paths and planting wrap around it rather than crossing it',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'compact pocket park preserving one clear lawn room, direct gateway-connected decomposed-granite paths and layered perimeter planting',
    isPilot: true,
  },
  linear_park_greenway: {
    id: 'linear-park-greenway-v1',
    version: 1,
    programDescription:
      'A continuous linear park and mobility greenway whose primary multi-use trail follows the parcel long axis from end to end. Native meadow, rain-garden and riparian planting bands flank the trail, widening into small rest or overlook nodes only where space permits. Every marked side gateway joins the main trail without a dead end.',
    groundDescription:
      'A 3.5-metre asphalt or compacted-limestone multi-use trail with soft shoulders, layered native wildflower meadow, rain-garden swales, low riparian groundcover and occasional small gravel rest pads. The main path remains clearly legible through the whole corridor.',
    criticalConstraints:
      'Preserve the diagrammed long-axis trail as one continuous, obstruction-free route connecting both corridor ends. Connect every marked gateway to it. Do not turn the corridor into disconnected pocket parks, a motor road, ornamental loops, a broad lawn carpet or a continuous canal. Keep all planting and rest pads outside the trail clear width.',
    canopyDescription:
      'Irregular shade-tree and riparian clusters form a varied outer frame and occasional canopy rooms, but never close the through-trail or obscure its connections.',
    plantingStructure: 'naturalistic_grove',
    guides: [
      { kind: 'axis', x: 0.50, y: 0.50, width: 0.90, height: 0, color: '#a4a198', strokeWidthM: 3.5 },
    ],
    guideLegend: [
      'the PALE-GREY long-axis line is the exact continuous 3.5-metre multi-use trail; carry it through the full corridor and join every gateway to it',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'linear greenway preserving an uninterrupted end-to-end multi-use trail with connected gateways and layered native corridor planting',
    isPilot: true,
  },
  formal_civic_plaza: {
    id: 'formal-civic-plaza-v1',
    version: 1,
    programDescription:
      'A dignified civic forecourt with a crisp rectangular field of warm stone paving, a central circular fountain basin, an axial but accessible paving hierarchy, and clear event space. Formal tree allees and seating belong at the outer edges rather than filling the civic center.',
    groundDescription:
      'Warm-grey and beige cut-stone pavers in a restrained geometric grid, darker flush bands defining the principal axes, a dark reflective circular fountain basin with a narrow stone rim, and small stone seating or tree-grate pads along the perimeter.',
    criticalConstraints:
      'Preserve the central fountain and keep a generous contiguous hardscape event area around it. Every marked gateway must enter the plaza on accessible flush paving. Do not convert the plaza into lawn, a neighborhood park, parking, a traffic circle or a decorative radial garden; keep trees, furniture and planters out of the central event field.',
    canopyDescription:
      'Two restrained rows of mature, high-canopy deciduous trees frame the plaza edges with regular civic rhythm while preserving clear views across the fountain and event surface.',
    plantingStructure: 'paved_plaza',
    guides: [
      { kind: 'ellipse', x: 0.50, y: 0.50, width: 0.18, height: 0.18, color: '#426c75', strokeColor: '#d2c4a7', strokeWidthM: 1.2 },
    ],
    guideLegend: [
      'the BLUE-GREY circle is the exact central fountain basin and stone rim; the surrounding parcel remains clear civic paving',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'formal civic plaza preserving the central fountain, accessible gateway axes, warm cut-stone paving and an open event field',
    isPilot: true,
  },
  fountain_water_feature: {
    id: 'fountain-water-feature-v1',
    version: 1,
    programDescription:
      'A compact decorative fountain court centered on one clear circular water basin. Concentric stone paving provides an accessible viewing and seating apron, with the fountain remaining the singular focal point.',
    groundDescription:
      'Dark reflective fountain water inside a polished stone rim, warm-grey concentric stone or tile paving, a restrained wet reflective halo immediately around the basin, and small flush seating pads at the outer edge.',
    criticalConstraints:
      'Keep the diagrammed basin centered, circular, fully open and entirely inside the parcel. Do not invent a lake, pool deck, splash playground, multiple basins, buildings or lawn. Maintain a continuous accessible paved apron between the fountain and every marked gateway.',
    canopyDescription:
      'Any canopy is limited to a few high-crowned perimeter trees beyond the paved viewing apron; the fountain, jets and approach views remain completely open.',
    plantingStructure: 'paved_plaza',
    guides: [
      { kind: 'ellipse', x: 0.50, y: 0.50, width: 0.46, height: 0.46, color: '#365f6b', strokeColor: '#d4c6aa', strokeWidthM: 1.1 },
    ],
    guideLegend: [
      'the BLUE-GREY circle is the exact decorative fountain basin and pale stone rim; preserve the warm paved apron around it',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'compact fountain court preserving one circular reflective basin, concentric accessible paving and clear perimeter approaches',
    isPilot: true,
  },
  stormwater_retention_pond: {
    id: 'stormwater-retention-pond-v1',
    version: 1,
    programDescription:
      'An engineered but naturalistic stormwater basin with a variable-level open-water pool, gently graded wet-meadow shelves, a clearly expressed inlet and outlet, a riprap energy-dissipation apron, and one gravel maintenance route on dry ground.',
    groundDescription:
      'Dark blue-green shallow water, muted golden-green sedge and wet-meadow bands, mown outer side slopes, grey riprap at the inlet, a small concrete outlet/weir pad and a narrow gravel maintenance track outside the normal water line.',
    criticalConstraints:
      'Preserve the diagrammed open-water pool and outlet pad. No trees, benches, paths, buildings or decorative features may enter the water, wet shelf, inlet, outlet or maintenance clear zone. This is functioning stormwater infrastructure, not a recreational lake, marina, playground or ornamental fountain. Cover all dry land with specified vegetation, gravel or infrastructure material and leave no blank ground.',
    canopyDescription:
      'Sparse, irregular native willow and shade-tree clusters remain on the outer upland edge only; the basin, wet shelf, inlet, outlet and maintenance access stay fully visible and operational.',
    plantingStructure: 'reservoir_perimeter',
    guides: [
      { kind: 'ellipse', x: 0.47, y: 0.52, width: 0.58, height: 0.42, color: '#416f79', strokeColor: '#889a69', strokeWidthM: 3.0 },
      { kind: 'rectangle', x: 0.15, y: 0.52, width: 0.07, height: 0.13, color: '#858984', strokeColor: '#656b68', strokeWidthM: 0.5 },
      { kind: 'rectangle', x: 0.79, y: 0.52, width: 0.06, height: 0.10, color: '#92918a', strokeColor: '#65655f', strokeWidthM: 0.5 },
      {
        kind: 'polyline',
        x: 0.88,
        y: 0.52,
        width: 0.18,
        height: 0,
        points: [[0.79, 0.52], [0.97, 0.52]],
        color: '#a99a7c',
        strokeColor: '#786d5d',
        strokeWidthM: 2.4,
      },
    ],
    guideLegend: [
      'the BLUE-GREEN ellipse is the exact variable-level open-water pool; its green rim is the wet-meadow and sedge shelf',
      'the WEST GREY rectangle is the exact inlet and riprap energy-dissipation clear zone; keep planting and furnishings outside it',
      'the GREY rectangle is the exact outlet/weir service pad and must remain clear and connected to dry maintenance access',
      'the TAN line is the exact dry gravel maintenance route from the outlet/weir pad to the parcel edge; keep its full width clear',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'stormwater basin preserving the exact open-water pool, wet shelf, inlet/outlet function and dry maintenance access',
    isPilot: true,
  },
  tennis_court_cluster: {
    id: 'tennis-court-cluster-v2',
    version: 2,
    programDescription:
      'A regulation tennis complex with up to four complete courts arranged in a compact two-by-two cluster. Use the maximum number of whole court envelopes that fit the parcel. Every retained court includes its full playing rectangle and safe run-off envelope, with a three-metre circulation spine, a controlled entry, perimeter fencing and a small spectator/furnishing strip outside the court clear zones.',
    groundDescription:
      'Up to four complete matte acrylic hard courts with accurate white tennis linework, darker acrylic run-off aprons, a pale concrete central circulation spine, narrow concrete gate pads and maintained low turf outside the perimeter fence. Variant materials may change court colour and edge character but never court dimensions or markings.',
    criticalConstraints:
      'Preserve only the complete 36.58 by 18.29 metre court envelopes retained by the whole-element fit preflight. Do not scale, crop, truncate or overlap a court to force the requested count into an undersized polygon. Keep the full run-off, nets, central circulation spine and gate route unobstructed; trees, benches, lighting, planting and fences stay outside the retained court envelopes and never interrupt a baseline or sideline.',
    canopyDescription:
      'No canopy overhangs any court or run-off area. Any final-render trees form a sparse windbreak outside the fence on the north or west perimeter only, with crown and root setbacks from playing surfaces and lighting.',
    plantingStructure: 'sports_perimeter',
    guides: [
      { kind: 'tennis_court', x: 0.28, y: 0.35, width: 0.28, height: 0.28, widthM: 36.58, heightM: 18.29, color: '#3f6f82', strokeColor: '#f4f2df', strokeWidthM: 0.08 },
      { kind: 'tennis_court', x: 0.72, y: 0.35, width: 0.28, height: 0.28, widthM: 36.58, heightM: 18.29, color: '#3f6f82', strokeColor: '#f4f2df', strokeWidthM: 0.08 },
      { kind: 'tennis_court', x: 0.28, y: 0.65, width: 0.28, height: 0.28, widthM: 36.58, heightM: 18.29, color: '#3f6f82', strokeColor: '#f4f2df', strokeWidthM: 0.08 },
      { kind: 'tennis_court', x: 0.72, y: 0.65, width: 0.28, height: 0.28, widthM: 36.58, heightM: 18.29, color: '#3f6f82', strokeColor: '#f4f2df', strokeWidthM: 0.08 },
      { kind: 'axis', x: 0.5, y: 0.5, width: 0.82, height: 0, color: '#bbb7ac', strokeWidthM: 3 },
    ],
    guideLegend: [
      'each retained BLUE-GREEN rectangle is one exact 36.58 by 18.29 metre tennis court envelope including regulation run-off and must remain complete and unobstructed',
      'the PALE-GREY long axis is the exact three-metre circulation spine linking every court gate to the site entry',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'tennis cluster preserving the maximum parcel-compatible count of complete regulation court/run-off envelopes, accurate linework and a clear central circulation spine',
    isPilot: true,
  },
  soccer_pitch_caged: {
    id: 'caged-soccer-pitch-v1',
    version: 1,
    programDescription:
      'An archetype-matched European street football cage containing up to two complete 30 by 18 metre 5-a-side pitches. Use the maximum number of whole pitch modules that fit the parcel; an oversized site receives two pitches rather than one stretched pitch.',
    groundDescription:
      'Deep green striped artificial turf with crisp white five-a-side markings, dark galvanized steel mesh, weathered white rebound boards, a narrow concrete gate apron and restrained spectator seating outside the cage. The material palette follows the selected archetype render rather than a generic sports skin.',
    criticalConstraints:
      'Every retained pitch is exactly 30 by 18 metres with two 3 by 2 metre goals. Never stretch, crop or overlap a pitch. Each pitch keeps its complete rebound-board and 3-to-4-metre mesh enclosure, gate, four-corner lighting and unobstructed playing surface. Omit coaching decks, storage buildings and people; larger buildings are rendered separately.',
    canopyDescription:
      'No trees or canopy overhang the cage. Any planting remains outside the concrete spectator apron and clear of gates, mesh and floodlights.',
    plantingStructure: 'caged_soccer_v0',
    guides: [
      { kind: 'soccer_field', x: 0.30, y: 0.50, width: 0.40, height: 0.72, widthM: 30, heightM: 18, color: '#286b38', strokeColor: '#f4f2df', strokeWidthM: 0.08, orientationPolicy: 'orthogonal' },
      { kind: 'soccer_field', x: 0.70, y: 0.50, width: 0.40, height: 0.72, widthM: 30, heightM: 18, color: '#286b38', strokeColor: '#f4f2df', strokeWidthM: 0.08, orientationPolicy: 'orthogonal' },
    ],
    guideLegend: [
      'each retained DARK-GREEN rectangle is one exact 30 by 18 metre caged 5-a-side pitch; keep complete regulation markings, goals, rebound boards and mesh enclosure',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'European street-cage soccer park preserving the maximum parcel-compatible count of complete 30 by 18 metre pitches with exact goals, rebound boards, mesh and floodlights',
    isPilot: true,
  },
  wetland_rain_garden: {
    id: 'wetland-rain-garden-v2',
    version: 2,
    programDescription:
      'A constructed wetland and bioretention garden organized as three hydraulically connected shallow cells, a visible inlet-to-outlet flow sequence, emergent planting shelves, a continuous dry maintenance edge and an accessible looping timber boardwalk network with a cross-link, southern gateway and small overlooks outside the primary flow path.',
    groundDescription:
      'Dark shallow-water pockets interwoven with yellow-green sedge, rush and wet-meadow shelves; gravel inlet and outlet aprons; muted native meadow on dry outer grades; and a narrow warm timber boardwalk with believable plank rhythm. The surface reads as an ecological water-treatment mosaic rather than an ornamental pond.',
    criticalConstraints:
      'Preserve the three distinct shallow wetland cells and their connected flow direction. No tree, bench, building, playground, generic lawn path or decorative fountain may enter a cell, inlet, outlet or wet shelf. The marked looping boardwalk, cross-link and southern gateway spur must remain continuous, accessible and elevated across the wet areas; all other access stays on dry outer ground. Never replace this network with one straight bridge, turn the system into one deep lake, or split it into disconnected ornamental pools.',
    canopyDescription:
      'Low emergent vegetation dominates the wet cells. Sparse native willow and deciduous canopy remains on the dry upland perimeter only, leaving the boardwalk, inlet, outlet and the full sequence of wetland cells legible from above.',
    plantingStructure: 'water_ecology',
    guides: [
      { kind: 'ellipse', x: 0.28, y: 0.47, width: 0.34, height: 0.40, color: '#496f72', strokeColor: '#84925f', strokeWidthM: 2.5 },
      { kind: 'ellipse', x: 0.52, y: 0.55, width: 0.36, height: 0.44, color: '#3e666b', strokeColor: '#7f915d', strokeWidthM: 2.8 },
      { kind: 'ellipse', x: 0.76, y: 0.44, width: 0.34, height: 0.40, color: '#557a78', strokeColor: '#8c9a64', strokeWidthM: 2.3 },
      ...WETLAND_BOARDWALK_PATHS.map((path) => ({
        kind: 'polyline' as const,
        x: 0.5,
        y: 0.5,
        width: 1,
        height: 1,
        points: [...path.points],
        closed: path.closed,
        color: '#b48d58',
        strokeColor: '#6e5435',
        strokeWidthM: 2.4,
      })),
    ],
    guideLegend: [
      'the three BLUE-GREEN cells are the exact connected shallow-water and emergent-planting sequence; keep their separate footprints and green wet shelves',
      'the WARM-TIMBER polylines are one exact continuous 2.4-metre accessible looping boardwalk network, including its cross-link and southern gateway spur; preserve every bend and junction',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'constructed wetland preserving three connected shallow treatment cells, emergent shelves, inlet/outlet function and one exact accessible boardwalk crossing',
    isPilot: true,
  },
  japanese_garden: {
    id: 'japanese-garden-v4',
    version: 4,
    programDescription:
      'A compact Japanese stroll garden with an asymmetrical koi pond, a short red pedestrian bridge, a raked-gravel garden, moss and low groundcover rooms, and stepping-stone circulation.',
    groundDescription:
      'Deep still pond water, irregular natural-stone pond edge, pale raked gravel with visible concentric patterns, mossy green groundcover, dark stepping stones and narrow compacted-earth paths. Paint the red lacquer bridge deck top and its two stone landing pads precisely on the marked alignment; live 3D rails and deck relief may overlay this footprint.',
    criticalConstraints:
      'Preserve the blue pond, pale gravel garden and red bridge alignment exactly where diagrammed. Do not convert this into a generic lawn park, formal European garden, playground or sports field.',
    canopyDescription:
      'Layered ornamental canopy of sculptural dark pines, spreading Japanese maples, lighter understory trees and a dense bamboo boundary screen, composed asymmetrically to frame views of the pond and bridge.',
    plantingStructure: 'japanese_stroll_garden',
    guides: [
      { kind: 'path_loop', x: 0.47, y: 0.52, width: 0.72, height: 0.68, color: '#8d7658', strokeWidthM: 1.8 },
      { kind: 'ellipse', x: 0.43, y: 0.54, width: 0.38, height: 0.27, widthM: 34, heightM: 20, color: '#315d69', strokeColor: '#263f45', strokeWidthM: 0.7 },
      { kind: 'rectangle', x: 0.73, y: 0.32, width: 0.25, height: 0.20, widthM: 22, heightM: 14, color: '#ddd1ad', strokeColor: '#92866a', strokeWidthM: 0.5 },
      { kind: 'line', x: 0.43, y: 0.54, width: 0.25, height: 0.0, widthM: JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.length, heightM: 0, color: '#a63d35', strokeWidthM: JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.width },
    ],
    guideLegend: [
      'the WARM-EARTH loop is the exact continuous 1.8-metre stroll path; preserve a complete circuit around the pond and garden rooms',
      'the BLUE-GREEN ellipse is the exact koi-pond footprint',
      'the PALE-BEIGE rectangle is the exact raked-gravel garden',
      'the RED bar crossing the pond is the exact red lacquer bridge-deck footprint; paint its top surface and keep clear stone landing pads at both ends',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'Japanese stroll garden preserving the diagrammed koi pond, raked-gravel court and bridge alignment',
    isPilot: true,
  },
  sports_field_complex: {
    id: 'sports-field-complex-v4',
    version: 4,
    programDescription:
      'A municipal outdoor sports complex with one full-size 100 by 64 metre football/soccer pitch and up to three regulation doubles tennis courts. Use the maximum number of whole tennis envelopes that fit the actual parcel, connected by a narrow perimeter access path.',
    groundDescription:
      'Closely mown athletic turf with crisp but realistically weathered white football markings, the retained complete blue-green acrylic tennis courts with regulation white linework, and narrow concrete or asphalt access paths. Keep all playing surfaces level and unobstructed.',
    criticalConstraints:
      'Preserve the 100 by 64 metre football pitch when its complete envelope fits, plus only the complete tennis safety envelopes retained by whole-element fit preflight. Each tennis envelope is 36.58 by 18.29 metres around a regulation 23.77 by 10.97 metre doubles court. Never scale, crop or truncate a field or court to fill leftover land. No trees, paths, furniture, ponds or buildings may intrude into a retained playing surface or safety run-off.',
    canopyDescription:
      'Tree cover is limited to varied mature perimeter windbreaks, entry groves and spectator shade clusters; every playing field, running lane and safety run-off remains completely open.',
    plantingStructure: 'sports_perimeter',
    guides: [
      { kind: 'soccer_field', x: 0.37, y: 0.50, width: 0.69, height: 0.80, widthM: 100, heightM: 64, color: '#5f8c54', strokeColor: '#f4f2df', strokeWidthM: 0.12 },
      { kind: 'tennis_court', x: 0.86, y: 0.20, width: 0.25, height: 0.23, widthM: 36.58, heightM: 18.29, color: '#4f7f73', strokeColor: '#f4f2df', strokeWidthM: 0.08 },
      { kind: 'tennis_court', x: 0.86, y: 0.50, width: 0.25, height: 0.23, widthM: 36.58, heightM: 18.29, color: '#4f7f73', strokeColor: '#f4f2df', strokeWidthM: 0.08 },
      { kind: 'tennis_court', x: 0.86, y: 0.80, width: 0.25, height: 0.23, widthM: 36.58, heightM: 18.29, color: '#4f7f73', strokeColor: '#f4f2df', strokeWidthM: 0.08 },
    ],
    guideLegend: [
      'the large GREEN rectangle is one exact 100 x 64 metre football/soccer playing field with regulation linework',
      'each BLUE-GREEN rectangle is an exact 36.58 x 18.29 metre tennis safety envelope containing one 23.77 x 10.97 metre regulation doubles court; never stretch the courts',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'sports-field complex preserving one full-size 100 x 64 metre football pitch when compatible and the maximum parcel-compatible count of complete regulation doubles tennis courts at exact real-world scale',
    isPilot: true,
  },
  athletics_precinct_sports_fields: {
    id: 'athletics-precinct-sports-fields-v1',
    version: 1,
    programDescription:
      'A regulation outdoor playing-field precinct containing up to two complete 100 by 64 metre community soccer pitches. Use the maximum count of whole fields that fits the actual polygon; leftover land becomes access, meadow buffer and spectator edge rather than a stretched or invented field.',
    groundDescription:
      'Closely mown striped sports turf with crisp white regulation markings, subdued meadow and gravel spectator margins, galvanized goals, modest aluminum bleachers and tall floodlight masts. Match the selected athletics archetype render while reserving clubhouses, grandstands and other large buildings for the separate building pipeline.',
    criticalConstraints:
      'Every retained soccer field is exactly 100 by 64 metres, within the regulation adult-field dimensional range, and stays level, complete and unobstructed. Never scale, crop, overlap or distort a field to fill the parcel. Keep goals, touchline run-off, lighting and bleachers outside play. Do not generate a clubhouse, grandstand, fieldhouse, parking lot, road or people as part of this park LEGO family.',
    canopyDescription:
      'The playing fields remain completely open. Sparse perimeter trees and meadow occur only beyond the touchline safety and spectator zones, leaving all goals and floodlight sightlines clear.',
    plantingStructure: 'athletics_fields_v0',
    guides: [
      { kind: 'soccer_field', x: 0.27, y: 0.50, width: 0.43, height: 0.72, widthM: 100, heightM: 64, color: '#5f8c54', strokeColor: '#f4f2df', strokeWidthM: 0.12, orientationPolicy: 'orthogonal' },
      { kind: 'soccer_field', x: 0.73, y: 0.50, width: 0.43, height: 0.72, widthM: 100, heightM: 64, color: '#5f8c54', strokeColor: '#f4f2df', strokeWidthM: 0.12, orientationPolicy: 'orthogonal' },
    ],
    guideLegend: [
      'each retained GREEN rectangle is one exact 100 by 64 metre regulation community soccer field; retain only complete fields and never enlarge one to consume an oversized site',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'athletics precinct preserving the maximum parcel-compatible count of complete 100 by 64 metre soccer fields with archetype-matched turf, goals, bleachers and floodlights but no large buildings',
    isPilot: true,
  },
  urban_forest: {
    id: 'urban-forest-v2',
    version: 2,
    programDescription:
      'A dense native urban woodland with a nearly continuous mixed deciduous-and-evergreen canopy, layered understory, shrub and groundcover strata, one narrow low-impact walking loop, and two small daylight clearings for orientation and habitat diversity.',
    groundDescription:
      'Dark leaf-litter and woodland-duff ground, mossy understory patches, native ferns and shrubs, a narrow warm-brown compacted-earth or bark-mulch trail, and two small muted meadow clearings. No broad mown lawn or ornamental paving.',
    criticalConstraints:
      'Preserve the diagrammed trail as one continuous, legible low-impact route and keep the two small clearings open. At least three quarters of the parcel must read as woodland habitat. Do not introduce sports fields, playground equipment, formal allees, broad paved plazas, parking, buildings or a generic lawn carpet; retain a layered scrub transition at every urban edge.',
    canopyDescription:
      'A near-closed, multi-age canopy of overlapping mature oak, ash, aspen and conifer crowns covers roughly 75-85 percent of the parcel, with strong height, species and green-tone variation, lighter understory visible in gaps and only the trail and two small clearings deliberately open.',
    plantingStructure: 'naturalistic_grove',
    guides: [
      { kind: 'path_loop', x: 0.50, y: 0.50, width: 0.82, height: 0.66, color: '#806b4e', strokeWidthM: 2.4 },
      { kind: 'ellipse', x: 0.30, y: 0.38, width: 0.16, height: 0.14, widthM: 18, heightM: 12, color: '#7f9564', strokeColor: '#61764e', strokeWidthM: 0.4 },
      { kind: 'ellipse', x: 0.72, y: 0.67, width: 0.18, height: 0.15, widthM: 20, heightM: 14, color: '#819a66', strokeColor: '#61764e', strokeWidthM: 0.4 },
    ],
    guideLegend: [
      'the BROWN loop is the exact continuous 2.4-metre low-impact woodland trail and must remain unobstructed through the parcel',
      'the two LIGHT-GREEN ellipses are the only daylight meadow clearings; retain dense layered woodland everywhere else',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'dense urban forest with a near-closed varied native canopy, one continuous low-impact trail and two small daylight clearings',
    isPilot: true,
  },
  botanical_garden: {
    id: 'botanical-garden-v5',
    version: 5,
    programDescription:
      'A curated botanical garden organized as a sequence of specimen-tree collections, geometric and organic perennial beds, a formal rose garden, demonstration plots, a compact conservatory pad and a connected interpretive walking loop.',
    groundDescription:
      'Pale gravel and warm unit-paver interpretive paths, richly varied horticultural beds in deep green, silver, gold, pink and purple, clipped lawn panels used only between collections, dark mulch beneath specimen trees, and a pale translucent conservatory foundation pad.',
    criticalConstraints:
      'Preserve every diagrammed collection bed, the continuous interpretive path and the conservatory pad. The parcel must read as a diverse ordered plant collection rather than a generic park. Do not enlarge or relocate the conservatory pad, replace beds with empty lawn, invent a fountain, pond, central axis, parterre or sports field, merge the three bed shapes, or let trees block paths, collection beds, demonstration plots or the formal rose-garden room.',
    canopyDescription:
      'A visibly curated collection of conical conifers, spreading deciduous specimens, columnar trees, flowering understory and small ornamental trees creates varied crown shapes, heights and seasonal color while leaving each themed bed and interpretive route readable.',
    plantingStructure: 'botanical_collection',
    guides: [
      { kind: 'path_loop', x: 0.50, y: 0.50, width: 0.82, height: 0.66, color: '#c6b99a', strokeWidthM: 2.8 },
      { kind: 'rectangle', x: 0.22, y: 0.24, width: 0.20, height: 0.15, widthM: 24, heightM: 14, color: '#b8c7c0', strokeColor: '#747f78', strokeWidthM: 0.7 },
      { kind: 'ellipse', x: 0.48, y: 0.35, width: 0.24, height: 0.20, widthM: 28, heightM: 16, color: '#a66d83', strokeColor: '#765062', strokeWidthM: 0.5 },
      { kind: 'ellipse', x: 0.70, y: 0.66, width: 0.26, height: 0.22, widthM: 30, heightM: 17, color: '#a89857', strokeColor: '#756b40', strokeWidthM: 0.5 },
      { kind: 'ellipse', x: 0.35, y: 0.72, width: 0.22, height: 0.18, widthM: 26, heightM: 14, color: '#78936d', strokeColor: '#536c4c', strokeWidthM: 0.5 },
    ],
    guideLegend: [
      'the PALE-GRAVEL loop is the exact continuous 2.8-metre interpretive path linking every collection room',
      'the PALE-GLASS rectangle is the exact compact conservatory foundation pad',
      'the ROSE, GOLD and SAGE ellipses are distinct formal, seasonal and woodland-edge plant collections; paths and canopy must preserve their shapes',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'botanical garden preserving a connected interpretive loop, compact conservatory pad, diverse specimen canopy and three distinct collection-bed rooms',
    isPilot: true,
  },
  nature_play_area: {
    id: 'nature-play-area-v3',
    version: 3,
    programDescription:
      'A nature-based play landscape with two linked activity clearings formed by low landforms, timber, boulders, sand, water-play channels and sensory planting, connected to every gateway by an accessible loop and framed by a mature shade grove.',
    groundDescription:
      'Warm engineered wood-fiber and sand play surfacing, rounded boulder and log zones, a shallow blue-grey rill on a contained pad, low meadow and sensory planting, pale accessible paths and small lawn pockets for informal play. Standing play elements are added only in the final render.',
    criticalConstraints:
      'Preserve both diagrammed play clearings, their safety fall zones and the continuous accessible connecting loop. Keep all gateways visible. Do not place trees, benches or planting inside the play pads or path clear width, do not substitute a plastic equipment field, sports pitch, formal plaza or pond, and keep every log, boulder and water-play element within the designated clearings.',
    canopyDescription:
      'Mature varied deciduous shade trees and smaller flowering understory form an irregular perimeter grove and a few edge clusters between play rooms, with grounded canopy shadows but completely open safety surfaces, gateway sightlines and accessible routes.',
    plantingStructure: 'nature_play_grove',
    guides: [
      { kind: 'path_loop', x: 0.50, y: 0.51, width: 0.78, height: 0.66, color: '#c7b99b', strokeWidthM: 3.0 },
      { kind: 'line', x: 0.50, y: 0.50, width: 0.72, height: 0.42, color: '#c7b99b', strokeWidthM: 3.0 },
      { kind: 'ellipse', x: 0.34, y: 0.40, width: 0.31, height: 0.28, widthM: 28, heightM: 22, color: '#b49162', strokeColor: '#7b6548', strokeWidthM: 0.6 },
      { kind: 'ellipse', x: 0.66, y: 0.62, width: 0.32, height: 0.29, widthM: 30, heightM: 22, color: '#c6aa72', strokeColor: '#806f4e', strokeWidthM: 0.6 },
      { kind: 'rectangle', x: 0.73, y: 0.31, width: 0.13, height: 0.10, widthM: 14, heightM: 5, color: '#668d99', strokeColor: '#496b74', strokeWidthM: 0.5 },
    ],
    guideLegend: [
      'the PALE perimeter loop is the exact continuous 3.0-metre accessible route joining gateways and both play rooms',
      'the PALE diagonal line is the exact accessible connecting path between gateways and both play rooms',
      'the two OCHRE ellipses are the exact wood-fiber and sand nature-play safety surfaces; keep them clear of canopy and paths',
      'the BLUE-GREY rectangle is the contained shallow water-play rill pad, not a pond',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'nature-play park preserving two linked safety-surface clearings, a contained water-play pad, accessible loop and shade-grove frame',
    isPilot: true,
  },
  reservoir_watershed_park: {
    id: 'reservoir-watershed-park-v3',
    version: 3,
    programDescription:
      'A compact urban watershed park organized around a clear rectangular impoundment lake. A continuous walking-and-cycling loop follows the full shoreline, a low concrete dam and spillway form one short edge, and a modest trailhead/viewpoint occupies dry ground near the dam.',
    groundDescription:
      'Deep blue-green still reservoir water with subtle aerial reflections; a pale compacted-gravel perimeter trail; narrow bands of cattails, willows, native wetland grasses and stone-armoured shoreline; mown upland lawn at the trailhead; and a low grey concrete dam/spillway band.',
    criticalConstraints:
      'The blue-green rectangle is authoritative and must remain open water at exactly the diagrammed scale, covering about 42 percent of the parcel. Keep the entire continuous shoreline trail readable. No trees, benches, buildings, paths or decorative planting may appear in the water. Cover every remaining dry-land area inside the parcel with mown upland turf, native wetland groundcover, pale gravel trail, stone-armoured shoreline or grey concrete dam; zero white, blank, unpainted or paper-like ground is permitted. This 1.1-hectare urban variant must not become a huge regional lake, generic lawn park, playground or marina.',
    canopyDescription:
      'A sparse single row of varied poplar and willow canopy follows the outer upland edge, with small naturalistic clusters near the trailhead; the lake surface, dam and perimeter trail remain unobstructed and legible from above.',
    plantingStructure: 'reservoir_perimeter',
    guides: [
      { kind: 'rectangle', x: 0.48, y: 0.50, width: 0.70, height: 0.60, color: '#356a78', strokeColor: '#b4a987', strokeWidthM: 3.0 },
      { kind: 'line', x: 0.84, y: 0.50, width: 0, height: 0.62, color: '#96958e', strokeWidthM: 3.2 },
    ],
    guideLegend: [
      'the BLUE-GREEN rectangle is the exact open-water reservoir footprint; its PALE outline is the continuous perimeter trail and shoreline band',
      'the GREY bar at the short edge is the exact low dam and spillway alignment; keep it clear of trees',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'compact urban reservoir with exact open-water footprint, continuous shoreline trail, low dam/spillway and sparse perimeter-only canopy',
    isPilot: true,
  },
};

// Community Park shares the same executable metric program as Neighborhood
// Park in Public Realm LEGO V1. Its catalog variants still provide distinct
// planting/material kits, while topology and fixed-program count stay locked.
PROFILES.community_park = {
  ...PROFILES.neighborhood_park,
  id: 'community-park-lego-v1',
  version: 1,
  programDescription: PROFILES.neighborhood_park.programDescription
    .replace('contemporary neighborhood park', 'community park'),
  renderSummary: PROFILES.neighborhood_park.renderSummary
    .replace('neighborhood park', 'community park'),
};

function normalizeId(value: unknown): string {
  return String(value ?? '').toLowerCase().trim().replace(/-/g, '_');
}

function findEntry(archetypeId: string): CatalogEntry | undefined {
  return CATALOG.find((entry) => archetypeId === entry.id)
    ?? CATALOG
      .filter((entry) => archetypeId.startsWith(`${entry.id}_`))
      .sort((left, right) => right.id.length - left.id.length)[0];
}

type CatalogParkFamily =
  | 'active_recreation'
  | 'naturalistic_grove'
  | 'garden_courtyard'
  | 'paved_plaza'
  | 'water_ecology'
  | 'sports_recreation'
  | 'parking_facility';

function containsAny(value: string, terms: string[]): boolean {
  return terms.some((term) => value.includes(term));
}

function catalogParkFamily(entry: CatalogEntry | undefined, archetypeId: string): CatalogParkFamily {
  const category = normalizeId(entry?.aestheticCategory);
  const semantic = normalizeId([
    archetypeId,
    entry?.title,
    category,
    entry?.spaceType,
    ...(entry?.generationTags ?? []),
  ].join(' '));
  if (containsAny(semantic, ['parking', 'airport', 'airfield'])) return 'parking_facility';
  // `court` used to be a raw substring and therefore misclassified every
  // courtyard and forecourt as a sports facility. Sports categories and
  // explicit activity nouns are unambiguous; a bare court is accepted only
  // as its own normalized token.
  const hasCourtToken = /(?:^|[_\s])courts?(?:$|[_\s])/.test(semantic);
  if (containsAny(category, ['sports_recreation']) || hasCourtToken || containsAny(semantic, [
    'tennis', 'pickleball', 'basketball', 'pitch', 'athletic', 'fitness',
    'golf', 'velodrome', 'pump_track', 'skate', 'bouldering', 'equestrian',
    'baseball', 'softball', 'cricket', 'disc_golf',
  ])) return 'sports_recreation';
  if (entry?.spaceType === 'plaza' || containsAny(category, [
    'civic', 'social_event', 'urban', 'plaza',
  ])) return 'paved_plaza';
  if (containsAny(category, ['water', 'ecological', 'river', 'natural']) || containsAny(semantic, [
    'pond', 'lake', 'wetland', 'stormwater', 'bioswale', 'riparian', 'reservoir',
    'riverfront', 'beach', 'marsh', 'canal', 'harbor', 'wharf', 'seawall',
  ])) return 'water_ecology';
  if (containsAny(category, ['garden', 'courtyard', 'victorian']) || containsAny(semantic, [
    'garden', 'orchard', 'arboretum', 'labyrinth', 'memorial', 'cemetery',
  ])) return 'garden_courtyard';
  if (containsAny(category, ['landscape', 'georgian']) || containsAny(semantic, [
    'forest', 'preserve', 'greenbelt', 'ravine', 'mount_royal', 'olmsted',
    'hilltop', 'foothill', 'grove', 'rewilding',
  ])) return 'naturalistic_grove';
  return 'active_recreation';
}

function sportGuides(archetypeId: string, accent: string): {
  guides: ParkGroundGuide[];
  legend: string[];
} {
  const white = '#f4f2df';
  if (archetypeId.includes('tennis')) {
    return {
      guides: [
        { kind: 'tennis_court', x: 0.5, y: 0.5, width: 0.78, height: 0.68, widthM: 36.58, heightM: 18.29, color: accent, strokeColor: white, strokeWidthM: 0.08 },
      ],
      legend: ['the marked court is one regulation 36.58 by 18.29 metre tennis court envelope including safe run-off; repeat only when the parcel can contain another complete envelope'],
    };
  }
  if (archetypeId.includes('pickleball')) {
    return {
      guides: [
        { kind: 'rectangle', x: 0.32, y: 0.5, width: 0.38, height: 0.58, widthM: 18.29, heightM: 9.14, color: accent, strokeColor: white, strokeWidthM: 0.08 },
        { kind: 'rectangle', x: 0.68, y: 0.5, width: 0.38, height: 0.58, widthM: 18.29, heightM: 9.14, color: accent, strokeColor: white, strokeWidthM: 0.08 },
      ],
      legend: ['the two marked envelopes are regulation pickleball courts with 18.29 by 9.14 metre total play-and-run-off dimensions'],
    };
  }
  if (archetypeId.includes('basketball')) {
    return {
      guides: [
        { kind: 'rectangle', x: 0.5, y: 0.5, width: 0.72, height: 0.62, widthM: 32, heightM: 19, color: accent, strokeColor: white, strokeWidthM: 0.1 },
      ],
      legend: ['the marked 32 by 19 metre envelope contains a regulation 28 by 15 metre basketball court plus two-metre safety run-off'],
    };
  }
  if (containsAny(archetypeId, ['running_track', 'velodrome'])) {
    return {
      guides: [
        { kind: 'track', x: 0.5, y: 0.5, width: 0.82, height: 0.74, widthM: 176.91, heightM: 92.52, color: '#a85647', strokeColor: white, strokeWidthM: 0.1 },
      ],
      legend: ['the marked 176.91 by 92.52 metre oval is a scale-locked standard 400-metre athletics-track envelope; never shrink it to fit an undersized parcel'],
    };
  }
  if (containsAny(archetypeId, ['soccer', 'sports_field', 'multi_sport', 'athletics_precinct'])) {
    return {
      guides: [
        { kind: 'soccer_field', x: 0.5, y: 0.5, width: 0.76, height: 0.68, widthM: 100, heightM: 64, color: '#5b8751', strokeColor: white, strokeWidthM: 0.12 },
      ],
      legend: ['the marked field is an exact 100 by 64 metre football/soccer pitch; preserve its linework, clear run-off and unobstructed playing surface'],
    };
  }
  if (archetypeId.includes('cricket')) {
    return {
      guides: [
        { kind: 'track', x: 0.5, y: 0.5, width: 0.86, height: 0.76, widthM: 150, heightM: 137, color: '#6c925c', strokeColor: white, strokeWidthM: 0.1, atomicGroup: 'cricket-field' },
        { kind: 'rectangle', x: 0.5, y: 0.5, width: 0.18, height: 0.08, widthM: 22.56, heightM: 3.05, color: '#b59d6c', strokeColor: white, strokeWidthM: 0.08, atomicGroup: 'cricket-field' },
      ],
      legend: ['the outer oval is a 150 by 137 metre community cricket field and the central strip is the exact 22.56 by 3.05 metre pitch'],
    };
  }
  if (containsAny(archetypeId, ['baseball', 'softball'])) {
    return {
      guides: [
        { kind: 'rectangle', x: 0.5, y: 0.5, width: 0.78, height: 0.72, widthM: 105, heightM: 105, color: '#6d9259', strokeColor: '#d8c49a', strokeWidthM: 0.12 },
      ],
      legend: ['the marked 105 by 105 metre envelope reserves a regulation community baseball/softball diamond, foul territory and safe outfield; keep all fixed objects outside it'],
    };
  }
  return {
    guides: [
      { kind: 'rectangle', x: 0.5, y: 0.5, width: 0.7, height: 0.58, color: accent, strokeColor: white, strokeWidthM: 0.12 },
    ],
    legend: ['the marked rectangle is the exact unobstructed primary recreation surface; keep its complete safety edge clear and put circulation outside it'],
  };
}

function familyGuides(family: CatalogParkFamily, archetypeId: string, accent: string): {
  guides: ParkGroundGuide[];
  legend: string[];
} {
  if (family === 'sports_recreation') return sportGuides(archetypeId, accent);
  if (family === 'parking_facility') return {
    guides: [
      { kind: 'rectangle', x: 0.5, y: 0.34, width: 0.82, height: 0.26, color: '#595d60', strokeColor: '#d8d8d2', strokeWidthM: 0.12 },
      { kind: 'rectangle', x: 0.5, y: 0.68, width: 0.82, height: 0.26, color: '#595d60', strokeColor: '#d8d8d2', strokeWidthM: 0.12 },
      { kind: 'axis', x: 0.5, y: 0.5, width: 0.9, height: 0, color: '#777b7d', strokeWidthM: 6.5 },
    ],
    legend: ['the two dark bands are full parking modules and the centre axis is the exact two-way drive aisle; stalls must be 2.6 by 5.5 metres and accessible routes remain continuous'],
  };
  if (family === 'paved_plaza') {
    const water = containsAny(archetypeId, ['fountain', 'pool', 'splash', 'water']);
    return {
      guides: [
        { kind: 'rectangle', x: 0.5, y: 0.5, width: 0.78, height: 0.68, color: accent, strokeColor: '#ded5c3', strokeWidthM: 0.35 },
        ...(water ? [{ kind: 'ellipse' as const, x: 0.5, y: 0.5, width: 0.24, height: 0.24, color: '#426c75', strokeColor: '#d2c4a7', strokeWidthM: 0.8 }] : []),
      ],
      legend: [water
        ? 'the large field is the clear accessible plaza and the blue centre is the exact water-feature basin; preserve clear event and approach space around it'
        : 'the marked field is the exact contiguous accessible hardscape room; keep its gateway-to-gateway movement paths clear of planting and fixed objects'],
    };
  }
  if (family === 'water_ecology') {
    if (containsAny(archetypeId, ['canal', 'corridor', 'seawall', 'boardwalk', 'promenade'])) return {
      guides: [
        { kind: 'axis', x: 0.5, y: 0.5, width: 0.9, height: 0, color: '#496f78', strokeWidthM: 8 },
        { kind: 'line', x: 0.5, y: 0.68, width: 0.76, height: 0, color: '#b8ad91', strokeWidthM: 3.5 },
      ],
      legend: ['the blue-green long axis is the continuous water/ecology corridor and the pale parallel line is its uninterrupted accessible trail or boardwalk'],
    };
    return {
      guides: [
        { kind: 'ellipse', x: 0.5, y: 0.5, width: 0.68, height: 0.5, color: '#426f78', strokeColor: '#788d68', strokeWidthM: 3 },
        { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.82, height: 0.68, color: '#aaa18b', strokeWidthM: 2.5 },
      ],
      legend: ['the blue-green footprint is the exact water or wetland cell and the pale loop is its dry, continuously accessible perimeter route; no object may enter either clear zone'],
    };
  }
  if (family === 'garden_courtyard') return {
    guides: [
      { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.78, height: 0.7, color: '#b3a384', strokeWidthM: 2.2 },
      { kind: 'ellipse', x: 0.34, y: 0.42, width: 0.3, height: 0.24, color: accent, strokeColor: '#526d48', strokeWidthM: 0.5 },
      { kind: 'ellipse', x: 0.66, y: 0.6, width: 0.32, height: 0.26, color: '#889b60', strokeColor: '#526d48', strokeWidthM: 0.5 },
    ],
    legend: ['the pale loop is the exact accessible garden circuit and the two planted rooms are intentional collection/quiet-garden beds; paths do not cut through them'],
  };
  if (family === 'naturalistic_grove') return {
    guides: [
      { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.82, height: 0.72, color: '#a99b7c', strokeWidthM: 2.8 },
      { kind: 'ellipse', x: 0.42, y: 0.48, width: 0.46, height: 0.34, color: '#758d58', strokeColor: '#506545', strokeWidthM: 0.6 },
    ],
    legend: ['the pale loop is the exact continuous trail and the green room is a managed clearing or meadow; retain surrounding habitat mass without blocking either'],
  };
  return {
    guides: [
      { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.82, height: 0.7, color: '#aaa18a', strokeWidthM: 2.5 },
      { kind: 'ellipse', x: 0.48, y: 0.48, width: 0.5, height: 0.38, color: accent, strokeColor: '#5d754a', strokeWidthM: 0.5 },
    ],
    legend: ['the pale loop is the exact connected circulation circuit and the green centre is the primary usable lawn/activity room; paths and planting remain outside its clear area'],
  };
}

function fallbackProfile(
  entry: CatalogEntry | undefined,
  archetypeId: string,
  variant?: CatalogVariant,
): ParkGroundProfile {
  const style = entry?.styleProfile;
  const family = catalogParkFamily(entry, archetypeId);
  const accent = variant?.color ?? (family === 'paved_plaza' ? '#a79a84' : '#78945c');
  const program = familyGuides(family, archetypeId, accent);
  const character = style?.landscapeCharacter
    ?? entry?.renderPrompt?.roofView
    ?? 'A realistic public open space with a coherent path and planting layout.';
  const materials = [style?.pavingType, style?.plantingType, style?.waterFeatures]
    .filter(Boolean)
    .join('; ');
  const variantDescription = variant?.description
    ? ` Selected variant (${variant.label ?? variant.id}): ${variant.description}`
    : '';
  const familyConstraint: Record<CatalogParkFamily, string> = {
    active_recreation: 'Keep the primary usable activity/lawn room open, connect every gateway to the loop, and place later trees or furniture only outside circulation and clear activity space.',
    naturalistic_grove: 'Retain a dominant connected habitat matrix, one legible clearing and one complete trail circuit; avoid ornamental symmetry, isolated tree dots or paths that terminate inside planting.',
    garden_courtyard: 'Preserve the complete stroll circuit and distinct planted rooms. Do not replace the chosen garden identity with generic lawn, radial parterre or unrelated water features.',
    paved_plaza: 'Keep a contiguous accessible hardscape field and continuous gateway routes. Fixed planting, water and furniture stay outside the required event and pedestrian clear zones.',
    water_ecology: 'Keep water, wet shelves, inlets/outlets and shoreline protection unobstructed. The marked dry route must remain continuous, accessible and separated from operational wet areas.',
    sports_recreation: 'Use regulation metric program dimensions and preserve the complete safety/run-off envelope. No tree, bench, path, water or decorative object may intrude on an active surface.',
    parking_facility: 'Use 2.6 by 5.5 metre standard stalls, 3.9 by 5.5 metre accessible stalls with access aisle, and 6.5 metre two-way drive aisles. Keep pedestrian and fire routes continuous.',
  };
  return {
    id: `catalog-${family.replace(/_/g, '-')}-v2`,
    version: 2,
    archetypeId,
    title: `${entry?.title ?? 'Open Space'}${variant?.label ? ` - ${variant.label}` : ''}`,
    programDescription: `${character}${variantDescription}`,
    groundDescription: `${materials || 'Use realistic, regionally appropriate landscape ground materials.'}${variantDescription}`,
    criticalConstraints:
      `Follow the selected ${entry?.title ?? archetypeId} archetype and variant rather than a generic neighborhood lawn park. ${familyConstraint[family]} Keep every large program element completely inside the parcel; if the parcel cannot fit a regulation element, report the incompatibility instead of scaling it down.`,
    canopyDescription:
      `${style?.plantingType ?? 'Regionally appropriate mature canopy and understory planting'}; ${style?.opennessEnclosure ?? 'balance enclosed canopy rooms with legible open clearings according to the selected archetype'}.`,
    // Catalog family ids describe the park's use. The scatter engine uses a
    // smaller executable vocabulary; sports surfaces require its dedicated
    // perimeter pattern so generic trees never fill the field interior.
    plantingStructure: family === 'sports_recreation' ? 'sports_perimeter' : family,
    guides: program.guides,
    guideLegend: program.legend,
    includeCentralPlaza: false,
    renderSummary: `${entry?.title ?? 'open-space'}${variant?.label ? ` / ${variant.label}` : ''} with its scale-locked ${family.replace(/_/g, ' ')} program, catalog materials and exact guide topology preserved`,
    isPilot: true,
  };
}

/** Camera-aware finishing instruction for mature, high-resolution park
 * imagery. It is shared by every park archetype so catalog entries retain
 * their own program while meeting one visual quality bar. */
export function buildParkRenderQualityInstruction(
  profile: ParkGroundProfile,
  angleFromNadirDeg: number,
): string {
  const common = (
    `MATURE PARK REALISM: ${profile.canopyDescription} `
    + 'Resolve the landscape as a coherent hierarchy of canopy, understory, lawn/meadow, planting beds, paths, water and hardscape rather than a flat green fill with scattered tree dots. '
    + 'Use believable species, age, crown-height, crown-shape and green-tone variation with irregular crown overlap. Paths form a continuous network with visible entrances and destinations. '
    + 'Trees and benches are render-finishing elements chosen only after the exact path, water and fixed-program layout is understood. Place trees in eligible dry lawn or planting soil with clear setbacks from paths, water, shore protection, fixed pads, dams and spillways. Place benches on small paved furnishing shoulders directly beside paths, gateways, overlooks or destinations, oriented toward the view or activity; never put a bench or tree on a path centerline, crossing, field, water surface or operational clear zone. '
    + 'No cloned evenly spaced trees, plastic spherical crowns, empty grass carpet, random disconnected paths or vegetation obscuring programmed clearings and water edges.'
  );
  if (angleFromNadirDeg <= 30) {
    return `${common} NEAR-NADIR QUALITY: the park must read as a precise aerial mosaic - dark, mid and light canopy masses, open lawn, beds, paths, water and hardscape stay distinctly legible, with realistic crown overlap and short contact shadows.`;
  }
  return `${common} OBLIQUE QUALITY: build convincing canopy depth through foreground, middle-distance and background layers, translucent crown edges and grounded contact shadows; paths, clearings, water and destination structures remain readable through deliberate canopy openings.`;
}

type ParkProfileZone = Pick<SiteZone, 'properties'> & Partial<Pick<SiteZone, 'zone_type'>>;

export type ParkSpecialtyStructureKind =
  | 'civic_fountain_assembly'
  | 'greenway_edge_assembly'
  | 'stormwater_control_assembly'
  | 'japanese_garden_bridge'
  | 'cricket_ground_assembly'
  | 'skate_park_v0_assembly'
  | 'inclusive_playground_v0_assembly'
  | 'dog_park_v0_assembly'
  | 'splash_pad_v0_assembly'
  | 'community_garden_v0_assembly'
  | 'tennis_cluster_v0_assembly'
  | 'nature_play_v0_assembly'
  | 'pump_track_v0_assembly'
  | 'outdoor_fitness_v0_assembly'
  | 'memorial_garden_v0_assembly'
  | 'archetype_full_park_assembly'
  | 'caged_soccer_v0_assembly'
  | 'sports_field_furniture'
  | 'tennis_court_furniture'
  | 'wetland_boardwalk'
  | 'botanical_conservatory';

function isPlazaZone(zone: ParkProfileZone): boolean {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const zoneType = String(zone.zone_type ?? '');
  return zoneType === 'parking'
    || zoneType === 'plaza'
    || typeof props.plaza_archetype_id === 'string'
    || typeof props.plaza_aesthetic === 'string';
}

export function resolveParkGroundProfile(zone: ParkProfileZone): ParkGroundProfile {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const plaza = isPlazaZone(zone);
  const legoContract = resolveParkLegoContract(zone);
  const archetypeId = normalizeId(
    legoContract?.supported
      ? legoContract.archetypeId
      : plaza
      ? (props.plaza_archetype_id ?? props.green_space_archetype_id)
      : (props.green_space_archetype_id ?? props.plaza_archetype_id),
  ) || (plaza ? 'formal_civic_plaza' : 'neighborhood_park');
  const entry = findEntry(archetypeId);
  const exact = PROFILES[archetypeId]
    ?? (archetypeId === 'community_park' && legoContract?.supported
      ? PROFILES.neighborhood_park
      : undefined)
    ?? Object.entries(PROFILES).find(([id]) => archetypeId.startsWith(`${id}_`))?.[1];
  const variantId = normalizeId(
    legoContract?.supported
      ? legoContract.variantId
      : plaza
      ? (props.plaza_selected_variant_id ?? props.green_space_selected_variant_id)
      : (props.green_space_selected_variant_id ?? props.plaza_selected_variant_id),
  );
  const variant = entry?.variants?.find((candidate) => (
    normalizeId(candidate.id) === variantId
    || normalizeId(candidate.id) === archetypeId
  ));
  if (!exact) {
    const fallback = fallbackProfile(entry, archetypeId, variant);
    return legoContract?.supported
      ? {
          ...fallback,
          legoFamilyId: legoContract.familyId,
          legoFamilyVersion: legoContract.familyVersion,
          variantId: legoContract.variantId,
        }
      : fallback;
  }
  const variantSuffix = variant?.label
    ? ` Selected variant style: ${variant.label}. Apply that variant only through compatible planting character, colour palette, paving and material finish; it does not authorize any new path, pond, fountain, field, bed, building or program element beyond this exact profile.`
    : '';
  return {
    ...exact,
    archetypeId,
    title: `${entry?.title ?? archetypeId.replace(/_/g, ' ')}${variant?.label ? ` - ${variant.label}` : ''}`,
    programDescription: `${exact.programDescription}${variantSuffix}`,
    groundDescription: `${exact.groundDescription}${variantSuffix}`,
    renderSummary: `${exact.renderSummary}${variant?.label ? `; selected ${variant.label} planting and material character without changing the locked program` : ''}`,
    ...(legoContract?.supported
      ? {
          legoFamilyId: legoContract.familyId,
          legoFamilyVersion: legoContract.familyVersion,
          variantId: legoContract.variantId,
        }
      : {}),
  };
}

/** Fixed structures are part of the editable park design rather than scene
 * dressing. Keep this decision pure and explicit so filtering render-only
 * trees/benches can never accidentally remove the structure's host frame. */
export function resolveParkSpecialtyStructureKind(
  zone: ParkProfileZone,
): ParkSpecialtyStructureKind | null {
  const legoContract = resolveParkLegoContract(zone);
  const exactKit = legoContract?.supported
    ? archetypeOwnedParkKitForFamily(legoContract.familyId)
    : null;
  if (legoContract?.source === 'public_realm_lego' && exactKit) {
    switch (exactKit.surfaceKind) {
      case 'skate': return 'skate_park_v0_assembly';
      case 'inclusive_playground': return 'inclusive_playground_v0_assembly';
      case 'dog_park': return 'dog_park_v0_assembly';
      case 'splash_pad': return 'splash_pad_v0_assembly';
      case 'community_garden': return 'community_garden_v0_assembly';
      case 'tennis_cluster': return 'tennis_cluster_v0_assembly';
      case 'nature_play': return 'nature_play_v0_assembly';
      case 'pump_track': return 'pump_track_v0_assembly';
      case 'outdoor_fitness': return 'outdoor_fitness_v0_assembly';
      case 'memorial_garden': return 'memorial_garden_v0_assembly';
      case 'pickleball_community':
      case 'track_oval_school':
      case 'baseball_club_hub':
      case 'cricket_village_green':
      case 'sports_complex_tournament': return 'archetype_full_park_assembly';
    }
  }
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && legoContract.familyId === 'park_skate_archetype_v0'
  ) return 'skate_park_v0_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && legoContract.familyId === 'park_civic_plaza'
  ) return 'civic_fountain_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && legoContract.familyId === 'park_linear_greenway'
  ) return 'greenway_edge_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && legoContract.familyId === 'park_water_ecology'
  ) return 'stormwater_control_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && legoContract.familyId === 'park_caged_soccer_v0'
  ) return 'caged_soccer_v0_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && legoContract.familyId === 'park_athletics_fields_v0'
  ) return 'sports_field_furniture';
  const archetypeId = resolveParkGroundProfile(zone).archetypeId;
  if (archetypeId.startsWith('japanese_garden')) return 'japanese_garden_bridge';
  if (archetypeId.startsWith('cricket_pitch_oval')) return 'cricket_ground_assembly';
  if (archetypeId.startsWith('sports_field_complex')) return 'sports_field_furniture';
  if (archetypeId.startsWith('athletics_precinct_sports_fields')) return 'sports_field_furniture';
  if (archetypeId.startsWith('soccer_pitch_caged')) return 'caged_soccer_v0_assembly';
  if (archetypeId.startsWith('tennis_court_cluster')) return 'tennis_court_furniture';
  if (archetypeId.startsWith('wetland_rain_garden')) return 'wetland_boardwalk';
  if (archetypeId.startsWith('botanical_garden')) return 'botanical_conservatory';
  return null;
}

export function shouldMountParkProgramFrame(
  zone: ParkProfileZone,
  liveAssetPlacementCount: number,
): boolean {
  return liveAssetPlacementCount > 0
    || resolveParkSpecialtyStructureKind(zone) !== null;
}

export function resolveParkPlantingStructure(zone: ParkProfileZone): string | undefined {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const legoContract = resolveParkLegoContract(zone);
  const legoAppearance = resolveParkLegoAppearance(zone);
  if (legoContract?.source === 'public_realm_lego' && legoContract.supported) {
    return legoContract.plantingStructure ?? legoAppearance?.plantingStructure;
  }
  if (typeof props.planting_structure === 'string' && props.planting_structure) {
    return props.planting_structure;
  }
  if (legoAppearance) return legoAppearance.plantingStructure;
  return resolveParkGroundProfile(zone).plantingStructure
    ?? (isPlazaZone(zone) ? 'paved_plaza' : undefined);
}

function legacyParkPlantingStructureForSignature(zone: ParkProfileZone): string | undefined {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  if (typeof props.planting_structure === 'string' && props.planting_structure) {
    return props.planting_structure;
  }
  return resolveParkGroundProfile(zone).plantingStructure
    ?? (isPlazaZone(zone) ? 'paved_plaza' : undefined);
}

function parkGroundPayloadHash(payload: string, version: 6 | 7): string {
  let hash = 0x811c9dc5;
  for (let index = 0; index < payload.length; index += 1) {
    hash ^= payload.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return `pg${version}-${(hash >>> 0).toString(16).padStart(8, '0')}`;
}

/** Stable signature: geometry or archetype changes make a persisted texture stale. */
export function parkGroundSourceSignature(
  zone: Pick<SiteZone, 'coordinates' | 'properties'> & Partial<Pick<SiteZone, 'zone_type'>>,
): string {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const profile = resolveParkGroundProfile(zone);
  const legoContract = resolveParkLegoContract(zone);
  const coordinates = zone.coordinates.map(([lng, lat]) => [
    Number(lng.toFixed(7)),
    Number(lat.toFixed(7)),
  ]);
  // GeoJSON/PostGIS rings repeat the first point while the Site Zone API
  // deliberately returns an open ring. They describe identical geometry and
  // must share one texture cache key; otherwise a harmless serialization
  // round-trip makes an existing paid ground drape look stale.
  if (
    coordinates.length > 1
    && coordinates[0][0] === coordinates[coordinates.length - 1][0]
    && coordinates[0][1] === coordinates[coordinates.length - 1][1]
  ) {
    coordinates.pop();
  }
  const access = Array.isArray(props.park_access_points)
    ? props.park_access_points.map((candidate) => (
      Array.isArray(candidate)
        ? [Number(Number(candidate[0]).toFixed(7)), Number(Number(candidate[1]).toFixed(7))]
        : candidate
    ))
    : [];
  const canonicalLegoContract = legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    ? legoContract
    : null;
  if (!canonicalLegoContract) {
    // Preserve the exact V6 object shape and property order. Paid legacy park
    // orthophotos persist this hash and must not be invalidated by LEGO V1.
    return parkGroundPayloadHash(JSON.stringify({
      generator: 'park-ground-v6-orientation-search',
      profile: profile.id,
      profileVersion: profile.version,
      zoneType: zone.zone_type,
      archetype: normalizeId(props.green_space_archetype_id),
      variant: normalizeId(props.green_space_selected_variant_id),
      plazaArchetype: normalizeId(props.plaza_archetype_id),
      plazaVariant: normalizeId(props.plaza_selected_variant_id),
      planting: legacyParkPlantingStructureForSignature(zone),
      access,
      coordinates,
    }), 6);
  }
  return parkGroundPayloadHash(JSON.stringify({
    generator: 'park-ground-v7-public-realm-lego',
    profile: profile.id,
    profileVersion: profile.version,
    zoneType: zone.zone_type,
    archetype: normalizeId(props.green_space_archetype_id),
    variant: normalizeId(props.green_space_selected_variant_id),
    plazaArchetype: normalizeId(props.plaza_archetype_id),
    plazaVariant: normalizeId(props.plaza_selected_variant_id),
    publicRealmLego: {
      familyId: canonicalLegoContract.familyId,
      familyVersion: canonicalLegoContract.familyVersion,
      archetypeId: canonicalLegoContract.archetypeId,
      variantId: canonicalLegoContract.variantId,
      plantingStructure: canonicalLegoContract.plantingStructure,
      appearanceKitId: canonicalLegoContract.appearanceKitId,
      catalogFingerprint: canonicalLegoContract.catalogFingerprint,
      capabilityFingerprint: canonicalLegoContract.capabilityFingerprint,
      recipeHash: canonicalLegoContract.recipeHash,
    },
    planting: resolveParkPlantingStructure(zone),
    access,
    coordinates,
  }), 7);
}

export const PILOT_PARK_ARCHETYPE_IDS = Object.freeze(Object.keys(PROFILES));
