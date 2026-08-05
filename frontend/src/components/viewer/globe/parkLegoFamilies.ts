import {
  archetypeOwnedParkKitForFamily,
  archetypeOwnedParkKitForSelection,
} from './parkArchetypeOwnedKits';

/** Public Realm LEGO V1 park families. These ids are shared with the backend
 * capability contract and are deliberately separate from catalog archetype
 * ids: one executable family can serve more than one compatible archetype. */
export const PARK_LEGO_FAMILY_VERSION = 1 as const;

export const PARK_LEGO_FAMILY_IDS = [
  'park_pocket_courtyard',
  'park_neighborhood_community',
  'park_civic_plaza',
  'park_linear_greenway',
  'park_skate_archetype_v0',
  'park_inclusive_playground_v0',
  'park_dog_archetype_v0',
  'park_splash_pad_v0',
  'park_community_garden_v0',
  'park_water_ecology',
] as const;

export type ParkLegoFamilyId = (typeof PARK_LEGO_FAMILY_IDS)[number];
export type ParkLegoPlantingStructure =
  | 'garden_courtyard'
  | 'formal_quad'
  | 'naturalistic_grove'
  | 'open_meadow'
  | 'active_recreation';
export type ParkLegoMaterialPattern =
  | 'rustic_gravel'
  | 'modern_turf'
  | 'native_meadow'
  | 'urban_pavers'
  | 'english_pastoral'
  | 'modern_minimal'
  | 'mediterranean_xeriscape'
  | 'tropical_lush';
export type ParkLegoPlaygroundStyle = 'timber' | 'steel' | 'nature' | 'contemporary';
export type ParkLegoShadeStyle = 'timber_pergola' | 'fabric_sail' | 'steel_canopy' | 'thatched';

export interface ParkLegoPalette {
  ground: string;
  lawn: string;
  meadow: string;
  path: string;
  pathEdge: string;
  playSurface: string;
  pavilionPad: string;
  timber: string;
  timberDark: string;
  metal: string;
  accent: string;
  accentSecondary: string;
  shade: string;
  pavilionRoof: string;
  benchSeat: string;
  benchFrame: string;
}

export interface ParkLegoAppearance {
  familyId: ParkLegoFamilyId;
  familyVersion: typeof PARK_LEGO_FAMILY_VERSION;
  archetypeId: string;
  variantId: string;
  variantIndex: number;
  label: string;
  plantingStructure: ParkLegoPlantingStructure;
  materialPattern: ParkLegoMaterialPattern;
  playgroundStyle: ParkLegoPlaygroundStyle;
  shadeStyle: ParkLegoShadeStyle;
  palette: ParkLegoPalette;
}

export interface ParkLegoContract {
  familyId: ParkLegoFamilyId;
  familyVersion: number;
  archetypeId: string;
  variantId: string;
  source: 'public_realm_lego' | 'legacy';
  supported: boolean;
  schemaVersion?: number;
  kind?: string;
  generator?: string;
  plantingStructure?: string;
  appearanceKitId?: string;
  catalogFingerprint?: string;
  capabilityFingerprint?: string;
  recipeHash?: string;
}

export interface ParkProgramModuleSpec {
  playground: {
    safetyDiameterM: number;
    towerDeckM: readonly [number, number, number];
    towerHeightM: number;
    slideLengthM: number;
    swingBayM: readonly [number, number, number];
  };
  shade: {
    spanM: number;
    lowEdgeHeightM: number;
    highEdgeHeightM: number;
  };
  pavilion: {
    widthM: number;
    depthM: number;
    clearHeightM: number;
    roofHeightM: number;
  };
}

export interface ParkProgramAnchorLayout {
  /** Normalized coordinates in the park's oriented program frame. */
  playground?: readonly [number, number];
  pavilion?: readonly [number, number];
}

export const CIVIC_FOUNTAIN_ASSEMBLY_SPEC = Object.freeze({
  outerRadiusM: 4.8,
  waterRadiusM: 3.9,
  rimHeightM: 0.32,
  waterHeightM: 0.24,
  centerPlinthRadiusM: 0.72,
  centerPlinthHeightM: 0.62,
  wholeElementClearanceM: 6,
});

/** Metric program is invariant across appearance variants. A selected visual
 * style may recolour or reshape finishes, but never scales equipment with the
 * parcel or changes its safety envelope. */
export const PARK_PROGRAM_MODULE_SPEC: Readonly<ParkProgramModuleSpec> = Object.freeze({
  playground: Object.freeze({
    safetyDiameterM: 12,
    towerDeckM: Object.freeze([2.2, 2.2, 0.28] as const),
    towerHeightM: 3.2,
    slideLengthM: 3.4,
    swingBayM: Object.freeze([3.8, 2.4, 2.5] as const),
  }),
  shade: Object.freeze({
    spanM: 7.2,
    lowEdgeHeightM: 3.0,
    highEdgeHeightM: 3.7,
  }),
  pavilion: Object.freeze({
    widthM: 6,
    depthM: 5,
    clearHeightM: 2.8,
    roofHeightM: 1.15,
  }),
});

export const NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS: Readonly<ParkProgramAnchorLayout> = Object.freeze({
  playground: Object.freeze([0.82, 0.22] as const),
  pavilion: Object.freeze([0.77, 0.58] as const),
});

type ParkLegoZone = {
  properties?: unknown;
  zone_type?: string;
};

interface AppearanceDefinition {
  label: string;
  plantingStructure: ParkLegoPlantingStructure;
  materialPattern: ParkLegoMaterialPattern;
  playgroundStyle: ParkLegoPlaygroundStyle;
  shadeStyle: ParkLegoShadeStyle;
  palette: ParkLegoPalette;
}

const RUSTIC: ParkLegoPalette = {
  ground: '#6f805c',
  lawn: '#7fa45f',
  meadow: '#7c8d58',
  path: '#a88f68',
  pathEdge: '#77654d',
  playSurface: '#c3a36d',
  pavilionPad: '#837668',
  timber: '#9a6a3e',
  timberDark: '#66442d',
  metal: '#3d4545',
  accent: '#b65337',
  accentSecondary: '#d39a43',
  shade: '#d2bd89',
  pavilionRoof: '#765842',
  benchSeat: '#8a5c38',
  benchFrame: '#343a39',
};

const MODERN: ParkLegoPalette = {
  ground: '#6c845f',
  lawn: '#6f9a64',
  meadow: '#718369',
  path: '#a5a8a3',
  pathEdge: '#707876',
  playSurface: '#8a726d',
  pavilionPad: '#8d918e',
  timber: '#9d815f',
  timberDark: '#685744',
  metal: '#4c5c5b',
  accent: '#d66045',
  accentSecondary: '#e0b64f',
  shade: '#d7d6c8',
  pavilionRoof: '#697674',
  benchSeat: '#9b8060',
  benchFrame: '#364344',
};

const MEADOW: ParkLegoPalette = {
  ground: '#788259',
  lawn: '#83a263',
  meadow: '#96935a',
  path: '#aa9368',
  pathEdge: '#786b4e',
  playSurface: '#b58f59',
  pavilionPad: '#887b69',
  timber: '#8a633d',
  timberDark: '#5b442e',
  metal: '#48514b',
  accent: '#9d6940',
  accentSecondary: '#d2b45e',
  shade: '#c8a862',
  pavilionRoof: '#776047',
  benchSeat: '#806043',
  benchFrame: '#3e4741',
};

const CONTEMPORARY: ParkLegoPalette = {
  ground: '#687b69',
  lawn: '#739c6b',
  meadow: '#75866a',
  path: '#969b98',
  pathEdge: '#5f6c6d',
  playSurface: '#927168',
  pavilionPad: '#858b89',
  timber: '#ad845b',
  timberDark: '#6c543e',
  metal: '#34464d',
  accent: '#ce583e',
  accentSecondary: '#4f8ca3',
  shade: '#d9c966',
  pavilionRoof: '#53666a',
  benchSeat: '#9f7856',
  benchFrame: '#2f4147',
};

const PASTORAL: ParkLegoPalette = {
  ...RUSTIC,
  ground: '#71845e',
  lawn: '#83a965',
  meadow: '#849369',
  path: '#b0a078',
  pavilionRoof: '#6f5542',
};

const XERISCAPE: ParkLegoPalette = {
  ...MEADOW,
  ground: '#938968',
  lawn: '#839263',
  meadow: '#a69667',
  path: '#b19a70',
  pathEdge: '#806a4c',
  playSurface: '#b7775a',
  pavilionPad: '#9c876c',
  accent: '#ba5f42',
  shade: '#d3b270',
  pavilionRoof: '#a56647',
};

const TROPICAL: ParkLegoPalette = {
  ...CONTEMPORARY,
  ground: '#4f7659',
  lawn: '#5c9362',
  meadow: '#4e7858',
  path: '#9b8062',
  pathEdge: '#5f5142',
  playSurface: '#a76651',
  pavilionPad: '#81715e',
  timber: '#8b603c',
  timberDark: '#4f3728',
  shade: '#b49357',
  pavilionRoof: '#86683f',
};

const POCKET_VARIANTS: readonly AppearanceDefinition[] = Object.freeze([
  {
    label: 'Rustic Timber & Gravel',
    plantingStructure: 'garden_courtyard',
    materialPattern: 'rustic_gravel',
    playgroundStyle: 'timber',
    shadeStyle: 'timber_pergola',
    palette: RUSTIC,
  },
  {
    label: 'Modern Steel & Turf',
    plantingStructure: 'formal_quad',
    materialPattern: 'modern_turf',
    playgroundStyle: 'steel',
    shadeStyle: 'steel_canopy',
    palette: MODERN,
  },
  {
    label: 'Natural Meadow',
    plantingStructure: 'naturalistic_grove',
    materialPattern: 'native_meadow',
    playgroundStyle: 'nature',
    shadeStyle: 'timber_pergola',
    palette: MEADOW,
  },
  {
    label: 'Urban Contemporary',
    plantingStructure: 'garden_courtyard',
    materialPattern: 'urban_pavers',
    playgroundStyle: 'contemporary',
    shadeStyle: 'fabric_sail',
    palette: CONTEMPORARY,
  },
]);

const NEIGHBORHOOD_VARIANTS: readonly AppearanceDefinition[] = Object.freeze([
  {
    ...POCKET_VARIANTS[0],
    plantingStructure: 'active_recreation',
  },
  {
    ...POCKET_VARIANTS[1],
    plantingStructure: 'active_recreation',
  },
  {
    ...POCKET_VARIANTS[2],
    plantingStructure: 'naturalistic_grove',
  },
  {
    ...POCKET_VARIANTS[3],
    plantingStructure: 'active_recreation',
  },
]);

const COMMUNITY_VARIANTS: readonly AppearanceDefinition[] = Object.freeze([
  {
    label: 'English Pastoral',
    plantingStructure: 'naturalistic_grove',
    materialPattern: 'english_pastoral',
    playgroundStyle: 'timber',
    shadeStyle: 'timber_pergola',
    palette: PASTORAL,
  },
  {
    label: 'Modern Minimalist',
    plantingStructure: 'active_recreation',
    materialPattern: 'modern_minimal',
    playgroundStyle: 'steel',
    shadeStyle: 'steel_canopy',
    palette: MODERN,
  },
  {
    label: 'Mediterranean Xeriscape',
    plantingStructure: 'naturalistic_grove',
    materialPattern: 'mediterranean_xeriscape',
    playgroundStyle: 'nature',
    shadeStyle: 'fabric_sail',
    palette: XERISCAPE,
  },
  {
    label: 'Tropical Lush',
    plantingStructure: 'naturalistic_grove',
    materialPattern: 'tropical_lush',
    playgroundStyle: 'timber',
    shadeStyle: 'thatched',
    palette: TROPICAL,
  },
]);

/** Appearance-only kits for cricket variants that do not yet claim a full
 * compiler family. The dedicated cricket assembly owns the playable program;
 * these definitions only select compatible perimeter trees, benches and
 * materials after the drape is complete. */
const CRICKET_DRESSING_VARIANTS: readonly AppearanceDefinition[] = Object.freeze([
  {
    label: 'Village Green',
    plantingStructure: 'naturalistic_grove',
    materialPattern: 'english_pastoral',
    playgroundStyle: 'timber',
    shadeStyle: 'thatched',
    palette: PASTORAL,
  },
  {
    label: 'Municipal Oval',
    plantingStructure: 'active_recreation',
    materialPattern: 'modern_minimal',
    playgroundStyle: 'steel',
    shadeStyle: 'steel_canopy',
    palette: MODERN,
  },
  {
    label: 'South Asian Ground',
    plantingStructure: 'open_meadow',
    materialPattern: 'urban_pavers',
    playgroundStyle: 'contemporary',
    shadeStyle: 'fabric_sail',
    palette: CONTEMPORARY,
  },
  {
    label: 'Caribbean Beach Pitch',
    plantingStructure: 'open_meadow',
    materialPattern: 'tropical_lush',
    playgroundStyle: 'timber',
    shadeStyle: 'thatched',
    palette: TROPICAL,
  },
]);

interface ParkSelectionMapping {
  variantId: string;
  appearanceKitId: string;
  plantingStructure: string;
}

function fourVariantMappings(
  archetypeId: string,
  appearanceKitIds: readonly string[],
  plantingStructures: readonly string[],
): readonly ParkSelectionMapping[] {
  return Object.freeze(appearanceKitIds.map((appearanceKitId, index) => Object.freeze({
    variantId: `${archetypeId}_v${index}`,
    appearanceKitId,
    plantingStructure: plantingStructures[index],
  })));
}

/** Exact frontend mirror of the backend's executable park-family
 * selections. Nested recipes are never repaired here: incompatible identities
 * remain unsupported so the live scene cannot claim a different program than
 * the compiler persisted. */
const PARK_FAMILY_SELECTIONS: Readonly<
  Record<ParkLegoFamilyId, Readonly<Record<string, readonly ParkSelectionMapping[]>>>
> = Object.freeze({
  park_pocket_courtyard: Object.freeze({
    urban_pocket_park: fourVariantMappings(
      'urban_pocket_park',
      ['rustic_timber_gravel_v1', 'modern_steel_turf_v1', 'natural_meadow_v1', 'urban_contemporary_v1'],
      ['garden_courtyard', 'formal_quad', 'naturalistic_grove', 'garden_courtyard'],
    ),
  }),
  park_neighborhood_community: Object.freeze({
    neighborhood_park: fourVariantMappings(
      'neighborhood_park',
      ['rustic_timber_gravel_v1', 'modern_steel_turf_v1', 'natural_meadow_v1', 'urban_contemporary_v1'],
      ['active_recreation', 'active_recreation', 'naturalistic_grove', 'active_recreation'],
    ),
    community_park: fourVariantMappings(
      'community_park',
      ['english_pastoral_v1', 'modern_minimalist_v1', 'mediterranean_xeriscape_v1', 'tropical_lush_v1'],
      ['naturalistic_grove', 'active_recreation', 'naturalistic_grove', 'naturalistic_grove'],
    ),
  }),
  park_civic_plaza: Object.freeze({
    formal_civic_plaza: Object.freeze([Object.freeze({
      variantId: 'formal_civic_plaza_v0',
      appearanceKitId: 'neoclassical_stone_v1',
      plantingStructure: 'paved_plaza',
    })]),
  }),
  park_linear_greenway: Object.freeze({
    linear_park_greenway: Object.freeze([Object.freeze({
      variantId: 'linear_park_greenway_v0',
      appearanceKitId: 'rail_trail_v1',
      plantingStructure: 'naturalistic_grove',
    })]),
  }),
  park_skate_archetype_v0: Object.freeze({
    skate_park: Object.freeze([Object.freeze({
      variantId: 'skate_park_v0',
      appearanceKitId: 'skate_park_v0_reference_skin',
      plantingStructure: 'skate_archetype_v0',
    })]),
  }),
  park_inclusive_playground_v0: Object.freeze({
    inclusive_playground: Object.freeze([Object.freeze({
      variantId: 'inclusive_playground_v0', appearanceKitId: 'inclusive_playground_v0_reference_skin', plantingStructure: 'inclusive_playground_v0',
    })]),
  }),
  park_dog_archetype_v0: Object.freeze({
    dog_park: Object.freeze([Object.freeze({
      variantId: 'dog_park_v0', appearanceKitId: 'dog_park_v0_reference_skin', plantingStructure: 'dog_park_v0',
    })]),
  }),
  park_splash_pad_v0: Object.freeze({
    splash_pad_area: Object.freeze([Object.freeze({
      variantId: 'splash_pad_area_v0', appearanceKitId: 'splash_pad_area_v0_reference_skin', plantingStructure: 'splash_pad_area_v0',
    })]),
  }),
  park_community_garden_v0: Object.freeze({
    community_garden: Object.freeze([Object.freeze({
      variantId: 'community_garden_v0', appearanceKitId: 'community_garden_v0_reference_skin', plantingStructure: 'community_garden_v0',
    })]),
  }),
  park_water_ecology: Object.freeze({
    stormwater_retention_pond: Object.freeze([Object.freeze({
      variantId: 'stormwater_retention_pond_v0',
      appearanceKitId: 'naturalistic_pond_v1',
      plantingStructure: 'reservoir_perimeter',
    })]),
  }),
});

function normalizeId(value: unknown): string {
  return String(value ?? '').trim().toLowerCase().replace(/-/g, '_');
}

function isFamilyId(value: string): value is ParkLegoFamilyId {
  return (PARK_LEGO_FAMILY_IDS as readonly string[]).includes(value);
}

const LOWERCASE_HEX_64 = /^[0-9a-f]{64}$/;

function isTrustedRecipeHash(value: unknown): value is string {
  return typeof value === 'string' && LOWERCASE_HEX_64.test(value);
}

function familyForArchetype(archetypeId: string, role: string): ParkLegoFamilyId | null {
  if (archetypeId.startsWith('urban_pocket_park')) {
    return 'park_pocket_courtyard';
  }
  if (
    archetypeId.startsWith('neighborhood_park')
    || archetypeId.startsWith('community_park')
  ) {
    return 'park_neighborhood_community';
  }
  if (archetypeId.startsWith('formal_civic_plaza')) return 'park_civic_plaza';
  if (archetypeId.startsWith('linear_park_greenway')) return 'park_linear_greenway';
  if (archetypeId === 'skate_park') return 'park_skate_archetype_v0';
  if (archetypeId === 'inclusive_playground') return 'park_inclusive_playground_v0';
  if (archetypeId === 'dog_park') return 'park_dog_archetype_v0';
  if (archetypeId === 'splash_pad_area') return 'park_splash_pad_v0';
  if (archetypeId === 'community_garden') return 'park_community_garden_v0';
  if (archetypeId.startsWith('stormwater_retention_pond')) return 'park_water_ecology';
  if (!archetypeId && role === 'courtyard') return 'park_pocket_courtyard';
  return null;
}

function defaultArchetype(familyId: ParkLegoFamilyId): string {
  switch (familyId) {
    case 'park_pocket_courtyard': return 'urban_pocket_park';
    case 'park_neighborhood_community': return 'neighborhood_park';
    case 'park_civic_plaza': return 'formal_civic_plaza';
    case 'park_linear_greenway': return 'linear_park_greenway';
    case 'park_skate_archetype_v0': return 'skate_park';
    case 'park_inclusive_playground_v0': return 'inclusive_playground';
    case 'park_dog_archetype_v0': return 'dog_park';
    case 'park_splash_pad_v0': return 'splash_pad_area';
    case 'park_community_garden_v0': return 'community_garden';
    case 'park_water_ecology': return 'stormwater_retention_pond';
  }
}

function canonicalVariantId(archetypeId: string, raw: unknown): { id: string; index: number } {
  const normalized = normalizeId(raw);
  const match = normalized.match(/(?:_variant_|_v)([0-3])$/);
  const index = match ? Number(match[1]) : 0;
  return { id: `${archetypeId}_v${index}`, index };
}

/** Resolve the nested compiler contract first, then legacy archetype fields.
 * Unsupported future family versions remain visible as contracts but are not
 * treated as executable V1 by the live procedural renderer. */
export function resolveParkLegoContract(zone: ParkLegoZone): ParkLegoContract | null {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const nested = props.public_realm_lego && typeof props.public_realm_lego === 'object'
    ? props.public_realm_lego as Record<string, unknown>
    : null;
  const role = normalizeId(props._plan_role);
  const legacyArchetype = normalizeId(
    props.green_space_archetype_id ?? props.plaza_archetype_id,
  );

  if (nested) {
    const nestedFamily = typeof nested.family_id === 'string' ? nested.family_id : '';
    if (!isFamilyId(nestedFamily)) return null;
    const familyId = nestedFamily;
    const familyVersion = typeof nested.family_version === 'number'
      ? nested.family_version
      : Number.NaN;
    const schemaVersion = typeof nested.schema_version === 'number'
      ? nested.schema_version
      : Number.NaN;
    const kind = typeof nested.kind === 'string' ? nested.kind : '';
    const generator = typeof nested.generator === 'string' ? nested.generator : '';
    const archetypeId = typeof nested.archetype_id === 'string' ? nested.archetype_id : '';
    const variantId = typeof nested.variant_id === 'string' ? nested.variant_id : '';
    const plantingStructure = typeof nested.planting_structure === 'string'
      ? nested.planting_structure
      : '';
    const appearanceKitId = typeof nested.appearance_kit_id === 'string'
      ? nested.appearance_kit_id
      : '';
    const selection = PARK_FAMILY_SELECTIONS[familyId][archetypeId]?.find(
      (candidate) => candidate.variantId === variantId,
    );
    const mappingIsExact = Boolean(
      selection
      && selection.appearanceKitId === appearanceKitId
      && selection.plantingStructure === plantingStructure,
    );
    const catalogFingerprint = nested?.catalog_fingerprint;
    const capabilityFingerprint = nested?.capability_fingerprint;
    const recipeHash = nested?.recipe_hash;
    const trustedRecipeIdentity = schemaVersion === 1
      && kind === 'park'
      && generator === 'park_kit'
      && isTrustedRecipeHash(catalogFingerprint)
      && isTrustedRecipeHash(capabilityFingerprint)
      && isTrustedRecipeHash(recipeHash);
    return {
      familyId,
      familyVersion,
      archetypeId,
      variantId,
      source: 'public_realm_lego',
      supported: familyVersion === PARK_LEGO_FAMILY_VERSION
        && mappingIsExact
        && trustedRecipeIdentity,
      ...(Number.isFinite(schemaVersion) ? { schemaVersion } : {}),
      ...(kind ? { kind } : {}),
      ...(generator ? { generator } : {}),
      ...(plantingStructure ? { plantingStructure } : {}),
      ...(appearanceKitId ? { appearanceKitId } : {}),
      ...(typeof catalogFingerprint === 'string'
        ? { catalogFingerprint }
        : {}),
      ...(typeof capabilityFingerprint === 'string'
        ? { capabilityFingerprint }
        : {}),
      ...(typeof recipeHash === 'string'
        ? { recipeHash }
        : {}),
    };
  }

  const familyId = familyForArchetype(legacyArchetype, role);
  if (!familyId) return null;
  const archetypeId = legacyArchetype || defaultArchetype(familyId);
  const variant = canonicalVariantId(
    archetypeId,
    props.green_space_selected_variant_id ?? props.plaza_selected_variant_id,
  );
  const legacySelection = PARK_FAMILY_SELECTIONS[familyId][archetypeId]?.find(
    (candidate) => candidate.variantId === variant.id,
  );
  return {
    familyId,
    familyVersion: PARK_LEGO_FAMILY_VERSION,
    archetypeId,
    variantId: variant.id,
    source: 'legacy',
    supported: Boolean(legacySelection),
  };
}

export function resolveParkLegoAppearance(zone: ParkLegoZone): ParkLegoAppearance | null {
  const contract = resolveParkLegoContract(zone);
  if (!contract?.supported) return null;
  if (
    contract.familyId !== 'park_pocket_courtyard'
    && contract.familyId !== 'park_neighborhood_community'
  ) return null;
  const variantIndex = canonicalVariantId(contract.archetypeId, contract.variantId).index;
  const variants = contract.familyId === 'park_pocket_courtyard'
    ? POCKET_VARIANTS
    : contract.archetypeId.startsWith('community_park')
      ? COMMUNITY_VARIANTS
      : NEIGHBORHOOD_VARIANTS;
  const definition = variants[variantIndex] ?? variants[0];
  const contractPlanting = contract.plantingStructure;
  const knownPlanting = (
    contractPlanting === 'garden_courtyard'
    || contractPlanting === 'formal_quad'
    || contractPlanting === 'naturalistic_grove'
    || contractPlanting === 'open_meadow'
    || contractPlanting === 'active_recreation'
  ) ? contractPlanting : null;
  // The neighborhood/community family always owns playground and pavilion
  // programs. Formal-quad/garden furniture rules intentionally suppress those
  // modules, so they are incompatible even if a stale caller requests them.
  const plantingStructure = knownPlanting && (
    contract.familyId === 'park_pocket_courtyard'
    || knownPlanting === 'active_recreation'
    || knownPlanting === 'naturalistic_grove'
    || knownPlanting === 'open_meadow'
  ) ? knownPlanting : definition.plantingStructure;
  return {
    familyId: contract.familyId,
    familyVersion: PARK_LEGO_FAMILY_VERSION,
    archetypeId: contract.archetypeId,
    variantId: `${contract.archetypeId}_v${variantIndex}`,
    variantIndex,
    ...definition,
    plantingStructure,
  };
}

export function isExecutableParkLegoFamily(zone: ParkLegoZone): boolean {
  return resolveParkLegoContract(zone)?.supported === true;
}

/** Archetype-owned surface and depth kits bypass the paid AI drape. Their
 * exact material bundle and fixed geometry are the visual source of truth. */
export function usesArchetypeOwnedParkSurface(zone: ParkLegoZone): boolean {
  const contract = resolveParkLegoContract(zone);
  if (contract?.supported !== true) return false;
  const kit = archetypeOwnedParkKitForFamily(contract.familyId);
  const selection = archetypeOwnedParkKitForSelection(contract.archetypeId, contract.variantId);
  return kit !== null && selection?.familyId === kit.familyId;
}

/** Choose a lightweight scene-dressing family even when an archetype does
 * not yet have a full compiler family. This never claims LEGO compatibility:
 * it only weights safe procedural props after the ground drape is complete. */
export function resolveParkDressingFamily(zone: ParkLegoZone): ParkLegoFamilyId {
  const contract = resolveParkLegoContract(zone);
  if (contract?.supported) return contract.familyId;
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const archetypeId = normalizeId(
    props.green_space_archetype_id
      ?? props.plaza_archetype_id
      ?? props.green_space_aesthetic
      ?? props.plaza_aesthetic,
  );
  const role = normalizeId(props._plan_role);
  const zoneType = normalizeId(zone.zone_type);
  if (
    zoneType === 'plaza'
    || zoneType === 'parking'
    || role === 'plaza'
    || archetypeId.includes('plaza')
    || archetypeId.includes('square')
  ) return 'park_civic_plaza';
  if (
    archetypeId.includes('pond')
    || archetypeId.includes('wetland')
    || archetypeId.includes('reservoir')
    || archetypeId.includes('watershed')
    || archetypeId.includes('riparian')
  ) return 'park_water_ecology';
  if (
    archetypeId.includes('linear')
    || archetypeId.includes('greenway')
    || archetypeId.includes('promenade')
    || archetypeId.includes('riverfront')
  ) return 'park_linear_greenway';
  if (
    role === 'courtyard'
    || archetypeId.includes('pocket')
    || archetypeId.includes('courtyard')
    || archetypeId.includes('garden')
  ) return 'park_pocket_courtyard';
  return 'park_neighborhood_community';
}

/** Resolve an archetype-specific visual kit for post-drape scene dressing.
 * Unlike `resolveParkLegoAppearance`, this function does not imply that the
 * archetype has a compiler-owned LEGO family or authorize generic program
 * modules such as playgrounds and picnic shelters. */
export function resolveParkDressingAppearance(
  zone: ParkLegoZone,
): ParkLegoAppearance | null {
  const executableAppearance = resolveParkLegoAppearance(zone);
  if (executableAppearance) return executableAppearance;
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const archetypeId = normalizeId(
    props.green_space_archetype_id ?? props.plaza_archetype_id,
  );
  if (!archetypeId.startsWith('cricket_pitch_oval')) return null;
  const variant = canonicalVariantId(
    'cricket_pitch_oval',
    props.green_space_selected_variant_id ?? props.plaza_selected_variant_id,
  );
  const definition = CRICKET_DRESSING_VARIANTS[variant.index]
    ?? CRICKET_DRESSING_VARIANTS[0];
  return {
    familyId: 'park_neighborhood_community',
    familyVersion: PARK_LEGO_FAMILY_VERSION,
    archetypeId: 'cricket_pitch_oval',
    variantId: variant.id,
    variantIndex: variant.index,
    ...definition,
  };
}

export function resolveParkProgramAnchorLayout(
  zone: ParkLegoZone,
): Readonly<ParkProgramAnchorLayout> | undefined {
  const contract = resolveParkLegoContract(zone);
  return contract?.supported && contract.familyId === 'park_neighborhood_community'
    ? NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS
    : undefined;
}
