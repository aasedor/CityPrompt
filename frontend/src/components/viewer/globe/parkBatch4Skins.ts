export interface Batch4ParkSkinDefinition {
  archetypeId: string;
  variantId: string;
  slug: string;
  roles: readonly ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'];
  people: false;
  largeBuildings: false;
}

const ROLES = ['paver', 'lawn', 'asphalt', 'planting', 'safety', 'timber'] as const;

const skin = (
  archetypeId: string,
  slug: string,
): Batch4ParkSkinDefinition => Object.freeze({
  archetypeId,
  variantId: `${archetypeId}_v0`,
  slug,
  roles: ROLES,
  people: false,
  largeBuildings: false,
});

/** Reviewed batch-4 selections and their stationary PBR libraries. Source
 * pixels set palette statistics only; they are never projected over a site. */
export const BATCH4_PARK_SKINS = Object.freeze([
  skin('community_park', 'community-park-english-pastoral'),
  skin('pond_lake', 'pond-lake-naturalistic'),
  skin('wetland_rain_garden', 'wetland-rain-garden-native'),
  skin('japanese_garden', 'japanese-stroll-garden'),
  skin('botanical_garden', 'botanical-collection-garden'),
  skin('urban_forest', 'urban-forest-native'),
  skin('reservoir_watershed_park', 'reservoir-watershed-concrete-edge'),
  skin('amphitheater_lawn', 'amphitheater-lawn-terraced'),
  skin('riparian_buffer', 'riparian-buffer-native'),
  skin('playground_adventure', 'playground-adventure-timber'),
]);

export function batch4ParkSkinForSelection(
  archetypeId: string,
  variantId: string,
): Batch4ParkSkinDefinition | null {
  return BATCH4_PARK_SKINS.find((candidate) => (
    candidate.archetypeId === archetypeId && candidate.variantId === variantId
  )) ?? null;
}

export function batch4ParkSkinRoot(definition: Batch4ParkSkinDefinition): string {
  return `/park-skins/${definition.slug}/adaptive-v1`;
}
