import streetPathCatalog from '@/data/streetPathArchetypes.json';
import type { SiteZone } from '@/types';
import {
  PUBLIC_REALM_STREET_CATALOG_FINGERPRINT,
  PUBLIC_REALM_STREET_FAMILIES,
  PUBLIC_REALM_STREET_FAMILY_VERSION,
  resolveStreetAppearanceKit,
  type PublicRealmStreetFamilyDefinition,
  type PublicRealmStreetFamilyId,
  type StreetAppearanceKit,
} from './streetFamilyCatalog';
import { validateStreetRecipeProperties } from './streetLegoContract';
import {
  PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_SHARED_SURFACE_LIFT_METERS,
  PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS,
} from './publicRealmDepthPolicy';

export type StreetBandKind =
  | 'motor'
  | 'cycle'
  | 'parking'
  | 'sidewalk'
  | 'planting'
  | 'median'
  | 'buffer'
  | 'path'
  | 'shoulder'
  | 'other';

export interface StreetSectionBand {
  sourceType: string;
  /** Authoritative physical surface from the source section. Appearance kits
   * may tint this material, but cannot turn brick, concrete or planting into
   * generic asphalt. */
  surface: string;
  label: string;
  kind: StreetBandKind;
  startM: number;
  endM: number;
  centerM: number;
  widthM: number;
  color: string;
  liftM: number;
  roughness?: number;
  metalness?: number;
}

export interface StreetSectionMarking {
  offsetM: number;
  color: string;
  widthM: number;
  dashed: boolean;
}

export interface StreetSectionProfile {
  archetypeId: string;
  title: string;
  variantId?: string;
  variantLabel?: string;
  variantDescription?: string;
  rowM: number;
  bands: StreetSectionBand[];
  markings: StreetSectionMarking[];
  treeOffsetsM: number[];
  /** Signed offsets of the actual carriageway / median curb lines. */
  curbOffsetsM: number[];
  /** Soft-edged paths should not inherit the generic road curb pair. */
  renderCurbs: boolean;
  renderSummary: string;
  /** Present only when the zone is backed by the executable Public Realm
   * LEGO contract. Legacy catalog sections remain valid but do not claim a
   * family capability. */
  familyId?: PublicRealmStreetFamilyId;
  familyVersion?: typeof PUBLIC_REALM_STREET_FAMILY_VERSION;
  appearanceKitId?: string;
  rendererFingerprint?: string;
  recipeHash?: string;
  sourceCapabilityFingerprint?: string;
  /** Canonical width from the persisted recipe target. Source profile bands
   * are scaled to this value without changing their order or semantics. */
  targetRowM?: number;
  metricWidthLocked?: boolean;
  appearance?: StreetAppearanceKit;
  isPilot: true;
}

/** Render-stage street landscaping must follow the engineered section rather
 * than a procedural tree row that is absent from the editable Tiles scene. */
export function buildStreetRenderGroundTruthInstruction(
  profile: StreetSectionProfile,
): string {
  const landscape = profile.treeOffsetsM.length > 0
    ? 'Street trees are render-stage elements: add varied mature trees only inside the designated planting bands, with clear crossings, driveways, sight triangles, cycle tracks and sidewalks; never place them in a travel or circulation surface.'
    : 'This section has no designated street-tree band: do not invent trees inside its carriageway, cycle facility, path, shoulder or sidewalk.';
  return (
    '3D STREET GROUND TRUTH visible in the screenshot - PRESERVE every lane, cycle track, sidewalk, median, curb and marking exactly; '
    + `${landscape} ${profile.renderSummary}`
  );
}

interface CatalogSectionZone {
  type?: string;
  width_m?: number;
  label?: string;
  surface?: string;
  planting?: string;
  note?: string;
}

interface CatalogEntry {
  id: string;
  title?: string;
  typicalWidth_m?: number;
  laneCount?: number;
  hasSidewalk?: boolean;
  hasMedian?: boolean;
  hasBikeLane?: boolean;
  transportModes?: string[];
  aestheticCategory?: string;
  volume?: string;
  propertyPresets?: {
    width?: number;
    lane_count?: number;
    road_surface?: string;
    mobility_profile?: string;
  };
  section?: { row_m?: number; zones?: CatalogSectionZone[] };
  variants?: Array<{
    id: string;
    label?: string;
    description?: string;
    color?: string;
  }>;
}

const CATALOG = (((streetPathCatalog as any).archetypes ?? streetPathCatalog) as CatalogEntry[]);

export const PILOT_STREET_ARCHETYPE_IDS = Object.freeze([
  // Normal master-planner outputs. Their legacy catalog cards predate exact
  // section arrays, so deterministic representative sections are supplied
  // below instead of falling through to a generic asphalt ribbon.
  'yield_street',
  'narrow_residential_street',
  'collector_road',
  'main_street_complete',
  'calgary_local',
  'protected_bike_lane_bidirectional',
  'calgary_arterial_4lane_50',
  'multi_use_trail',
  'toronto_victorian_residential_street',
  'toronto_laneway',
] as const);

interface SyntheticSection {
  rowM: number;
  zones: readonly CatalogSectionZone[];
  renderCurbs?: boolean;
}

const SYNTHETIC_SECTIONS: Record<string, SyntheticSection> = {
  green_alley: {
    rowM: 5,
    renderCurbs: false,
    zones: [
      { type: 'boulevard', width_m: 0.75, label: 'Bioswale planting edge' },
      { type: 'shared_lane', width_m: 3.5, label: 'Permeable shared lane', surface: 'permeable unit paving' },
      { type: 'boulevard', width_m: 0.75, label: 'Bioswale planting edge' },
    ],
  },
  woonerf_shared_street: {
    rowM: 10,
    renderCurbs: false,
    zones: [
      { type: 'shoulder', width_m: 0.4, label: 'Flush stone edge', surface: 'stone paving' },
      { type: 'boulevard', width_m: 1.25, label: 'Alternating planter edge', surface: 'permeable paving' },
      { type: 'shared_lane', width_m: 6.7, label: 'Warm brick shared surface', surface: 'brick paving' },
      { type: 'boulevard', width_m: 1.25, label: 'Alternating planter edge', surface: 'permeable paving' },
      { type: 'shoulder', width_m: 0.4, label: 'Flush stone edge', surface: 'stone paving' },
    ],
  },
  yield_street: {
    rowM: 6,
    renderCurbs: false,
    zones: [
      { type: 'shoulder', width_m: 0.3, label: 'Flush edge', surface: 'unit paving' },
      { type: 'shared_lane', width_m: 5.4, label: 'Yield shared surface', surface: 'brick paving' },
      { type: 'shoulder', width_m: 0.3, label: 'Flush edge', surface: 'unit paving' },
    ],
  },
  narrow_residential_street: {
    rowM: 10,
    zones: [
      { type: 'sidewalk', width_m: 1.2, label: 'Sidewalk', surface: 'concrete' },
      { type: 'boulevard', width_m: 0.6, label: 'Planting strip' },
      { type: 'parking', width_m: 1.4, label: 'Flexible parking' },
      { type: 'shared_lane', width_m: 3.6, label: 'Unmarked yield carriageway' },
      { type: 'parking', width_m: 1.4, label: 'Flexible parking' },
      { type: 'boulevard', width_m: 0.6, label: 'Planting strip' },
      { type: 'sidewalk', width_m: 1.2, label: 'Sidewalk', surface: 'concrete' },
    ],
  },
  collector_road: {
    rowM: 16,
    zones: [
      { type: 'sidewalk', width_m: 1.5, label: 'Sidewalk', surface: 'concrete' },
      { type: 'boulevard', width_m: 1.25, label: 'Tree boulevard' },
      { type: 'travel_lane', width_m: 3.25, label: 'Travel lane' },
      { type: 'turn_lane', width_m: 4, label: 'Centre turn lane' },
      { type: 'travel_lane', width_m: 3.25, label: 'Travel lane' },
      { type: 'boulevard', width_m: 1.25, label: 'Tree boulevard' },
      { type: 'sidewalk', width_m: 1.5, label: 'Sidewalk', surface: 'concrete' },
    ],
  },
  main_street_complete: {
    rowM: 18,
    zones: [
      { type: 'sidewalk', width_m: 2, label: 'Wide sidewalk', surface: 'concrete' },
      { type: 'boulevard', width_m: 1.25, label: 'Tree/furnishing zone' },
      { type: 'parking', width_m: 2.1, label: 'Parallel parking' },
      { type: 'travel_lane', width_m: 3.65, label: 'Travel / sharrow lane' },
      { type: 'travel_lane', width_m: 3.65, label: 'Travel / sharrow lane' },
      { type: 'parking', width_m: 2.1, label: 'Parallel parking' },
      { type: 'boulevard', width_m: 1.25, label: 'Tree/furnishing zone' },
      { type: 'sidewalk', width_m: 2, label: 'Wide sidewalk', surface: 'concrete' },
    ],
  },
  toronto_victorian_residential_street: {
    rowM: 16,
    zones: [
      { type: 'sidewalk', width_m: 1.5, label: 'Sidewalk', surface: 'concrete' },
      { type: 'boulevard', width_m: 1, label: 'Maple tree boulevard' },
      { type: 'parking', width_m: 1.75, label: 'Parallel parking' },
      { type: 'travel_lane', width_m: 3.75, label: 'Unmarked residential lane' },
      { type: 'travel_lane', width_m: 3.75, label: 'Unmarked residential lane' },
      { type: 'parking', width_m: 1.75, label: 'Parallel parking' },
      { type: 'boulevard', width_m: 1, label: 'Maple tree boulevard' },
      { type: 'sidewalk', width_m: 1.5, label: 'Sidewalk', surface: 'concrete' },
    ],
  },
  toronto_laneway: {
    rowM: 5,
    renderCurbs: false,
    zones: [
      { type: 'shoulder', width_m: 0.25, label: 'Flush drainage edge', surface: 'concrete' },
      { type: 'shared_lane', width_m: 4.5, label: 'Shared service lane', surface: 'asphalt' },
      { type: 'shoulder', width_m: 0.25, label: 'Flush drainage edge', surface: 'concrete' },
    ],
  },
};

/** Appearance-owned tropical sections keep the source right-of-way exact
 * while trading flexible edge space for a continuous palm-planted median.
 * Both lane programs stay above the reviewed low-speed viability floor. */
const TROPICAL_BOULEVARD_SECTIONS: Readonly<Record<string, SyntheticSection>> = Object.freeze({
  narrow_residential_street: Object.freeze({
    rowM: 10,
    zones: Object.freeze([
      { type: 'sidewalk', width_m: 1.25, label: 'Warm flush sidewalk', surface: 'warm architectural concrete' },
      { type: 'travel_lane', width_m: 3, label: 'Low-speed tropical lane', surface: 'fine warm asphalt' },
      { type: 'planted_median', width_m: 1.5, label: 'Palm-planted center median', surface: 'lush tropical planting' },
      { type: 'travel_lane', width_m: 3, label: 'Low-speed tropical lane', surface: 'fine warm asphalt' },
      { type: 'sidewalk', width_m: 1.25, label: 'Warm flush sidewalk', surface: 'warm architectural concrete' },
    ]),
  }),
  main_street_complete: Object.freeze({
    rowM: 18,
    zones: Object.freeze([
      { type: 'sidewalk', width_m: 2, label: 'Warm commercial sidewalk', surface: 'warm architectural concrete' },
      { type: 'parking', width_m: 2, label: 'Parallel parking', surface: 'fine warm asphalt' },
      { type: 'travel_lane', width_m: 3.4, label: 'Tropical boulevard lane', surface: 'fine warm asphalt' },
      { type: 'planted_median', width_m: 3.2, label: 'Palm-planted center median', surface: 'lush tropical planting' },
      { type: 'travel_lane', width_m: 3.4, label: 'Tropical boulevard lane', surface: 'fine warm asphalt' },
      { type: 'parking', width_m: 2, label: 'Parallel parking', surface: 'fine warm asphalt' },
      { type: 'sidewalk', width_m: 2, label: 'Warm commercial sidewalk', surface: 'warm architectural concrete' },
    ]),
  }),
});

function inferCatalogSection(entry: CatalogEntry): SyntheticSection {
  const rowM = Math.max(3, Number(entry.propertyPresets?.width) || Number(entry.typicalWidth_m) || 12);
  const modes = new Set((entry.transportModes ?? []).map(normalizeId));
  const semantic = normalizeId(`${entry.id} ${entry.aestheticCategory ?? ''} ${entry.propertyPresets?.mobility_profile ?? ''}`);
  const hasAuto = modes.has('automobile') || modes.has('car') || modes.has('truck');
  const hasTransit = modes.has('transit') || semantic.includes('transit') || semantic.includes('rail') || semantic.includes('tram');
  const hasCycle = Boolean(entry.hasBikeLane) || modes.has('bicycle') || semantic.includes('cycle') || semantic.includes('bike');
  const pedestrianOnly = !hasAuto && !hasTransit && modes.has('walking') && !hasCycle;
  const cyclePath = !hasAuto && !hasTransit && hasCycle;
  const shared = hasAuto && !entry.hasSidewalk && (Number(entry.laneCount) || 1) <= 1;

  if (pedestrianOnly) {
    const planting = rowM >= 9 ? Math.min(1.5, rowM * 0.12) : 0;
    return {
      rowM,
      renderCurbs: false,
      zones: [
        ...(planting > 0 ? [{ type: 'boulevard', width_m: planting, label: 'Planting / furnishing edge' }] : []),
        { type: 'multi_use_pathway', width_m: rowM - planting * 2, label: 'Pedestrian promenade', surface: entry.propertyPresets?.road_surface ?? 'unit paving' },
        ...(planting > 0 ? [{ type: 'boulevard', width_m: planting, label: 'Planting / furnishing edge' }] : []),
      ],
    };
  }
  if (cyclePath) {
    const shoulder = Math.min(0.5, rowM * 0.1);
    return {
      rowM,
      renderCurbs: false,
      zones: [
        { type: 'shoulder', width_m: shoulder, label: 'Soft edge', surface: 'gravel' },
        { type: hasCycle && modes.has('walking') ? 'multi_use_pathway' : 'cycle_track', width_m: rowM - shoulder * 2, label: hasCycle && modes.has('walking') ? 'Shared cycle / pedestrian path' : 'Cycle path', surface: 'asphalt' },
        { type: 'shoulder', width_m: shoulder, label: 'Soft edge', surface: 'gravel' },
      ],
    };
  }
  if (shared) {
    const edge = Math.min(0.4, rowM * 0.06);
    return {
      rowM,
      renderCurbs: false,
      zones: [
        { type: 'shoulder', width_m: edge, label: 'Flush drainage edge', surface: 'unit paving' },
        { type: 'shared_lane', width_m: rowM - edge * 2, label: 'Low-speed shared surface', surface: entry.propertyPresets?.road_surface ?? 'unit paving' },
        { type: 'shoulder', width_m: edge, label: 'Flush drainage edge', surface: 'unit paving' },
      ],
    };
  }

  const zones: CatalogSectionZone[] = [];
  const sidewalkWidth = entry.hasSidewalk ? Math.min(1.8, rowM * 0.11) : 0;
  let plantingWidth = entry.hasSidewalk && rowM >= 14 ? Math.min(1.5, rowM * 0.08) : 0;
  let cycleWidth = entry.hasBikeLane ? Math.min(1.8, rowM * 0.1) : 0;
  let medianWidth = entry.hasMedian ? Math.min(3, rowM * 0.1) : 0;
  const parkingSemantic = ['main_street', 'residential', 'brownstone', 'commercial', 'rue', 'straat', 'carrer', 'thoroughfare']
    .some((term) => semantic.includes(term));
  let parkingWidth = parkingSemantic && rowM >= 14 ? Math.min(2.1, rowM * 0.11) : 0;
  let laneCount = Math.max(1, Number(entry.laneCount) || Number(entry.propertyPresets?.lane_count) || (hasTransit ? 2 : 1));
  let fixedWidth = (sidewalkWidth + plantingWidth + cycleWidth + parkingWidth) * 2 + medianWidth;
  while ((rowM - fixedWidth) / laneCount < 2.65) {
    if (plantingWidth > 0) plantingWidth = 0;
    else if (parkingWidth > 0) parkingWidth = 0;
    else if (cycleWidth > 0) cycleWidth = 0;
    else if (medianWidth > 0) medianWidth = 0;
    else if (laneCount > 2) laneCount -= 1;
    else break;
    fixedWidth = (sidewalkWidth + plantingWidth + cycleWidth + parkingWidth) * 2 + medianWidth;
  }
  const laneWidth = Math.max(0.1, (rowM - fixedWidth) / laneCount);
  const leftLanes = Math.ceil(laneCount / 2);
  const rightLanes = laneCount - leftLanes;
  if (sidewalkWidth) zones.push({ type: 'sidewalk', width_m: sidewalkWidth, label: 'Sidewalk', surface: 'concrete' });
  if (plantingWidth) zones.push({ type: 'boulevard', width_m: plantingWidth, label: 'Tree / furnishing boulevard' });
  if (cycleWidth) zones.push({ type: 'cycle_track', width_m: cycleWidth, label: 'Protected cycle track', surface: 'red asphalt' });
  if (parkingWidth) zones.push({ type: 'parking', width_m: parkingWidth, label: 'Parallel parking' });
  for (let index = 0; index < leftLanes; index += 1) {
    zones.push({ type: hasTransit && index === 0 ? 'transit_lane' : 'travel_lane', width_m: laneWidth, label: hasTransit && index === 0 ? 'Transit lane' : 'Travel lane' });
  }
  if (medianWidth) zones.push({ type: 'median', width_m: medianWidth, label: 'Raised / planted median' });
  for (let index = 0; index < rightLanes; index += 1) {
    zones.push({ type: hasTransit && index === rightLanes - 1 ? 'transit_lane' : 'travel_lane', width_m: laneWidth, label: hasTransit && index === rightLanes - 1 ? 'Transit lane' : 'Travel lane' });
  }
  if (parkingWidth) zones.push({ type: 'parking', width_m: parkingWidth, label: 'Parallel parking' });
  if (cycleWidth) zones.push({ type: 'cycle_track', width_m: cycleWidth, label: 'Protected cycle track', surface: 'red asphalt' });
  if (plantingWidth) zones.push({ type: 'boulevard', width_m: plantingWidth, label: 'Tree / furnishing boulevard' });
  if (sidewalkWidth) zones.push({ type: 'sidewalk', width_m: sidewalkWidth, label: 'Sidewalk', surface: 'concrete' });
  return { rowM, zones };
}

function normalizeId(value: unknown): string {
  return String(value ?? '').toLowerCase().trim().replace(/-/g, '_');
}

function asRecord(value: unknown): Record<string, unknown> | undefined {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown>
    : undefined;
}

interface ResolvedStreetLegoContract {
  family?: PublicRealmStreetFamilyDefinition;
  sourceArchetypeId: string;
  requestedVariantId: string;
  requestedAppearanceKitId: string;
  targetRowM?: number;
  recipeHash?: string;
  sourceCapabilityFingerprint?: string;
}

/** Resolve either a strictly validated Public Realm LEGO V1 recipe or the
 * pre-existing Classic source identity. Invalid/partial V1 envelopes are
 * deliberately unable to opt a Classic street into metric family geometry. */
function resolveStreetLegoContract(
  zoneOrId: Pick<SiteZone, 'properties'> | string,
): ResolvedStreetLegoContract {
  const props = typeof zoneOrId === 'string'
    ? undefined
    : asRecord(zoneOrId.properties);
  const validation = props ? validateStreetRecipeProperties(props) : undefined;
  const validated = validation?.valid ? validation.recipe : undefined;
  const role = normalizeId(props?.street_role);
  const roleFallback: Record<string, string> = {
    spine: 'main_street_complete',
    primary: 'main_street_complete',
    collector: 'collector_road',
    local: 'toronto_victorian_residential_street',
    residential: 'toronto_victorian_residential_street',
    lane: 'toronto_laneway',
    laneway: 'toronto_laneway',
    alley: 'toronto_laneway',
    trail: 'multi_use_trail',
    path: 'multi_use_trail',
    roundabout: 'roundabout',
  };
  const rawInput = typeof zoneOrId === 'string' ? normalizeId(zoneOrId) : '';
  const family = validated
    ? PUBLIC_REALM_STREET_FAMILIES[validated.familyId]
    : undefined;
  const directArchetype = normalizeId(
    validated?.archetypeId
    ?? props?.road_archetype_id
    ?? (family ? '' : rawInput),
  );
  const sourceArchetypeId = directArchetype
    || roleFallback[role]
    || family?.sourceArchetypeIds[0]
    || '';
  return {
    family,
    sourceArchetypeId,
    requestedVariantId: normalizeId(
      validated?.variantId
      ?? props?.road_selected_variant_id,
    ),
    requestedAppearanceKitId: validated?.appearanceKitId ?? '',
    targetRowM: validated?.targetRowM,
    recipeHash: validated?.recipeHash,
    sourceCapabilityFingerprint: validated?.capabilityFingerprint,
  };
}

function familySectionFor(
  family: PublicRealmStreetFamilyDefinition | undefined,
): SyntheticSection | undefined {
  if (!family) return undefined;
  // Local Public Realm is intentionally multi-profile: every source program
  // retains its own reviewed section and is fitted only to the recipe target.
  if (family.id === 'street_local_public_realm') return undefined;
  if (family.crossSection.length === 0 || family.nativeRowM === null) return undefined;
  return {
    rowM: family.nativeRowM,
    zones: family.crossSection.map((band) => ({
      type: band.type,
      width_m: band.widthM,
      label: band.label,
      surface: band.surface,
    })),
  };
}

function applyFamilyAppearance(
  bands: StreetSectionBand[],
  appearance: StreetAppearanceKit | undefined,
): StreetSectionBand[] {
  if (!appearance) return bands;
  const palette = appearance.palette;
  return bands.map((band) => ({
    ...band,
    color: (() => {
      switch (band.kind) {
        case 'motor': return palette.motor;
        case 'cycle': return palette.cycle;
        case 'parking': return palette.parking;
        case 'sidewalk': return palette.sidewalk;
        case 'planting': return palette.planting;
        case 'median': return palette.planting;
        case 'buffer': return palette.buffer;
        case 'path': return palette.path;
        case 'shoulder': return palette.shoulder;
        default: return band.color;
      }
    })(),
    roughness: palette.roughness,
    metalness: palette.metalness,
    ...(appearance.id === 'modern_minimalist_v1'
      ? { liftM: PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS }
      : {}),
  }));
}

function classify(type: string): StreetBandKind {
  if (['lane', 'travel_lane', 'shared_lane', 'turn_lane', 'turn', 'alley', 'transit_lane', 'rail_lane'].includes(type)) return 'motor';
  if (['cycle', 'cycle_track', 'bike_lane', 'advisory_bike_lane', 'bicycle_pathway'].includes(type)) return 'cycle';
  if (['parking', 'parking_lane'].includes(type)) return 'parking';
  if (type === 'sidewalk') return 'sidewalk';
  if (['boulevard', 'furnishing', 'planted_median'].includes(type)) return 'planting';
  if (type === 'median') return 'median';
  if (['buffer', 'transit_island'].includes(type)) return 'buffer';
  if (['mup', 'multi_use_pathway', 'multi_use_trail'].includes(type)) return 'path';
  if (['shoulder', 'ditch'].includes(type)) return 'shoulder';
  return 'other';
}

function bandStyle(kind: StreetBandKind, surface: string): Pick<StreetSectionBand, 'color' | 'liftM'> {
  const lower = surface.toLowerCase();
  switch (kind) {
    case 'motor':
      if (lower.includes('brick') || lower.includes('cobble') || lower.includes('unit paving')) {
        return { color: '#a76547', liftM: PUBLIC_REALM_STREET_SHARED_SURFACE_LIFT_METERS };
      }
      return { color: '#565a5d', liftM: PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS };
    case 'cycle':
      if (lower.includes('green')) return { color: '#4f8065', liftM: PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + 0.005 };
      if (lower.includes('red') || lower.includes('brown')) return { color: '#9a624f', liftM: PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + 0.005 };
      return { color: '#656f72', liftM: PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + 0.005 };
    case 'parking': return { color: '#62666a', liftM: PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS };
    case 'sidewalk': return { color: '#b8b5ac', liftM: PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS };
    case 'planting': return { color: '#587545', liftM: PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS - 0.005 };
    case 'median': return { color: '#71875b', liftM: PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS + 0.005 };
    case 'buffer': return { color: '#8d987a', liftM: PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS - 0.01 };
    case 'path': return { color: '#a8a69e', liftM: PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + 0.005 };
    case 'shoulder':
      if (lower.includes('stone')) return { color: '#c4b69e', liftM: PUBLIC_REALM_STREET_SHARED_SURFACE_LIFT_METERS };
      return { color: lower.includes('gravel') ? '#8d8370' : '#737678', liftM: PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS + 0.01 };
    default: return { color: '#89877f', liftM: PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS };
  }
}

function addMarkings(
  archetypeId: string,
  bands: StreetSectionBand[],
): StreetSectionMarking[] {
  const markings: StreetSectionMarking[] = [];
  const motorBands = bands.filter((band) => band.kind === 'motor');
  for (let index = 0; index < bands.length - 1; index += 1) {
    const left = bands[index];
    const right = bands[index + 1];
    if (left.kind === 'motor' && right.kind === 'motor') {
      if (archetypeId === 'collector_road' && (
        left.sourceType === 'turn_lane' || right.sourceType === 'turn_lane'
      )) {
        markings.push({
          offsetM: left.endM,
          color: '#d6b34a',
          widthM: 0.12,
          dashed: false,
        });
        continue;
      }
      const isTwoWayCenterline = motorBands.length === 2;
      // Calgary's local section is intentionally unmarked at this scale.
      if (isTwoWayCenterline && [
        'calgary_local',
        'narrow_residential_street',
        'main_street_complete',
        'yield_street',
        'toronto_victorian_residential_street',
        'toronto_laneway',
      ].includes(archetypeId)) continue;
      markings.push({
        offsetM: left.endM,
        color: isTwoWayCenterline ? '#d6b34a' : '#e8e5dc',
        widthM: isTwoWayCenterline ? 0.12 : 0.14,
        dashed: true,
      });
    }
  }
  for (const band of bands) {
    const normalizedLabel = band.label.toLowerCase();
    if (band.kind === 'cycle' && (normalizedLabel.includes('two-way') || normalizedLabel.includes('bidirectional'))) {
      markings.push({ offsetM: band.centerM, color: '#d6b34a', widthM: 0.1, dashed: false });
    }
  }
  return markings;
}

export function resolvePilotStreetSectionProfile(
  zoneOrId: Pick<SiteZone, 'properties'> | string,
): StreetSectionProfile | null {
  const contract = resolveStreetLegoContract(zoneOrId);
  const normalized = contract.sourceArchetypeId;
  const entry = CATALOG.find((candidate) => normalized === candidate.id)
    ?? CATALOG
      .filter((candidate) => normalized.startsWith(`${candidate.id}_`))
      .sort((left, right) => right.id.length - left.id.length)[0];
  if (!entry) return null;
  const pilotId = entry.id;
  const selectedVariantId = contract.requestedVariantId;
  const variant = entry.variants?.find((candidate) => (
    normalizeId(candidate.id) === selectedVariantId
    || (selectedVariantId.startsWith('v') && normalizeId(candidate.id).endsWith(`_${selectedVariantId}`))
    || normalizeId(candidate.id) === normalized
  ));
  const appearance = contract.family
    ? resolveStreetAppearanceKit(
      contract.family,
      contract.requestedAppearanceKitId || contract.requestedVariantId,
    )
    : undefined;
  const withVariant = <T extends StreetSectionProfile>(profile: T): T => ({
    ...profile,
    bands: applyFamilyAppearance(profile.bands, appearance),
    ...(appearance?.id === 'modern_minimalist_v1' ? {
      curbOffsetsM: [],
      renderCurbs: false,
    } : {}),
    ...(contract.family ? {
      familyId: contract.family.id,
      familyVersion: contract.family.familyVersion,
      appearanceKitId: appearance?.id,
      appearance,
      rendererFingerprint: PUBLIC_REALM_STREET_CATALOG_FINGERPRINT,
      recipeHash: contract.recipeHash,
      sourceCapabilityFingerprint: contract.sourceCapabilityFingerprint,
      targetRowM: contract.targetRowM,
      metricWidthLocked: true,
      title: `${contract.family.label} - ${appearance?.label ?? contract.family.defaultAppearanceKitId}`,
    } : {}),
    ...(variant ? {
      variantId: variant.id,
      variantLabel: variant.label,
      variantDescription: variant.description,
      ...(!contract.family ? { title: `${profile.title}${variant.label ? ` - ${variant.label}` : ''}` } : {}),
    } : {}),
    renderSummary: [
      profile.renderSummary,
      contract.family
        ? `Public Realm LEGO ${contract.family.id} v${contract.family.familyVersion}, appearance kit ${appearance?.label ?? contract.family.defaultAppearanceKitId}`
        : '',
      variant
        ? `selected source variant ${variant.label ?? variant.id}: ${variant.description ?? 'preserve its catalog material character'}`
        : '',
    ].filter(Boolean).join('; '),
  });
  // The catalog's legacy trail card predates exact cross-section data. Give
  // contextual path connectors an explicit, scale-locked section so they do
  // not fall through to the generic motor-road treatment (curbs + white road
  // dashes). The 4 m total matches the catalog and the plan generator.
  if (pilotId === 'multi_use_trail') {
    const bands: StreetSectionBand[] = [
      {
        sourceType: 'soft_shoulder', label: 'Soft shoulder', kind: 'shoulder',
        surface: 'soft landscape shoulder',
        startM: -2, endM: -1.75, centerM: -1.875, widthM: 0.25,
        color: '#7c8068', liftM: PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS + 0.01,
      },
      {
        sourceType: 'multi_use_trail', label: 'Multi-use trail', kind: 'path',
        surface: 'asphalt',
        startM: -1.75, endM: 1.75, centerM: 0, widthM: 3.5,
        color: '#aaa8a0', liftM: PUBLIC_REALM_STREET_ROAD_SURFACE_LIFT_METERS + 0.005,
      },
      {
        sourceType: 'soft_shoulder', label: 'Soft shoulder', kind: 'shoulder',
        surface: 'soft landscape shoulder',
        startM: 1.75, endM: 2, centerM: 1.875, widthM: 0.25,
        color: '#7c8068', liftM: PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS + 0.01,
      },
    ];
    return withVariant({
      archetypeId: pilotId,
      title: entry?.title ?? 'Multi-Use Trail',
      rowM: 4,
      bands,
      markings: [{ offsetM: 0, color: '#d6b34a', widthM: 0.08, dashed: true }],
      treeOffsetsM: [],
      curbOffsetsM: [],
      renderCurbs: false,
      renderSummary: 'exact 4.0m soft-edged multi-use trail: 0.25m shoulders and 3.5m paved path',
      isPilot: true,
    });
  }
  const familySection = familySectionFor(contract.family);
  const synthetic = SYNTHETIC_SECTIONS[pilotId];
  const baseCompiledSection = familySection ?? (entry.section?.zones?.length
    ? { rowM: Number(entry.section.row_m) || Number(entry.typicalWidth_m) || 1, zones: entry.section.zones }
    : (synthetic ?? inferCatalogSection(entry)));
  const compiledSection = appearance?.id === 'tropical_boulevard_v1'
    ? TROPICAL_BOULEVARD_SECTIONS[pilotId] ?? baseCompiledSection
    : baseCompiledSection;
  const sourceZones = compiledSection.zones;
  if (!sourceZones?.length) return null;
  const widths = sourceZones.map((zone) => Math.max(0, Number(zone.width_m) || 0));
  const measuredRow = widths.reduce((sum, width) => sum + width, 0);
  const rowM = Math.round(
    (measuredRow || compiledSection.rowM || Number(entry.typicalWidth_m) || 1) * 1_000_000,
  ) / 1_000_000;
  let cursor = -rowM / 2;
  const bands = sourceZones.map((zone, index): StreetSectionBand => {
    const widthM = widths[index];
    const startM = cursor;
    const endM = cursor + widthM;
    cursor = endM;
    const sourceType = normalizeId(zone.type);
    const surface = normalizeId(zone.surface || (() => {
      if (['boulevard', 'furnishing', 'median'].includes(sourceType)) return 'planting';
      if (sourceType === 'sidewalk') return 'concrete';
      if (['parking', 'parking_lane'].includes(sourceType)) return 'asphalt';
      return 'asphalt';
    })());
    const kind = classify(sourceType);
    return {
      sourceType,
      surface,
      label: zone.label || sourceType.replace(/_/g, ' '),
      kind,
      startM,
      endM,
      centerM: (startM + endM) / 2,
      widthM,
      ...bandStyle(kind, zone.surface ?? ''),
    };
  });
  const treeOffsetsM = bands
    .filter((band) => band.kind === 'planting' && band.widthM >= 0.55)
    .map((band) => band.centerM);
  const drivableKinds = new Set<StreetBandKind>(['motor', 'parking', 'cycle']);
  const curbOffsetsM = compiledSection.renderCurbs === false
    ? []
    : bands.slice(0, -1).flatMap((band, index) => {
      const next = bands[index + 1];
      return drivableKinds.has(band.kind) !== drivableKinds.has(next.kind)
        ? [band.endM]
        : [];
    });
  const composition = bands
    .filter((band) => band.widthM >= 0.4 && !['setback'].includes(band.sourceType))
    .map((band) => `${band.label} ${band.widthM.toFixed(1)}m`)
    .join(', ');
  return withVariant({
    archetypeId: pilotId,
    title: entry.title ?? pilotId.replace(/_/g, ' '),
    rowM,
    bands,
    markings: addMarkings(pilotId, bands),
    treeOffsetsM,
    curbOffsetsM,
    renderCurbs: curbOffsetsM.length > 0,
    renderSummary: `exact ${rowM.toFixed(1)}m right-of-way cross-section: ${composition}`,
    isPilot: true,
  });
}

export const CATALOG_STREET_ARCHETYPE_IDS = Object.freeze(CATALOG.map((entry) => entry.id));
