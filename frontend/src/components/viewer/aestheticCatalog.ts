
import type { SiteZoneProperties } from '@/types';
import buildingArchetypeLibrary from '@/data/buildingArchetypes.json';
import streetPathArchetypeLibrary from '@/data/streetPathArchetypes.json';
import openSpaceArchetypeLibrary from '@/data/openSpaceArchetypes.json';
import archetypeVisualSystem from '@/data/archetypeVisualSystem.json';
import { TRANSPORT_STANDARDS, type TransportStandardEntry } from '@/data/transportStandards';

export type AestheticCategory = {
  id: string;
  label: string;
  description: string;
};

export type TransportModeKey = 'walking' | 'bicycle' | 'transit' | 'automobile';

export type StyleProfile = {
  materials?: string[];
  massing?: string;
  facadeRhythm?: string;
  roofForm?: string;
  frontageType?: string;
  windowStyle?: string;
  heightTendency?: string;
  streetRelationship?: string;
  renderingMood?: string;
  articulation?: string;
  publicRealm?: string;
  corridorCharacter?: string;
  movementHierarchy?: string;
  surfaceType?: string;
  plantingCharacter?: string;
  edgeConditions?: string;
  landscapeCharacter?: string;
  pavingType?: string;
  plantingType?: string;
  seatingRealm?: string;
  waterFeatures?: string;
  opennessEnclosure?: string;
  [key: string]: unknown;
};

export type ArchetypeImage = {
  id: string;
  label: string;
  description: string;
  camera: 'street' | 'corner' | 'promenade' | 'courtyard';
  imageUrl: string;
  thumbnailUrl?: string;
  imagePath?: string;
  lighting?: string;
  generationTags?: string[];
  prompt?: {
    positive: string;
    negative: string;
    compositionRules: string[];
    renderingRules: string[];
    output: {
      width: number;
      height: number;
      aspectRatio: string;
    };
  };
};

export type GenerationStyleInput = {
  domain?: 'building' | 'street_pathway' | 'park_plaza';
  developmentType?: string;
  buildingSubcategory?: string;
  subtype?: string;
  aestheticCategoryId?: string;
  aestheticCategoryLabel?: string;
  archetypeId: string;
  archetypeLabel: string;
  archetypeImageUrl: string;
  archetypeImagePath?: string;
  archetypeImageIds?: string[];
  generationTags?: string[];
  imagePrompt?: {
    positive: string;
    negative: string;
    compositionRules: string[];
    renderingRules: string[];
    output: {
      width: number;
      height: number;
      aspectRatio: string;
    };
  };
  styleProfile: StyleProfile;
  downstreamHints?: {
    sceneDressing?: string[];
    materialDirection?: string[];
    reuseKeys?: string[];
  };
};

export type ArchetypeVariant = {
  id: string;
  label: string;
  thumbnailUrl?: string;
  renderPrompt?: { mapOverlay?: string; roofView?: string; negative?: string };
  facadeDetail?: Record<string, string>;
  roofDetail?: Record<string, string>;
  shadeId?: string;
  palette?: Record<string, string>;
  description?: string;
  /** Per-variant floor/area overrides — when set, these take priority over archetype-level values */
  minFloors?: number;
  maxFloors?: number;
  suggestedFloorHeight?: number;
  suggestedAreaSqm?: number;
  minAreaSqm?: number;
  maxAreaSqm?: number;
  suggestedWidth_m?: number;
  suggestedDepth_m?: number;
  aspectRatio?: string;
};

export type BuildingFootprintProfile = 'rectangle' | 'l_shape' | 'u_shape' | 'courtyard';

export type FootprintProfileGuidance = {
  recommendedWidth_m: [number, number];
  recommendedDepth_m: [number, number];
  recommendedFloors: [number, number];
  wingDepth_m?: [number, number];
  minimumCourtyard_m?: number;
};

export type FootprintCompatibility = {
  preferredProfiles: BuildingFootprintProfile[];
  recommendedWidth_m: [number, number];
  recommendedDepth_m: [number, number];
  recommendedFloors: [number, number];
  wingDepth_m?: [number, number];
  profiles?: Partial<Record<BuildingFootprintProfile, FootprintProfileGuidance>>;
  preferredBayMultiple_m?: number;
  minimumCourtyard_m?: number;
  notes?: string[];
};

export type AestheticOption = {
  id: string;
  categoryId?: string;
  label: string;
  description: string;
  photoUrl: string;
  photoUrls?: string[];
  transportModes?: TransportModeKey[];
  developmentType?: string;
  developmentTypes?: string[];
  buildingSubcategory?: string;
  generationTags?: string[];
  archetypeImages?: ArchetypeImage[];
  styleProfile?: StyleProfile;
  generationStyleInput?: Partial<GenerationStyleInput>;
  minFloors?: number;
  maxFloors?: number;
  suggestedFloorHeight?: number;
  suggestedAreaSqm?: number;
  minAreaSqm?: number;
  maxAreaSqm?: number;
  suggestedWidth_m?: number;
  suggestedDepth_m?: number;
  minWidth_m?: number;
  maxWidth_m?: number;
  minDepth_m?: number;
  maxDepth_m?: number;
  aspectRatio?: string;
  footprintCompatibility?: FootprintCompatibility;
  propertyPresets?: Partial<SiteZoneProperties>;
  variants?: ArchetypeVariant[];
  /** Authored engineering section used as both picker preview and AI drape guidance. */
  standardSection?: Pick<TransportStandardEntry,
    'sectionSvgUrl' | 'standardFamily' | 'citation' | 'rowM' | 'targetSpeedKmh'>;
};

type ArchetypeVisualVariant = {
  id: string;
  title: string;
  description: string;
  camera: string;
  lighting: string;
};

type ArchetypeVisualSystem = {
  output: {
    width: number;
    height: number;
    aspectRatio: string;
  };
  sharedCompositionRules: string[];
  sharedRenderingRules: string[];
  sharedNegativeGuidance: string[];
  cardVariants: ArchetypeVisualVariant[];
};

type ArchetypeSeed = {
  id: string;
  title: string;
  aestheticCategory: string;
  description: string;
  buildingSubcategory?: string;
  spaceType?: 'park' | 'plaza';
  transportModes?: TransportModeKey[];
  volume?: string;
  generationTags?: string[];
  styleProfile?: StyleProfile;
  developmentType?: string;
  developmentTypes?: string[];
  prompt?: {
    subject?: string;
    details?: string[];
    negative?: string[];
  };
  minFloors?: number;
  maxFloors?: number;
  suggestedFloorHeight?: number;
  suggestedAreaSqm?: number;
  minAreaSqm?: number;
  maxAreaSqm?: number;
  suggestedWidth_m?: number;
  suggestedDepth_m?: number;
  minWidth_m?: number;
  maxWidth_m?: number;
  minDepth_m?: number;
  maxDepth_m?: number;
  aspectRatio?: string;
  footprintCompatibility?: FootprintCompatibility;
  propertyPresets?: Partial<SiteZoneProperties>;
  variants?: ArchetypeVariant[];
  thumbnailUrl?: string;
};

type ArchetypeLibrary = {
  categories: AestheticCategory[];
  archetypes: ArchetypeSeed[];
};

const VISUAL_SYSTEM = archetypeVisualSystem as ArchetypeVisualSystem;
const BUILDING_LIBRARY = buildingArchetypeLibrary as ArchetypeLibrary & { visualSystem?: ArchetypeVisualSystem };
const ROAD_LIBRARY = streetPathArchetypeLibrary as ArchetypeLibrary;
const OPEN_SPACE_LIBRARY = openSpaceArchetypeLibrary as ArchetypeLibrary;

const BUILDING_VISUAL_SYSTEM = BUILDING_LIBRARY.visualSystem || VISUAL_SYSTEM;
const APP_BASE_URL = import.meta.env.BASE_URL || '/';

function resolvePublicAssetUrl(path: string): string {
  if (!path.startsWith('/')) return path;
  const normalizedBase = APP_BASE_URL.endsWith('/') ? APP_BASE_URL : `${APP_BASE_URL}/`;
  return `${normalizedBase}${path.slice(1)}`;
}

export const TRANSPORT_MODE_ORDER: TransportModeKey[] = ['walking', 'bicycle', 'transit', 'automobile'];

export const TRANSPORT_MODE_OPTIONS: Array<{ id: TransportModeKey; label: string; description: string }> = [
  { id: 'walking', label: 'Walking', description: 'Pedestrian-focused movement and public realm comfort' },
  { id: 'bicycle', label: 'Bicycle', description: 'Protected or low-stress cycling movement' },
  { id: 'transit', label: 'Transit', description: 'Frequent bus/tram/LRT movement and stops' },
  { id: 'automobile', label: 'Automobile', description: 'Vehicle access for daily circulation and servicing' },
];
function normalizeCamera(camera?: string): ArchetypeImage['camera'] {
  if (camera === 'corner' || camera === 'promenade' || camera === 'courtyard') {
    return camera;
  }
  return 'street';
}

function dedupeStrings(values: unknown): string[] {
  if (!Array.isArray(values)) return [];
  const set = new Set<string>();
  for (const value of values) {
    if (typeof value === 'string' && value.trim().length > 0) {
      set.add(value.trim());
    }
  }
  return Array.from(set);
}

function joinPromptParts(parts: Array<string | undefined>): string {
  return parts
    .filter((part): part is string => typeof part === 'string' && part.trim().length > 0)
    .map((part) => part.trim())
    .join('. ');
}

function buildImagePrompt(
  visualSystem: ArchetypeVisualSystem,
  seed: ArchetypeSeed,
  variant: ArchetypeVisualVariant,
): NonNullable<ArchetypeImage['prompt']> {
  const compositionRules = [...visualSystem.sharedCompositionRules];
  const renderingRules = [
    ...visualSystem.sharedRenderingRules,
    `${variant.title} with ${variant.lighting} lighting`,
  ];

  const positive = joinPromptParts([
    seed.prompt?.subject,
    ...dedupeStrings(seed.prompt?.details),
    ...compositionRules,
    ...renderingRules,
    `Output ${visualSystem.output.width}x${visualSystem.output.height} (${visualSystem.output.aspectRatio})`,
  ]);

  const negative = joinPromptParts([
    ...dedupeStrings(seed.prompt?.negative),
    ...visualSystem.sharedNegativeGuidance,
  ]);

  return {
    positive,
    negative,
    compositionRules,
    renderingRules,
    output: {
      width: visualSystem.output.width,
      height: visualSystem.output.height,
      aspectRatio: visualSystem.output.aspectRatio,
    },
  };
}

const FRONT_DAY_VARIANT_ID = 'variant_0';

function toArchetypeImages(
  domainPath: string,
  visualSystem: ArchetypeVisualSystem,
  seed: ArchetypeSeed,
): ArchetypeImage[] {
  const variants = visualSystem.cardVariants || [];
  // Derive the folder from the authored thumbnail path whenever one exists.
  // Building ids and asset folders are not always the same slug (for example
  // contemporary_midrise_residential vs contemporary_mid_rise_residential),
  // so falling back to the catalogue id merely because a folder uses
  // underscores produces valid-looking URLs that 404 in the picker.
  const thumbSlug = seed.thumbnailUrl
    ? seed.thumbnailUrl.split('/').slice(-2, -1)[0]
    : undefined;
  const folderSlug = thumbSlug || seed.id;
  return variants.map((variant) => {
    const imagePath = `/archetypes/${domainPath}/${folderSlug}/${variant.id}.png`;
    const thumbPath = `/archetypes/${domainPath}/${folderSlug}/${variant.id}_thumb.jpg`;
    return {
      id: `${seed.id}_${variant.id}`,
      label: variant.title,
      description: variant.description,
      camera: normalizeCamera(variant.camera),
      imageUrl: resolvePublicAssetUrl(imagePath),
      thumbnailUrl: resolvePublicAssetUrl(thumbPath),
      imagePath,
      lighting: variant.lighting,
      generationTags: dedupeStrings(seed.generationTags),
      prompt: buildImagePrompt(visualSystem, seed, variant),
    };
  });
}

function getPrimaryArchetypeImage(images: ArchetypeImage[]): ArchetypeImage | undefined {
  return images.find((image) => image.id.endsWith(`_${FRONT_DAY_VARIANT_ID}`)) || images[0];
}

function categoryLabel(categories: AestheticCategory[], id?: string): string | undefined {
  if (!id) return undefined;
  return categories.find((category) => category.id === id)?.label;
}

function toAestheticOption(
  domain: 'building' | 'street_pathway' | 'park_plaza',
  domainPath: string,
  visualSystem: ArchetypeVisualSystem,
  categories: AestheticCategory[],
  seed: ArchetypeSeed,
): AestheticOption {
  const archetypeImages = toArchetypeImages(domainPath, visualSystem, seed);
  const primary = getPrimaryArchetypeImage(archetypeImages);
  const orderedArchetypeImages = primary
    ? [primary, ...archetypeImages.filter((image) => image.id !== primary.id)]
    : archetypeImages;
  const tags = dedupeStrings(seed.generationTags);
  const styleProfile = (seed.styleProfile || {}) as StyleProfile;
  const category = seed.aestheticCategory;

  // The catalogue's hero is the canonical archetype reference. Design
  // variants remain fallback references, but generated 3D previews must never
  // replace the authored archetype image in the picker.
  const authoredHero = seed.thumbnailUrl
    ? resolvePublicAssetUrl(seed.thumbnailUrl)
    : undefined;
  const heroFromVariant = seed.variants?.[0]?.thumbnailUrl;
  const resolvedVariantHero = heroFromVariant
    ? resolvePublicAssetUrl(heroFromVariant)
    : undefined;
  const heroUrl = authoredHero || resolvedVariantHero || primary?.imageUrl || '';
  const photoUrls = [
    authoredHero,
    resolvedVariantHero,
    ...orderedArchetypeImages.map((image) => image.imageUrl),
  ].filter((url, index, values): url is string => Boolean(url) && values.indexOf(url) === index);

  return {
    id: seed.id,
    categoryId: category,
    label: seed.title,
    description: seed.description,
    photoUrl: heroUrl,
    photoUrls,
    transportModes: Array.isArray(seed.transportModes) ? seed.transportModes : undefined,
    developmentType: seed.developmentType || (Array.isArray(seed.developmentTypes) ? seed.developmentTypes[0] : undefined),
    developmentTypes: seed.developmentType ? [seed.developmentType] : (Array.isArray(seed.developmentTypes) ? seed.developmentTypes : undefined),
    buildingSubcategory: seed.buildingSubcategory,
    generationTags: tags,
    archetypeImages: orderedArchetypeImages,
    styleProfile,
    minFloors: seed.minFloors,
    maxFloors: seed.maxFloors,
    suggestedFloorHeight: seed.suggestedFloorHeight,
    suggestedAreaSqm: seed.suggestedAreaSqm,
    minAreaSqm: seed.minAreaSqm,
    maxAreaSqm: seed.maxAreaSqm,
    suggestedWidth_m: seed.suggestedWidth_m,
    suggestedDepth_m: seed.suggestedDepth_m,
    minWidth_m: seed.minWidth_m,
    maxWidth_m: seed.maxWidth_m,
    minDepth_m: seed.minDepth_m,
    maxDepth_m: seed.maxDepth_m,
    aspectRatio: seed.aspectRatio,
    footprintCompatibility: seed.footprintCompatibility,
    propertyPresets: seed.propertyPresets,
    variants: seed.variants,
    generationStyleInput: {
      domain,
      buildingSubcategory: seed.buildingSubcategory || seed.id,
      subtype: seed.spaceType || seed.buildingSubcategory || seed.id,
      aestheticCategoryId: category,
      aestheticCategoryLabel: categoryLabel(categories, category),
      archetypeId: primary?.id || seed.id,
      archetypeLabel: primary?.label || seed.title,
      archetypeImageUrl: primary?.imageUrl || '',
      archetypeImagePath: primary?.imagePath,
      archetypeImageIds: orderedArchetypeImages.map((image) => image.id),
      generationTags: tags,
      imagePrompt: primary?.prompt,
      styleProfile,
      downstreamHints: {
        sceneDressing: tags,
        materialDirection: styleProfile.materials || [],
        reuseKeys: [
          seed.id,
          seed.aestheticCategory,
          seed.buildingSubcategory || seed.spaceType || seed.id,
        ].filter(Boolean) as string[],
      },
    },
  };
}

function mapPresetRecord(options: AestheticOption[]): Record<string, Partial<SiteZoneProperties>> {
  const record: Record<string, Partial<SiteZoneProperties>> = {};
  for (const option of options) {
    if (option.propertyPresets && Object.keys(option.propertyPresets).length > 0) {
      record[option.id] = option.propertyPresets;
    }
  }
  return record;
}
export const BUILDING_AESTHETIC_CATEGORIES_V2: AestheticCategory[] = BUILDING_LIBRARY.categories;
export const BUILDING_AESTHETIC_OPTIONS_V2: AestheticOption[] = BUILDING_LIBRARY.archetypes.map((seed) =>
  toAestheticOption('building', 'buildings', BUILDING_VISUAL_SYSTEM, BUILDING_LIBRARY.categories, seed),
);

// Derived from the catalog (like buildings/openspaces) so new street categories
// — e.g. "Calgary Street Manual" — appear in the picker automatically instead of
// being silently dropped by a hardcoded list.
export const ROADWAY_AESTHETIC_CATEGORIES_V2: AestheticCategory[] = ROAD_LIBRARY.categories;
const TRANSPORT_STANDARD_BY_ARCHETYPE = new Map(
  TRANSPORT_STANDARDS.map((standard) => [standard.archetypeId, standard]),
);

export const ROADWAY_AESTHETIC_OPTIONS_V2: AestheticOption[] = ROAD_LIBRARY.archetypes.map((seed) => {
  const option = toAestheticOption(
    'street_pathway',
    'streets',
    VISUAL_SYSTEM,
    ROAD_LIBRARY.categories,
    seed,
  );
  const standard = TRANSPORT_STANDARD_BY_ARCHETYPE.get(seed.id);
  if (!standard?.sectionSvgUrl) return option;

  const sectionUrl = resolvePublicAssetUrl(standard.sectionSvgUrl);
  const sectionImage: ArchetypeImage = {
    id: `${seed.id}_manual_section`,
    label: `${standard.title} — Manual cross-section`,
    description: [
      `${standard.standardFamily} engineering section`,
      standard.rowM ? `${standard.rowM} m right-of-way` : null,
      standard.targetSpeedKmh ? `${standard.targetSpeedKmh} km/h target speed` : null,
    ].filter(Boolean).join(' · '),
    camera: 'street',
    imageUrl: sectionUrl,
    imagePath: standard.sectionSvgUrl,
    lighting: 'engineering diagram',
  };

  return {
    ...option,
    photoUrl: sectionUrl,
    photoUrls: dedupeStrings([sectionUrl, ...(option.photoUrls ?? [])]),
    archetypeImages: [
      sectionImage,
      ...(option.archetypeImages ?? []).filter((image) => image.imageUrl !== sectionUrl),
    ],
    standardSection: {
      sectionSvgUrl: standard.sectionSvgUrl,
      standardFamily: standard.standardFamily,
      citation: standard.citation,
      rowM: standard.rowM,
      targetSpeedKmh: standard.targetSpeedKmh,
    },
    generationStyleInput: {
      ...option.generationStyleInput,
      archetypeImageUrl: sectionUrl,
      archetypeImagePath: standard.sectionSvgUrl,
      archetypeImageIds: [
        sectionImage.id,
        ...(option.generationStyleInput?.archetypeImageIds ?? []),
      ],
    },
  };
});

const OPEN_SPACE_OPTIONS = OPEN_SPACE_LIBRARY.archetypes.map((seed) =>
  toAestheticOption('park_plaza', 'openspaces', VISUAL_SYSTEM, OPEN_SPACE_LIBRARY.categories, seed),
);

const GREEN_SPACE_CATEGORY_IDS = new Set(
  OPEN_SPACE_LIBRARY.archetypes
    .filter((seed) => seed.spaceType !== 'plaza')
    .map((seed) => seed.aestheticCategory),
);

const PLAZA_CATEGORY_IDS = new Set(
  OPEN_SPACE_LIBRARY.archetypes
    .filter((seed) => seed.spaceType === 'plaza')
    .map((seed) => seed.aestheticCategory),
);

export const GREEN_SPACE_AESTHETIC_CATEGORIES_V2: AestheticCategory[] = OPEN_SPACE_LIBRARY.categories.filter(
  (category) => GREEN_SPACE_CATEGORY_IDS.has(category.id),
);

export const PLAZA_AESTHETIC_CATEGORIES_V2: AestheticCategory[] = OPEN_SPACE_LIBRARY.categories.filter(
  (category) => PLAZA_CATEGORY_IDS.has(category.id),
);

export const GREEN_SPACE_AESTHETIC_OPTIONS_V2: AestheticOption[] = OPEN_SPACE_OPTIONS.filter((option) => {
  const seed = OPEN_SPACE_LIBRARY.archetypes.find((item) => item.id === option.id);
  return seed?.spaceType !== 'plaza';
});

export const PLAZA_AESTHETIC_OPTIONS_V2: AestheticOption[] = OPEN_SPACE_OPTIONS.filter((option) => {
  const seed = OPEN_SPACE_LIBRARY.archetypes.find((item) => item.id === option.id);
  return seed?.spaceType === 'plaza';
});

// Combined parks + plazas — used by the unified "Parks / Plazas" picker so
// users see all openspace archetypes regardless of the zone subtype they
// drew the polygon with. The panel routes the selection to the correct
// persistence prefix (green_space vs plaza) based on the picked archetype's
// spaceType.
export const OPENSPACE_AESTHETIC_OPTIONS_V2: AestheticOption[] = OPEN_SPACE_OPTIONS;
export const OPENSPACE_AESTHETIC_CATEGORIES_V2: AestheticCategory[] = OPEN_SPACE_LIBRARY.categories.filter(
  (category) => GREEN_SPACE_CATEGORY_IDS.has(category.id) || PLAZA_CATEGORY_IDS.has(category.id),
);

export const ROADWAY_AESTHETIC_PRESETS_V2: Record<string, Partial<SiteZoneProperties>> = mapPresetRecord(ROADWAY_AESTHETIC_OPTIONS_V2);
export const GREEN_SPACE_AESTHETIC_PRESETS_V2: Record<string, Partial<SiteZoneProperties>> = mapPresetRecord(GREEN_SPACE_AESTHETIC_OPTIONS_V2);
export const PLAZA_AESTHETIC_PRESETS_V2: Record<string, Partial<SiteZoneProperties>> = mapPresetRecord(PLAZA_AESTHETIC_OPTIONS_V2);

/**
 * Map a zone_type (and optional development_type property) to the set of
 * `developmentTypes` values that should be shown.  Returns `null` when no
 * filtering should be applied (i.e. show everything).
 */
export function getAllowedDevelopmentTypes(
  zoneType: string,
  developmentType?: string,
): string[] | null {
  // If the user has already picked a specific development_type property,
  // use exact match for granular filtering (e.g. residential_single_family)
  if (developmentType) {
    return [developmentType];
  }

  // Fall back to zone_type level filtering
  switch (zoneType) {
    case 'residential':
      return ['residential', 'residential_single_family', 'residential_duplex', 'residential_multifamily', 'residential_highrise'];
    case 'commercial':
      return ['commercial', 'commercial_light', 'commercial_retail', 'commercial_office'];
    case 'industrial':
      return ['industrial', 'industrial_light', 'industrial_heavy', 'industrial_warehouse'];
    case 'mixed_use':
      return ['mixed_use', 'mixed-use'];
    case 'building':
    case 'development_area':
    default:
      // Generic building zone or unknown — show everything
      return null;
  }
}

/**
 * Filter building archetype options by zone / development type.
 * If `allowedTypes` is null, all options pass through.
 */
export function filterOptionsByDevelopmentType(
  options: AestheticOption[],
  allowedTypes: string[] | null,
): AestheticOption[] {
  if (!allowedTypes) return options;
  return options.filter((option) => {
    // Check single developmentType first (preferred)
    if (option.developmentType) {
      return allowedTypes.includes(option.developmentType);
    }
    // Fallback to array for backwards compatibility
    if (!option.developmentTypes || option.developmentTypes.length === 0) return true;
    return option.developmentTypes.some((dt) => allowedTypes.includes(dt));
  });
}

export function normalizeTransportModes(value: unknown): TransportModeKey[] {
  if (!Array.isArray(value)) return [];
  const allowed = new Set<TransportModeKey>(TRANSPORT_MODE_ORDER);
  const unique = new Set<TransportModeKey>();
  for (const mode of value) {
    if (typeof mode === 'string' && allowed.has(mode as TransportModeKey)) {
      unique.add(mode as TransportModeKey);
    }
  }
  return TRANSPORT_MODE_ORDER.filter((mode) => unique.has(mode));
}

export function inferTransportModesFromProperties(properties: SiteZoneProperties): TransportModeKey[] {
  const explicit = normalizeTransportModes(properties.transport_modes);
  if (explicit.length > 0) return explicit;

  const profile = String(properties.mobility_profile || '').toLowerCase();
  if (profile === 'walking_only') return ['walking'];
  if (profile === 'pedestrian_first') return ['walking', 'bicycle'];
  if (profile === 'vehicle_access') return ['automobile', 'transit'];
  if (profile === 'balanced') return ['walking', 'bicycle', 'transit', 'automobile'];

  return ['walking', 'automobile'];
}

export function inferMobilityProfileFromModes(modes: TransportModeKey[]): 'walking_only' | 'pedestrian_first' | 'balanced' | 'vehicle_access' {
  const hasWalk = modes.includes('walking');
  const hasBike = modes.includes('bicycle');
  const hasTransit = modes.includes('transit');
  const hasAuto = modes.includes('automobile');

  if (hasWalk && !hasBike && !hasTransit && !hasAuto) return 'walking_only';
  if (hasAuto && !hasWalk && !hasBike) return 'vehicle_access';
  if (hasWalk && !hasAuto) return 'pedestrian_first';
  if (hasAuto && (hasTransit || hasBike || hasWalk)) return 'balanced';
  return 'pedestrian_first';
}

export function applyModeDrivenRoadDefaults(
  base: SiteZoneProperties,
  inputModes: TransportModeKey[],
  volumeInput?: string,
): SiteZoneProperties {
  const modes = TRANSPORT_MODE_ORDER.filter((mode) => inputModes.includes(mode));
  const next: SiteZoneProperties = { ...base };

  next.transport_modes = modes.length > 0 ? modes : undefined;

  const activeCount = Math.max(modes.length, 1);
  const ranks = new Map<TransportModeKey, number>();
  modes.forEach((mode, idx) => ranks.set(mode, idx + 1));
  TRANSPORT_MODE_ORDER
    .filter((mode) => !modes.includes(mode))
    .forEach((mode) => ranks.set(mode, Math.min(4, activeCount + 1)));

  next.priority_pedestrian = ranks.get('walking');
  next.priority_cycling = ranks.get('bicycle');
  next.priority_transit = ranks.get('transit');
  next.priority_auto = ranks.get('automobile');

  const volume = (volumeInput || String(next.volume || 'medium')) as 'low' | 'medium' | 'high';
  const hasWalk = modes.includes('walking');
  const hasBike = modes.includes('bicycle');
  const hasTransit = modes.includes('transit');
  const hasAuto = modes.includes('automobile');

  next.mobility_profile = inferMobilityProfileFromModes(modes);
  next.has_sidewalks = hasWalk;
  next.sidewalks = hasWalk ? 'both' : 'none';

  if (hasAuto) {
    next.width = volume === 'high' ? 22 : volume === 'low' ? 12 : 16;
    next.lane_count = volume === 'high' ? 4 : 2;
    next.road_surface = hasTransit ? 'asphalt' : (next.road_surface as string) || 'asphalt';
  } else if (hasBike && hasWalk) {
    next.width = volume === 'high' ? 11 : volume === 'low' ? 7 : 9;
    next.lane_count = 1;
    next.road_surface = (next.road_surface as string) || 'asphalt';
  } else if (hasWalk) {
    next.width = volume === 'high' ? 8 : volume === 'low' ? 5 : 6;
    next.lane_count = 1;
    next.road_surface = (next.road_surface as string) || 'paver';
  }

  if (hasTransit && !hasAuto) {
    next.width = Math.max(12, Number(next.width || 12));
    next.lane_count = Math.max(2, Number(next.lane_count || 2));
  }

  return next;
}

export function mapDevelopmentTypeToCategory(_value?: string): string | undefined {
  return undefined;
}






