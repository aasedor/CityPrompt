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
  | 'tennis_court'
  | 'basketball_court';

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

/** Regulation LEGO families render their playable surface as a planar,
 * textured 3D module. The terrain-following procedural ground must leave that
 * same guide to the assembly, otherwise the sloped copy remains visible below
 * it and reads as a second floating court or field. */
const LEGO_ASSEMBLY_SURFACE_GUIDE_KIND: Partial<Record<ParkLegoFamilyId, ParkGuideKind>> = {
  park_basketball_court_v0: 'basketball_court',
  park_tennis_cluster_v0: 'tennis_court',
  park_caged_soccer_v0: 'soccer_field',
  park_athletics_fields_v0: 'soccer_field',
  park_ice_rink_multipurpose_v3: 'rounded_rectangle',
  park_velodrome_open_air_v0: 'track',
  park_mtb_skills_dirt_v2: 'track',
};

export function isParkGuideRenderedByLegoAssembly(
  familyId: ParkLegoFamilyId | undefined,
  guideKind: ParkGuideKind,
): boolean {
  return familyId !== undefined
    && LEGO_ASSEMBLY_SURFACE_GUIDE_KIND[familyId] === guideKind;
}

const SEMANTIC_PLAY_SURFACE_KINDS = new Set<ParkGuideKind>([
  'soccer_field',
  'tennis_court',
  'track',
  'basketball_court',
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
  if (
    guide.kind === 'rectangle'
    || guide.kind === 'rounded_rectangle'
    || guide.kind === 'ellipse'
    || guide.kind === 'basketball_court'
  ) {
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
  basketball_court: {
    id: 'basketball-court-archetype-v2',
    version: 2,
    programDescription:
      'A classic public-park basketball enclosure containing up to two complete 32 by 19 metre full-court envelopes. Use the maximum number of whole regulation modules that fit: an oversized parcel receives two courts instead of one stretched playing surface.',
    groundDescription:
      'Weathered charcoal asphalt with fine aggregate variation, restrained crack and patch character, accurate off-white regulation markings, a narrow concrete apron, galvanized chain-link fencing, steel backboards, simple player benches and tall floodlights.',
    criticalConstraints:
      'Every retained full court contains one exact 28 by 15 metre playing rectangle inside a 32 by 19 metre play-and-run-off envelope. Never stretch, crop, overlap or invent non-standard markings. Hoops remain 3.05 metres high and align to each baseline. Fences, benches, lights, bins, trees and circulation stay outside every complete court envelope. Do not render people or surrounding large buildings.',
    canopyDescription:
      'No canopy overhangs a court, hoop, fence or floodlight. Any trees remain sparse and outside the enclosure, with clear gates and spectator sightlines.',
    plantingStructure: 'basketball_classic_v0',
    guides: [
      { kind: 'basketball_court', x: 0.27, y: 0.50, width: 0.40, height: 0.62, widthM: 32, heightM: 19, color: '#363938', strokeColor: '#eeeade', strokeWidthM: 0.10, orientationPolicy: 'orthogonal' },
      { kind: 'basketball_court', x: 0.73, y: 0.50, width: 0.40, height: 0.62, widthM: 32, heightM: 19, color: '#363938', strokeColor: '#eeeade', strokeWidthM: 0.10, orientationPolicy: 'orthogonal' },
    ],
    guideLegend: [
      'each retained CHARCOAL rectangle is one exact 32 by 19 metre full-court envelope containing a 28 by 15 metre regulation playing court; keep complete markings, two hoops, run-off and enclosure',
    ],
    includeCentralPlaza: false,
    renderSummary:
      'classic asphalt basketball park preserving the maximum parcel-compatible count of complete regulation full courts, exact markings, paired hoops, chain-link enclosure, benches and floodlights',
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

// Batch 4 replaces generic catalog fallbacks with exact v0 LEGO programs.
// These programs are topology contracts: reference imagery supplies material
// hierarchy and spatial relationships, while the parcel fit may rotate or
// omit whole metric elements but may never stretch them.
PROFILES.pond_lake = {
  id: 'pond-lake-lego-v1', version: 1,
  programDescription: 'A naturalistic neighborhood pond with one coherent open-water basin, a continuous dry walking loop, a small timber viewing dock and layered willow, sedge and fieldstone shoreline rooms.',
  groundDescription: 'Deep variegated blue-green water, irregular fieldstone edge, dark organic wet shelf, yellow-green sedges, warm fine gravel and muted meadow turf derived from the Naturalistic Pond reference.',
  criticalConstraints: 'Preserve exactly one pond, one complete dry loop and one small dock. The dock touches the water edge but never becomes a marina. Do not turn the pond into a formal pool, treatment-cell network, fountain, sports field or generic lawn.',
  canopyDescription: 'Irregular willow and deciduous clusters frame roughly half the shoreline, with open views from the dock and path and no trees in open water.',
  plantingStructure: 'pond_lake_v0',
  guides: [
    { kind: 'ellipse', x: 0.48, y: 0.51, width: 0.62, height: 0.48, color: '#315b63', strokeColor: '#69785d', strokeWidthM: 2.2 },
    { kind: 'path_loop', x: 0.48, y: 0.51, width: 0.78, height: 0.70, color: '#b5a47f', strokeColor: '#786a50', strokeWidthM: 2.6 },
    { kind: 'line', x: 0.77, y: 0.52, width: 0.15, height: 0, widthM: 9, color: '#8d6842', strokeColor: '#60462f', strokeWidthM: 2.4, orientationPolicy: 'fixed' },
  ],
  guideLegend: ['the BLUE-GREEN ellipse is the single naturalistic pond and emergent shoreline shelf', 'the TAN loop is the exact continuous dry walking path', 'the BROWN bar is the exact small timber viewing dock alignment'],
  includeCentralPlaza: false,
  renderSummary: 'naturalistic pond preserving one coherent basin, irregular planted shoreline, continuous dry loop and small timber dock',
  isPilot: true,
};

PROFILES.amphitheater_lawn = {
  id: 'amphitheater-lawn-lego-v1', version: 1,
  programDescription: 'A grass performance bowl with four shallow concentric lawn terraces focused on one 18 by 8 metre timber stage and an accessible path along the upper rim.',
  groundDescription: 'Variegated closely mown turf, darker terrace risers, weathered timber stage boards, pale compacted-gravel rim path and muted native-meadow shoulders.',
  criticalConstraints: 'Keep every terrace focused on the stage and preserve clear sightlines. The stage is a small park structure, not a building. No acoustic shell, grandstand, road, parking, people or trees inside the seating fan.',
  canopyDescription: 'Varied mature shade trees remain only on the upper perimeter behind the rim path.',
  plantingStructure: 'amphitheater_lawn_v0',
  guides: [
    { kind: 'ellipse', x: 0.50, y: 0.55, width: 0.76, height: 0.66, color: '#668552', strokeColor: '#4e6d44', strokeWidthM: 0.8 },
    { kind: 'ellipse', x: 0.50, y: 0.56, width: 0.62, height: 0.52, color: '#728f5b', strokeColor: '#4e6d44', strokeWidthM: 0.8 },
    { kind: 'ellipse', x: 0.50, y: 0.58, width: 0.48, height: 0.38, color: '#78965f', strokeColor: '#4e6d44', strokeWidthM: 0.8 },
    { kind: 'ellipse', x: 0.50, y: 0.60, width: 0.34, height: 0.24, color: '#809d66', strokeColor: '#4e6d44', strokeWidthM: 0.8 },
    { kind: 'rectangle', x: 0.50, y: 0.76, width: 0.27, height: 0.12, widthM: 18, heightM: 8, color: '#8d6540', strokeColor: '#5d402b', strokeWidthM: 0.5 },
    { kind: 'path_loop', x: 0.50, y: 0.54, width: 0.88, height: 0.80, color: '#b6aa8c', strokeWidthM: 2.8 },
  ],
  guideLegend: ['the four nested GREEN ellipses are the shallow terraced lawn-seating bowl', 'the BROWN rectangle is the exact 18 by 8 metre timber stage', 'the PALE outer loop is the accessible upper-rim path'],
  includeCentralPlaza: false,
  renderSummary: 'terraced grass amphitheater preserving four lawn tiers, one timber stage, an accessible rim path and open sightlines',
  isPilot: true,
};

PROFILES.riparian_buffer = {
  id: 'riparian-buffer-lego-v1', version: 1,
  programDescription: 'A narrow restored creek corridor with one continuous sinuous channel, broad planted banks, a parallel multi-use trail on dry ground and one small timber crossing at a central pinch point.',
  groundDescription: 'Shallow blue-grey water, gravel and cobble bars, dark moist bank soil, layered willow and emergent planting, tawny meadow and warm compacted gravel.',
  criticalConstraints: 'Keep the creek continuous from end to end and preserve vegetated buffers on both banks. The dry trail parallels rather than replaces the creek. Use one modest crossing only; no ornamental pond, lawn carpet, hard canal, road or buildings.',
  canopyDescription: 'Willows and varied riparian trees form irregular staggered groups rather than cloned rows, preserving trail and water views.',
  plantingStructure: 'riparian_buffer_v0',
  guides: [
    { kind: 'polyline', x: 0.50, y: 0.50, width: 1, height: 1, points: [[0.02, 0.43], [0.18, 0.58], [0.36, 0.40], [0.54, 0.55], [0.72, 0.39], [0.98, 0.52]], color: '#466f75', strokeColor: '#6f8060', strokeWidthM: 6.5 },
    { kind: 'polyline', x: 0.50, y: 0.73, width: 1, height: 1, points: [[0.02, 0.72], [0.22, 0.82], [0.44, 0.68], [0.66, 0.78], [0.98, 0.68]], color: '#b2a27f', strokeColor: '#75684e', strokeWidthM: 3.2 },
    { kind: 'line', x: 0.52, y: 0.58, width: 0, height: 0, widthM: 14, heightM: 0, color: '#8d6842', strokeColor: '#60462f', strokeWidthM: 2.2, rotationDeg: 90, orientationPolicy: 'fixed' },
  ],
  guideLegend: ['the BLUE-GREEN sinuous route is the continuous creek channel and planted bank shelf', 'the TAN route is the exact dry 3.2-metre multi-use trail', 'the BROWN crossing is one small timber bridge'],
  includeCentralPlaza: false,
  renderSummary: 'restored riparian corridor preserving a continuous creek, layered native banks, parallel dry trail and one timber crossing',
  isPilot: true,
};

PROFILES.playground_adventure = {
  id: 'playground-adventure-lego-v1', version: 1,
  programDescription: 'A rustic adventure playground with interconnected rough-hewn timber towers, rope bridges and climbing nets, a separate swing bay, two linked gravel and engineered-wood-fibre safety rooms, split-rail fencing and a clear perimeter circulation loop.',
  groundDescription: 'Complex warm-grey compacted gravel, tan engineered wood fibre, weathered timber, galvanized slide metal, dark rope, meadow grasses and wildflower margins sampled from the exact Rustic Timber & Gravel v0 reference.',
  criticalConstraints: 'Preserve two distinct safety rooms and complete fall zones. Keep timber towers, rope routes, slides and swings at child-scaled real dimensions. Fencing, boulders and meadow stay outside moving-equipment clearances. No people, large buildings, colored rubber mosaic, fabric shade sails or monocolour surface.',
  canopyDescription: 'Sparse shade trees and meadow remain outside the split-rail fence and fall zones; the timber climbing network stays fully legible.',
  plantingStructure: 'playground_adventure_v0',
  guides: [
    { kind: 'rounded_rectangle', x: 0.43, y: 0.48, width: 0.55, height: 0.58, widthM: 24, heightM: 24, color: '#8a806f', strokeColor: '#b4a47e', strokeWidthM: 1.0 },
    { kind: 'rounded_rectangle', x: 0.76, y: 0.58, width: 0.24, height: 0.40, widthM: 10, heightM: 16, color: '#9a896d', strokeColor: '#b4a47e', strokeWidthM: 1.0 },
    { kind: 'path_loop', x: 0.52, y: 0.52, width: 0.90, height: 0.82, color: '#c2b59c', strokeWidthM: 2.4 },
  ],
  guideLegend: ['the WARM-GREY and TAN rounded rectangles are distinct gravel/wood-fibre tower and swing safety rooms with complete fall zones', 'the PALE loop is the exact clear perimeter circulation and split-rail-fence access route'],
  includeCentralPlaza: false,
  renderSummary: 'rustic adventure playground preserving rough timber towers, rope climbing, distinct gravel and wood-fibre safety rooms, split-rail fencing and a clear perimeter route',
  isPilot: true,
};

PROFILES.community_park = {
  id: 'community-park-lego-v1',
  version: 1,
  programDescription: 'A large English-pastoral community park organized around one complete 100 by 64 metre recreation field, a naturalistic pond, a continuous serpentine walking circuit, a picnic grove and one modest pavilion pad. Irregular residual land remains meadow and shade grove.',
  groundDescription: 'Varied mown turf, darker striped field grass, deep blue-green pond water, warm compacted-gravel paths, native meadow, weathered timber and small pale concrete pads.',
  criticalConstraints: 'Retain the complete regulation field only when it fits; never stretch or crop it. Keep pond, field and picnic/social edge separate and connected by the walking circuit. No large buildings, roads, parking or people.',
  canopyDescription: 'Irregular mature deciduous groups frame the pond, picnic grove and outer path while keeping the complete field open.',
  plantingStructure: 'naturalistic_grove',
  guides: [
    { kind: 'soccer_field', x: 0.35, y: 0.55, width: 0.45, height: 0.50, widthM: 100, heightM: 64, color: '#668b53', strokeColor: '#eeeade', strokeWidthM: 0.10, orientationPolicy: 'orthogonal' },
    { kind: 'ellipse', x: 0.76, y: 0.34, width: 0.27, height: 0.25, color: '#3c6870', strokeColor: '#72815f', strokeWidthM: 2.0 },
    { kind: 'path_loop', x: 0.50, y: 0.50, width: 0.88, height: 0.78, color: '#b6a785', strokeColor: '#786a50', strokeWidthM: 3.0 },
    { kind: 'ellipse', x: 0.76, y: 0.72, width: 0.20, height: 0.16, color: '#8d9c61', strokeColor: '#68764e', strokeWidthM: 0.6 },
    { kind: 'rectangle', x: 0.79, y: 0.64, width: 0.08, height: 0.08, widthM: 8, heightM: 7, color: '#9c8a70', strokeColor: '#665b4b', strokeWidthM: 0.5 },
  ],
  guideLegend: ['the large GREEN rectangle is one complete 100 by 64 metre recreation field and is omitted rather than stretched', 'the BLUE-GREEN ellipse is the naturalistic community pond and planted shelf', 'the TAN loop is the continuous serpentine walking circuit', 'the SAGE picnic grove and SMALL BROWN pavilion pad form one connected social edge'],
  includeCentralPlaza: false,
  renderSummary: 'English-pastoral community park preserving a complete recreation field, naturalistic pond, serpentine loop and picnic/pavilion social edge',
  isPilot: true,
};

// Batch 5 exact v0 programs. These are reference-owned composition grammars,
// not generic category fallbacks. Repetition is intentional and metric: whole
// lanes/courts/tees are omitted when a site cannot contain them.
PROFILES.disc_golf_course = {
  id: 'disc-golf-wooded-lego-v1', version: 1,
  programDescription: 'A compact nine-hole wooded championship disc-golf route. Nine concrete tee pads address nine separate metal basket targets through alternating fairway clearings, with one continuous wayfinding trail and small spectator clearings at the longest holes.',
  groundDescription: 'Dark woodland floor, layered native understory, pale weathered concrete tees, warm fine-gravel trail, irregular mown fairway openings and galvanized target baskets sampled from the exact Wooded Championship v0 reference.',
  criticalConstraints: 'Keep every tee paired to one visible basket and maintain a safe non-crossing throwing corridor. Tee pads remain 4 by 2 metres and targets remain human-scaled; do not enlarge one fairway to consume an oversized site. People and surrounding buildings are reference-only scale cues.',
  canopyDescription: 'Dense mixed-age deciduous and pine canopy frames rather than fills each throwing corridor; fairway sightlines and the trail remain open.',
  plantingStructure: 'disc_golf_wooded_v0',
  guides: [
    { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.88, height: 0.78, color: '#ab9b7c', strokeWidthM: 2.4 },
    ...[[0.15,0.22],[0.38,0.16],[0.68,0.20],[0.84,0.36],[0.70,0.50],[0.84,0.70],[0.58,0.80],[0.32,0.72],[0.16,0.52]].flatMap(([x,y], index): ParkGroundGuide[] => [
      { kind: 'rectangle', x, y, width: 0.025, height: 0.035, widthM: 4, heightM: 2, color: '#b5b2a8', strokeColor: '#78766e', strokeWidthM: 0.15, orientationPolicy: 'flexible', atomicGroup: `disc-hole-${index}` },
      { kind: 'ellipse', x: Math.min(0.93, x + (index % 2 === 0 ? 0.12 : -0.11)), y: Math.min(0.91, y + 0.08), width: 0.018, height: 0.018, widthM: 2.4, heightM: 2.4, color: '#8d963f', atomicGroup: `disc-hole-${index}` },
    ]),
  ],
  guideLegend: ['the TAN loop is the continuous nine-hole wayfinding route', 'each GREY tee rectangle is paired with one GREEN target circle and one protected wooded fairway sightline'],
  includeCentralPlaza: false, renderSummary: 'nine-hole wooded disc-golf course with exact tee pads, galvanized basket targets, non-crossing fairway clearings and a continuous trail', isPilot: true,
};

PROFILES.bocce_petanque_court = {
  id: 'bocce-piazza-lego-v1', version: 1,
  programDescription: 'One traditional Italian-piazza bocce lane with a 27.5 by 4 metre oyster-shell playing bed, low stone containment, an accessible side walk and a vine-covered timber pergola with shaded spectator seating.',
  groundDescription: 'Variegated pale oyster shell, honey-grey stone borders, warm sun-aged timber, terracotta accents and muted Mediterranean planting drawn from the Italian Piazza v0 reference.',
  criticalConstraints: 'Preserve the complete lane and level playing bed. Stone edges, balls, pergola posts and seating remain outside the playing rectangle. Large surrounding buildings and people are excluded.',
  canopyDescription: 'Olive-like small trees and vines stay on the social edge; the playing lane remains fully open.', plantingStructure: 'bocce_piazza_v0',
  guides: [
    { kind: 'rounded_rectangle', x: 0.50, y: 0.56, width: 0.78, height: 0.30, widthM: 27.5, heightM: 4, color: '#d1c5a5', strokeColor: '#8a7c63', strokeWidthM: 0.25, orientationPolicy: 'orthogonal' },
    { kind: 'line', x: 0.50, y: 0.25, width: 0.72, height: 0, color: '#8b6848', strokeWidthM: 3.2, orientationPolicy: 'orthogonal' },
  ],
  guideLegend: ['the PALE lane is one exact regulation bocce playing bed with complete stone containment', 'the BROWN side band is the pergola, accessible walk and spectator edge'], includeCentralPlaza: false,
  renderSummary: 'Italian-piazza bocce court with oyster-shell lane, low stone containment, vine pergola and shaded social edge', isPilot: true,
};

PROFILES.climbing_bouldering_wall = {
  id: 'climbing-competition-lego-v1', version: 1,
  programDescription: 'A competition bouldering park with one continuous 22 by 17 metre black fall-zone mat and five angular wall volumes of varied height and overhang, carrying sparse colour-coded climbing routes and a clear spectator deck.',
  groundDescription: 'Black segmented impact mats, warm-grey and pale-plywood wall faces, charcoal undersides, bright yellow/blue/orange holds, board-formed concrete and timber spectator decking sampled from Competition Boulder v0.',
  criticalConstraints: 'Keep all walls within the continuous fall zone, maximum climbing height 4.5 metres, and preserve open landing clearance around every face. Holds are route cues, not random confetti. Do not render climbers or surrounding buildings.',
  canopyDescription: 'Minimal edge planting only; no trees over fall mats or climbing faces.', plantingStructure: 'climbing_competition_v0',
  guides: [
    { kind: 'rounded_rectangle', x: 0.50, y: 0.52, width: 0.78, height: 0.72, widthM: 22, heightM: 17, color: '#272927', strokeColor: '#131413', strokeWidthM: 0.4, orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.26, y: 0.48, width: 0.18, height: 0.35, widthM: 5.5, heightM: 8, color: '#a99e8b' },
    { kind: 'rectangle', x: 0.52, y: 0.43, width: 0.22, height: 0.42, widthM: 7, heightM: 9, color: '#898d89' },
    { kind: 'rectangle', x: 0.78, y: 0.55, width: 0.16, height: 0.32, widthM: 5, heightM: 7, color: '#c5b79e' },
  ],
  guideLegend: ['the BLACK rounded rectangle is the complete impact-safety room', 'the three faceted rectangles locate the interlocking competition wall volumes and remain inside the fall zone'], includeCentralPlaza: false,
  renderSummary: 'competition bouldering park with angular overhanging walls, colour-coded routes, continuous fall mat and spectator edge', isPilot: true,
};

PROFILES.mini_golf_course = {
  id: 'mini-golf-classic-lego-v1', version: 1,
  programDescription: 'A compact nine-hole classic miniature-golf course. Narrow artificial-turf putting lanes follow a connected serpentine sequence around a windmill, castle gate, loop and small ship obstacle, with low masonry lane edges and one clear accessible circuit.',
  groundDescription: 'Variegated green putting turf, red-brown brick walks, warm-grey block edging, painted timber obstacles and trimmed evergreen planting drawn from Classic Themed v0.',
  criticalConstraints: 'Build nine individually legible lanes in order, not one oversized putting green. Keep obstacle footprints and masonry edges outside each ball route and preserve accessible circulation. People and perimeter buildings are omitted.',
  canopyDescription: 'Low clipped shrubs and small ornamental trees frame lanes without covering putting surfaces.', plantingStructure: 'mini_golf_classic_v0',
  guides: [
    { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.90, height: 0.80, color: '#a8654b', strokeWidthM: 2.0 },
    ...[[0.20,0.22],[0.50,0.20],[0.80,0.23],[0.75,0.43],[0.43,0.42],[0.20,0.48],[0.24,0.70],[0.53,0.70],[0.80,0.72]].map(([x,y], index): ParkGroundGuide => ({ kind: 'rounded_rectangle', x, y, width: 0.18, height: 0.12, widthM: 7.5, heightM: 2.4, color: index % 2 ? '#557b47' : '#63864f', strokeColor: '#8b8476', strokeWidthM: 0.30, orientationPolicy: 'flexible' })),
  ],
  guideLegend: ['the RED-BRICK loop is the connected accessible circuit', 'the nine GREEN rounded lanes are whole putting holes with low masonry edges and distinct classic obstacles'], includeCentralPlaza: false,
  renderSummary: 'nine-hole classic mini-golf course with individually legible turf lanes, masonry edges, windmill, castle, loop and ship obstacles', isPilot: true,
};

PROFILES.beach_volleyball_courts = {
  id: 'beach-volleyball-competition-lego-v1', version: 1,
  programDescription: 'One complete competition beach-volleyball court: an exact 16 by 8 metre playing rectangle centered in a 24 by 16 metre sand-and-free-zone envelope, with a 2.43 metre net, referee stand, restrained spectator edge and tournament lighting kept outside run-off.',
  groundDescription: 'Fine variegated pale sand with subtle rake and footprint texture, deep-blue boundary tape, white net mesh, dark navy padded posts and warm-grey concrete spectator edges sampled from Competition Standard v0.',
  criticalConstraints: 'Never stretch the playing rectangle or free zone. Nets, referee stand, lights and seating stay outside boundary tape and required run-off. A larger parcel may host additional whole envelopes only; no oversized single court. No people or large buildings.',
  canopyDescription: 'Only low coastal planting outside the free zone; no canopy shadows on the competition court.', plantingStructure: 'beach_volleyball_competition_v0',
  guides: [
    { kind: 'rounded_rectangle', x: 0.50, y: 0.50, width: 0.88, height: 0.78, widthM: 24, heightM: 16, color: '#d8c99e', strokeColor: '#294d7c', strokeWidthM: 0, orientationPolicy: 'orthogonal', atomicGroup: 'volleyball-1' },
    { kind: 'line', x: 0.50, y: 0.50, width: 0, height: 0, widthM: 8, color: '#e9ebe6', strokeColor: '#294d7c', strokeWidthM: 0.12, rotationDeg: 90, orientationPolicy: 'fixed', atomicGroup: 'volleyball-1' },
  ],
  guideLegend: ['the SAND rectangle is one complete 24 by 16 metre play-and-free-zone envelope', 'the WHITE-BLUE centre bar is the exact competition net alignment'], includeCentralPlaza: false,
  renderSummary: 'competition beach-volleyball court with exact sand envelope, blue boundary, padded net posts, referee stand and clear spectator edge', isPilot: true,
};

PROFILES.pollinator_meadow = {
  id: 'pollinator-prairie-lego-v1', version: 1,
  programDescription: 'A prairie-restoration pollinator meadow organized as four interlocking native-grass and wildflower drifts around one continuously mown walking loop, two interpretive nodes and a deliberately open sunny interior.',
  groundDescription: 'Complex tawny-green prairie matrix with purple coneflower, yellow rudbeckia and pale seed-head flecks, narrow mown turf edges and warm compacted-earth path tones sampled from Prairie Restoration v0.',
  criticalConstraints: 'Preserve broad contiguous habitat rather than flower confetti or ornamental beds. The loop remains continuous; interpretation stays on small shoulders. No generic lawn, buildings or people.',
  canopyDescription: 'Very sparse perimeter trees only; the meadow interior stays sunlit and structurally varied.', plantingStructure: 'pollinator_prairie_v0',
  guides: [
    { kind: 'path_loop', x: 0.50, y: 0.52, width: 0.80, height: 0.68, color: '#b7a47e', strokeWidthM: 2.2 },
    { kind: 'ellipse', x: 0.30, y: 0.36, width: 0.40, height: 0.30, color: '#8b8551' },
    { kind: 'ellipse', x: 0.68, y: 0.35, width: 0.42, height: 0.30, color: '#766f46' },
    { kind: 'ellipse', x: 0.34, y: 0.69, width: 0.44, height: 0.28, color: '#8c774c' },
    { kind: 'ellipse', x: 0.72, y: 0.66, width: 0.38, height: 0.30, color: '#777f4e' },
  ],
  guideLegend: ['the TAN loop is the exact continuously mown route', 'the four overlapping GREEN-GOLD fields are contiguous native prairie drifts with different flowering and grass structure'], includeCentralPlaza: false,
  renderSummary: 'prairie-restoration pollinator meadow with four habitat drifts, continuous mown loop and restrained interpretive nodes', isPilot: true,
};

PROFILES.urban_orchard_food_forest = {
  id: 'orchard-heritage-lego-v1', version: 1,
  programDescription: 'A heritage apple orchard with five staggered fruit-tree rows, a central harvest path, wildflower understory, a small cider-press shed pad and a timber picnic pergola on the social edge.',
  groundDescription: 'Mixed orchard grass and wildflower understory, warm gravel, weathered timber, red-green apple accents and muted autumn foliage sampled from Heritage Apple Orchard v0.',
  criticalConstraints: 'Tree rows adapt by adding or removing whole regularly spaced trees; never scale one tree or shed to fill the site. Keep harvest path and row-end turning space clear. The shed is a small park kit, not a large building.',
  canopyDescription: 'Low broad fruit crowns vary subtly in size and colour while retaining productive row spacing.', plantingStructure: 'orchard_heritage_v0',
  guides: [
    { kind: 'line', x: 0.50, y: 0.52, width: 0.84, height: 0, color: '#b4a17b', strokeWidthM: 2.8 },
    ...[0.22,0.36,0.50,0.64,0.78].map((y): ParkGroundGuide => ({ kind: 'line', x: 0.50, y, width: 0.78, height: 0, color: '#607344', strokeWidthM: 4.0 })),
    { kind: 'rectangle', x: 0.76, y: 0.82, width: 0.13, height: 0.14, widthM: 6, heightM: 5, color: '#775439', strokeColor: '#4c3627', strokeWidthM: 0.3 },
    { kind: 'line', x: 0.30, y: 0.83, width: 0.22, height: 0, color: '#8b6949', strokeWidthM: 4.0 },
  ],
  guideLegend: ['the PALE central line is the clear harvest spine', 'five GREEN bands are productive tree rows with meadow understory', 'the SMALL BROWN pad and bar are the cider-press shed and picnic pergola social edge'], includeCentralPlaza: false,
  renderSummary: 'heritage apple orchard with adaptive whole-tree rows, meadow understory, clear harvest spine, cider-press shed and picnic pergola', isPilot: true,
};

PROFILES.bioswale_rain_garden = {
  id: 'bioswale-streetside-lego-v1', version: 1,
  programDescription: 'A linear streetside bioswale composed of three hydraulically connected planting cells, repeated curb-cut inlets, two stone check dams, a dry parallel sidewalk and two narrow accessible crossings.',
  groundDescription: 'Dark moist soil, layered sedge and flowering-rush planting, river cobble, rusted-steel inlet grates, pale concrete curb and asphalt edge sampled from Streetside Bioswale v0.',
  criticalConstraints: 'Maintain downhill hydraulic continuity through all three cells. Curb cuts face the street edge, overflow remains clear and every crossing spans rather than fills the swale. No decorative pond, buildings or people.',
  canopyDescription: 'Small multi-stem trees appear only in wider dry shoulders; wet cells remain low and legible.', plantingStructure: 'bioswale_streetside_v0',
  guides: [
    { kind: 'polyline', x: 0.50, y: 0.56, width: 1, height: 1, points: [[0.03,0.58],[0.22,0.46],[0.42,0.60],[0.62,0.45],[0.82,0.58],[0.97,0.48]], color: '#526b46', strokeColor: '#6f7f58', strokeWidthM: 6.0 },
    { kind: 'polyline', x: 0.50, y: 0.20, width: 1, height: 1, points: [[0.02,0.20],[0.98,0.20]], color: '#c0b9aa', strokeWidthM: 2.4 },
    { kind: 'line', x: 0.34, y: 0.50, width: 0, height: 0, widthM: 10, color: '#8d795d', strokeWidthM: 1.4, rotationDeg: 90, orientationPolicy: 'fixed' },
    { kind: 'line', x: 0.70, y: 0.50, width: 0, height: 0, widthM: 10, color: '#8d795d', strokeWidthM: 1.4, rotationDeg: 90, orientationPolicy: 'fixed' },
  ],
  guideLegend: ['the GREEN sinuous band is the connected three-cell treatment swale', 'the PALE parallel line is the dry sidewalk', 'the two BROWN crossbars are narrow accessible bridges/check-dam points'], includeCentralPlaza: false,
  renderSummary: 'streetside bioswale with three connected treatment cells, curb-cut inlets, check dams, dry parallel walk and accessible crossings', isPilot: true,
};

PROFILES.sculpture_garden = {
  id: 'sculpture-museum-court-lego-v1', version: 1,
  programDescription: 'A formal museum sculpture court with a branching white-gravel gallery route, five separate display plinths, restrained geometric planting islands and a varied set of abstract metal and stone sculptures sized to pedestrian viewing distance.',
  groundDescription: 'Complex white-grey gravel, dark weathering steel, pale limestone, bronze-black metal, warm timber benches and silvery-green ornamental planting sampled from Museum Sculpture Court v0.',
  criticalConstraints: 'Keep clear 360-degree viewing space around every sculpture and preserve distinct objects rather than one oversized monument. Gallery buildings and people remain outside the park model.',
  canopyDescription: 'A few narrow specimen trees and low ornamental grasses define rooms without hiding sculpture silhouettes.', plantingStructure: 'sculpture_museum_court_v0',
  guides: [
    { kind: 'path_loop', x: 0.50, y: 0.52, width: 0.84, height: 0.72, color: '#d3d0c8', strokeWidthM: 3.2 },
    ...[[0.22,0.30],[0.48,0.28],[0.74,0.34],[0.34,0.68],[0.68,0.70]].map(([x,y], index): ParkGroundGuide => ({ kind: 'rectangle', x, y, width: 0.08, height: 0.08, widthM: index === 0 ? 4 : 3, heightM: index === 0 ? 4 : 3, color: '#918779', strokeColor: '#625d56', strokeWidthM: 0.25, orientationPolicy: 'flexible' })),
  ],
  guideLegend: ['the WHITE-GREY loop is the connected gallery route', 'five STONE squares are separate sculpture plinths with complete viewing clearances'], includeCentralPlaza: false,
  renderSummary: 'museum sculpture court with branching gravel route, five curated abstract works, separate viewing rooms and restrained planting', isPilot: true,
};

PROFILES.labyrinth_meditation = {
  id: 'labyrinth-classical-lego-v1', version: 1,
  programDescription: 'A classical Chartres-inspired walking labyrinth formed by seven concentric stone-and-turf rings with one legible winding entrance route, a central stone bench and a clipped formal hedge frame.',
  groundDescription: 'Variegated pale limestone set into dense green turf, honey-grey stone bench, dark clipped boxwood and fine gravel thresholds sampled from Classical Stone Labyrinth v0.',
  criticalConstraints: 'The rings must read as one continuous walking labyrinth, not a target or decorative circles. Preserve a clear entrance, accessible path width and quiet center. No people or surrounding buildings.',
  canopyDescription: 'Clipped hedge and sparse corner trees frame but never shade or obstruct the labyrinth.', plantingStructure: 'labyrinth_classical_v0',
  guides: [
    ...[0.82,0.72,0.62,0.52,0.42,0.32,0.22].map((size, index): ParkGroundGuide => ({ kind: 'ellipse', x: 0.50, y: 0.50, width: size, height: size, widthM: 18 - index * 2, heightM: 18 - index * 2, color: index % 2 === 0 ? '#d0c9b8' : '#62804f', strokeColor: '#a49c89', strokeWidthM: 0.65, atomicGroup: 'labyrinth', orientationPolicy: 'fixed' })),
    { kind: 'line', x: 0.50, y: 0.86, width: 0, height: 0, widthM: 5, color: '#d0c9b8', strokeWidthM: 1.2, rotationDeg: 90, orientationPolicy: 'fixed', atomicGroup: 'labyrinth' },
  ],
  guideLegend: ['the alternating STONE and TURF rings form one continuous seven-circuit labyrinth with a single southern entrance', 'the center remains a quiet destination with one stone bench'], includeCentralPlaza: false,
  renderSummary: 'classical seven-circuit stone-and-turf labyrinth with clear entrance, central stone bench and clipped hedge frame', isPilot: true,
};

PROFILES.outdoor_ice_rink = {
  id: 'ice-rink-multipurpose-lego-v1', version: 1,
  programDescription: 'A year-round multipurpose recreation pad preserving one complete 60 by 30 metre rink envelope, permanent transparent boards, four lighting standards, controlled gates and seasonal ice-versus-hardcourt markings without adding a recreation building.',
  groundDescription: 'Cool mottled ice-white or pale sealed-concrete playing surface, muted blue and red linework, dark wet asphalt apron, brushed galvanized board frames and warm timber benches sampled from Multipurpose Pad v3.',
  criticalConstraints: 'Keep one complete rectangular pad inside its permanent boards. The seasonal state changes only the playing finish and markings; boards, gates, clear apron and lights stay fixed. Never overlap duplicate pads, stretch the rink, add people or generate the recreation-hub building visible in the reference.',
  canopyDescription: 'Sparse winter-tolerant edge planting only; no canopy enters the boards, light throw or gate clearances.', plantingStructure: 'ice_rink_multipurpose_v3',
  guides: [
    { kind: 'rounded_rectangle', x: 0.50, y: 0.50, width: 0.86, height: 0.72, widthM: 60, heightM: 30, color: '#d8e5e8', strokeColor: '#87989a', strokeWidthM: 0.18, atomicGroup: 'rink', orientationPolicy: 'flexible' },
    { kind: 'line', x: 0.50, y: 0.50, width: 0, height: 0, widthM: 30, color: '#a34b4c', strokeWidthM: 0.16, rotationDeg: 90, atomicGroup: 'rink', orientationPolicy: 'fixed' },
    { kind: 'line', x: 0.36, y: 0.50, width: 0, height: 0, widthM: 30, color: '#506d9a', strokeWidthM: 0.13, rotationDeg: 90, atomicGroup: 'rink', orientationPolicy: 'fixed' },
    { kind: 'line', x: 0.64, y: 0.50, width: 0, height: 0, widthM: 30, color: '#506d9a', strokeWidthM: 0.13, rotationDeg: 90, atomicGroup: 'rink', orientationPolicy: 'fixed' },
  ],
  guideLegend: ['the PALE 60 x 30 metre rounded rectangle is one complete convertible rink pad', 'the RED and BLUE cross-lines are seasonal rink markings contained inside the permanent boards'], includeCentralPlaza: false,
  renderSummary: 'year-round multipurpose rink pad with one complete board enclosure, controlled gates, seasonal linework and four permanent lights', isPilot: true,
};

PROFILES.kayak_launch_dock = {
  id: 'kayak-river-launch-lego-v1', version: 1,
  programDescription: 'A compact river launch organized as one accessible upland staging terrace, stacked kayak racks, a sloped transfer launch and one floating dock parallel to the active river edge, all connected to the riverside trail.',
  groundDescription: 'Blue-grey moving water, dark riparian cobble, weathered composite dock boards, galvanized rails, warm gravel and layered green-gold bank planting sampled from River Launch v0.',
  criticalConstraints: 'Preserve the dry-to-wet sequence: trail, staging, rack, accessible slide and floating dock. The dock remains at the water edge and the rack remains on dry land. No boats or people are required; the small kiosk in the reference is omitted as a separately rendered building.',
  canopyDescription: 'Layered riparian shrubs and a few irregular trees frame the upland bank while leaving the launch route and river sightline open.', plantingStructure: 'kayak_river_launch_v0',
  guides: [
    { kind: 'polyline', x: 0.50, y: 0.80, width: 1, height: 1, points: [[0.02,0.74],[0.25,0.78],[0.52,0.72],[0.76,0.80],[0.98,0.74]], color: '#57777a', strokeColor: '#667b61', strokeWidthM: 12 },
    { kind: 'rectangle', x: 0.62, y: 0.72, width: 0.34, height: 0.10, widthM: 26, heightM: 4, color: '#8c7760', strokeColor: '#5d5247', strokeWidthM: 0.2, atomicGroup: 'launch', orientationPolicy: 'orthogonal' },
    { kind: 'line', x: 0.43, y: 0.62, width: 0, height: 0, widthM: 12, color: '#9a8a72', strokeWidthM: 2.4, rotationDeg: 58, atomicGroup: 'launch', orientationPolicy: 'fixed' },
    { kind: 'rectangle', x: 0.24, y: 0.36, width: 0.15, height: 0.16, widthM: 9, heightM: 6, color: '#75624c', strokeColor: '#4d443a', strokeWidthM: 0.2, orientationPolicy: 'flexible' },
    { kind: 'polyline', x: 0.50, y: 0.25, width: 1, height: 1, points: [[0.02,0.28],[0.30,0.22],[0.62,0.26],[0.98,0.20]], color: '#b6a889', strokeWidthM: 3.2 },
  ],
  guideLegend: ['the BLUE-GREEN lower band is the active river edge', 'the BROWN rectangle and sloped connector are the floating dock and accessible transfer launch', 'the small upland pad is the stacked rack and staging zone'], includeCentralPlaza: false,
  renderSummary: 'river kayak launch with dry staging and racks, accessible transfer slide, floating dock and connected riverside trail', isPilot: true,
};

PROFILES.tidal_marsh_boardwalk = {
  id: 'tidal-marsh-cordgrass-lego-v1', version: 1,
  programDescription: 'A cordgrass salt-marsh preserve with one elevated timber boardwalk running from a modest dry trailhead to a single hexagonal overlook beside a sinuous tidal creek.',
  groundDescription: 'Variegated Spartina cordgrass in olive, straw and deep green, dark reflective tidal mud and water, weathered grey-brown timber and pale gravel sampled from Cordgrass Salt-Marsh Boardwalk v0.',
  criticalConstraints: 'Keep the boardwalk continuous and elevated above marsh vegetation. Preserve one overlook and one tidal creek; do not turn the marsh into a lake, scatter generic paths, add parking across the habitat, or render the surrounding buildings and people.',
  canopyDescription: 'No trees in the salt marsh. Low dense cordgrass remains the dominant vertical texture with slightly taller dry-edge shrubs only at the trailhead.', plantingStructure: 'tidal_marsh_cordgrass_v0',
  guides: [
    { kind: 'polyline', x: 0.50, y: 0.52, width: 1, height: 1, points: [[0.05,0.86],[0.20,0.72],[0.34,0.65],[0.48,0.48],[0.66,0.44],[0.82,0.28]], color: '#887257', strokeColor: '#5e5142', strokeWidthM: 2.6, orientationPolicy: 'fixed' },
    { kind: 'ellipse', x: 0.84, y: 0.27, width: 0.13, height: 0.17, widthM: 12, heightM: 12, color: '#8c765b', strokeColor: '#5e5142', strokeWidthM: 0.3, orientationPolicy: 'fixed' },
    { kind: 'polyline', x: 0.58, y: 0.55, width: 1, height: 1, points: [[0.10,0.30],[0.28,0.40],[0.42,0.34],[0.58,0.56],[0.74,0.60],[0.94,0.78]], color: '#516f73', strokeWidthM: 7.0 },
    { kind: 'rectangle', x: 0.10, y: 0.88, width: 0.09, height: 0.10, widthM: 8, heightM: 5, color: '#94816a', strokeColor: '#655847', strokeWidthM: 0.2, orientationPolicy: 'flexible' },
  ],
  guideLegend: ['the WARM-TIMBER route is one exact elevated boardwalk ending at one overlook', 'the BLUE-GREEN route is the winding tidal creek through continuous cordgrass habitat'], includeCentralPlaza: false,
  renderSummary: 'cordgrass salt marsh with one elevated boardwalk, one hexagonal overlook, a tidal creek and restrained dry trailhead', isPilot: true,
};

PROFILES.outdoor_cinema_lawn = {
  id: 'cinema-lawn-projection-lego-v1', version: 1,
  programDescription: 'A permanent park-lawn cinema with one fixed screen at the focal end, a clear gently sloped audience lawn, a rear projection/storage booth and a perimeter circulation loop that preserves sightlines.',
  groundDescription: 'Mottled deep-green cinema turf, warm compacted gravel, pale stone screen plinth, dark steel frame and weathered timber sampled from Park-Lawn Projection v1.',
  criticalConstraints: 'The screen, lawn centreline and booth must align. Keep the full sightline cone empty of trees, kiosks, furniture and people. The screen is park infrastructure; surrounding buildings and temporary audiences are not part of the LEGO model.',
  canopyDescription: 'Mature canopy frames the two long edges and rear corners only, never the screen face or audience sightline cone.', plantingStructure: 'cinema_lawn_projection_v1',
  guides: [
    { kind: 'ellipse', x: 0.50, y: 0.55, width: 0.72, height: 0.60, widthM: 58, heightM: 34, color: '#66834f', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.50, y: 0.18, width: 0.22, height: 0.06, widthM: 16, heightM: 3, color: '#a8a397', strokeColor: '#4d5453', strokeWidthM: 0.25, atomicGroup: 'cinema', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.50, y: 0.87, width: 0.12, height: 0.10, widthM: 8, heightM: 6, color: '#756354', strokeColor: '#4e4339', strokeWidthM: 0.2, atomicGroup: 'cinema', orientationPolicy: 'orthogonal' },
    { kind: 'path_loop', x: 0.50, y: 0.53, width: 0.88, height: 0.82, color: '#b4a586', strokeWidthM: 2.8 },
  ],
  guideLegend: ['the GREEN ellipse is the unobstructed audience sightline lawn', 'the PALE focal bar and rear BROWN pad are the fixed screen and aligned projection booth', 'the outer PALE loop carries circulation outside the viewing field'], includeCentralPlaza: false,
  renderSummary: 'permanent park-lawn cinema with aligned screen and booth, unobstructed audience lawn and edge-only circulation', isPilot: true,
};

PROFILES.food_truck_plaza = {
  id: 'food-truck-permanent-lego-v1', version: 1,
  programDescription: 'A purpose-built food-truck park with eight whole utility-served truck bays arranged along two edges in an L, a central communal picnic court, perimeter planters and a compact service-kiosk pad.',
  groundDescription: 'Variegated stamped concrete, charcoal asphalt service strips, colourful painted truck panels, black steel, honey timber tables and ornamental grasses sampled from Permanent Food-Truck Park v1.',
  criticalConstraints: 'Add or remove whole truck bays to fit the polygon; never stretch a truck. Keep the central pedestrian court and one clear service aisle. Trucks are reusable park props, while surrounding mixed-use buildings and people are excluded.',
  canopyDescription: 'Small honey-locust trees and grasses stay in edge planters, clear of utility bays, truck doors, service aisle and the picnic court.', plantingStructure: 'food_truck_permanent_v1',
  guides: [
    ...[0.18,0.38,0.58,0.78].map((x, index): ParkGroundGuide => ({ kind: 'rectangle', x, y: 0.14, width: 0.14, height: 0.10, widthM: 7, heightM: 3, color: ['#9a3f31','#c69d28','#577c6b','#ca7040'][index], strokeColor: '#3e4543', strokeWidthM: 0.18, orientationPolicy: 'orthogonal' })),
    ...[0.30,0.48,0.66,0.84].map((y, index): ParkGroundGuide => ({ kind: 'rectangle', x: 0.10, y, width: 0.10, height: 0.14, widthM: 7, heightM: 3, color: ['#3f5360','#bb623b','#73783d','#bb7441'][index], strokeColor: '#3e4543', strokeWidthM: 0.18, rotationDeg: 90, orientationPolicy: 'orthogonal' })),
    { kind: 'rounded_rectangle', x: 0.57, y: 0.58, width: 0.58, height: 0.54, widthM: 28, heightM: 20, color: '#aaa49a', strokeColor: '#81796f', strokeWidthM: 0.2, orientationPolicy: 'flexible' },
    { kind: 'rectangle', x: 0.86, y: 0.83, width: 0.12, height: 0.12, widthM: 7, heightM: 5, color: '#75604d', strokeColor: '#483d35', strokeWidthM: 0.2, orientationPolicy: 'flexible' },
  ],
  guideLegend: ['the eight coloured edge rectangles are whole utility-served truck bays arranged in an L', 'the central STAMPED-CONCRETE court holds communal picnic tables and clear pedestrian circulation', 'the small corner pad is service infrastructure, not a large building'], includeCentralPlaza: false,
  renderSummary: 'permanent food-truck park with adaptive whole truck bays, central picnic court, service aisle, string-light grid and edge planters', isPilot: true,
};

PROFILES.festival_event_lawn = {
  id: 'great-lawn-lego-v1', version: 1,
  programDescription: 'A classic metropolitan great lawn: one broad uninterrupted grass field with gentle landform, a continuous perimeter walk, a few edge-only utility hookups and no permanently baked festival stage, tents or crowd.',
  groundDescription: 'Complex cool and warm turf bands, subtle mowing variation, compacted tan path, dark utility covers and layered park-edge planting sampled from Great Lawn v2.',
  criticalConstraints: 'Keep at least 75 percent of the interior as one contiguous flexible lawn. Temporary event equipment and people are absent in the everyday state. Paths, trees and utilities remain at the edge and must not subdivide the field.',
  canopyDescription: 'Mature irregular tree groups form an outer frame with occasional openings; the entire central event field stays open and sunlit.', plantingStructure: 'great_lawn_v2',
  guides: [
    { kind: 'rounded_rectangle', x: 0.50, y: 0.50, width: 0.78, height: 0.68, color: '#68864e', fitPolicy: 'clip' },
    { kind: 'path_loop', x: 0.50, y: 0.50, width: 0.92, height: 0.86, color: '#b4a57f', strokeWidthM: 3.4 },
    { kind: 'rectangle', x: 0.12, y: 0.22, width: 0.05, height: 0.06, widthM: 5, heightM: 4, color: '#6c6962', orientationPolicy: 'flexible' },
    { kind: 'rectangle', x: 0.88, y: 0.78, width: 0.05, height: 0.06, widthM: 5, heightM: 4, color: '#6c6962', orientationPolicy: 'flexible' },
  ],
  guideLegend: ['the LARGE GREEN field remains one unbroken flexible great lawn', 'the PALE loop and two tiny DARK pads are perimeter circulation and event hookups only'], includeCentralPlaza: false,
  renderSummary: 'everyday-state great lawn with contiguous turf, gentle landform, perimeter walk, edge utilities and no temporary event clutter', isPilot: true,
};

PROFILES.campus_central_quad = {
  id: 'campus-meadow-quad-lego-v1', version: 1,
  programDescription: 'A naturalized campus quad organized by four gateway-to-gateway desire lines crossing at a central social node, with native meadow rooms, boulder seating and irregular shade-tree groups; academic buildings remain separate LEGO families.',
  groundDescription: 'Tawny-green native meadow, small wildflower flecks, warm decomposed granite, grey glacial boulders and white-barked trees sampled from Naturalized Meadow Quad v0.',
  criticalConstraints: 'Every desire line must connect opposite campus gateways and remain continuous. Keep the crossing node usable and the meadow in large contiguous rooms. Do not generate academic buildings, people or a generic mown-lawn carpet.',
  canopyDescription: 'Irregular birch and shade-tree groups align with meadow rooms, leaving all desire-line intersections and building approaches open.', plantingStructure: 'campus_meadow_quad_v0',
  guides: [
    { kind: 'polyline', x: 0.50, y: 0.50, width: 1, height: 1, points: [[0.02,0.50],[0.34,0.50],[0.50,0.50],[0.68,0.50],[0.98,0.50]], color: '#b7a785', strokeWidthM: 3.4 },
    { kind: 'polyline', x: 0.50, y: 0.50, width: 1, height: 1, points: [[0.50,0.02],[0.50,0.34],[0.50,0.50],[0.50,0.68],[0.50,0.98]], color: '#b7a785', strokeWidthM: 3.4 },
    { kind: 'polyline', x: 0.50, y: 0.50, width: 1, height: 1, points: [[0.04,0.08],[0.34,0.36],[0.50,0.50],[0.72,0.72],[0.96,0.92]], color: '#b7a785', strokeWidthM: 2.8 },
    { kind: 'ellipse', x: 0.50, y: 0.50, width: 0.13, height: 0.16, widthM: 12, heightM: 12, color: '#aea38c', orientationPolicy: 'fixed' },
    ...[[0.27,0.26],[0.73,0.27],[0.28,0.74],[0.73,0.72]].map(([x,y], index): ParkGroundGuide => ({ kind: 'ellipse', x, y, width: 0.30, height: 0.26, color: ['#7e8050','#8a8350','#737b4a','#8b774a'][index], fitPolicy: 'clip' })),
  ],
  guideLegend: ['the PALE cross and diagonal routes are gateway-to-gateway desire lines meeting at one central social node', 'the four GREEN-GOLD rooms are contiguous naturalized meadow, not leftover lawn'], includeCentralPlaza: false,
  renderSummary: 'naturalized campus meadow quad with exact desire-line crossings, central social node, boulder seating and building-free ecological rooms', isPilot: true,
};

PROFILES.urban_beach = {
  id: 'urban-beach-family-lego-v1', version: 1,
  programDescription: 'A family urban beach combining one broad sand-play field, a shallow splash zone, an accessible curving boardwalk, three shade-sail bays, a compact lifeguard chair and picnic edge.',
  groundDescription: 'Variegated pale sand, wet sand transition, warm composite decking, pale grey splash paving, turquoise water-play accents and tan shade fabric sampled from Family Splash Beach v2.',
  criticalConstraints: 'Preserve an accessible dry route between entry, splash zone, shade and sand. Keep the water-play zone shallow and separate from open water. No people, beach bar or surrounding buildings; the lifeguard element is a small park prop only.',
  canopyDescription: 'Shade comes from fabric sails and a few perimeter trees; no tree trunk enters the sand-play or splash safety clearances.', plantingStructure: 'urban_beach_family_v2',
  guides: [
    { kind: 'ellipse', x: 0.34, y: 0.56, width: 0.56, height: 0.62, widthM: 38, heightM: 28, color: '#d5c39a', orientationPolicy: 'orthogonal' },
    { kind: 'ellipse', x: 0.70, y: 0.48, width: 0.28, height: 0.34, widthM: 18, heightM: 14, color: '#83b7b7', strokeColor: '#c8c5b9', strokeWidthM: 0.2, orientationPolicy: 'orthogonal' },
    { kind: 'polyline', x: 0.50, y: 0.58, width: 1, height: 1, points: [[0.04,0.84],[0.24,0.74],[0.48,0.66],[0.66,0.64],[0.92,0.76]], color: '#957653', strokeWidthM: 3.4 },
    { kind: 'line', x: 0.30, y: 0.28, width: 0, height: 0, widthM: 14, color: '#b49a72', strokeWidthM: 5.5, rotationDeg: -10, atomicGroup: 'shade-sails', orientationPolicy: 'fixed' },
    { kind: 'line', x: 0.48, y: 0.24, width: 0, height: 0, widthM: 14, color: '#b49a72', strokeWidthM: 5.5, rotationDeg: 8, atomicGroup: 'shade-sails', orientationPolicy: 'fixed' },
    { kind: 'line', x: 0.66, y: 0.28, width: 0, height: 0, widthM: 14, color: '#b49a72', strokeWidthM: 5.5, rotationDeg: -8, atomicGroup: 'shade-sails', orientationPolicy: 'fixed' },
  ],
  guideLegend: ['the broad TAN field is family sand play and the BLUE-GREEN field is a separate shallow splash zone', 'the BROWN route is the continuous accessible boardwalk', 'three upper TAN bars locate complete shade-sail bays'], includeCentralPlaza: false,
  renderSummary: 'family urban beach with sand play, shallow splash zone, continuous accessible boardwalk, three shade sails and lifeguard kit', isPilot: true,
};

PROFILES.velodrome_cycling_track = {
  id: 'velodrome-open-air-lego-v1', version: 1,
  programDescription: 'An open-air competition velodrome preserving one complete approximately 250 metre banked oval around a grass infield, with a blue safety band, home-straight bleachers, timing tower and entry apron.',
  groundDescription: 'Pale weathered concrete track, powder-blue cote d azur, crisp black and red measurement lines, deep green infield, light concrete bleachers and dark steel railings sampled from Open-Air Velodrome v0.',
  criticalConstraints: 'Never stretch, clip or duplicate the track. Preserve a continuous closed circuit, clear infield, banked bends and aligned home-straight timing infrastructure. Indoor arena roofs and surrounding buildings are separate and excluded.',
  canopyDescription: 'Low perimeter planting and a few entry trees only; no canopy crosses the track, infield or rider sightlines.', plantingStructure: 'velodrome_open_air_v0',
  guides: [
    { kind: 'track', x: 0.50, y: 0.50, width: 0.88, height: 0.74, widthM: 125, heightM: 72, color: '#c9b992', strokeColor: '#6ca0b2', strokeWidthM: 8.0, atomicGroup: 'velodrome', orientationPolicy: 'flexible' },
    { kind: 'ellipse', x: 0.50, y: 0.50, width: 0.56, height: 0.42, widthM: 78, heightM: 42, color: '#62824e', atomicGroup: 'velodrome', orientationPolicy: 'flexible' },
    { kind: 'rectangle', x: 0.50, y: 0.91, width: 0.48, height: 0.09, widthM: 60, heightM: 8, color: '#a7a49d', strokeColor: '#6c6d6b', strokeWidthM: 0.25, orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.82, y: 0.82, width: 0.07, height: 0.08, widthM: 7, heightM: 6, color: '#77746e', strokeColor: '#4f514f', strokeWidthM: 0.2, orientationPolicy: 'flexible' },
  ],
  guideLegend: ['the PALE closed oval with BLUE inner band is one complete banked cycling circuit', 'the GREEN infield stays clear', 'the lower PALE bar and small DARK pad are open bleachers and timing tower'], includeCentralPlaza: false,
  renderSummary: 'open-air velodrome with one continuous banked track, blue safety band, clear grass infield, home-straight bleachers and timing tower', isPilot: true,
};

PROFILES.mountain_bike_park = {
  id: 'mtb-skills-dirt-lego-v1', version: 1,
  programDescription: 'A neighbourhood mountain-bike skills park combining one connected pump loop, a directional three-jump line, a parallel beginner return, rock-and-log technical features and a small open shelter pad.',
  groundDescription: 'Compacted ochre dirt, pale concrete pump features, dark tire-worn lines, meadow-green infill, grey boulders and weathered logs sampled from Skills and Dirt Park v2.',
  criticalConstraints: 'Every riding line must have a clear entry, sequence and return without crossing another landing. Add or remove whole jumps and technical modules rather than stretching them. Earthwork sits on the flattened park polygon and must not rely on Google terrain. No riders, dogs or surrounding buildings.',
  canopyDescription: 'Low meadow and sparse edge trees preserve clear sightlines between starts, landings and returns.', plantingStructure: 'mtb_skills_dirt_v2',
  guides: [
    { kind: 'track', x: 0.34, y: 0.50, width: 0.48, height: 0.62, widthM: 48, heightM: 32, color: '#9b8563', strokeColor: '#6f5e48', strokeWidthM: 3.0, atomicGroup: 'pump-loop', orientationPolicy: 'flexible' },
    { kind: 'polyline', x: 0.72, y: 0.44, width: 1, height: 1, points: [[0.56,0.22],[0.66,0.34],[0.73,0.47],[0.80,0.60],[0.88,0.76]], color: '#98744e', strokeColor: '#66523d', strokeWidthM: 4.0 },
    { kind: 'polyline', x: 0.66, y: 0.60, width: 1, height: 1, points: [[0.88,0.82],[0.74,0.82],[0.60,0.75],[0.54,0.66]], color: '#b09872', strokeWidthM: 2.6 },
    { kind: 'rectangle', x: 0.73, y: 0.26, width: 0.08, height: 0.08, widthM: 6, heightM: 5, color: '#78604a', orientationPolicy: 'flexible' },
    { kind: 'rectangle', x: 0.77, y: 0.50, width: 0.10, height: 0.08, widthM: 8, heightM: 5, color: '#77736b', orientationPolicy: 'flexible' },
  ],
  guideLegend: ['the closed OCHRE loop is one connected pump circuit', 'the DARK-DIRT diagonal is a directional jump line with complete takeoff and landing modules', 'the PALE return reconnects the riding sequence without crossing landings'], includeCentralPlaza: false,
  renderSummary: 'skills and dirt bike park with connected pump loop, three-jump progression, beginner return, technical features and small shelter pad', isPilot: true,
};

PROFILES.regional_park_v0 = {
  id: 'regional-english-landscape-lego-v1', version: 1,
  programDescription: 'An English landscape park organized around one naturalistic pond, a serpentine circuit, a small romantic bridge, broad rolling meadow rooms and irregular specimen-tree groups. The number of meadow rooms and secondary path branches responds to site area without enlarging any single feature out of scale.',
  groundDescription: 'Layered emerald and olive turf, darker pond-edge reeds, pale warm gravel, weathered grey stone and black-green iron sampled from Regional Park v0.',
  criticalConstraints: 'Keep one legible pond and one continuous circuit. On oversized sites add whole meadow rooms, tree groups and secondary loops; never inflate the pond, bridge or path width. Buildings, roads and people visible beyond the reference park are excluded.',
  canopyDescription: 'Irregular mature deciduous groups frame long meadow views, with isolated specimen trees and a denser woodland edge; the pond foreground remains visually open.', plantingStructure: 'regional_english_landscape_v0',
  guides: [
    { kind: 'ellipse', x: 0.42, y: 0.60, width: 0.28, height: 0.24, color: '#667f75', strokeColor: '#657650', strokeWidthM: 4, fitPolicy: 'clip' },
    { kind: 'path_loop', x: 0.48, y: 0.53, width: 0.78, height: 0.68, color: '#b9aa87', strokeWidthM: 3.2, fitPolicy: 'clip' },
    { kind: 'polyline', x: 0.50, y: 0.50, width: 1, height: 1, points: [[0.06,0.72],[0.22,0.62],[0.40,0.54],[0.58,0.42],[0.76,0.36],[0.94,0.25]], color: '#b9aa87', strokeWidthM: 2.8 },
    { kind: 'line', x: 0.42, y: 0.52, width: 0, height: 0, widthM: 14, color: '#7d7567', strokeWidthM: 2.4, rotationDeg: -12, orientationPolicy: 'fixed' },
  ],
  guideLegend: ['BLUE-GREEN oval is the single naturalistic pond', 'PALE loops are a connected serpentine walking network', 'short GREY crossing is one human-scale romantic bridge'], includeCentralPlaza: false,
  renderSummary: 'English regional landscape with pond, serpentine gravel circuit, romantic bridge, rolling meadow rooms and irregular specimen trees', isPilot: true,
};

PROFILES.beer_garden_v0 = {
  id: 'beer-garden-munich-lego-v1', version: 1,
  programDescription: 'A Munich-style beer garden with a pale gravel dining floor, parallel two-sided trestle-table rows, a regular mature chestnut canopy, clipped perimeter hedge, small self-service kiosk and overhead Bavarian pennant strings.',
  groundDescription: 'Mottled pale compacted gravel, honey and weathered timber, dark green steel, dense chestnut foliage and clipped hedge green sampled from Beer Garden v0.',
  criticalConstraints: 'Dining rows remain parallel and preserve 1.5 metre service aisles. Add or remove complete table-and-bench modules according to site size; never stretch furniture. Keep the kiosk small and park-serving. Render no patrons or surrounding buildings.',
  canopyDescription: 'A regular chestnut grid shades the dining field while trunks stay between table rows and out of the central service aisle.', plantingStructure: 'beer_garden_munich_v0',
  guides: [
    { kind: 'rounded_rectangle', x: 0.50, y: 0.50, width: 0.84, height: 0.80, color: '#c1b69a', strokeColor: '#526443', strokeWidthM: 1.1, fitPolicy: 'clip' },
    { kind: 'rectangle', x: 0.50, y: 0.12, width: 0.18, height: 0.12, widthM: 6, heightM: 4, color: '#7f5b3c', strokeColor: '#4d392a', strokeWidthM: 0.2, orientationPolicy: 'orthogonal' },
  ],
  guideLegend: ['PALE rectangle is the gravel dining room', 'small BROWN pad is the self-service kiosk', '3D assembly calculates whole trestle rows and chestnut bays from available width'], includeCentralPlaza: false,
  renderSummary: 'Munich beer garden with scalable whole trestle-table rows, chestnut canopy, hedge frame, service aisle, kiosk and pennant strings', isPilot: true,
};

PROFILES.sunken_plaza_v0 = {
  id: 'sunken-courtyard-lego-v1', version: 1,
  programDescription: 'A compact stone sunken court reached by broad shallow steps from three sides, focused on one low bronze fountain and framed at the rim by clipped hedges. Café frontage remains a clear edge reservation for separately rendered buildings.',
  groundDescription: 'Warm limestone flags with fine tonal variation, pale stone risers, dark bronze, restrained water blue and clipped boxwood sampled from Sunken Plaza v0.',
  criticalConstraints: 'Keep the lower court central and visibly below the rim, with three usable step approaches and one accessible side route. The central fountain must not block circulation. Do not generate surrounding mixed-use blocks, cafés, awnings or people.',
  canopyDescription: 'No canopy in the lower court; low clipped hedge only at the upper rim.', plantingStructure: 'sunken_courtyard_v0',
  guides: [
    { kind: 'rounded_rectangle', x: 0.50, y: 0.54, width: 0.62, height: 0.58, color: '#c9c0ae', strokeColor: '#9f9788', strokeWidthM: 5, fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.50, y: 0.54, width: 0.14, height: 0.14, widthM: 4.5, heightM: 4.5, color: '#718a8c', strokeColor: '#857f72', strokeWidthM: 0.45, orientationPolicy: 'fixed' },
    { kind: 'line', x: 0.50, y: 0.89, width: 0, height: 0, widthM: 12, color: '#b6ae9f', strokeWidthM: 5.0, orientationPolicy: 'fixed' },
  ],
  guideLegend: ['inner STONE court sits below the rim', 'BLUE centre is one low fountain', 'three sides become broad seat-steps while one edge remains an accessible clear route'], includeCentralPlaza: true,
  renderSummary: 'intimate three-sided sunken limestone courtyard with broad steps, clipped rim hedge and one low bronze fountain', isPilot: true,
};

PROFILES.stepped_terraced_plaza_v3 = {
  id: 'terraced-cascade-lego-v1', version: 1,
  programDescription: 'A Robson-style modernist civic terrace descending in broad concrete seat-steps beside a three-basin waterfall axis, heavy planted side terraces and a continuous accessible ramp wrapping one edge.',
  groundDescription: 'Variegated warm-grey concrete, charcoal joints, dark reflective basin water, weathered steel rails and layered deep-green conifers and maples sampled from Stepped Plaza v3.',
  criticalConstraints: 'Preserve a continuous high-to-low sequence, three catch basins and a non-stair accessible route. Add or remove complete terrace bands for site depth; never stretch riser height or place planting across the ramp. Surrounding civic buildings and people are separate.',
  canopyDescription: 'Dense tree and conifer planters occupy side terraces only, leaving the cascade, steps and accessible route legible.', plantingStructure: 'terraced_cascade_v3',
  guides: [
    { kind: 'axis', x: 0.50, y: 0.50, width: 0, height: 0, widthM: 62, color: '#73959a', strokeWidthM: 4.2, rotationDeg: 90, orientationPolicy: 'fixed' },
    { kind: 'polyline', x: 0.82, y: 0.50, width: 1, height: 1, points: [[0.84,0.08],[0.92,0.22],[0.88,0.40],[0.94,0.58],[0.88,0.76],[0.82,0.92]], color: '#aaa79f', strokeWidthM: 3.2 },
    { kind: 'rectangle', x: 0.50, y: 0.28, width: 0.12, height: 0.08, widthM: 12, heightM: 7, color: '#607f84', orientationPolicy: 'fixed' },
    { kind: 'rectangle', x: 0.50, y: 0.50, width: 0.12, height: 0.08, widthM: 12, heightM: 7, color: '#607f84', orientationPolicy: 'fixed' },
    { kind: 'rectangle', x: 0.50, y: 0.72, width: 0.12, height: 0.08, widthM: 12, heightM: 7, color: '#607f84', orientationPolicy: 'fixed' },
  ],
  guideLegend: ['central BLUE axis is a continuous three-basin cascade', 'GREY edge line is the accessible wrap ramp', '3D assembly derives whole seat-step bands from site depth'], includeCentralPlaza: true,
  renderSummary: 'modernist terraced plaza with broad seat-steps, three-basin waterfall, planted side terraces and accessible wrap ramp', isPilot: true,
};

PROFILES.market_square_v1 = {
  id: 'market-festival-lawn-lego-v1', version: 1,
  programDescription: 'A flat open festival lawn framed by a hard service loop, removable vendor pads, power bollards and shade-sail anchor points. The everyday model remains uncluttered and ready for temporary programming.',
  groundDescription: 'Subtly striped event turf, warm speckled gravel, pale service concrete, galvanized utility hardware and dark perimeter planting sampled from Market Square v1.',
  criticalConstraints: 'Keep one contiguous central lawn. Add or remove complete vendor pads and utility points with perimeter length; never subdivide the field or generate temporary tents, crowds or large buildings.',
  canopyDescription: 'Sparse edge trees and low planting only; the entire central lawn and emergency/service route remain clear.', plantingStructure: 'market_festival_lawn_v1',
  guides: [
    { kind: 'rounded_rectangle', x: 0.50, y: 0.49, width: 0.72, height: 0.66, color: '#68834c', fitPolicy: 'clip' },
    { kind: 'path_loop', x: 0.50, y: 0.49, width: 0.88, height: 0.82, color: '#b6a98b', strokeWidthM: 4.2, fitPolicy: 'clip' },
    { kind: 'rectangle', x: 0.18, y: 0.86, width: 0.10, height: 0.08, widthM: 7, heightM: 5, color: '#aaa398', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.82, y: 0.86, width: 0.10, height: 0.08, widthM: 7, heightM: 5, color: '#aaa398', orientationPolicy: 'orthogonal' },
  ],
  guideLegend: ['GREEN centre is one uninterrupted event lawn', 'TAN loop is the service and strolling route', 'small PALE pads are removable vendor hookups'], includeCentralPlaza: false,
  renderSummary: 'open festival lawn with service loop, scalable vendor hookups, power bollards, shade anchors and clear everyday state', isPilot: true,
};

PROFILES.promenade_boardwalk_v0 = {
  id: 'boardwalk-maritime-lego-v1', version: 1,
  programDescription: 'A linear maritime timber promenade with rope rail on the water side, regularly spaced nautical lamps, view benches, weathered bollards and a narrow band of coastal planting on the land side.',
  groundDescription: 'Variegated weathered timber boards, dark rope, blackened steel, salt-grey concrete and blue-green coastal planting sampled from Promenade v0.',
  criticalConstraints: 'Maintain one continuous accessible promenade and an unbroken water-side safety rail. Furniture repeats by complete bays as length grows; board width, rail height and bench size stay human-scaled. No boats, waterfront buildings or people.',
  canopyDescription: 'Low salt-tolerant grasses stay landward; no tree canopy obstructs the water view or accessible clear width.', plantingStructure: 'boardwalk_maritime_v0',
  guides: [
    { kind: 'polyline', x: 0.50, y: 0.48, width: 1, height: 1, points: [[0.03,0.54],[0.22,0.48],[0.42,0.52],[0.62,0.44],[0.82,0.48],[0.97,0.42]], color: '#876f55', strokeWidthM: 7.0 },
    { kind: 'rectangle', x: 0.72, y: 0.40, width: 0.10, height: 0.18, widthM: 10, heightM: 5, color: '#897259', orientationPolicy: 'fixed' },
  ],
  guideLegend: ['wide BROWN route is the continuous timber promenade', 'water side receives rope rail, lights and spaced view bays', 'small BROWN pad is a cantilevered lookout'], includeCentralPlaza: false,
  renderSummary: 'weathered maritime boardwalk with continuous rope rail, nautical lights, view benches, bollards, lookout and landward coastal planting', isPilot: true,
};

PROFILES.fountain_water_feature_v1 = {
  id: 'fountain-formal-pool-lego-v1', version: 1,
  programDescription: 'A long formal reflecting pool with polished granite coping, two symmetric rows of water jets, a clear ceremonial walk and clipped hedges and urns framing the long sides.',
  groundDescription: 'Dark blue-grey reflective water, charcoal and warm-grey granite, pale jet foam, clipped boxwood and off-white stone urns sampled from Fountain v1.',
  criticalConstraints: 'Keep the basin complete, level and centered. Jets stay symmetrically paired and coping remains continuous. Add or remove whole jet pairs for basin length; do not scale nozzles or render surrounding pavilions and people.',
  canopyDescription: 'Low clipped hedges and paired topiary punctuate the exterior only; no canopy crosses the reflecting pool.', plantingStructure: 'fountain_formal_pool_v1',
  guides: [
    { kind: 'rectangle', x: 0.50, y: 0.50, width: 0.64, height: 0.36, widthM: 36, heightM: 12, color: '#58767e', strokeColor: '#414746', strokeWidthM: 1.2, atomicGroup: 'formal-pool', orientationPolicy: 'flexible' },
    { kind: 'axis', x: 0.50, y: 0.50, width: 0, height: 0, widthM: 32, color: '#d4e1dc', strokeWidthM: 0.35, atomicGroup: 'formal-pool', orientationPolicy: 'flexible' },
  ],
  guideLegend: ['BLUE-GREY rectangle is one complete formal pool', 'PALE axis becomes symmetric paired water jets', 'dark continuous edge is polished granite coping'], includeCentralPlaza: true,
  renderSummary: 'formal reflecting pool with continuous granite coping, scalable paired jet rows, ceremonial walk, clipped hedges and classical urns', isPilot: true,
};

PROFILES.swimming_pool_complex_v0 = {
  id: 'natural-swimming-pond-lego-v1', version: 1,
  programDescription: 'A natural swimming landscape combining one rectilinear lap basin and pale sun deck inside a larger organic regeneration pond, with a short timber dock and planted biological filtration edge.',
  groundDescription: 'Layered turquoise and deep olive water, pale limestone deck, natural cobble, weathered timber and lush reed planting sampled from Swimming Pool Complex v0.',
  criticalConstraints: 'Preserve the visual and functional distinction between the clean geometric swimming basin and irregular planted pond. Keep one continuous dry deck and a clear entry. Do not add bathhouse buildings, furniture crowds or people.',
  canopyDescription: 'Willows and wetland planting frame the outer pond but remain outside the lap basin, deck and swimming entry clearances.', plantingStructure: 'natural_swimming_pond_v0',
  guides: [
    { kind: 'ellipse', x: 0.48, y: 0.53, width: 0.78, height: 0.70, color: '#56786e', strokeColor: '#657556', strokeWidthM: 5.0, fitPolicy: 'clip' },
    { kind: 'rectangle', x: 0.58, y: 0.54, width: 0.40, height: 0.28, widthM: 25, heightM: 12.5, color: '#65a0a3', strokeColor: '#d0c6af', strokeWidthM: 2.2, atomicGroup: 'swim-basin', orientationPolicy: 'flexible' },
    { kind: 'line', x: 0.26, y: 0.55, width: 0, height: 0, widthM: 10, color: '#8a7157', strokeWidthM: 2.2, rotationDeg: 10, orientationPolicy: 'fixed' },
  ],
  guideLegend: ['organic DARK water is the regeneration pond', 'TURQUOISE rectangle is the human-scale lap basin', 'PALE edge is the dry deck and short BROWN element is the dock'], includeCentralPlaza: false,
  renderSummary: 'natural swimming pond with geometric lap basin, pale sun deck, organic regeneration water, biological planting and timber dock', isPilot: true,
};

PROFILES.nature_preserve_v1 = {
  id: 'nature-preserve-prairie-lego-v1', version: 1,
  programDescription: 'A tallgrass prairie preserve structured by broad habitat blocks, one narrow mown trail loop, a modest timber observation deck and sparse Bur oak savanna at the perimeter.',
  groundDescription: 'Complex rust, straw, olive and deep-green prairie tones, pale mown grass, weathered timber and dark earth sampled from Nature Preserve v1.',
  criticalConstraints: 'Habitat remains dominant and contiguous. Trails are narrow and observation infrastructure modest. Add whole habitat drifts and trail loops to large sites; never carpet the preserve with lawn, plazas, furniture, people or buildings.',
  canopyDescription: 'Sparse Bur oak groups mark the perimeter and horizon; the tallgrass interior stays open and sunlit.', plantingStructure: 'nature_preserve_prairie_v1',
  guides: [
    { kind: 'path_loop', x: 0.52, y: 0.52, width: 0.72, height: 0.62, color: '#b49f74', strokeWidthM: 2.0, fitPolicy: 'clip' },
    { kind: 'polyline', x: 0.50, y: 0.50, width: 1, height: 1, points: [[0.08,0.72],[0.24,0.58],[0.42,0.52],[0.62,0.40],[0.88,0.30]], color: '#b49f74', strokeWidthM: 1.7 },
    { kind: 'rectangle', x: 0.72, y: 0.34, width: 0.10, height: 0.08, widthM: 8, heightM: 6, color: '#80684d', orientationPolicy: 'fixed' },
  ],
  guideLegend: ['TAN lines are narrow mown habitat trails', 'small BROWN pad is one observation deck', 'the unmarked majority remains layered tallgrass habitat'], includeCentralPlaza: false,
  renderSummary: 'tallgrass prairie preserve with contiguous habitat, narrow mown trail network, timber observation deck and sparse Bur oak savanna', isPilot: true,
};

PROFILES.riverfront_park_beach_v1 = {
  id: 'riverfront-lake-beach-lego-v1', version: 1,
  programDescription: 'A lake swimming beach with a broad crescent of sand, grass picnic edge, T-shaped swimming dock, offshore swim float, compact kayak rack and a reserved bathhouse pad for a separately rendered building family.',
  groundDescription: 'Variegated warm sand, clear turquoise shallows, dark green lawn, weathered cedar dock boards and brightly coloured kayak accents sampled from Riverfront Park v1.',
  criticalConstraints: 'Keep a continuous public water edge and clear swimming zone. The dock, float and kayak rack retain human scale while sand length adapts to the shoreline. Reserve but do not generate the bathhouse. No swimmers, sunbathers or surrounding buildings.',
  canopyDescription: 'Mature shade trees stay behind the sand on the picnic lawn; trunks do not enter the swimming sightline or dock approach.', plantingStructure: 'riverfront_lake_beach_v1',
  guides: [
    { kind: 'ellipse', x: 0.48, y: 0.58, width: 0.74, height: 0.50, color: '#d2bd8e', strokeColor: '#75a8a7', strokeWidthM: 7.0, fitPolicy: 'clip' },
    { kind: 'polyline', x: 0.68, y: 0.47, width: 1, height: 1, points: [[0.66,0.68],[0.72,0.54],[0.76,0.38],[0.68,0.34],[0.84,0.34]], color: '#876b50', strokeWidthM: 2.6 },
    { kind: 'rectangle', x: 0.24, y: 0.34, width: 0.14, height: 0.10, widthM: 12, heightM: 8, color: '#7a6552', strokeColor: '#5d5147', strokeWidthM: 0.2, orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.33, y: 0.72, width: 0.12, height: 0.05, widthM: 9, heightM: 3, color: '#b05d3e', orientationPolicy: 'orthogonal' },
  ],
  guideLegend: ['GOLD crescent is the beach and BLUE edge the swimming water', 'BROWN T route is the swimming dock', 'upper BROWN pad is bathhouse reservation only; lower coloured bar is the kayak rack'], includeCentralPlaza: false,
  renderSummary: 'lake swimming beach with crescent sand, picnic lawn, T dock, swim float, kayak rack and reserved bathhouse pad', isPilot: true,
};

PROFILES.reclaimed_industrial_park_v0 = {
  id: 'reclaimed-industrial-wharf-lego-v1', version: 1,
  programDescription: 'A linear reclaimed wharf with a continuous timber-and-concrete promenade, native planting strips, water-play pad and a row of whole cor-ten dock-crane relic modules.',
  groundDescription: 'Reclaimed grey timber and concrete bands, rust-orange steel, deep river tones and tawny native grasses sampled from the Domino-style wharf reference.',
  criticalConstraints: 'The pedestrian route stays continuous and keeps a clear accessible width. Repeat one to four complete crane modules as length permits; never stretch a crane or let its base interrupt circulation. Surrounding warehouses, boats and people are excluded.',
  canopyDescription: 'Low grasses and sparse riverside trees preserve long views and crane silhouettes.', plantingStructure: 'reclaimed_wharf_v0',
  guides: [{ kind: 'polyline', x: 0.5, y: 0.55, width: 1, height: 1, points: [[0.04,0.62],[0.24,0.56],[0.48,0.58],[0.72,0.50],[0.96,0.52]], color: '#816c55', strokeWidthM: 5.5 }],
  guideLegend: ['wide BROWN route is the uninterrupted reclaimed wharf walk', 'whole rust crane modules repeat landward as available length increases'], includeCentralPlaza: false,
  renderSummary: 'reclaimed industrial wharf with textured promenade, native grasses and whole cor-ten crane relics', isPilot: true,
};

PROFILES.quarry_sunken_garden_park_v2 = {
  id: 'quarry-tier-cascade-lego-v1', version: 1,
  programDescription: 'A limestone quarry bowl resolved as three to five complete garden terraces, a side cascade and two linked reflecting basins.',
  groundDescription: 'Warm limestone, gravel, clipped green parterre, flowering shrub colour and blue-green water sampled from the tiered quarry reference.',
  criticalConstraints: 'Terraces remain readable whole levels and descend in order. Add a complete terrace on oversized sites rather than enlarging one step. Keep every public route clear of basin edges. No surrounding hilltown buildings or people.',
  canopyDescription: 'Low clipped planting occupies upper tiers; specimen trees stay on the rim.', plantingStructure: 'quarry_tier_cascade_v2',
  guides: [
    { kind: 'rectangle', x: 0.50, y: 0.63, width: 0.34, height: 0.13, color: '#668b8c', orientationPolicy: 'flexible' },
    { kind: 'rectangle', x: 0.50, y: 0.42, width: 0.25, height: 0.10, color: '#668b8c', orientationPolicy: 'flexible' },
  ], guideLegend: ['BLUE rectangles are linked water terraces', 'the remaining bowl is complete limestone garden tiers'], includeCentralPlaza: false,
  renderSummary: 'terraced limestone quarry garden with whole level bands, formal planting and cascading pools', isPilot: true,
};

PROFILES.estate_picnic_grove_v1 = {
  id: 'estate-oak-picnic-lego-v1', version: 1,
  programDescription: 'A broad mown play lawn ringed by a crushed-stone loop and a matrix of mature oak shade modules, each paired with one picnic table and one fixed grill.',
  groundDescription: 'Variegated green turf, pale compacted stone, dark oak canopy, weathered timber and charcoal steel sampled from the oak-grove reference.',
  criticalConstraints: 'Every picnic station is a complete oak-table-grill module. Oversized sites receive more modules and retain the central play clear; tables and grills never scale with the parcel. No people.',
  canopyDescription: 'Widely spaced mature oaks create dappled shade without closing the canopy.', plantingStructure: 'estate_oak_picnic_v1',
  guides: [{ kind: 'path_loop', x: 0.5, y: 0.5, width: 0.82, height: 0.74, color: '#b7a379', strokeWidthM: 2.4, fitPolicy: 'clip' }],
  guideLegend: ['TAN loop is the crushed-stone walk', 'open centre remains casual-play turf; complete oak picnic stations occupy the outer lawn'], includeCentralPlaza: false,
  renderSummary: 'wide-spaced oak grove with repeated whole picnic stations, central play lawn and crushed-stone loop', isPilot: true,
};

PROFILES.constructed_wetland_eco_park_variant_0 = {
  id: 'constructed-wetland-boardwalk-lego-v1', version: 1,
  programDescription: 'An urban wetland mosaic of three to five complete planted water cells linked by a zig-zag timber boardwalk and viewing deck.',
  groundDescription: 'Dark reflective water, reed green, tawny wet meadow and weathered timber sampled from the urban boardwalk wetland reference.',
  criticalConstraints: 'Water cells remain discrete habitat basins and the dry boardwalk remains continuous. Add whole cells and deck bays for large sites. The nature pavilion and surrounding buildings are reserved or excluded; no people.',
  canopyDescription: 'Reeds dominate cells; only sparse bank trees occur at the perimeter.', plantingStructure: 'constructed_wetland_boardwalk_v0',
  guides: [
    { kind: 'ellipse', x: 0.28, y: 0.45, width: 0.34, height: 0.28, color: '#557b73', fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.68, y: 0.57, width: 0.40, height: 0.30, color: '#4f716c', fitPolicy: 'clip' },
    { kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.05,0.72],[0.25,0.56],[0.43,0.64],[0.62,0.44],[0.82,0.52],[0.95,0.31]], color: '#81674e', strokeWidthM: 2.2 },
  ], guideLegend: ['BLUE-GREEN ellipses are whole wetland cells', 'BROWN zig-zag is the continuous raised boardwalk'], includeCentralPlaza: false,
  renderSummary: 'urban constructed wetland with discrete reed cells and continuous zig-zag timber boardwalk', isPilot: true,
};

PROFILES.academic_courtyard_variant_0 = {
  id: 'academic-planted-courtyard-lego-v1', version: 1,
  programDescription: 'A compact paved study court with crisp raised perennial planters, built-in timber ledges and clear short routes between implied entrances.',
  groundDescription: 'Warm pale paving, fieldstone planter bases, rich grasses and weathered timber sampled from the modern planted courtyard reference.',
  criticalConstraints: 'Keep accessible cross routes and whole raised beds. Add a whole bed on wider courts rather than enlarging furniture. Seat ledges stay at human height and never obstruct entrances. The enclosing academic buildings and people are excluded.',
  canopyDescription: 'A few multi-stem trees rise from planted beds; the courtyard centre remains open.', plantingStructure: 'academic_planted_court_v0',
  guides: [
    { kind: 'rounded_rectangle', x: 0.27, y: 0.35, width: 0.30, height: 0.22, color: '#65754f', orientationPolicy: 'orthogonal' },
    { kind: 'rounded_rectangle', x: 0.68, y: 0.62, width: 0.34, height: 0.24, color: '#596d4b', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.66, y: 0.27, width: 0.22, height: 0.16, color: '#6a7b55', orientationPolicy: 'orthogonal' },
  ], guideLegend: ['GREEN blocks are complete raised perennial beds with seat ledges', 'unmarked pale ground is the accessible study court'], includeCentralPlaza: true,
  renderSummary: 'compact modern academic courtyard with raised planted beds, seating ledges and clear cross routes', isPilot: true,
};

PROFILES.campus_pedestrian_spine_variant_0 = {
  id: 'campus-green-spine-lego-v1', version: 1,
  programDescription: 'A long central pedestrian walk with paired rain-garden bands, a regular tree allee and complete bench-light bays that repeat with corridor length.',
  groundDescription: 'Warm light paving, deep meadow greens, flowering perennials and timber seat ledges sampled from the green campus-spine reference.',
  criticalConstraints: 'Preserve one continuous accessible axis. Add whole tree and furnishing bays for additional length; do not broaden the path into a plaza or permit planting to pinch its clear width. Flanking buildings and people are excluded.',
  canopyDescription: 'Two regular tree rows reinforce the corridor without closing the central sky view.', plantingStructure: 'campus_green_spine_v0',
  guides: [{ kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.50,0.03],[0.49,0.26],[0.51,0.51],[0.49,0.75],[0.50,0.97]], color: '#aaa59a', strokeWidthM: 5.2 }],
  guideLegend: ['PALE central route is one continuous pedestrian spine', 'paired green bands and tree bays repeat along both sides'], includeCentralPlaza: false,
  renderSummary: 'green campus pedestrian spine with continuous walk, rain gardens and repeating tree bays', isPilot: true,
};

PROFILES.botanical_garden_v3 = {
  id: 'botanical-rose-garden-lego-v1', version: 1,
  programDescription: 'A romantic botanical rose garden of complete flower-bed rooms connected by brick-and-stone paths and a short sequence of human-scale timber rose arbors.',
  groundDescription: 'Weathered brick and stone, layered rose pinks, perennial blues, deep foliage and aged timber sampled from the cottage botanical reference.',
  criticalConstraints: 'Beds remain complete garden rooms and paths stay continuous. Add whole bed-and-arbor bays for large sites. The glass conservatory is edge context only and is not generated here; no people.',
  canopyDescription: 'Small flowering trees and rose arbors create framed views without obscuring the garden-room sequence.', plantingStructure: 'botanical_rose_garden_v3',
  guides: [
    { kind: 'ellipse', x: 0.28, y: 0.39, width: 0.27, height: 0.24, color: '#8b5660', fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.66, y: 0.37, width: 0.30, height: 0.25, color: '#9a6970', fitPolicy: 'clip' },
    { kind: 'rounded_rectangle', x: 0.48, y: 0.70, width: 0.36, height: 0.23, color: '#765b63', orientationPolicy: 'flexible' },
  ], guideLegend: ['ROSE shapes are complete planted garden rooms', 'timber arbors punctuate the connecting walk'], includeCentralPlaza: false,
  renderSummary: 'romantic rose botanical garden with complete flower rooms, textured paths and timber arbors', isPilot: true,
};

PROFILES.research_garden_teaching_arboretum_variant_0 = {
  id: 'research-arboretum-lego-v1', version: 1,
  programDescription: 'A labelled specimen-tree collection arranged as varied whole tree groups along an interpretive loop, with boulder outcrops and small identification plaques.',
  groundDescription: 'Meadow and mown-lawn variation, pale aggregate paths, fieldstone, mixed specimen foliage and weathered sign timber sampled from the arboretum reference.',
  criticalConstraints: 'Tree species and maturity vary by complete specimens, never by stretching. Keep the interpretive loop clear, signs modest and every boulder outside the accessible route. Campus buildings and people are excluded.',
  canopyDescription: 'Open-spaced specimen crowns allow every collection tree to read individually.', plantingStructure: 'research_arboretum_v0',
  guides: [{ kind: 'path_loop', x: 0.5, y: 0.52, width: 0.78, height: 0.68, color: '#b0a17f', strokeWidthM: 2.6, fitPolicy: 'clip' }],
  guideLegend: ['TAN loop is the interpretive path', 'varied whole specimen trees, plaques and boulders occupy the surrounding meadow'], includeCentralPlaza: false,
  renderSummary: 'teaching arboretum with varied specimen trees, interpretive loop, plaques and boulder outcrops', isPilot: true,
};

PROFILES.rewilding_ecological_restoration_zone_variant_1 = {
  id: 'rewilding-reforestation-lego-v1', version: 1,
  programDescription: 'A young reforestation field of dense but irregular sapling cohorts, native understory, retained rubble islands and whole habitat-log piles.',
  groundDescription: 'Pioneer birch green, dark mulch, wildflower flecks, weathered logs and mineral rubble sampled from the reforestation reference.',
  criticalConstraints: 'Regeneration habitat dominates. Add complete sapling cohorts and log piles as area grows; keep access paths narrow, retain irregular succession gaps and do not introduce manicured lawn, buildings or people.',
  canopyDescription: 'Young uneven saplings form an establishing canopy with visible gaps and succession layers.', plantingStructure: 'rewilding_reforestation_v1',
  guides: [{ kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.05,0.70],[0.28,0.58],[0.48,0.62],[0.70,0.43],[0.95,0.36]], color: '#a79a7c', strokeWidthM: 2.0 }],
  guideLegend: ['thin TAN line is the restrained access trail', 'all other ground is irregular sapling cohorts, understory and habitat debris'], includeCentralPlaza: false,
  renderSummary: 'brownfield reforestation zone with young pioneer cohorts, wild understory and habitat log piles', isPilot: true,
};

PROFILES.stormwater_resilience_park_variant_3 = {
  id: 'stormwater-arid-channel-lego-v1', version: 1,
  programDescription: 'A dry-climate resilience park centred on a rock-lined ephemeral channel, gravel detention pockets, drought planting and repeated small shade bays.',
  groundDescription: 'Layered tan gravel, ochre stone, dusty green xeric planting and dark weathered timber sampled from the arid stormwater reference.',
  criticalConstraints: 'The conveyance channel remains continuous and unobstructed. Repeat whole gravel basins and shade bays as room permits; do not fill the channel with permanent blue water. No surrounding buildings or people.',
  canopyDescription: 'Sparse desert trees and pergolas provide targeted shade while leaving the waterway open.', plantingStructure: 'stormwater_arid_channel_v3',
  guides: [{ kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.04,0.68],[0.22,0.54],[0.40,0.61],[0.58,0.42],[0.76,0.49],[0.96,0.30]], color: '#99866d', strokeWidthM: 6.5 }],
  guideLegend: ['wide OCHRE route is the dry rock conveyance channel', 'xeric planting and complete shade bays occupy higher ground'], includeCentralPlaza: false,
  renderSummary: 'arid stormwater park with continuous dry rock channel, gravel basins and drought planting', isPilot: true,
};

PROFILES.urban_pocket_park_v0 = {
  id: 'urban-pocket-rustic-lego-v1', version: 1,
  programDescription: 'A compact gravel garden room with one small lawn, a looping path, whole rough-timber pergola bays, split-rail edges, wildflower borders and boulder seats.',
  groundDescription: 'Warm compacted gravel, varied turf, meadow flecks, rough timber and natural stone sampled from the exact rustic pocket-park reference.',
  criticalConstraints: 'Keep one legible central lawn and complete accessible loop. Add or remove whole pergola bays, benches and boulders; never stretch furniture or crowd the path. Do not generate surrounding buildings or people.',
  canopyDescription: 'Two to four broad shade trees frame the lawn and pergola without closing the small room.', plantingStructure: 'urban_pocket_rustic_v0',
  guides: [
    { kind: 'path_loop', x: 0.5, y: 0.52, width: 0.82, height: 0.72, color: '#a88f6b', strokeWidthM: 1.8, fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.52, y: 0.50, width: 0.42, height: 0.34, color: '#71894e', fitPolicy: 'clip' },
    { kind: 'rectangle', x: 0.5, y: 0.18, width: 0.48, height: 0.10, color: '#76533a', orientationPolicy: 'orthogonal' },
  ], guideLegend: ['TAN loop is compacted gravel', 'GREEN centre is one lawn room', 'BROWN edge is whole timber pergola bays'], includeCentralPlaza: false,
  renderSummary: 'rustic pocket park with gravel loop, central lawn, timber pergola, split rails, wildflowers and boulder seating', isPilot: true,
};

PROFILES.neighborhood_park_v3 = {
  id: 'neighborhood-contemporary-lego-v1', version: 1,
  programDescription: 'A contemporary neighborhood park organized as one open lawn, one paved social room, one complete water-jet pad and repeated raised planting/furniture bays.',
  groundDescription: 'Large-format pale and charcoal permeable pavers, textured lawn, ornamental grasses, coloured concrete and dark powder-coated metal sampled from the exact v3 reference.',
  criticalConstraints: 'Allocate site growth by adding complete social or planting bays while preserving the lawn and continuous loop. Keep the water jets together on one pad; do not enlarge one feature to fill an oversized polygon. No people or surrounding buildings.',
  canopyDescription: 'Mature shade trees occupy the social and planter edges, leaving lawn and water play open.', plantingStructure: 'neighborhood_contemporary_v3',
  guides: [
    { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.86, height: 0.74, color: '#aaa8a1', strokeWidthM: 2.8, fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.30, y: 0.48, width: 0.34, height: 0.34, color: '#6f8a57', fitPolicy: 'clip' },
    { kind: 'rectangle', x: 0.68, y: 0.48, width: 0.30, height: 0.28, color: '#aaa49b', orientationPolicy: 'flexible' },
    { kind: 'ellipse', x: 0.69, y: 0.48, width: 0.13, height: 0.13, color: '#6b979d' },
  ], guideLegend: ['GREEN is the open lawn', 'PALE rectangle is the social room', 'BLUE circle is one water-jet pad'], includeCentralPlaza: false,
  renderSummary: 'urban contemporary neighborhood park with open lawn, geometric social paving, raised planters and one integrated water-jet pad', isPilot: true,
};

PROFILES.cemetery_memorial_grounds_v0 = {
  id: 'cemetery-classical-lego-v1', version: 1,
  programDescription: 'A symmetrical memorial landscape with one central gravel allee, paired parterre rooms, a circular fountain node and repeated complete rows of modest stone memorials.',
  groundDescription: 'Pale gravel, clipped dark boxwood, varied lawn, weathered limestone and restrained white stone sampled from the exact classical reference.',
  criticalConstraints: 'Preserve the main axis, fountain and mirrored parterre hierarchy. Add or remove whole memorial rows as area changes; never scale individual markers or block paths. No chapel, mausoleum, surrounding buildings or people.',
  canopyDescription: 'Formal allées and columnar evergreens frame the axis while memorial lawns remain legible.', plantingStructure: 'cemetery_classical_v0',
  guides: [
    { kind: 'axis', x: 0.5, y: 0.5, width: 0, height: 0.88, color: '#b7a683', strokeWidthM: 4.0 },
    { kind: 'ellipse', x: 0.5, y: 0.52, width: 0.14, height: 0.14, color: '#718f96', strokeColor: '#c8bda6', strokeWidthM: 1.0 },
    { kind: 'rectangle', x: 0.30, y: 0.52, width: 0.25, height: 0.50, color: '#557048', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.70, y: 0.52, width: 0.25, height: 0.50, color: '#557048', orientationPolicy: 'orthogonal' },
  ], guideLegend: ['TAN vertical line is the main allee', 'BLUE centre is the fountain', 'paired GREEN rooms are parterre and memorial lawns'], includeCentralPlaza: false,
  renderSummary: 'classical memorial grounds with axial gravel allee, fountain, mirrored parterres and complete stone-marker rows', isPilot: true,
};

PROFILES.courtyard_plaza_v1 = {
  id: 'courtyard-linear-water-lego-v1', version: 1,
  programDescription: 'A compact contemporary court with one continuous shallow linear rill, large-format granite paving, whole concrete seat-wall bays and specimen trees in flush grates.',
  groundDescription: 'Variegated light granite, dark water, architectural concrete, restrained planting and timber seat caps sampled from the exact v1 courtyard reference.',
  criticalConstraints: 'The rill remains continuous and the main accessible route remains clear. Add whole seat-wall/tree bays around it; never widen the water channel or furniture to consume residual space. Buildings and people are excluded.',
  canopyDescription: 'A short row of high-canopy specimen trees shades seating while preserving courtyard sightlines.', plantingStructure: 'courtyard_linear_water_v1',
  guides: [
    { kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.08,0.58],[0.32,0.58],[0.54,0.46],[0.92,0.46]], color: '#557c84', strokeWidthM: 1.4 },
    { kind: 'rectangle', x: 0.29, y: 0.28, width: 0.30, height: 0.14, color: '#71805c', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.70, y: 0.70, width: 0.30, height: 0.14, color: '#71805c', orientationPolicy: 'orthogonal' },
  ], guideLegend: ['BLUE route is one continuous shallow rill', 'GREEN blocks are whole planter and seat-wall bays'], includeCentralPlaza: true,
  renderSummary: 'contemporary granite courtyard with continuous linear water rill, concrete seating walls and flush-grate specimen trees', isPilot: true,
};

PROFILES.street_plaza_parklet_v1 = {
  id: 'parklet-sf-timber-lego-v1', version: 1,
  programDescription: 'A narrow curbside Douglas-fir deck containing complete café-table bays, a continuous timber slat guard edge and terracotta herb planters.',
  groundDescription: 'Weathered warm timber, dark asphalt edge, terracotta pots and varied herb foliage sampled from the exact San Francisco parklet reference.',
  criticalConstraints: 'Keep the deck level and preserve one clear accessible aisle. Repeat only complete table-planter bays with length; guard edges remain continuous and furniture stays human-scaled. Do not generate roadway vehicles, storefronts or people.',
  canopyDescription: 'Planters contain herbs and small shrubs only; no full trees are forced into the narrow deck.', plantingStructure: 'parklet_sf_timber_v1',
  guides: [{ kind: 'rectangle', x: 0.5, y: 0.5, width: 0.90, height: 0.78, color: '#8c694a', orientationPolicy: 'orthogonal' }],
  guideLegend: ['BROWN rectangle is one level timber deck; complete table and planter bays repeat along its length'], includeCentralPlaza: false,
  renderSummary: 'San Francisco timber parklet with clear aisle, slat guard, café-table bays and terracotta herb planters', isPilot: true,
};

PROFILES.parisian_jardin_v1 = {
  id: 'french-parterre-axis-lego-v1', version: 1,
  programDescription: 'A Jardin a la Francaise composed around one long reflecting-water axis, mirrored clipped parterres, gravel cross walks and whole topiary bays.',
  groundDescription: 'Pale compacted gravel, dark clipped boxwood, warm stone coping, blue-grey water and flower accents sampled from the exact Variant 2 reference.',
  criticalConstraints: 'Preserve strict bilateral symmetry and the complete water axis. Add mirrored pairs of whole parterre rooms as sites grow; never stretch a hedge room or offset one side independently. Surrounding buildings and people are excluded.',
  canopyDescription: 'Clipped topiary and small formal trees reinforce the axis without obscuring the parterre geometry.', plantingStructure: 'french_parterre_axis_v1',
  guides: [
    { kind: 'axis', x: 0.5, y: 0.5, width: 0, height: 0.72, color: '#698d93', strokeWidthM: 4.0 },
    { kind: 'rectangle', x: 0.28, y: 0.34, width: 0.30, height: 0.22, color: '#4f6944', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.72, y: 0.34, width: 0.30, height: 0.22, color: '#4f6944', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.28, y: 0.68, width: 0.30, height: 0.22, color: '#5b744b', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.72, y: 0.68, width: 0.30, height: 0.22, color: '#5b744b', orientationPolicy: 'orthogonal' },
  ], guideLegend: ['BLUE line is the reflecting axis', 'four GREEN blocks are mirrored complete parterre rooms'], includeCentralPlaza: false,
  renderSummary: 'French formal garden with continuous water axis, mirrored parterre rooms, pale gravel walks and clipped topiary', isPilot: true,
};

PROFILES.london_garden_square_v1 = {
  id: 'london-railed-square-lego-v1', version: 1,
  programDescription: 'An enclosed London garden square with one central lawn room, perimeter walk, continuous black iron railing, mature shade trees and path-facing benches.',
  groundDescription: 'Deep green lawn, pale stone and gravel, dark iron, brick edging and layered shrub planting sampled from the exact Variant 2 reference.',
  criticalConstraints: 'Keep one continuous enclosure with legible gates and a clear perimeter walk. Add whole tree-bench bays as size increases; never close gates or scatter furniture across the lawn. Buildings and people are excluded.',
  canopyDescription: 'Mature deciduous trees ring the edge and maintain an open central lawn.', plantingStructure: 'london_railed_square_v1',
  guides: [
    { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.82, height: 0.72, color: '#aaa080', strokeWidthM: 2.4, fitPolicy: 'clip' },
    { kind: 'rounded_rectangle', x: 0.5, y: 0.5, width: 0.58, height: 0.48, color: '#66814f', orientationPolicy: 'orthogonal' },
  ], guideLegend: ['TAN loop is the perimeter walk', 'GREEN centre is one open lawn; black railing follows the outer boundary with gates'], includeCentralPlaza: false,
  renderSummary: 'London garden square with railed enclosure, central lawn, perimeter tree walk and benches', isPilot: true,
};

PROFILES.halifax_public_gardens_v0 = {
  id: 'halifax-rose-bandstand-lego-v1', version: 1,
  programDescription: 'A Victorian public garden of complete rose-bed rooms around a gravel promenade, one ornate open bandstand and a formal wrought-iron entry gate.',
  groundDescription: 'Layered red, pink and white roses, dark boxwood, pale gravel, black iron and cream-painted timber sampled from the exact Rose Garden Peak reference.',
  criticalConstraints: 'Keep rose rooms complete and the promenade continuous. Generate one modest park bandstand, not a large building, and one entry gate. Add paired bed rooms rather than stretching flowers; do not render people or surrounding buildings.',
  canopyDescription: 'Mature canopy frames the boundary while rose rooms and bandstand remain sunlit.', plantingStructure: 'halifax_rose_bandstand_v0',
  guides: [
    { kind: 'path_loop', x: 0.5, y: 0.52, width: 0.82, height: 0.72, color: '#b1a080', strokeWidthM: 2.8, fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.30, y: 0.48, width: 0.27, height: 0.24, color: '#934f62' },
    { kind: 'ellipse', x: 0.70, y: 0.48, width: 0.27, height: 0.24, color: '#a86772' },
    { kind: 'ellipse', x: 0.50, y: 0.28, width: 0.15, height: 0.15, color: '#d7cfb9' },
  ], guideLegend: ['TAN loop is the promenade', 'ROSE circles are whole beds', 'PALE centre is one open bandstand'], includeCentralPlaza: false,
  renderSummary: 'Victorian Halifax garden with rose rooms, gravel promenade, ornate bandstand and wrought-iron gate', isPilot: true,
};

PROFILES.picturesque_olmsted_park_v3 = {
  id: 'olmsted-multilandscape-lego-v1', version: 1,
  programDescription: 'A compacted sequence of whole Olmsted landscape rooms: open meadow, wooded ramble, lake, rustic bridge, formal overlook and paired-tree mall within one serpentine perimeter drive.',
  groundDescription: 'Variegated meadow and lawn greens, dark woodland, natural water, weathered stone and warm bridge timber sampled from the exact Central Park multi-landscape reference.',
  criticalConstraints: 'Preserve the sequence and contrast between complete rooms. On compact sites reduce the number of secondary bays, not the identity of meadow, woodland, lake, bridge and mall. Do not render surrounding buildings or people.',
  canopyDescription: 'Dense woodland and paired elm mall contrast with a fully open meadow and readable lake edge.', plantingStructure: 'olmsted_multilandscape_v3',
  guides: [
    { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.88, height: 0.80, color: '#a69577', strokeWidthM: 3.2, fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.63, y: 0.58, width: 0.36, height: 0.30, color: '#5f8585', fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.28, y: 0.40, width: 0.32, height: 0.28, color: '#719055', fitPolicy: 'clip' },
    { kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.48,0.62],[0.58,0.57],[0.70,0.54]], color: '#7b5d47', strokeWidthM: 2.5 },
  ], guideLegend: ['TAN loop is the carriage walk', 'BLUE is the lake', 'GREEN is the meadow', 'BROWN crossing is the rustic bridge'], includeCentralPlaza: false,
  renderSummary: 'Olmsted multi-landscape park with meadow, wooded ramble, lake, rustic bridge, formal overlook and paired-tree mall', isPilot: true,
};

PROFILES.hilltop_topographic_park_v3 = {
  id: 'hilltop-viewpoint-lego-v1', version: 1,
  programDescription: 'A forested hill park with one continuous crushed-gravel switchback trail and two to five complete concrete-and-cedar viewpoint platforms placed at distinct elevations.',
  groundDescription: 'Crushed mineral gravel, rugged rock, deep fir green, rough cedar and pale architectural concrete sampled from the exact Pacific terraced-viewpoint reference.',
  criticalConstraints: 'The switchback stays continuous and grades read as an ordered ascent. Add whole viewpoint platforms only where width permits; never stretch a deck or float it away from terrain. No skyline buildings or people.',
  canopyDescription: 'Mature fir and cedar mass on slopes while deliberate clearings preserve each overlook view.', plantingStructure: 'hilltop_viewpoint_v3',
  guides: [
    { kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.08,0.82],[0.34,0.70],[0.18,0.54],[0.58,0.44],[0.38,0.28],[0.88,0.16]], color: '#ab9878', strokeWidthM: 2.8 },
    { kind: 'rectangle', x: 0.34, y: 0.70, width: 0.18, height: 0.12, color: '#99938a', orientationPolicy: 'flexible' },
    { kind: 'rectangle', x: 0.58, y: 0.43, width: 0.20, height: 0.13, color: '#99938a', orientationPolicy: 'flexible' },
    { kind: 'rectangle', x: 0.84, y: 0.17, width: 0.22, height: 0.14, color: '#99938a', orientationPolicy: 'flexible' },
  ], guideLegend: ['TAN zig-zag is one continuous ascending trail', 'GREY rectangles are whole viewpoint platforms at ordered elevations'], includeCentralPlaza: false,
  renderSummary: 'Pacific hilltop park with continuous switchback ascent, whole terraced viewpoint decks, cedar accents and fir-covered slopes', isPilot: true,
};

PROFILES.amsterdam_hofje_garden_v0 = {
  id: 'amsterdam-hofje-lego-v1', version: 1,
  programDescription: 'A secluded hofje garden with a simple gravel cross, four complete low-hedge planting rooms, one central pump or well, two small shade trees and a single legible gate.',
  groundDescription: 'Warm gravel, clipped boxwood, rose and herb planting, aged stone and dark iron sampled from the exact Variant 1 reference.',
  criticalConstraints: 'Preserve one enclosed garden room, one central feature and a clear gate-to-centre route. Add paired planting beds, never surrounding dwellings or people; keep every hedge and bench human-scaled.',
  canopyDescription: 'One or two modest deciduous trees shade the garden without turning the small court into a grove.', plantingStructure: 'amsterdam_hofje_v0',
  guides: [
    { kind: 'axis', x: 0.5, y: 0.5, width: 0, height: 0.78, color: '#ae9c80', strokeWidthM: 1.8 },
    { kind: 'axis', x: 0.5, y: 0.5, width: 0, height: 0.78, color: '#ae9c80', strokeWidthM: 1.8, rotationDeg: 90 },
    { kind: 'rectangle', x: 0.28, y: 0.28, width: 0.28, height: 0.25, color: '#596d48', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.72, y: 0.28, width: 0.28, height: 0.25, color: '#596d48', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.28, y: 0.72, width: 0.28, height: 0.25, color: '#65764c', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.72, y: 0.72, width: 0.28, height: 0.25, color: '#65764c', orientationPolicy: 'orthogonal' },
  ], guideLegend: ['TAN cross is the gravel walk', 'four GREEN rooms are whole hedge and flower beds', 'centre receives one well or pump'], includeCentralPlaza: false,
  renderSummary: 'Amsterdam hofje garden with gravel cross, clipped planting rooms, central well, modest trees and one gate', isPilot: true,
};

PROFILES.amsterdam_plein_v0 = {
  id: 'amsterdam-plein-lego-v1', version: 1,
  programDescription: 'A flexible brick-paved plein with a broad clear centre, repeatable whole market-stall bays, edge tree line, benches and bicycle racks.',
  groundDescription: 'Variegated Dutch brick and stone, warm stall timber, dark metal and restrained edge planting sampled from the exact Variant 1 reference.',
  criticalConstraints: 'Keep the centre clear for markets and events. Add complete stall and edge-tree bays as length permits; do not generate focal buildings, storefronts, vehicles or people.',
  canopyDescription: 'Mature trees stay on one or two edges so the civic centre remains open.', plantingStructure: 'amsterdam_plein_v0',
  guides: [
    { kind: 'rounded_rectangle', x: 0.5, y: 0.55, width: 0.76, height: 0.58, color: '#a58f74', orientationPolicy: 'flexible' },
    { kind: 'rectangle', x: 0.5, y: 0.17, width: 0.78, height: 0.13, color: '#7f6046', orientationPolicy: 'orthogonal' },
  ], guideLegend: ['BRICK centre stays flexible', 'BROWN edge contains whole market-stall bays and trees'], includeCentralPlaza: true,
  renderSummary: 'Dutch brick plein with flexible civic centre, repeatable market stalls, bicycle racks and edge trees', isPilot: true,
};

PROFILES.amsterdam_vondelpark_v3 = {
  id: 'amsterdam-vondelpark-pavilion-lego-v1', version: 1,
  programDescription: 'A naturalistic Vondelpark room with winding paths, open lawn, irregular pond, a small footbridge, dense mature tree groups and one modest park pavilion terrace.',
  groundDescription: 'Layered lawn and meadow greens, pale gravel, dark water, mature foliage and warm pavilion timber sampled from the exact Variant 4 reference.',
  criticalConstraints: 'Preserve contrast between open lawn, wooded edge and pond. Scale with whole landscape rooms and tree groups; emit only a modest park shelter, never the reference buildings or people.',
  canopyDescription: 'Dense plane, elm, beech and chestnut groups frame open lawns and water.', plantingStructure: 'amsterdam_vondelpark_v3',
  guides: [
    { kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.05,0.72],[0.24,0.58],[0.45,0.62],[0.66,0.42],[0.94,0.30]], color: '#a89a7f', strokeWidthM: 3.0 },
    { kind: 'ellipse', x: 0.66, y: 0.63, width: 0.30, height: 0.25, color: '#5c8587', fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.30, y: 0.42, width: 0.34, height: 0.30, color: '#6d8a52', fitPolicy: 'clip' },
    { kind: 'rectangle', x: 0.78, y: 0.22, width: 0.18, height: 0.13, color: '#826348', orientationPolicy: 'flexible' },
  ], guideLegend: ['TAN line is a winding park route', 'BLUE is the pond', 'GREEN is open lawn', 'BROWN is one modest pavilion terrace'], includeCentralPlaza: false,
  renderSummary: 'Vondelpark landscape room with winding path, lawn, pond, bridge, mature grove and modest pavilion terrace', isPilot: true,
};

PROFILES.barcelona_pati_interior_v0 = {
  id: 'barcelona-pati-green-lego-v1', version: 1,
  programDescription: 'A reclaimed Eixample courtyard with central fountain, shaded gravel paths, four complete Mediterranean planting rooms, benches and one compact play bay.',
  groundDescription: 'Warm gravel and stone, citrus and palm greens, bougainvillea colour, pale fountain stone and timber seating sampled from Variant 1.',
  criticalConstraints: 'Keep a clear passage-to-fountain route and complete planting rooms. Add whole tree or bench bays only; do not generate the enclosing buildings or people.',
  canopyDescription: 'Palms, citrus and cypress create layered shade while leaving the centre visible.', plantingStructure: 'barcelona_pati_green_v0',
  guides: [
    { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.82, height: 0.72, color: '#aa9577', strokeWidthM: 2.0, fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.5, y: 0.5, width: 0.17, height: 0.17, color: '#638b90', strokeColor: '#b6a78f', strokeWidthM: 1.0 },
    { kind: 'rectangle', x: 0.27, y: 0.30, width: 0.26, height: 0.22, color: '#5e7149', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.73, y: 0.30, width: 0.26, height: 0.22, color: '#5e7149', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.27, y: 0.70, width: 0.26, height: 0.22, color: '#6f7950', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.73, y: 0.70, width: 0.26, height: 0.22, color: '#6f7950', orientationPolicy: 'orthogonal' },
  ], guideLegend: ['TAN loop is the shaded path', 'BLUE centre is the fountain', 'GREEN blocks are Mediterranean planting rooms'], includeCentralPlaza: false,
  renderSummary: 'green Eixample interior courtyard with fountain, Mediterranean planting rooms, shaded paths and compact play bay', isPilot: true,
};

PROFILES.barcelona_placa_xamfra_v2 = {
  id: 'barcelona-xamfra-corner-lego-v1', version: 1,
  programDescription: 'A compact chamfer-corner plaza with an octagonal Gaudi-tile room, diagonal pedestrian flow, one mature shade tree and complete cafe-table clusters.',
  groundDescription: 'Warm hexagonal stone, dark tree grate, timber tables and restrained planter green sampled from exact Variant 3.',
  criticalConstraints: 'Keep diagonal movement clear and preserve the chamfer geometry. Repeat complete table clusters around one tree; do not generate corner buildings, storefronts or people.',
  canopyDescription: 'One dominant plane tree anchors the intimate urban room.', plantingStructure: 'barcelona_xamfra_v2',
  guides: [
    { kind: 'rounded_rectangle', x: 0.5, y: 0.5, width: 0.74, height: 0.68, color: '#aaa098', orientationPolicy: 'flexible', rotationDeg: 45 },
    { kind: 'axis', x: 0.5, y: 0.5, width: 0, height: 0.86, color: '#c0b5a5', strokeWidthM: 3.2, rotationDeg: 45 },
    { kind: 'ellipse', x: 0.5, y: 0.5, width: 0.13, height: 0.13, color: '#4f6b48' },
  ], guideLegend: ['PALE octagon is Gaudi-tile paving', 'diagonal route stays clear', 'GREEN centre is one mature tree'], includeCentralPlaza: true,
  renderSummary: 'Barcelona chamfer plaza with octagonal tile room, diagonal pedestrian route, central plane tree and cafe clusters', isPilot: true,
};

PROFILES.barcelona_superilla_v1 = {
  id: 'barcelona-superilla-green-lego-v1', version: 1,
  programDescription: 'A traffic-calmed superblock interior made from complete coloured-pavement rooms, raised planters, social furniture, play tables and a continuous pedestrian/cycle route.',
  groundDescription: 'Muted yellow, green, blue and terracotta pavement, planted beds, timber and dark metal sampled from exact Variant 2.',
  criticalConstraints: 'Keep a continuous through-route and distribute growth through additional complete activity rooms. Never stretch one painted zone to fill the parcel; exclude surrounding buildings, cars and people.',
  canopyDescription: 'Regular planter trees shade activity rooms without obscuring the through-route.', plantingStructure: 'barcelona_superilla_v1',
  guides: [
    { kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.04,0.66],[0.30,0.58],[0.50,0.50],[0.72,0.42],[0.96,0.34]], color: '#b5aa95', strokeWidthM: 5.0 },
    { kind: 'rectangle', x: 0.25, y: 0.30, width: 0.28, height: 0.20, color: '#c1a34e', orientationPolicy: 'flexible', rotationDeg: -8 },
    { kind: 'rectangle', x: 0.64, y: 0.28, width: 0.28, height: 0.20, color: '#71927a', orientationPolicy: 'flexible', rotationDeg: 7 },
    { kind: 'rectangle', x: 0.34, y: 0.73, width: 0.30, height: 0.20, color: '#668b9c', orientationPolicy: 'flexible', rotationDeg: 5 },
    { kind: 'rectangle', x: 0.76, y: 0.70, width: 0.26, height: 0.20, color: '#b36f57', orientationPolicy: 'flexible', rotationDeg: -6 },
  ], guideLegend: ['PALE route is continuous', 'four COLOURED blocks are complete activity rooms with planters and furniture'], includeCentralPlaza: false,
  renderSummary: 'Barcelona superilla with connected pedestrian route, coloured activity rooms, planters, play tables and social furniture', isPilot: true,
};

PROFILES.calgary_prairie_plaza_v1 = {
  id: 'calgary-prairie-market-lego-v1', version: 1,
  programDescription: 'An open prairie civic plaza with a shallow reflecting pool, complete timber market-stall bays, native grass planters, wind screens and generous event space.',
  groundDescription: 'Warm sandstone and concrete, blue-grey water, prairie grasses, timber stalls and weathered metal sampled from Summer Market Square.',
  criticalConstraints: 'Protect the open centre and pool axis. Add complete stalls and planters along edges; no office buildings, skybridges, vehicles or people.',
  canopyDescription: 'Sparse edge trees and prairie planters preserve the defining open sky.', plantingStructure: 'calgary_prairie_market_v1',
  guides: [
    { kind: 'rectangle', x: 0.5, y: 0.56, width: 0.78, height: 0.52, color: '#aaa095', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.5, y: 0.55, width: 0.42, height: 0.10, color: '#668c91', orientationPolicy: 'orthogonal' },
    { kind: 'rectangle', x: 0.5, y: 0.17, width: 0.78, height: 0.13, color: '#806047', orientationPolicy: 'orthogonal' },
  ], guideLegend: ['PALE centre is open event paving', 'BLUE bar is reflecting water', 'BROWN edge is whole market-stall bays'], includeCentralPlaza: true,
  renderSummary: 'Calgary prairie plaza with open event paving, reflecting pool, timber market stalls and native grass planters', isPilot: true,
};

PROFILES.calgary_princes_island_v0 = {
  id: 'calgary-princes-island-festival-lego-v1', version: 1,
  programDescription: 'A Bow River island park with one festival lawn, cottonwood trail network, wetland/lagoon room, raised boardwalk and a modest outdoor-stage shelter.',
  groundDescription: 'Manicured and meadow greens, pale paths, wetland water, cottonwood foliage and weathered timber sampled from Summer Festival Ground.',
  criticalConstraints: 'Keep festival lawn open and wetland connected. Add whole cottonwood groups and boardwalk bays; generate only a modest park stage, never skyline buildings or people.',
  canopyDescription: 'Cottonwood rows define paths and wetland edges while the event lawn remains open.', plantingStructure: 'calgary_princes_island_v0',
  guides: [
    { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.88, height: 0.78, color: '#a89a80', strokeWidthM: 3.0, fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.31, y: 0.48, width: 0.40, height: 0.36, color: '#6f8d53', fitPolicy: 'clip' },
    { kind: 'ellipse', x: 0.72, y: 0.62, width: 0.28, height: 0.25, color: '#5a7f7c', fitPolicy: 'clip' },
    { kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.58,0.72],[0.70,0.62],[0.84,0.54]], color: '#806447', strokeWidthM: 2.5 },
    { kind: 'rectangle', x: 0.28, y: 0.28, width: 0.17, height: 0.12, color: '#806047', orientationPolicy: 'flexible' },
  ], guideLegend: ['GREEN is festival lawn', 'BLUE is wetland/lagoon', 'BROWN line is boardwalk', 'BROWN block is a modest stage shelter'], includeCentralPlaza: false,
  renderSummary: 'Prince’s Island park with festival lawn, cottonwood paths, wetland lagoon, boardwalk and modest stage shelter', isPilot: true,
};

PROFILES.montreal_mount_royal_v2 = {
  id: 'montreal-mount-royal-grove-lego-v1', version: 1,
  programDescription: 'A Mount Royal hillside park with continuous switchback carriage path, dense maple grove, granite retaining terraces and one whole stone belvedere platform.',
  groundDescription: 'Pale gravel, granite and limestone, deep maple green with autumn accents, dark iron and weathered timber sampled from exact Variant 3.',
  criticalConstraints: 'Maintain an ordered ascent and terrain contact. Add whole path turns and tree cohorts; never stretch or float the belvedere, and do not generate skyline buildings or people.',
  canopyDescription: 'Dense sugar-maple cohorts open only at paths and the belvedere view corridor.', plantingStructure: 'montreal_mount_royal_v2',
  guides: [
    { kind: 'polyline', x: 0.5, y: 0.5, width: 1, height: 1, points: [[0.06,0.82],[0.38,0.72],[0.18,0.56],[0.62,0.46],[0.40,0.28],[0.90,0.17]], color: '#aa987b', strokeWidthM: 3.2 },
    { kind: 'rectangle', x: 0.82, y: 0.18, width: 0.22, height: 0.14, color: '#92908a', orientationPolicy: 'flexible' },
  ], guideLegend: ['TAN switchback is the carriage path', 'GREY block is one whole stone belvedere'], includeCentralPlaza: false,
  renderSummary: 'Mount Royal maple grove with switchback carriage path, stone terraces and terrain-seated belvedere', isPilot: true,
};

PROFILES.montreal_square_v3 = {
  id: 'montreal-neighbourhood-square-lego-v1', version: 1,
  programDescription: 'An intimate Montréal neighbourhood square with geometric gravel walks, central fountain/monument, low iron perimeter, mature maples, seasonal beds and complete bench bays.',
  groundDescription: 'Pale gravel, stone edging, varied lawn, maple green, dark iron and warm timber sampled from exact Variant 4.',
  criticalConstraints: 'Keep the centre visible and all gates clear. Add whole tree-bench bays around one fountain; no surrounding triplex buildings or people.',
  canopyDescription: 'A ring of mature maples shades paths while preserving the central room.', plantingStructure: 'montreal_square_v3',
  guides: [
    { kind: 'path_loop', x: 0.5, y: 0.5, width: 0.82, height: 0.72, color: '#aa9c82', strokeWidthM: 2.4, fitPolicy: 'clip' },
    { kind: 'axis', x: 0.5, y: 0.5, width: 0, height: 0.78, color: '#b1a48e', strokeWidthM: 2.2 },
    { kind: 'axis', x: 0.5, y: 0.5, width: 0, height: 0.78, color: '#b1a48e', strokeWidthM: 2.2, rotationDeg: 90 },
    { kind: 'ellipse', x: 0.5, y: 0.5, width: 0.14, height: 0.14, color: '#8f8b82', strokeColor: '#b8aa92', strokeWidthM: 1.0 },
  ], guideLegend: ['TAN loop and cross are gravel paths', 'GREY centre is one fountain or monument', 'low iron fence follows the outer edge'], includeCentralPlaza: false,
  renderSummary: 'Montréal neighbourhood square with geometric gravel walks, central fountain, iron perimeter, mature maples and benches', isPilot: true,
};

PROFILES.parisian_place_v2 = {
  id: 'paris-place-royale-lego-v1', version: 1,
  programDescription: 'A ceremonial Parisian place with an uninterrupted cobbled centre, disciplined edge tree bays, removable café clusters and four clear approaches.',
  groundDescription: 'Variegated pale cobble, limestone edging, clipped green and dark iron sampled from exact Variant 3.',
  criticalConstraints: 'Keep the civic centre open and all approaches legible; do not emit surrounding façades or people.',
  canopyDescription: 'Small formal tree groups stay at the perimeter.', plantingStructure: 'paris_place_royale_v2',
  guides: [{ kind:'rounded_rectangle',x:.5,y:.5,width:.78,height:.66,color:'#a9a095',orientationPolicy:'orthogonal' },{ kind:'axis',x:.5,y:.5,width:0,height:.86,color:'#c1b8a8',strokeWidthM:4 },{ kind:'axis',x:.5,y:.5,width:0,height:.86,color:'#c1b8a8',strokeWidthM:4,rotationDeg:90 }],
  guideLegend:['PALE centre is open cobbled civic space','cross axes preserve four approaches'], includeCentralPlaza:true, renderSummary:'Paris place royale with open cobbled centre, formal edge trees and removable café bays', isPilot:true,
};
PROFILES.parisian_square_v3 = {
  id:'paris-square-tree-grid-lego-v1',version:1,programDescription:'An intimate Parisian square with a gravel social room, ordered tree grid, complete bench bays and a low perimeter.',
  groundDescription:'Pale gravel, limestone, mature plane-tree green and dark metal sampled from exact Variant 4.',criticalConstraints:'Preserve a shaded centre and clear gates; exclude enclosing buildings and people.',canopyDescription:'A regular plane-tree grid creates a high shaded ceiling.',plantingStructure:'paris_square_tree_grid_v3',
  guides:[{kind:'rounded_rectangle',x:.5,y:.5,width:.78,height:.68,color:'#ac9d83',orientationPolicy:'orthogonal'},{kind:'path_loop',x:.5,y:.5,width:.86,height:.76,color:'#beb39e',strokeWidthM:2.4,fitPolicy:'clip'}],guideLegend:['TAN room is social gravel','loop is the shaded circulation edge'],includeCentralPlaza:true,renderSummary:'Paris square with gravel room, ordered tree grid, perimeter and whole bench bays',isPilot:true,
};
PROFILES.london_circus_v1 = {
  id:'london-circus-planted-lego-v1',version:1,programDescription:'A rounded London circus public room with radial pedestrian spokes, a planted central island, curved seating and a clear cycle ring.',groundDescription:'Warm stone, brick, clipped planting and dark metal sampled from exact Variant 2.',criticalConstraints:'Keep the circular geometry and complete radial routes; do not emit surrounding crescent buildings or people.',canopyDescription:'Trees reinforce the circular edge and central planted room.',plantingStructure:'london_circus_planted_v1',
  guides:[{kind:'ellipse',x:.5,y:.5,width:.68,height:.68,color:'#9ba079'},{kind:'path_loop',x:.5,y:.5,width:.82,height:.82,color:'#aaa092',strokeWidthM:3,fitPolicy:'clip'},{kind:'axis',x:.5,y:.5,width:0,height:.88,color:'#c1b6a3',strokeWidthM:3,rotationDeg:45},{kind:'axis',x:.5,y:.5,width:0,height:.88,color:'#c1b6a3',strokeWidthM:3,rotationDeg:-45}],guideLegend:['GREEN disc is planted island','TAN ring and spokes stay clear'],includeCentralPlaza:true,renderSummary:'London circus with planted centre, radial paths, curved benches and cycle ring',isPilot:true,
};
PROFILES.newyork_pocket_park_v0 = {
  id:'newyork-pocket-water-lego-v1',version:1,programDescription:'A compact Manhattan pocket park with one linear water rill, complete seat-planter bays, dense shade planting and a modest open pergola.',groundDescription:'Dark stone, weathered timber, layered green and reflective water sampled from exact Variant 1.',criticalConstraints:'Protect the entry-to-water route and add whole bays rather than stretched furniture; no people or enclosing towers.',canopyDescription:'Layered small trees enclose the room while keeping the entry visible.',plantingStructure:'newyork_pocket_water_v0',
  guides:[{kind:'rectangle',x:.5,y:.5,width:.72,height:.14,color:'#5f8588',orientationPolicy:'flexible'},{kind:'axis',x:.5,y:.5,width:0,height:.82,color:'#a49988',strokeWidthM:2.6},{kind:'rectangle',x:.2,y:.5,width:.18,height:.64,color:'#536c49',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.8,y:.5,width:.18,height:.64,color:'#536c49',orientationPolicy:'orthogonal'}],guideLegend:['BLUE rill is the water spine','GREEN bands are whole seat-planter bays'],includeCentralPlaza:false,renderSummary:'New York pocket park with water rill, planted seat bays and compact pergola',isPilot:true,
};
PROFILES.newyork_community_garden_v3 = {
  id:'newyork-community-greenhouse-lego-v1',version:1,programDescription:'A productive community garden with whole raised-bed rows, central accessible path, tool/compost bay and one modest greenhouse.',groundDescription:'Brick paths, dark soil, varied crop green, timber and translucent greenhouse panels sampled from exact Variant 4.',criticalConstraints:'Use repeatable complete beds with service access; the greenhouse is a small park utility, never a large building.',canopyDescription:'Fruit trees and vines stay along edges so crop beds receive sun.',plantingStructure:'newyork_community_greenhouse_v3',
  guides:[{kind:'axis',x:.5,y:.5,width:0,height:.88,color:'#a98b6e',strokeWidthM:2.4},{kind:'rectangle',x:.25,y:.5,width:.28,height:.70,color:'#5c734c',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.75,y:.5,width:.28,height:.70,color:'#66794e',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.78,y:.18,width:.18,height:.18,color:'#9aa19b',orientationPolicy:'orthogonal'}],guideLegend:['TAN axis is accessible path','GREEN zones contain whole crop beds','GREY block is one modest greenhouse'],includeCentralPlaza:false,renderSummary:'New York community garden with raised beds, accessible path, compost bay and modest greenhouse',isPilot:true,
};
PROFILES.vancouver_seawall_v2 = {
  id:'vancouver-seawall-cycle-lego-v1',version:1,programDescription:'A linear waterfront promenade with separated walking and cycling lanes, continuous seawall edge, view benches and sparse salt-tolerant planting.',groundDescription:'Grey concrete, muted asphalt, timber seating, dark rail and coastal green sampled from exact Variant 3.',criticalConstraints:'Keep both routes continuous and parallel; repeat whole rest bays, never waterfront buildings or people.',canopyDescription:'Sparse wind-shaped trees mark rest bays without blocking views.',plantingStructure:'vancouver_seawall_cycle_v2',
  guides:[{kind:'axis',x:.5,y:.38,width:0,height:.90,color:'#7f8583',strokeWidthM:4.2,rotationDeg:90},{kind:'axis',x:.5,y:.62,width:0,height:.90,color:'#aaa39a',strokeWidthM:3.2,rotationDeg:90}],guideLegend:['DARK lane is continuous cycle route','PALE lane is continuous promenade'],includeCentralPlaza:false,renderSummary:'Vancouver seawall with separated cycle and walking lanes, seawall edge and view bays',isPilot:true,
};
PROFILES.vancouver_beach_park_v0 = {
  id:'vancouver-beach-pavilion-lego-v1',version:1,programDescription:'A beach-edge park with paired cycle/walk routes, dune planting drifts, view lawns, complete rest bays and one modest open pavilion.',groundDescription:'Pale concrete, sand, coastal grass, cedar and blue-grey accents sampled from exact Variant 1.',criticalConstraints:'Preserve shoreline-parallel movement and view corridors; emit no apartment buildings, vehicles or people.',canopyDescription:'Wind-tolerant trees and dune grasses frame open water views.',plantingStructure:'vancouver_beach_pavilion_v0',
  guides:[{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.04,.64],[.30,.58],[.62,.52],[.96,.44]],color:'#aaa28f',strokeWidthM:4},{kind:'ellipse',x:.55,y:.72,width:.62,height:.24,color:'#728957',fitPolicy:'clip'},{kind:'rectangle',x:.22,y:.24,width:.20,height:.15,color:'#80634b',orientationPolicy:'flexible'}],guideLegend:['TAN route follows the beach','GREEN is dune planting','BROWN is one modest pavilion'],includeCentralPlaza:false,renderSummary:'Vancouver beach park with paired routes, dune planting, view lawn and modest pavilion',isPilot:true,
};
PROFILES.toronto_ravine_v1 = {
  id:'toronto-ravine-creek-lego-v1',version:1,programDescription:'A Toronto ravine corridor with a meandering creek, continuous valley trail, whole footbridge crossings, native understory and deciduous grove cohorts.',groundDescription:'Pale gravel, creek stone, layered green and weathered timber sampled from Summer Creek Shade.',criticalConstraints:'Keep creek and trail continuous and terrain-seated; no houses, skyline buildings or people.',canopyDescription:'Dense maple, oak and cedar cohorts shade the creek with small openings at crossings.',plantingStructure:'toronto_ravine_creek_v1',
  guides:[{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.04,.68],[.25,.55],[.48,.62],[.72,.40],[.96,.34]],color:'#587f82',strokeWidthM:4},{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.04,.40],[.28,.46],[.55,.34],[.78,.50],[.96,.44]],color:'#a3967f',strokeWidthM:3}],guideLegend:['BLUE line is creek','TAN line is valley trail'],includeCentralPlaza:false,renderSummary:'Toronto ravine with creek, continuous trail, bridge crossings and native grove cohorts',isPilot:true,
};
PROFILES.toronto_urban_square_v1 = {
  id:'toronto-urban-market-lego-v1',version:1,programDescription:'A flexible Toronto civic square with open market centre, complete vendor bays, rain-planter seating and four clear pedestrian approaches.',groundDescription:'Variegated grey paver, warm timber, rain-garden green and dark metal sampled from Summer Market Plaza.',criticalConstraints:'Keep the event centre open and add whole vendor bays only; exclude surrounding buildings and people.',canopyDescription:'Shade trees sit in perimeter rain-planter bays.',plantingStructure:'toronto_urban_market_v1',
  guides:[{kind:'rounded_rectangle',x:.5,y:.52,width:.76,height:.58,color:'#a8a49b',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.16,width:.78,height:.14,color:'#667a55',orientationPolicy:'orthogonal'}],guideLegend:['GREY centre remains flexible','GREEN edge contains whole rain-planter and vendor bays'],includeCentralPlaza:true,renderSummary:'Toronto urban square with flexible market centre, rain planters and whole vendor bays',isPilot:true,
};
PROFILES.halifax_coastal_park_v2 = {
  id:'halifax-coastal-fog-path-lego-v1',version:1,programDescription:'A fog-coast forest park with granite gravel path, spruce/fir grove cohorts, low heath planting, whole timber boardwalk bays and one lookout.',groundDescription:'Cool granite, pale gravel, spruce green, fog-muted grass and weathered timber sampled from Foggy Morning Path.',criticalConstraints:'Keep one continuous path and terrain contact; exclude houses, skyline buildings and people.',canopyDescription:'Wind-shaped spruce and fir groups alternate with low coastal openings.',plantingStructure:'halifax_coastal_fog_path_v2',
  guides:[{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.04,.72],[.24,.58],[.48,.62],[.70,.42],[.96,.30]],color:'#a39987',strokeWidthM:3.2},{kind:'rectangle',x:.82,y:.24,width:.20,height:.15,color:'#80644a',orientationPolicy:'flexible'}],guideLegend:['TAN line is granite-gravel path','BROWN block is a whole timber lookout'],includeCentralPlaza:false,renderSummary:'Halifax coastal forest park with fog path, spruce cohorts, heath planting and timber lookout',isPilot:true,
};

PROFILES.city_hall_government_plaza_v2 = { id:'city-hall-modernist-fountain-lego-v1',version:1,programDescription:'A mid-century civic plaza with a long reflecting fountain, orthogonal ceremonial walks, complete raised planter bays and open gathering pavement.',groundDescription:'Warm aggregate concrete, pale stone, blue-grey water, clipped lawn and bronze accents sampled from the exact modernist reference.',criticalConstraints:'Keep the pool and processional axes complete; exclude city-hall buildings, vehicles and people.',canopyDescription:'Disciplined trees occupy only raised perimeter planters.',plantingStructure:'city_hall_modernist_fountain_v2',guides:[{kind:'rounded_rectangle',x:.5,y:.5,width:.84,height:.70,color:'#aaa39a',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.5,width:.50,height:.12,color:'#5d858b',orientationPolicy:'orthogonal'},{kind:'axis',x:.5,y:.5,width:0,height:.90,color:'#c0b5a2',strokeWidthM:3},{kind:'rectangle',x:.16,y:.5,width:.13,height:.50,color:'#64784e',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.84,y:.5,width:.13,height:.50,color:'#64784e',orientationPolicy:'orthogonal'}],guideLegend:['BLUE bar is the reflecting fountain','PALE axis stays ceremonial and clear','GREEN blocks are whole planter bays'],includeCentralPlaza:true,renderSummary:'modernist civic fountain plaza with a long pool, formal axes and planter rooms',isPilot:true};
PROFILES.cathedral_religious_forecourt_v3 = { id:'cathedral-courtyard-fountain-lego-v1',version:1,programDescription:'An Islamic-inspired patterned courtyard with one central fountain, four clear axes, repeated shade-tree bays and a quiet paved perimeter.',groundDescription:'Cream and rose stone geometry, turquoise water, clipped green and dark timber sampled from the exact mosque-courtyard reference.',criticalConstraints:'Preserve the symmetrical courtyard and one fountain; do not generate the mosque, minarets or people.',canopyDescription:'Small shade trees form balanced perimeter rooms.',plantingStructure:'cathedral_courtyard_fountain_v3',guides:[{kind:'rounded_rectangle',x:.5,y:.5,width:.82,height:.74,color:'#b7a58f',orientationPolicy:'orthogonal'},{kind:'axis',x:.5,y:.5,width:0,height:.86,color:'#d0c2aa',strokeWidthM:2.8},{kind:'axis',x:.5,y:.5,width:0,height:.86,color:'#d0c2aa',strokeWidthM:2.8,rotationDeg:90},{kind:'ellipse',x:.5,y:.5,width:.15,height:.15,color:'#568b90'}],guideLegend:['cross axes organize the courtyard','BLUE centre is one complete fountain'],includeCentralPlaza:true,renderSummary:'patterned mosque courtyard with central fountain and balanced shade-tree bays',isPilot:true};
PROFILES.cultural_institution_forecourt_v0 = { id:'cultural-museum-terrace-lego-v1',version:1,programDescription:'A modern museum forecourt composed of a broad arrival terrace, low stepped plinth, sculpture lawn and long seat-planter edges.',groundDescription:'Large-format grey stone, textured concrete, deep lawn and rusted-metal accents sampled from the exact reference.',criticalConstraints:'Keep the stepped approach and sculpture lawn legible; exclude the museum building, large pavilions and people.',canopyDescription:'Sparse specimen trees frame rather than fill the forecourt.',plantingStructure:'cultural_museum_terrace_v0',guides:[{kind:'rectangle',x:.5,y:.62,width:.84,height:.45,color:'#9b9b96',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.34,width:.76,height:.12,color:'#b2ada3',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.16,width:.62,height:.22,color:'#607b4d',orientationPolicy:'orthogonal'}],guideLegend:['GREY room is arrival terrace','PALE band is broad steps','GREEN room is sculpture lawn'],includeCentralPlaza:true,renderSummary:'modern museum terrace with steps, sculpture lawn and seat-planter edges',isPilot:true};
PROFILES.transit_plaza_v2 = { id:'transit-green-civic-lego-v1',version:1,programDescription:'A green civic transit plaza with one uninterrupted access spine, modest open shelters, rain-planter seating bays and clear boarding edges.',groundDescription:'Variegated unit pavers, charcoal transit bands, fresh planting and weathered metal sampled from the exact reference.',criticalConstraints:'Keep the access and boarding paths continuous; emit only modest open shelters, never stations, buses or people.',canopyDescription:'Street trees repeat in rain-planter bays outside circulation.',plantingStructure:'transit_green_civic_v2',guides:[{kind:'axis',x:.5,y:.5,width:0,height:.90,color:'#888b87',strokeWidthM:5,rotationDeg:90},{kind:'rectangle',x:.5,y:.22,width:.78,height:.20,color:'#5c7750',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.24,y:.76,width:.20,height:.12,color:'#79614c',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.76,y:.76,width:.20,height:.12,color:'#79614c',orientationPolicy:'orthogonal'}],guideLegend:['DARK spine is uninterrupted transit access','GREEN band contains rain planters','BROWN blocks are modest shelters'],includeCentralPlaza:true,renderSummary:'green transit plaza with clear access spine, rain planters and modest shelters',isPilot:true};
PROFILES.amphitheater_performance_space_v0 = { id:'amphitheater-terraced-lego-v1',version:1,programDescription:'A terrain-seated amphitheater with concentric complete seating terraces, central performance floor, modest stage platform and accessible rim route.',groundDescription:'Weathered timber, warm concrete, lawn terraces and dark stage surfacing sampled from the exact reference.',criticalConstraints:'Maintain the bowl hierarchy and sightline opening; do not emit a roofed theatre, surrounding buildings or people.',canopyDescription:'Trees shade only the upper rim and leave the bowl open.',plantingStructure:'amphitheater_terraced_v0',guides:[{kind:'ellipse',x:.5,y:.56,width:.78,height:.66,color:'#6d8756'},{kind:'ellipse',x:.5,y:.58,width:.58,height:.44,color:'#9a8f78'},{kind:'ellipse',x:.5,y:.60,width:.38,height:.25,color:'#7d735f'},{kind:'rectangle',x:.5,y:.30,width:.28,height:.14,color:'#765540',orientationPolicy:'flexible'}],guideLegend:['nested rings are complete seating terraces','BROWN block is one modest stage'],includeCentralPlaza:false,renderSummary:'terraced performance bowl with complete seating rings, stage and accessible rim',isPilot:true};
PROFILES.concert_pavilion_lawn_v2 = { id:'concert-timber-lawn-lego-v1',version:1,programDescription:'A large audience lawn focused on one modest open timber stage canopy, with perimeter paths and tree-grove side rooms.',groundDescription:'Layered turf, gravel paths, dark timber and muted metal sampled from the exact Tanglewood reference.',criticalConstraints:'Keep the audience lawn unobstructed; generate only a modest park stage canopy, never the reference concert-hall building or people.',canopyDescription:'Mature groves frame the lawn sides and preserve the stage view cone.',plantingStructure:'concert_timber_lawn_v2',guides:[{kind:'ellipse',x:.5,y:.57,width:.70,height:.58,color:'#678451'},{kind:'rectangle',x:.5,y:.20,width:.28,height:.16,color:'#70513d',orientationPolicy:'orthogonal'},{kind:'path_loop',x:.5,y:.52,width:.86,height:.76,color:'#aa9e88',strokeWidthM:3,fitPolicy:'clip'}],guideLegend:['GREEN room is audience lawn','BROWN block is modest open stage','loop is perimeter circulation'],includeCentralPlaza:false,renderSummary:'concert lawn with open audience room, timber stage canopy and perimeter groves',isPilot:true};
PROFILES.night_market_v0 = { id:'night-market-hawker-lego-v1',version:1,programDescription:'A narrow market lane with two repeatable rows of complete hawker stalls, lantern cables, service gaps and an open central promenade.',groundDescription:'Dark worn pavers, warm timber, varied awnings and jewel-toned lantern accents sampled from the exact hawker-lane reference.',criticalConstraints:'Keep the central lane and cross-gaps clear; use whole stall bays and no people, vehicles or enclosing buildings.',canopyDescription:'Minimal trees at entries so the stall lane remains legible.',plantingStructure:'night_market_hawker_v0',guides:[{kind:'axis',x:.5,y:.5,width:0,height:.90,color:'#8f8170',strokeWidthM:5,rotationDeg:90},{kind:'rectangle',x:.5,y:.22,width:.84,height:.20,color:'#7b533a',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.78,width:.84,height:.20,color:'#7b533a',orientationPolicy:'orthogonal'}],guideLegend:['TAN spine is open market lane','BROWN bands contain whole stall bays'],includeCentralPlaza:true,renderSummary:'Asian hawker lane with complete stall rows, service gaps and lantern canopy',isPilot:true};
PROFILES.parade_ground_v3 = { id:'parade-national-mall-lego-v1',version:1,programDescription:'A long ceremonial mall with continuous central lawn, linear reflecting water, parallel formal walks and regular tree allées.',groundDescription:'Varied lawn, pale gravel, blue-grey water and dark mature canopy sampled from the exact National Mall reference.',criticalConstraints:'Preserve the uninterrupted axis and water geometry; exclude monuments, government buildings, roads, vehicles and people.',canopyDescription:'Formal double tree rows reinforce but never block the central view axis.',plantingStructure:'parade_national_mall_v3',guides:[{kind:'rectangle',x:.5,y:.5,width:.86,height:.54,color:'#67804f',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.5,width:.56,height:.10,color:'#5d848a',orientationPolicy:'orthogonal'},{kind:'axis',x:.5,y:.25,width:0,height:.88,color:'#b1a58f',strokeWidthM:3,rotationDeg:90},{kind:'axis',x:.5,y:.75,width:0,height:.88,color:'#b1a58f',strokeWidthM:3,rotationDeg:90}],guideLegend:['GREEN band is continuous ceremonial lawn','BLUE bar is reflecting water','parallel TAN lines are formal walks'],includeCentralPlaza:false,renderSummary:'National Mall ceremonial axis with lawn, reflecting water, walks and tree allées',isPilot:true};
PROFILES.canal_waterway_v3 = { id:'canal-ecological-wetland-lego-v1',version:1,programDescription:'An ecological canal with one continuous water channel, repeatable marsh cells, parallel maintenance path and whole boardwalk crossings.',groundDescription:'Silted blue-green water, reed beds, weathered timber and granular paths sampled from the exact wetland reference.',criticalConstraints:'Keep water and dry route continuous; bridges span the channel as whole units and no people or buildings are generated.',canopyDescription:'Willow and wetland shrubs occupy bank cells without filling the channel.',plantingStructure:'canal_ecological_wetland_v3',guides:[{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.03,.58],[.28,.48],[.52,.54],[.76,.42],[.97,.46]],color:'#537d80',strokeWidthM:8},{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.03,.74],[.28,.64],[.52,.70],[.76,.58],[.97,.62]],color:'#a1937c',strokeWidthM:3},{kind:'rectangle',x:.30,y:.52,width:.22,height:.30,color:'#607750',orientationPolicy:'flexible'},{kind:'rectangle',x:.72,y:.46,width:.22,height:.30,color:'#657a50',orientationPolicy:'flexible'}],guideLegend:['BLUE line is continuous canal','TAN line is maintenance path','GREEN blocks are whole marsh cells'],includeCentralPlaza:false,renderSummary:'ecological wetland canal with marsh cells, boardwalk crossings and continuous dry path',isPilot:true};
PROFILES.custom_parks_plazas_v1 = { id:'custom-biophilic-urban-lego-v1',version:1,programDescription:'A biophilic urban park assembled as linked planted rooms, a meandering accessible path, rain-garden pockets and complete integrated seat-planter bays.',groundDescription:'Complex green foliage, mottled stone, weathered timber and moist planting soil sampled from the exact biophilic reference.',criticalConstraints:'Keep all paths connected and adapt room counts to the polygon; do not stretch furniture, add generic lawn filler, buildings or people.',canopyDescription:'Layered small-canopy trees and understory form distinct rooms with open path windows.',plantingStructure:'custom_biophilic_urban_v1',guides:[{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.05,.70],[.25,.42],[.48,.58],[.70,.32],[.95,.48]],color:'#a99d88',strokeWidthM:3},{kind:'ellipse',x:.24,y:.68,width:.30,height:.28,color:'#56764c'},{kind:'ellipse',x:.52,y:.28,width:.30,height:.24,color:'#657f50'},{kind:'ellipse',x:.78,y:.66,width:.28,height:.27,color:'#4f704a'}],guideLegend:['TAN line is connected accessible path','GREEN ovals are whole layered garden rooms'],includeCentralPlaza:false,renderSummary:'biophilic urban park with linked garden rooms, rain pockets and integrated seating',isPilot:true};
PROFILES.rooftop_garden_v0 = {id:'rooftop-intensive-garden-lego-v1',version:1,programDescription:'An intensive rooftop garden deck with complete raised planting rooms, one accessible circulation loop, integrated seat walls, wind screens and a modest open pergola.',groundDescription:'Pale pavers, deep planting soil, layered shrubs, small ornamental trees, weathered timber and dark metal sampled from the exact intensive-garden reference.',criticalConstraints:'Treat the drawn polygon as the roof deck; keep a safe parapet setback and do not generate the supporting building, people or oversized rooftop structures.',canopyDescription:'Small wind-tolerant trees and layered shrubs stay inside raised beds.',plantingStructure:'rooftop_intensive_garden_v0',guides:[{kind:'rounded_rectangle',x:.5,y:.5,width:.86,height:.78,color:'#a8a197',orientationPolicy:'orthogonal'},{kind:'path_loop',x:.5,y:.5,width:.72,height:.62,color:'#c0b39e',strokeWidthM:2,fitPolicy:'clip'},{kind:'rectangle',x:.24,y:.5,width:.22,height:.58,color:'#567449',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.76,y:.5,width:.22,height:.58,color:'#607b4d',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.20,width:.22,height:.14,color:'#75543f',orientationPolicy:'orthogonal'}],guideLegend:['GREEN rooms are whole intensive planters','loop is accessible circulation','BROWN block is a modest open pergola'],includeCentralPlaza:false,renderSummary:'intensive roof garden deck with raised planting rooms, loop, seating and modest pergola',isPilot:true};
PROFILES.garden_healing = {id:'community-healing-garden-lego-v1',version:1,programDescription:'A therapeutic community garden organized as a calm accessible loop, sensory planting rooms, raised horticultural beds, quiet seating niches and one modest open pergola.',groundDescription:'Warm permeable paving, timber, fragrant planting, varied perennial colour and soft lawn sampled from the exact healing-garden reference.',criticalConstraints:'Keep the accessible loop continuous and every bed reachable; do not generate clinic buildings, people or generic playground equipment.',canopyDescription:'Small flowering trees shade seating without closing the garden rooms.',plantingStructure:'community_healing_garden_v2',guides:[{kind:'path_loop',x:.5,y:.5,width:.82,height:.72,color:'#b2a38d',strokeWidthM:2.5,fitPolicy:'clip'},{kind:'ellipse',x:.28,y:.42,width:.30,height:.30,color:'#65784d'},{kind:'ellipse',x:.68,y:.58,width:.32,height:.30,color:'#5b744b'},{kind:'rectangle',x:.50,y:.20,width:.22,height:.13,color:'#75543f',orientationPolicy:'flexible'}],guideLegend:['TAN loop is fully accessible','GREEN rooms are sensory and horticultural beds','BROWN block is one modest pergola'],includeCentralPlaza:false,renderSummary:'community healing garden with accessible loop, sensory beds and quiet pergola',isPilot:true};
PROFILES.greenbelt_buffer_park_v1 = {id:'greenbelt-rail-trail-lego-v1',version:1,programDescription:'A long forested greenbelt with one continuous multi-use rail-trail, woodland buffer cohorts, understory strips and repeatable complete rest bays.',groundDescription:'Dark asphalt, pale gravel shoulders, mature conifer-deciduous green and weathered timber sampled from the exact commuter rail-trail reference.',criticalConstraints:'Maintain a continuous clear trail and buffer width; add or omit whole rest bays rather than widening the trail, and do not generate trains, buildings or people.',canopyDescription:'Dense edge cohorts form a corridor while preserving trail clearance.',plantingStructure:'greenbelt_rail_trail_v1',guides:[{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.03,.56],[.26,.48],[.52,.54],[.76,.45],[.97,.50]],color:'#515552',strokeWidthM:4},{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.03,.68],[.26,.60],[.52,.66],[.76,.57],[.97,.62]],color:'#a0947e',strokeWidthM:2}],guideLegend:['DARK line is continuous multi-use trail','TAN line is a soft parallel shoulder'],includeCentralPlaza:false,renderSummary:'forested greenbelt rail-trail with continuous route, woodland buffers and rest bays',isPilot:true};
PROFILES.foothill_trail_park_v2 = {id:'foothill-heathland-trail-lego-v1',version:1,programDescription:'A terrain-led heathland park with a continuous ridge trail, branching short loops, whole heather drift cells, stone outcrops and compact viewpoint bays.',groundDescription:'Ochre gravel, exposed stone, purple-brown heather and muted upland grasses sampled from the exact heathland-moor reference.',criticalConstraints:'Seat every route and rock on terrain, keep the ridge path continuous and do not flatten the site into lawn or generate huts, people or buildings.',canopyDescription:'Low scrub and sparse wind-shaped trees preserve open ridge views.',plantingStructure:'foothill_heathland_trail_v2',guides:[{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.04,.76],[.22,.56],[.46,.62],[.66,.40],[.95,.28]],color:'#a18464',strokeWidthM:2.8},{kind:'ellipse',x:.28,y:.34,width:.34,height:.28,color:'#716447'},{kind:'ellipse',x:.72,y:.68,width:.34,height:.26,color:'#655c45'}],guideLegend:['TAN line is the terrain-seated ridge trail','EARTH rooms are whole heathland drift cells'],includeCentralPlaza:false,renderSummary:'heathland foothill park with ridge trail, heather drifts, stone outcrops and viewpoints',isPilot:true};
PROFILES.marina_yacht_harbor_v2 = {id:'marina-pacific-dock-lego-v1',version:1,programDescription:'A Pacific-style marina basin with one continuous public quay, modular floating dock fingers, gangways, utility pedestals and an unobstructed water manoeuvring channel.',groundDescription:'Blue-grey water, weathered timber, dark floats, galvanized rails and cool concrete sampled from the exact floating-dock reference.',criticalConstraints:'Repeat complete dock fingers at fixed spacing and keep the navigation channel open; do not render boats, marina buildings or people.',canopyDescription:'Sparse salt-tolerant planting stays on the landward quay.',plantingStructure:'marina_pacific_dock_v2',guides:[{kind:'rectangle',x:.5,y:.56,width:.88,height:.66,color:'#527b80',orientationPolicy:'orthogonal'},{kind:'axis',x:.5,y:.18,width:0,height:.88,color:'#a6a098',strokeWidthM:5,rotationDeg:90},{kind:'axis',x:.22,y:.55,width:0,height:.54,color:'#765840',strokeWidthM:2.4},{kind:'axis',x:.42,y:.55,width:0,height:.54,color:'#765840',strokeWidthM:2.4},{kind:'axis',x:.62,y:.55,width:0,height:.54,color:'#765840',strokeWidthM:2.4},{kind:'axis',x:.82,y:.55,width:0,height:.54,color:'#765840',strokeWidthM:2.4}],guideLegend:['BLUE room is open marina water','PALE line is public quay','BROWN fingers are complete floating docks'],includeCentralPlaza:false,renderSummary:'Pacific marina basin with public quay, modular floating docks and clear water channel',isPilot:true};
PROFILES.working_pier_wharf_conversion_v3 = {id:'working-pier-brooklyn-park-lego-v1',version:1,programDescription:'A converted public pier with a continuous deck spine, complete lawn and planting rooms, edge promenade, view-bench bays and preserved service clearances.',groundDescription:'Weathered timber and concrete, textured lawn, coastal planting and dark steel rails sampled from the exact Brooklyn park-pier reference.',criticalConstraints:'Preserve the pier outline and clear edge route; exclude skyline, bridge, market buildings, kiosks and people because architecture is generated separately.',canopyDescription:'Small wind-tolerant trees occupy planted rooms without blocking edge views.',plantingStructure:'working_pier_brooklyn_park_v3',guides:[{kind:'rounded_rectangle',x:.5,y:.5,width:.88,height:.72,color:'#928b82',orientationPolicy:'orthogonal'},{kind:'axis',x:.5,y:.5,width:0,height:.84,color:'#b5aa98',strokeWidthM:4,rotationDeg:90},{kind:'rectangle',x:.34,y:.40,width:.28,height:.34,color:'#66804f',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.68,y:.62,width:.28,height:.30,color:'#5c774b',orientationPolicy:'orthogonal'}],guideLegend:['GREY field is continuous pier deck','TAN spine stays clear','GREEN blocks are complete park rooms'],includeCentralPlaza:false,renderSummary:'landscaped Brooklyn-style park pier with deck spine, lawns, planting and view bays',isPilot:true};
PROFILES.floating_park_pool_v2 = {id:'floating-meadow-loop-lego-v1',version:1,programDescription:'A floating park assembled from complete buoyant meadow islands connected by one continuous boardwalk loop, with rail edges and compact pause decks.',groundDescription:'Blue-grey water, weathered timber, meadow grasses and layered perennial colour sampled from the exact floating-boardwalk reference.',criticalConstraints:'Keep every island separated from water and every boardwalk connection complete; do not render pools, boats, buildings or people.',canopyDescription:'Low meadow planting and a few small trees keep wind exposure and water views legible.',plantingStructure:'floating_meadow_loop_v2',guides:[{kind:'ellipse',x:.5,y:.5,width:.84,height:.72,color:'#537c81'},{kind:'path_loop',x:.5,y:.5,width:.68,height:.56,color:'#785a42',strokeWidthM:3,fitPolicy:'clip'},{kind:'ellipse',x:.34,y:.48,width:.28,height:.30,color:'#68804e'},{kind:'ellipse',x:.66,y:.52,width:.28,height:.30,color:'#5f794b'}],guideLegend:['BLUE room is surrounding water','BROWN loop is continuous boardwalk','GREEN islands are whole meadow modules'],includeCentralPlaza:false,renderSummary:'floating meadow islands joined by a continuous timber boardwalk loop',isPilot:true};
PROFILES.lighthouse_point_park_v2 = {id:'lighthouse-pacific-headland-lego-v1',version:1,programDescription:'A Pacific cliff-headland park with a safe setback loop, wind-shaped grove cells, rock outcrops, viewpoint bays and a reserved lighthouse-building footprint.',groundDescription:'Cool rock, pale gravel, coastal heath, dark evergreen and weathered timber sampled from the exact promontory reference.',criticalConstraints:'Keep paths behind the cliff setback and reserve the landmark pad, but do not generate the lighthouse building, support buildings or people.',canopyDescription:'Wind-shaped evergreens cluster inland while the ocean-facing edge stays low and open.',plantingStructure:'lighthouse_pacific_headland_v2',guides:[{kind:'path_loop',x:.5,y:.5,width:.78,height:.68,color:'#a69a84',strokeWidthM:2.6,fitPolicy:'clip'},{kind:'ellipse',x:.72,y:.42,width:.23,height:.23,color:'#98918a'},{kind:'ellipse',x:.28,y:.58,width:.34,height:.34,color:'#526a49'}],guideLegend:['TAN loop follows safe cliff setback','GREY circle reserves the separate lighthouse building','GREEN room is wind-shaped grove'],includeCentralPlaza:false,renderSummary:'Pacific headland park with setback trail, cliff viewpoints, coastal grove and lighthouse reservation',isPilot:true};
PROFILES.lake_edge_plaza_v2 = {id:'lake-edge-timber-deck-lego-v1',version:1,programDescription:'A linear lake-edge public room with a continuous timber promenade, whole step-seat bays, rain-planter pockets, guardrail and clear landward access.',groundDescription:'Weathered warm timber, mottled stone, blue-grey water and layered shoreline planting sampled from the exact modern lakefront deck reference.',criticalConstraints:'Keep the shoreline route continuous and the water edge protected; do not render adjacent buildings, boats or people.',canopyDescription:'Regular shade trees and grasses occupy landward planter bays only.',plantingStructure:'lake_edge_timber_deck_v2',guides:[{kind:'axis',x:.5,y:.48,width:0,height:.90,color:'#785a40',strokeWidthM:7,rotationDeg:90},{kind:'axis',x:.5,y:.70,width:0,height:.90,color:'#527b80',strokeWidthM:8,rotationDeg:90},{kind:'rectangle',x:.25,y:.28,width:.22,height:.18,color:'#60784d',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.72,y:.28,width:.22,height:.18,color:'#687e50',orientationPolicy:'orthogonal'}],guideLegend:['BROWN line is continuous timber promenade','BLUE edge is lake water','GREEN blocks are whole rain-planter bays'],includeCentralPlaza:false,renderSummary:'modern timber lakefront deck with continuous promenade, seating steps and rain planters',isPilot:true};
PROFILES.stormwater_naturalized_drainage_corridor_variant_0 = {id:'stormwater-natural-creek-lego-v1',version:1,programDescription:'A naturalized drainage corridor with one continuous low-flow creek, floodplain bench cells, riparian planting, a parallel accessible trail and complete bridge crossings.',groundDescription:'Silted water, rounded creek stone, wet meadow, dense riparian green and weathered timber sampled from the exact naturalized-creek reference.',criticalConstraints:'Maintain hydraulic continuity and separate the dry trail from the low-flow channel; do not generate buildings, vehicles or people.',canopyDescription:'Riparian willow and shrub cohorts alternate with open floodplain cells.',plantingStructure:'stormwater_natural_creek_v0',guides:[{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.03,.62],[.25,.48],[.50,.57],[.74,.41],[.97,.50]],color:'#537d80',strokeWidthM:6},{kind:'polyline',x:.5,y:.5,width:1,height:1,points:[[.03,.78],[.25,.64],[.50,.73],[.74,.57],[.97,.66]],color:'#a0947f',strokeWidthM:3},{kind:'ellipse',x:.32,y:.36,width:.32,height:.24,color:'#61794d'},{kind:'ellipse',x:.70,y:.70,width:.30,height:.22,color:'#57734a'}],guideLegend:['BLUE line is continuous low-flow creek','TAN line is accessible trail','GREEN cells are floodplain planting benches'],includeCentralPlaza:false,renderSummary:'naturalized stormwater creek with floodplain cells, riparian planting, trail and bridges',isPilot:true};
PROFILES.surface_parking_lot_v0 = {id:'surface-parking-standard-lego-v1',version:1,programDescription:'A standard surface lot assembled from regulation-size parking stalls, complete double-loaded rows, drive aisles, accessible bays, curbed tree islands and light poles.',groundDescription:'Mottled dark asphalt, pale striping, concrete curb and sparse planting sampled from the exact standard-asphalt reference.',criticalConstraints:'Add or remove whole stall rows to fit the polygon; never enlarge stalls, overlap rows, generate buildings or people.',canopyDescription:'Sparse trees occupy curbed islands outside every clear drive aisle.',plantingStructure:'surface_parking_standard_v0',guides:[{kind:'rounded_rectangle',x:.5,y:.5,width:.90,height:.84,color:'#505352',orientationPolicy:'orthogonal'},{kind:'axis',x:.5,y:.5,width:0,height:.82,color:'#d8d4c8',strokeWidthM:.15,rotationDeg:90}],guideLegend:['DARK field is the parking module','PALE marks indicate regulation stall rows'],includeCentralPlaza:false,renderSummary:'standard asphalt parking with regulation stalls, drive aisles, curbed islands and lights',isPilot:true};
PROFILES.structured_parking_garage_v2 = {id:'structured-parking-urban-lego-v1',version:1,programDescription:'An urban parking-garage site with a separate-building reservation, clear vehicle arrival aisle, pedestrian threshold, ramp alignment and landscape buffer.',groundDescription:'Warm concrete, charcoal asphalt, perforated-metal grey and restrained planting sampled from the exact urban-structured reference.',criticalConstraints:'Reserve the garage footprint but do not generate the large garage building, retail wrap, vehicles in motion or people.',canopyDescription:'Street trees remain outside the reserved garage footprint and turning envelope.',plantingStructure:'structured_parking_urban_v2',guides:[{kind:'rectangle',x:.5,y:.44,width:.72,height:.62,color:'#a19d95',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.86,width:.82,height:.20,color:'#505352',orientationPolicy:'orthogonal'}],guideLegend:['GREY block reserves the separate garage building','DARK apron is vehicle and pedestrian arrival'],includeCentralPlaza:false,renderSummary:'urban structured-parking site with garage reservation and complete arrival circulation',isPilot:true};
PROFILES.underground_parking_entry_v1 = {id:'underground-parking-green-lego-v1',version:1,programDescription:'A landscaped surface above underground parking with one complete descending vehicle ramp, retaining walls, guardrails, ventilation grates and accessible surface paths.',groundDescription:'Pale concrete, charcoal ramp paving, lawn and layered green infrastructure sampled from the exact landscaped entry reference.',criticalConstraints:'Keep the below-grade garage invisible and the ramp opening clear; do not generate surface stalls, a garage building or people.',canopyDescription:'Trees and rain planting frame but never obstruct ramp sightlines.',plantingStructure:'underground_parking_green_v1',guides:[{kind:'rounded_rectangle',x:.5,y:.5,width:.92,height:.88,color:'#69845b',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.58,width:.28,height:.48,color:'#414443',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.23,y:.24,width:.13,height:.08,color:'#353a39',orientationPolicy:'orthogonal'}],guideLegend:['GREEN field is usable surface landscape','DARK slot is the complete ramp opening','small DARK block is a flush ventilation grate'],includeCentralPlaza:false,renderSummary:'landscaped underground-parking surface with complete ramp opening, walls and grates',isPilot:true};
PROFILES.green_parking_lot_v1 = {id:'green-parking-infrastructure-lego-v1',version:1,programDescription:'A permeable parking lot with complete regulation stall rows, generous tree islands, continuous bioswales, rain-garden low points and optional open solar canopies.',groundDescription:'Green-grey grass pavers, bioswale grasses, concrete grid and weathered metal sampled from the exact green-infrastructure reference.',criticalConstraints:'Preserve standard stall and aisle dimensions; repeat whole rows and bioswale cells rather than stretching them, and generate no buildings or people.',canopyDescription:'Shade trees repeat in generous islands at row ends and bioswales.',plantingStructure:'green_parking_infrastructure_v1',guides:[{kind:'rounded_rectangle',x:.5,y:.5,width:.90,height:.84,color:'#728469',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.82,width:.78,height:.10,color:'#526f4b',orientationPolicy:'orthogonal'}],guideLegend:['GREEN-GREY field is permeable parking','DARK GREEN band is a continuous bioswale'],includeCentralPlaza:false,renderSummary:'permeable green parking with regulation rows, tree islands and bioswales',isPilot:true};
PROFILES.airport_airfield_variant_2 = {id:'airport-general-aviation-lego-v1',version:1,programDescription:'A general-aviation airfield organized around one complete runway, parallel taxiway logic, apron stands, small-aircraft kit and reserved hangar/terminal footprints.',groundDescription:'Weathered runway asphalt, pale apron concrete, dry grass and muted safety markings sampled from the exact general-aviation reference.',criticalConstraints:'Keep runway clearances and taxi connectivity legible; reserve hangars and terminal as separate buildings and generate no people.',canopyDescription:'Low airfield grass only; no trees within runway or taxiway safety areas.',plantingStructure:'airport_general_aviation_v2',guides:[{kind:'rectangle',x:.5,y:.62,width:.86,height:.26,color:'#494d4e',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.28,y:.19,width:.34,height:.20,color:'#8d8d88',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.17,y:.08,width:.26,height:.08,color:'#b0ada5',orientationPolicy:'orthogonal'}],guideLegend:['DARK band is one complete runway','GREY apron receives aircraft stands','PALE block reserves separate hangars'],includeCentralPlaza:false,renderSummary:'general-aviation airfield with complete runway, apron, aircraft stands and hangar reservations',isPilot:true};
PROFILES.equestrian_center_variant_1 = {id:'equestrian-working-stable-lego-v1',version:1,programDescription:'A rustic working equestrian centre with one complete sand arena, fenced paddock cells, round-pen logic, service lane and a separately reserved stable footprint.',groundDescription:'Weathered timber, compacted earth, sand, sparse pasture and galvanized hardware sampled from the exact working-stable reference.',criticalConstraints:'Keep every arena and paddock enclosure complete; reserve the large barn separately and do not generate horses, people or grandstands.',canopyDescription:'Sparse shade trees sit outside fences and riding clearances.',plantingStructure:'equestrian_working_stable_v1',guides:[{kind:'rectangle',x:.66,y:.58,width:.52,height:.48,color:'#a68a67',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.20,y:.30,width:.28,height:.22,color:'#6f5844',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.18,y:.80,width:.16,height:.20,color:'#75805b',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.36,y:.80,width:.16,height:.20,color:'#75805b',orientationPolicy:'orthogonal'}],guideLegend:['TAN room is a complete riding arena','BROWN block reserves the stable building','GREEN cells are fenced paddocks'],includeCentralPlaza:false,renderSummary:'rustic equestrian centre with sand arena, paddocks and separate stable reservation',isPilot:true};
PROFILES.golf_course_18_hole_variant_0 = {id:'golf-seaside-links-lego-v1',version:1,programDescription:'A seaside links grammar of complete tee-fairway-green hole modules, revetted pot bunkers, dune rough, flags and a connected walking/cart route; capacity scales only by whole holes.',groundDescription:'Fawn dune grass, firm striped turf, pale sand and dark stone sampled from the exact seaside-links reference.',criticalConstraints:'Preserve playable tee-to-green sequences and whole bunkers; never stretch one fairway to fill an oversized polygon or generate clubhouse buildings or people.',canopyDescription:'Treeless dune rough and marram grass preserve the open coastal character.',plantingStructure:'golf_seaside_links_v0',guides:[{kind:'rounded_rectangle',x:.5,y:.5,width:.96,height:.94,color:'#8a805d',orientationPolicy:'flexible'},{kind:'ellipse',x:.24,y:.34,width:.14,height:.28,color:'#6f8656'},{kind:'ellipse',x:.50,y:.58,width:.14,height:.28,color:'#6f8656'},{kind:'ellipse',x:.76,y:.38,width:.14,height:.28,color:'#6f8656'}],guideLegend:['EARTH field is dune rough','GREEN capsules are complete hole modules repeated by capacity'],includeCentralPlaza:false,renderSummary:'seaside links with capacity-aware whole holes, dune rough, pot bunkers and flags',isPilot:true};
PROFILES.golf_driving_range_variant_0 = {id:'driving-range-single-tier-lego-v1',version:1,programDescription:'A single-tier driving range with one deep landing corridor, distance targets, flags, continuous side netting and a complete row of open covered hitting bays.',groundDescription:'Striped turf, worn tee concrete, weathered timber and dark net poles sampled from the exact covered single-tier reference.',criticalConstraints:'Preserve range depth and a clear firing corridor; the open bay canopy is modest, while pro-shop buildings are reserved separately; no people.',canopyDescription:'Trees remain beyond side netting and never enter the landing field.',plantingStructure:'driving_range_single_tier_v0',guides:[{kind:'rectangle',x:.5,y:.54,width:.82,height:.82,color:'#668052',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.91,width:.72,height:.11,color:'#88877f',orientationPolicy:'orthogonal'}],guideLegend:['GREEN field is the landing corridor','GREY band is the complete open hitting-bay row'],includeCentralPlaza:false,renderSummary:'single-tier driving range with target field, tall netting and open covered bays',isPilot:true};
PROFILES.multi_sport_complex_variant_3 = {id:'multi-sport-track-field-lego-v1',version:1,programDescription:'A track-and-field precinct with a complete 400 m-style oval grammar, striped infield, floodlight kit, spectator edge and a separately reserved fieldhouse footprint.',groundDescription:'Red synthetic track, striped green turf, pale concrete and brick-grey accents sampled from the exact track-and-field reference.',criticalConstraints:'Keep the oval and infield as one complete regulation-shaped module; reserve the large fieldhouse separately and generate no grandstand building or people.',canopyDescription:'Sparse plaza trees remain outside athletic safety zones.',plantingStructure:'multi_sport_track_field_v3',guides:[{kind:'ellipse',x:.60,y:.5,width:.66,height:.72,color:'#a85443'},{kind:'rectangle',x:.60,y:.5,width:.42,height:.39,color:'#5f8252',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.11,y:.5,width:.14,height:.44,color:'#9a958b',orientationPolicy:'orthogonal'}],guideLegend:['RED oval is the complete track module','GREEN rectangle is the infield','GREY block reserves the separate fieldhouse'],includeCentralPlaza:false,renderSummary:'track-and-field precinct with complete oval, infield, floodlights and fieldhouse reservation',isPilot:true};
PROFILES.suburban_retail_parking_lot_v1 = {id:'retail-parking-landscaped-lego-v1',version:1,programDescription:'A landscaped retail parking field with regulation stall rows, wide drive aisles, accessible bays, pedestrian crossings, cart corrals, tree islands, bioswale edge, light poles and pylon.',groundDescription:'Mottled asphalt, bright striping, concrete, prairie planting and muted retail hardware sampled from the exact landscaped-lot reference.',criticalConstraints:'The store is a separate building reservation; add or remove whole parking rows and never enlarge stalls, embed storefront buildings or generate people.',canopyDescription:'Shade trees repeat in islands without obstructing sight triangles or drive aisles.',plantingStructure:'retail_parking_landscaped_v1',guides:[{kind:'rounded_rectangle',x:.5,y:.54,width:.90,height:.78,color:'#505352',orientationPolicy:'orthogonal'},{kind:'rectangle',x:.5,y:.08,width:.72,height:.07,color:'#b9b4aa',orientationPolicy:'orthogonal'}],guideLegend:['DARK field is regulation retail parking','PALE edge reserves the separate storefront building'],includeCentralPlaza:false,renderSummary:'landscaped retail parking with regulation rows, crossings, tree islands, lights and store reservation',isPilot:true};

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
        { kind: 'basketball_court', x: 0.5, y: 0.5, width: 0.72, height: 0.62, widthM: 32, heightM: 19, color: accent, strokeColor: white, strokeWidthM: 0.1 },
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

function basketballVariantProfile(
  variantId: string,
): Partial<Omit<ParkGroundProfile, 'archetypeId' | 'title'>> {
  const fullCourt = (
    x: number,
    y: number,
    color: string,
  ): ParkGroundGuide => ({
    kind: 'basketball_court', x, y, width: 0.40, height: 0.62,
    widthM: 32, heightM: 19, color, strokeColor: '#eeeade', strokeWidthM: 0.10,
    orientationPolicy: 'orthogonal',
  });
  if (variantId.endsWith('_v1')) {
    return {
      programDescription:
        'A professional acrylic basketball facility containing up to two complete regulation full-court modules. Use the maximum number of whole 32 by 19 metre court envelopes that fit; never enlarge a single court to consume an oversized parcel.',
      groundDescription:
        'Cushioned blue acrylic playing surfaces with red perimeter aprons and keys, crisp bright-white markings, transparent backboards with padded support bases, black mesh fencing, four-corner LED sports lights, one compact scoreboard and aluminum spectator bleachers outside the run-off.',
      criticalConstraints:
        'Each retained module is one exact 28 by 15 metre playing court inside a 32 by 19 metre envelope. Keep every line, paired hoop, run-off, fence and gate complete. Scoreboards, bleachers, lights and all other objects remain outside the play-and-run-off envelope. Do not render people or surrounding large buildings.',
      plantingStructure: 'basketball_pro_v1',
      guides: [fullCourt(0.27, 0.50, '#315d68'), fullCourt(0.73, 0.50, '#315d68')],
      guideLegend: [
        'each retained BLUE-RED module is one complete regulation full court with its own two hoops, acrylic zones, full run-off, black enclosure and spectator edge',
      ],
      renderSummary:
        'professional blue-and-red acrylic basketball facility preserving the maximum fitting count of complete regulation full courts with padded hoops, black mesh, scoreboard, bleachers and LED lights',
    };
  }
  if (variantId.endsWith('_v2')) {
    return {
      programDescription:
        'One compact community half-court: a single regulation-width 15 by 14 metre playing room inside a complete 19 by 17 metre envelope, with one hoop, a colourful geometric ground mural, low chain-link enclosure and an integrated concrete seating wall.',
      groundDescription:
        'Deep blue cushioned acrylic overlaid with angular navy, amber, orange and pale-blue mural fields, accurate half-court boundary, key and three-point markings, a warm-grey cast-concrete apron and seating wall, timber seat caps and a restrained low fence behind the hoop.',
      criticalConstraints:
        'Build exactly one half-court and one 3.05 metre hoop. Do not mirror it into a full court, add a second hoop, shrink its regulation width, or let furniture enter the 19 by 17 metre play-and-run-off envelope. Keep the concrete seating wall outside the playable lines and preserve an open gate. Do not render people or surrounding large buildings.',
      plantingStructure: 'basketball_half_court_v2',
      guides: [{
        kind: 'basketball_court', x: 0.50, y: 0.50, width: 0.68, height: 0.68,
        widthM: 19, heightM: 17, color: '#253e61', strokeColor: '#f1eee5', strokeWidthM: 0.10,
        orientationPolicy: 'orthogonal',
      }],
      guideLegend: [
        'the single BLUE MURAL square is one complete 19 by 17 metre community half-court envelope with one hoop and an integrated seating-wall edge; never turn it into a full court',
      ],
      renderSummary:
        'compact one-hoop community half-court with exact half-court markings, angular blue-and-amber mural, low fence and integrated concrete seating wall',
    };
  }
  if (variantId.endsWith('_v3')) {
    return {
      programDescription:
        'One complete urban streetball full court inside a 32 by 19 metre envelope, organized as a hard-edged neighborhood plaza with paired hoops, an art-painted worn asphalt surface, a graffiti-panel fence edge and concrete step seating.',
      groundDescription:
        'Patched charcoal asphalt with visible aggregate, restrained cracks and faded repairs; accurate off-white regulation lines; layered muted coral, teal, ochre and blue street-art graphics; dark chain-link fencing with individual graffiti panels; and raw concrete spectator steps on the open plaza side.',
      criticalConstraints:
        'Keep one exact 28 by 15 metre full playing court, two 3.05 metre hoops and a complete 32 by 19 metre envelope. Art is a surface layer and must not replace or distort regulation markings. Fence panels, steps, lights and furniture stay outside run-off. Do not render people or surrounding large buildings.',
      plantingStructure: 'basketball_streetball_v3',
      guides: [fullCourt(0.50, 0.50, '#3f4240')],
      guideLegend: [
        'the single WORN ART-PAINTED rectangle is one complete regulation streetball court with paired hoops, faded markings, graffiti fence edge and concrete spectator steps',
      ],
      renderSummary:
        'urban streetball full court combining exact regulation geometry with patched asphalt, restrained surface art, graffiti panels and concrete step seating',
    };
  }
  return {};
}

export type ParkSpecialtyStructureKind =
  | 'civic_fountain_assembly'
  | 'greenway_edge_assembly'
  | 'stormwater_control_assembly'
  | 'basketball_court_assembly'
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
  | 'botanical_conservatory'
  | 'pond_dock_assembly'
  | 'riparian_bridge_assembly'
  | 'reservoir_edge_assembly'
  | 'amphitheater_lawn_assembly'
  | 'adventure_play_assembly'
  | 'batch5_archetype_assembly'
  | 'batch6_archetype_assembly'
  | 'batch7_archetype_assembly'
  | 'batch8_archetype_assembly'
  | 'batch9_archetype_assembly'
  | 'batch10_archetype_assembly'
  | 'batch11_archetype_assembly'
  | 'batch12_archetype_assembly'
  | 'batch13_archetype_assembly'
  | 'batch14_archetype_assembly';

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
  const compiledLegoContract = legoContract?.supported && legoContract.source === 'public_realm_lego'
    ? legoContract
    : null;
  const archetypeId = normalizeId(
    compiledLegoContract
      ? compiledLegoContract.archetypeId
      : plaza
      ? (props.plaza_archetype_id ?? props.green_space_archetype_id)
      : (props.green_space_archetype_id ?? props.plaza_archetype_id),
  ) || (plaza ? 'formal_civic_plaza' : 'neighborhood_park');
  const entry = findEntry(archetypeId);
  const variantId = normalizeId(
    compiledLegoContract
      ? compiledLegoContract.variantId
      : plaza
      ? (props.plaza_selected_variant_id ?? props.green_space_selected_variant_id)
      : (props.green_space_selected_variant_id ?? props.plaza_selected_variant_id),
  );
  const exact = (compiledLegoContract ? PROFILES[variantId] : undefined)
    ?? PROFILES[archetypeId]
    ?? (archetypeId === 'community_park' && compiledLegoContract
      ? PROFILES.neighborhood_park
      : undefined)
    ?? Object.entries(PROFILES).find(([id]) => archetypeId.startsWith(`${id}_`))?.[1];
  const variant = entry?.variants?.find((candidate) => (
    normalizeId(candidate.id) === variantId
    || normalizeId(candidate.id) === archetypeId
  ));
  if (!exact) {
    const fallback = fallbackProfile(entry, archetypeId, variant);
    return compiledLegoContract
      ? {
          ...fallback,
          legoFamilyId: compiledLegoContract.familyId,
          legoFamilyVersion: compiledLegoContract.familyVersion,
          variantId: compiledLegoContract.variantId,
        }
      : fallback;
  }
  const variantOwnsProgram = archetypeId === 'basketball_court';
  const resolvedExact = variantOwnsProgram
    ? { ...exact, ...basketballVariantProfile(variantId) }
    : exact;
  const variantSuffix = variant?.label && !variantOwnsProgram
    ? ` Selected variant style: ${variant.label}. Apply that variant only through compatible planting character, colour palette, paving and material finish; it does not authorize any new path, pond, fountain, field, bed, building or program element beyond this exact profile.`
    : '';
  const exactReferenceSuffix = exact === PROFILES[variantId] && variant?.description
    ? ` Exact catalogue reference: ${variant.description}`
    : '';
  return {
    ...resolvedExact,
    archetypeId,
    title: `${entry?.title ?? archetypeId.replace(/_/g, ' ')}${variant?.label ? ` - ${variant.label}` : ''}`,
    programDescription: `${resolvedExact.programDescription}${exactReferenceSuffix}${variantSuffix}`,
    groundDescription: `${resolvedExact.groundDescription}${variantSuffix}`,
    renderSummary: `${resolvedExact.renderSummary}${variant?.label && !variantOwnsProgram ? `; selected ${variant.label} planting and material character without changing the locked program` : ''}`,
    ...(compiledLegoContract
      ? {
          legoFamilyId: compiledLegoContract.familyId,
          legoFamilyVersion: compiledLegoContract.familyVersion,
          variantId: compiledLegoContract.variantId,
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
  ) {
    if (legoContract.archetypeId === 'pond_lake') return 'pond_dock_assembly';
    if (legoContract.archetypeId === 'wetland_rain_garden') return 'wetland_boardwalk';
    if (legoContract.archetypeId === 'riparian_buffer') return 'riparian_bridge_assembly';
    if (legoContract.archetypeId === 'reservoir_watershed_park') return 'reservoir_edge_assembly';
    return 'stormwater_control_assembly';
  }
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && legoContract.familyId === 'park_amphitheater_lawn_v0'
  ) return 'amphitheater_lawn_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && legoContract.familyId === 'park_playground_adventure_v0'
  ) return 'adventure_play_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && [
      'park_disc_golf_wooded_v0',
      'park_bocce_piazza_v0',
      'park_climbing_competition_v0',
      'park_mini_golf_classic_v0',
      'park_beach_volleyball_competition_v0',
      'park_pollinator_prairie_v0',
      'park_orchard_heritage_v0',
      'park_bioswale_streetside_v0',
      'park_sculpture_museum_court_v0',
      'park_labyrinth_classical_v0',
    ].includes(legoContract.familyId)
  ) return 'batch5_archetype_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && [
      'park_ice_rink_multipurpose_v3',
      'park_kayak_river_launch_v0',
      'park_tidal_marsh_cordgrass_v0',
      'park_cinema_lawn_projection_v1',
      'park_food_truck_permanent_v1',
      'park_great_lawn_v2',
      'park_campus_meadow_quad_v0',
      'park_urban_beach_family_v2',
      'park_velodrome_open_air_v0',
      'park_mtb_skills_dirt_v2',
    ].includes(legoContract.familyId)
  ) return 'batch6_archetype_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && [
      'park_regional_english_landscape_v0',
      'park_beer_garden_munich_v0',
      'park_sunken_courtyard_v0',
      'park_terraced_cascade_v3',
      'park_market_festival_lawn_v1',
      'park_boardwalk_maritime_v0',
      'park_fountain_formal_pool_v1',
      'park_natural_swimming_pond_v0',
      'park_nature_preserve_prairie_v1',
      'park_riverfront_lake_beach_v1',
    ].includes(legoContract.familyId)
  ) return 'batch7_archetype_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && [
      'park_reclaimed_wharf_v0',
      'park_quarry_tier_cascade_v2',
      'park_estate_oak_picnic_v1',
      'park_constructed_wetland_boardwalk_v0',
      'park_academic_planted_court_v0',
      'park_campus_green_spine_v0',
      'park_botanical_rose_garden_v3',
      'park_research_arboretum_v0',
      'park_rewilding_reforestation_v1',
      'park_stormwater_arid_channel_v3',
    ].includes(legoContract.familyId)
  ) return 'batch8_archetype_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && [
      'park_urban_pocket_rustic_v0',
      'park_neighborhood_contemporary_v3',
      'park_cemetery_classical_v0',
      'park_courtyard_linear_water_v1',
      'park_parklet_sf_timber_v1',
      'park_french_parterre_axis_v1',
      'park_london_railed_square_v1',
      'park_halifax_rose_bandstand_v0',
      'park_olmsted_multilandscape_v3',
      'park_hilltop_viewpoint_v3',
    ].includes(legoContract.familyId)
  ) return 'batch9_archetype_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && [
      'park_amsterdam_hofje_garden_v0',
      'park_amsterdam_plein_v0',
      'park_amsterdam_vondelpark_pavilion_v3',
      'park_barcelona_pati_green_v0',
      'park_barcelona_xamfra_corner_v2',
      'park_barcelona_superilla_green_v1',
      'park_calgary_prairie_market_v1',
      'park_calgary_princes_island_festival_v0',
      'park_montreal_mount_royal_grove_v2',
      'park_montreal_neighbourhood_square_v3',
    ].includes(legoContract.familyId)
  ) return 'batch10_archetype_assembly';
  if (
    legoContract?.source === 'public_realm_lego' && legoContract.supported
    && ['park_paris_place_royale_v2','park_paris_square_tree_grid_v3','park_london_circus_planted_v1','park_newyork_pocket_water_v0','park_newyork_community_greenhouse_v3','park_vancouver_seawall_cycle_v2','park_vancouver_beach_pavilion_v0','park_toronto_ravine_creek_v1','park_toronto_urban_market_v1','park_halifax_coastal_fog_path_v2'].includes(legoContract.familyId)
  ) return 'batch11_archetype_assembly';
  if (
    legoContract?.source === 'public_realm_lego' && legoContract.supported
    && ['park_city_hall_modernist_fountain_v2','park_cathedral_courtyard_fountain_v3','park_cultural_museum_terrace_v0','park_transit_green_civic_v2','park_amphitheater_terraced_v0','park_concert_timber_lawn_v2','park_night_market_hawker_v0','park_parade_national_mall_v3','park_canal_ecological_wetland_v3','park_custom_biophilic_urban_v1'].includes(legoContract.familyId)
  ) return 'batch12_archetype_assembly';
  if (
    legoContract?.source === 'public_realm_lego' && legoContract.supported
    && ['park_rooftop_intensive_garden_v0','park_community_healing_garden_v2','park_greenbelt_rail_trail_v1','park_foothill_heathland_trail_v2','park_marina_pacific_dock_v2','park_working_pier_brooklyn_park_v3','park_floating_meadow_loop_v2','park_lighthouse_pacific_headland_v2','park_lake_edge_timber_deck_v2','park_stormwater_natural_creek_v0'].includes(legoContract.familyId)
  ) return 'batch13_archetype_assembly';
  if (
    legoContract?.source === 'public_realm_lego' && legoContract.supported
    && ['park_surface_parking_standard_v0','park_structured_parking_urban_v2','park_underground_parking_green_v1','park_green_parking_infrastructure_v1','park_airport_general_aviation_v2','park_equestrian_working_stable_v1','park_golf_seaside_links_v0','park_driving_range_single_tier_v0','park_multi_sport_track_field_v3','park_retail_parking_landscaped_v1'].includes(legoContract.familyId)
  ) return 'batch14_archetype_assembly';
  if (
    legoContract?.source === 'public_realm_lego'
    && legoContract.supported
    && legoContract.familyId === 'park_basketball_court_v0'
  ) return 'basketball_court_assembly';
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
  if (archetypeId.startsWith('basketball_court')) return 'basketball_court_assembly';
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
