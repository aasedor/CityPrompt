import type { SiteZone } from '@/types';

/**
 * Interchangeable material packages for the neighborhood-park LEGO pilot.
 * The park profile owns topology and metric program geometry; a skin may only
 * change surface colour, texture cadence and material finish.
 */
export type ParkSkinMaterialRole =
  | 'lawn'
  | 'path'
  | 'meadow'
  | 'rain_garden'
  | 'playground'
  | 'pavilion';

export type ParkSkinGroundPattern =
  | 'rustic_aggregate'
  | 'synthetic_turf_grid'
  | 'natural_meadow'
  | 'permeable_paver';

export interface ParkSkinMaterial {
  fill: string;
  edge: string;
}

export interface ParkSkinAtlas {
  albedo: string;
  normal: string;
  roughness: string;
  ao: string;
  sourceReference: string;
}

export interface ParkSkinTextureSet {
  albedo: string;
  normal: string;
  roughness: string;
  ao: string;
  metresPerTile: number;
}

export interface ParkSkinMaterialKit {
  base: Readonly<ParkSkinTextureSet>;
  materials: Readonly<Record<ParkSkinMaterialRole, ParkSkinTextureSet>>;
}

export interface ParkKitSkin {
  id: string;
  version: number;
  label: string;
  topologyFamily: 'neighborhood_park';
  groundPattern: ParkSkinGroundPattern;
  baseGround: string;
  grainPalette: readonly string[];
  atlas: Readonly<ParkSkinAtlas>;
  materialKit?: Readonly<ParkSkinMaterialKit>;
  materials: Readonly<Record<ParkSkinMaterialRole, ParkSkinMaterial>>;
}

function atlas(variant: string): ParkSkinAtlas {
  const root = `/park-skins/neighborhood-park/${variant}`;
  const sourceRoot = '/archetypes/openspaces/neighborhood-park';
  return {
    albedo: `${root}/albedo.jpg`,
    normal: `${root}/normal.png`,
    roughness: `${root}/roughness.jpg`,
    ao: `${root}/ao.jpg`,
    sourceReference: `${sourceRoot}/${variant}_angle_90.jpg`,
  };
}

function adaptiveUrbanTexture(role: string, metresPerTile: number): ParkSkinTextureSet {
  const root = `/park-skins/neighborhood-park/adaptive-urban/${role}`;
  return {
    albedo: `${root}/albedo.jpg`,
    normal: `${root}/normal.png`,
    roughness: `${root}/roughness.jpg`,
    ao: `${root}/ao.jpg`,
    metresPerTile,
  };
}

const ADAPTIVE_URBAN_MATERIAL_KIT: ParkSkinMaterialKit = {
  base: adaptiveUrbanTexture('paver', 5),
  materials: {
    lawn: adaptiveUrbanTexture('lawn', 6),
    path: adaptiveUrbanTexture('asphalt', 4),
    meadow: adaptiveUrbanTexture('planting', 3),
    rain_garden: adaptiveUrbanTexture('planting', 3),
    playground: adaptiveUrbanTexture('safety', 3),
    pavilion: adaptiveUrbanTexture('timber', 3),
  },
};

const SKINS = {
  neighborhood_park_v0: {
    id: 'neighborhood-park-rustic-v1',
    version: 1,
    label: 'Rustic Timber & Gravel',
    topologyFamily: 'neighborhood_park',
    groundPattern: 'rustic_aggregate',
    baseGround: '#697651',
    grainPalette: ['#7f8358', '#5d6c49', '#8a7750', '#596142'],
    atlas: atlas('variant_0'),
    materials: {
      lawn: { fill: '#74865a', edge: '#526642' },
      path: { fill: '#b29a70', edge: '#715f43' },
      meadow: { fill: '#8c8952', edge: '#626b42' },
      rain_garden: { fill: '#5e7759', edge: '#425d48' },
      playground: { fill: '#9a7c55', edge: '#67533b' },
      pavilion: { fill: '#817260', edge: '#554a3d' },
    },
  },
  neighborhood_park_v1: {
    id: 'neighborhood-park-modern-v1',
    version: 1,
    label: 'Modern Steel & Turf',
    topologyFamily: 'neighborhood_park',
    groundPattern: 'synthetic_turf_grid',
    baseGround: '#607761',
    grainPalette: ['#66866a', '#56705d', '#748878', '#4e6656'],
    atlas: atlas('variant_1'),
    materials: {
      lawn: { fill: '#4f825c', edge: '#3d664b' },
      path: { fill: '#a7aaa6', edge: '#596361' },
      meadow: { fill: '#718469', edge: '#536958' },
      rain_garden: { fill: '#55766b', edge: '#3d5f58' },
      playground: { fill: '#756b69', edge: '#4d5152' },
      pavilion: { fill: '#999e9c', edge: '#535b5a' },
    },
  },
  neighborhood_park_v2: {
    id: 'neighborhood-park-meadow-v1',
    version: 1,
    label: 'Natural Meadow',
    topologyFamily: 'neighborhood_park',
    groundPattern: 'natural_meadow',
    baseGround: '#768052',
    grainPalette: ['#92905a', '#68764b', '#a18c4f', '#566b47'],
    atlas: atlas('variant_2'),
    materials: {
      lawn: { fill: '#748b59', edge: '#556d47' },
      path: { fill: '#b5a983', edge: '#746848' },
      meadow: { fill: '#9a9253', edge: '#6c7045' },
      rain_garden: { fill: '#5a7658', edge: '#405e49' },
      playground: { fill: '#9b875c', edge: '#685c43' },
      pavilion: { fill: '#806f58', edge: '#584b3d' },
    },
  },
  neighborhood_park_v3: {
    id: 'neighborhood-park-urban-v1',
    version: 1,
    label: 'Urban Contemporary',
    topologyFamily: 'neighborhood_park',
    groundPattern: 'permeable_paver',
    baseGround: '#667466',
    grainPalette: ['#6e7e6c', '#59695d', '#778477', '#526159'],
    atlas: atlas('variant_3'),
    materialKit: ADAPTIVE_URBAN_MATERIAL_KIT,
    materials: {
      lawn: { fill: '#5d8260', edge: '#45684f' },
      path: { fill: '#9d9d95', edge: '#515b5b' },
      meadow: { fill: '#788169', edge: '#596957' },
      rain_garden: { fill: '#50736a', edge: '#385b55' },
      playground: { fill: '#986a57', edge: '#69483d' },
      pavilion: { fill: '#8e918c', edge: '#505958' },
    },
  },
} as const satisfies Record<string, ParkKitSkin>;

export const NEIGHBORHOOD_PARK_SKIN_VARIANTS = Object.freeze(Object.keys(SKINS));

function normalizeId(value: unknown): string {
  return typeof value === 'string' ? value.trim().toLowerCase().replace(/-/g, '_') : '';
}

/** Resolve a skin only for the bounded one-family pilot. */
export function resolveParkKitSkin(
  zone: Pick<SiteZone, 'properties'>,
): ParkKitSkin | null {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const archetypeId = normalizeId(props.green_space_archetype_id);
  const variantId = normalizeId(props.green_space_selected_variant_id);
  const key = variantId || archetypeId;
  if (!archetypeId.startsWith('neighborhood_park') && !key.startsWith('neighborhood_park')) {
    return null;
  }
  return SKINS[key as keyof typeof SKINS] ?? null;
}

export function isNeighborhoodParkLegoPilot(
  zone: Pick<SiteZone, 'properties'>,
): boolean {
  return resolveParkKitSkin(zone) !== null;
}
