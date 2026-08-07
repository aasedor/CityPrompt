export interface Batch7ParkSkinDefinition {
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
  variantId: string,
  slug: string,
): Batch7ParkSkinDefinition => Object.freeze({
  archetypeId,
  variantId,
  slug,
  roles: ROLES,
  people: false,
  largeBuildings: false,
});

/** Batch 7 is image-led and exact-selection only. Source pixels provide
 * material statistics and crop evidence, but are never projected onto the
 * site. The LEGO geometry remains adaptive to the receiving polygon. */
export const BATCH7_PARK_SKINS = Object.freeze([
  skin('regional_park', 'regional_park_v0', 'regional-park-english-landscape'),
  skin('beer_garden', 'beer_garden_v0', 'beer-garden-munich-chestnut'),
  skin('sunken_plaza', 'sunken_plaza_v0', 'sunken-plaza-intimate-courtyard'),
  skin('stepped_terraced_plaza', 'stepped_terraced_plaza_v3', 'stepped-plaza-modernist-cascade'),
  skin('market_square', 'market_square_v1', 'market-square-festival-lawn'),
  skin('promenade_boardwalk', 'promenade_boardwalk_v0', 'promenade-maritime-boardwalk'),
  skin('fountain_water_feature', 'fountain_water_feature_v1', 'fountain-formal-reflecting-pool'),
  skin('swimming_pool_complex', 'swimming_pool_complex_v0', 'swimming-natural-pond'),
  skin('nature_preserve', 'nature_preserve_v1', 'nature-preserve-tallgrass-prairie'),
  skin('riverfront_park_beach', 'riverfront_park_beach_v1', 'riverfront-lake-swimming-beach'),
]);

export function batch7ParkSkinForSelection(
  archetypeId: string,
  variantId: string,
): Batch7ParkSkinDefinition | null {
  return BATCH7_PARK_SKINS.find((candidate) => (
    candidate.archetypeId === archetypeId && candidate.variantId === variantId
  )) ?? null;
}

export function batch7ParkSkinRoot(definition: Batch7ParkSkinDefinition): string {
  return `/park-skins/${definition.slug}/adaptive-v1`;
}
